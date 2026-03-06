import os
import json
import re
import anthropic


def get_anthropic_client():
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY não configurada. Configure a variável de ambiente.")
    return anthropic.Anthropic(api_key=api_key)


def build_schema_context(schema: dict) -> str:
    """Converte o schema do banco em texto legível para o modelo."""
    if not schema:
        return "Schema não disponível."
    lines = []
    for table, info in schema.items():
        cols = info.get('columns', [])
        col_str = ', '.join([f"{c['name']} ({c['type']})" for c in cols])
        lines.append(f"Tabela: {table}\n  Colunas: {col_str}")
    return '\n'.join(lines)


def natural_language_to_sql(
    natural_language: str,
    schema: dict,
    db_type: str = 'postgresql',
    previous_queries: list = None
) -> dict:
    """
    Converte linguagem natural em SQL usando Claude da Anthropic.
    
    Returns:
        dict com keys: sql, explanation, confidence, error
    """
    client = get_anthropic_client()
    schema_text = build_schema_context(schema)

    history_text = ""
    if previous_queries:
        history_text = "\n\nConsultas anteriores do usuário (para contexto):\n"
        for pq in previous_queries[-3:]:
            history_text += f"- Pergunta: {pq.get('nl', '')}\n  SQL: {pq.get('sql', '')}\n"

    system_prompt = f"""Você é um especialista em SQL e análise de dados. Sua tarefa é converter perguntas em linguagem natural para consultas SQL precisas e eficientes.

Banco de dados: {db_type.upper()}

Schema do banco de dados:
{schema_text}
{history_text}

Regras importantes:
1. Gere APENAS SQL válido para {db_type.upper()}
2. Use aliases descritivos nas colunas
3. Limite resultados a 1000 linhas por padrão (use LIMIT 1000)
4. Prefira JOINs explícitos (INNER JOIN, LEFT JOIN)
5. Nunca gere SQL destrutivo (DELETE, DROP, TRUNCATE, UPDATE sem WHERE)
6. Se a pergunta for ambígua, escolha a interpretação mais segura e comum

Responda SEMPRE em JSON com este formato exato:
{{
  "sql": "SELECT ... FROM ...",
  "explanation": "Explicação em português do que a consulta faz",
  "confidence": 0.95,
  "warnings": []
}}"""

    user_message = f"Pergunta: {natural_language}"

    try:
        response = client.messages.create(
            model=os.getenv('ANTHROPIC_MODEL', 'claude-3-5-haiku-20241022'),
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )

        content = response.content[0].text.strip()

        # Extrair JSON da resposta
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return {
                'sql': result.get('sql', ''),
                'explanation': result.get('explanation', ''),
                'confidence': result.get('confidence', 0.8),
                'warnings': result.get('warnings', []),
                'error': None
            }
        else:
            return {
                'sql': content,
                'explanation': 'SQL gerado pelo assistente.',
                'confidence': 0.7,
                'warnings': [],
                'error': None
            }

    except anthropic.AuthenticationError:
        return {
            'sql': None,
            'explanation': None,
            'confidence': 0,
            'warnings': [],
            'error': 'Chave da API Anthropic inválida. Verifique a variável ANTHROPIC_API_KEY.'
        }
    except anthropic.RateLimitError:
        return {
            'sql': None,
            'explanation': None,
            'confidence': 0,
            'warnings': [],
            'error': 'Limite de requisições da API atingido. Aguarde alguns segundos e tente novamente.'
        }
    except Exception as e:
        return {
            'sql': None,
            'explanation': None,
            'confidence': 0,
            'warnings': [],
            'error': f'Erro ao processar consulta: {str(e)}'
        }


def suggest_visualizations(sql: str, columns: list, row_count: int) -> list:
    """Sugere tipos de visualização adequados para os dados retornados."""
    suggestions = []
    col_names = [c.lower() for c in columns] if columns else []

    # Detectar colunas de data/tempo
    date_cols = [c for c in col_names if any(k in c for k in ['date', 'data', 'time', 'mes', 'ano', 'year', 'month'])]
    # Detectar colunas numéricas por nome comum
    num_cols = [c for c in col_names if any(k in c for k in ['total', 'valor', 'amount', 'count', 'qtd', 'price', 'preco', 'sum', 'avg', 'media'])]

    if date_cols and num_cols:
        suggestions.append({'type': 'line', 'label': 'Gráfico de Linha (Série Temporal)', 'icon': 'trending-up'})
        suggestions.append({'type': 'bar', 'label': 'Gráfico de Barras', 'icon': 'bar-chart-2'})
    elif len(columns) == 2 and row_count <= 20:
        suggestions.append({'type': 'pie', 'label': 'Gráfico de Pizza', 'icon': 'pie-chart'})
        suggestions.append({'type': 'bar', 'label': 'Gráfico de Barras', 'icon': 'bar-chart-2'})
    elif num_cols:
        suggestions.append({'type': 'bar', 'label': 'Gráfico de Barras', 'icon': 'bar-chart-2'})
        suggestions.append({'type': 'scatter', 'label': 'Gráfico de Dispersão', 'icon': 'activity'})

    suggestions.append({'type': 'table', 'label': 'Tabela de Dados', 'icon': 'table'})
    return suggestions
