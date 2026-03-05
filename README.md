# 🔮 Wanda — Consultas Inteligentes em Linguagem Natural

> **Pergunte em português. Obtenha dados.**

Wanda é uma plataforma SaaS que transforma perguntas em linguagem natural em consultas SQL precisas, utilizando a API Claude da Anthropic. Conecte seu banco de dados e comece a extrair insights sem escrever uma linha de código.

---

## ✨ Funcionalidades

- **NL → SQL com IA**: Claude AI converte perguntas em português para SQL otimizado
- **Multi-banco**: PostgreSQL, MySQL, SQL Server, SQLite
- **Dashboards**: Gráficos interativos com Chart.js
- **Exportação**: CSV e PDF profissional
- **Histórico**: Todas as consultas salvas com paginação
- **Feedback**: Sistema 👍/👎 para melhoria contínua
- **Autenticação**: Login seguro com bcrypt e Flask-Login

---

## 🚀 Deploy Rápido (Render.com)

1. Fork este repositório
2. Crie um banco MySQL (Railway ou PlanetScale)
3. No Render.com: New Web Service → conecte o fork
4. Configure as variáveis de ambiente:
   - `SECRET_KEY`, `ANTHROPIC_API_KEY`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD`
5. Deploy!

---

## 💻 Desenvolvimento Local

```bash
git clone https://github.com/Lsadagurschi/Wanda.git
cd Wanda
cp .env.example .env
# Edite o .env com suas credenciais
docker-compose up -d
# Acesse http://localhost:5000
```

---

## 📁 Estrutura

```
src/
├── main.py          # Ponto de entrada Flask
├── extensions.py    # db, login_manager, bcrypt
├── models/          # User, DatabaseConnection, Query
├── routes/          # landing, auth, dashboard, connections, query
├── services/        # nl2sql (Claude), db_connector, export
└── templates/       # HTML com Tailwind CSS
```

---

## 🔑 Variáveis de Ambiente

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | Chave secreta Flask |
| `ANTHROPIC_API_KEY` | API key do Claude (Anthropic) |
| `DB_HOST` | Host do MySQL |
| `DB_PORT` | Porta (padrão: 3306) |
| `DB_NAME` | Nome do banco |
| `DB_USERNAME` | Usuário do banco |
| `DB_PASSWORD` | Senha do banco |

---

*Powered by Claude AI (Anthropic)*