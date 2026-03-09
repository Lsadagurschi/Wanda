import time
import json
from typing import Optional
from urllib.parse import quote_plus


def get_connection_engine(conn_model):
    """
    Cria um engine SQLAlchemy para o banco de dados do usuário.
    Suporta: postgresql, mysql, sqlite, mssql

    SSL:
    - PostgreSQL (Neon, RDS, Cloud SQL): sslmode=require aplicado automaticamente
    - MySQL: ssl_ca configurável via variável de ambiente
    """
    from sqlalchemy import create_engine

    db_type = conn_model.db_type.lower()

    # Se o usuário forneceu uma connection string completa, usa diretamente
    if conn_model.connection_string:
        url = conn_model.connection_string
        # Garante sslmode=require para Neon e outros provedores cloud PostgreSQL
        if 'neon.tech' in url and 'sslmode' not in url:
            sep = '&' if '?' in url else '?'
            url = f"{url}{sep}sslmode=require"
        engine = create_engine(
            url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 15}
        )
        return engine

    # Senha com URL encoding para caracteres especiais
    password = quote_plus(str(conn_model.password_enc)) if conn_model.password_enc else ''
    username = conn_model.username or ''

    if db_type == 'sqlite':
        url = f"sqlite:///{conn_model.database}"
        return create_engine(url, pool_pre_ping=True)

    elif db_type == 'postgresql':
        host = conn_model.host or 'localhost'
        port = conn_model.port or 5432
        database = conn_model.database or 'postgres'

        url = (
            f"postgresql+psycopg2://{username}:{password}"
            f"@{host}:{port}/{database}"
        )

        # Detecta provedores cloud que exigem SSL obrigatório
        cloud_hosts = ['neon.tech', 'rds.amazonaws.com', 'cloudsql', 'supabase.co',
                       'railway.app', 'render.com', 'elephantsql.com', 'heroku']
        requires_ssl = any(h in host for h in cloud_hosts)

        if requires_ssl:
            # SSL obrigatório para provedores cloud (Neon, RDS, Supabase, etc.)
            connect_args = {
                "connect_timeout": 15,
                "sslmode": "require",
            }
        else:
            # SSL preferencial para hosts locais/privados (não obrigatório)
            connect_args = {
                "connect_timeout": 15,
                "sslmode": "prefer",
            }

        return create_engine(
            url,
            pool_pre_ping=True,
            pool_size=2,
            max_overflow=3,
            pool_timeout=20,
            connect_args=connect_args
        )

    elif db_type == 'mysql':
        host = conn_model.host or 'localhost'
        port = conn_model.port or 3306
        database = conn_model.database or ''

        url = (
            f"mysql+pymysql://{username}:{password}"
            f"@{host}:{port}/{database}"
        )

        # SSL para MySQL em provedores cloud
        cloud_hosts = ['railway.app', 'rds.amazonaws.com', 'planetscale.com',
                       'render.com', 'cleardb.net']
        requires_ssl = any(h in host for h in cloud_hosts)

        connect_args = {"connect_timeout": 15}
        if requires_ssl:
            connect_args["ssl"] = {"ssl_disabled": False}

        return create_engine(
            url,
            pool_pre_ping=True,
            pool_size=2,
            max_overflow=3,
            connect_args=connect_args
        )

    elif db_type == 'mssql':
        host = conn_model.host or 'localhost'
        port = conn_model.port or 1433
        database = conn_model.database or ''

        url = (
            f"mssql+pyodbc://{username}:{password}"
            f"@{host}:{port}/{database}"
            f"?driver=ODBC+Driver+17+for+SQL+Server"
        )
        return create_engine(url, pool_pre_ping=True, connect_args={"timeout": 15})

    else:
        raise ValueError(f"Tipo de banco não suportado: {db_type}")


def test_connection(conn_model) -> dict:
    """Testa se a conexão com o banco está funcionando."""
    try:
        engine = get_connection_engine(conn_model)
        with engine.connect() as conn:
            conn.execute(__import__('sqlalchemy').text("SELECT 1"))
        return {'success': True, 'message': 'Conexão estabelecida com sucesso!'}
    except Exception as e:
        error_msg = str(e)
        # Mensagens de erro mais amigáveis
        if 'SSL' in error_msg or 'ssl' in error_msg:
            return {'success': False, 'message': f'Erro SSL: Verifique se o host requer SSL. Detalhe: {error_msg}'}
        elif 'password authentication failed' in error_msg:
            return {'success': False, 'message': 'Senha incorreta. Verifique as credenciais.'}
        elif 'could not connect to server' in error_msg or 'Connection refused' in error_msg:
            return {'success': False, 'message': f'Host inacessível. Verifique o endereço e a porta. Detalhe: {error_msg}'}
        elif 'does not exist' in error_msg:
            return {'success': False, 'message': f'Banco de dados não encontrado. Verifique o nome do banco. Detalhe: {error_msg}'}
        else:
            return {'success': False, 'message': f'Erro de conexão: {error_msg}'}


def extract_schema(conn_model) -> dict:
    """Extrai o schema (tabelas e colunas) do banco de dados do usuário."""
    from sqlalchemy import inspect, text

    try:
        engine = get_connection_engine(conn_model)
        inspector = inspect(engine)
        schema = {}

        # Para PostgreSQL, inspeciona o schema 'public' por padrão
        db_type = conn_model.db_type.lower()
        schema_name = 'public' if db_type == 'postgresql' else None

        table_names = inspector.get_table_names(schema=schema_name)

        for table_name in table_names:
            columns = []
            for col in inspector.get_columns(table_name, schema=schema_name):
                columns.append({
                    'name': col['name'],
                    'type': str(col['type']),
                    'nullable': col.get('nullable', True)
                })

            # Tentar obter contagem de linhas
            try:
                qualified_name = f'"{schema_name}"."{table_name}"' if schema_name else f'"{table_name}"'
                with engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {qualified_name}"))
                    row_count = result.scalar()
            except Exception:
                row_count = None

            schema[table_name] = {
                'columns': columns,
                'row_count': row_count
            }

        return schema
    except Exception as e:
        raise Exception(f"Erro ao extrair schema: {str(e)}")


def execute_query(conn_model, sql: str, limit: int = 1000) -> dict:
    """
    Executa uma query SQL no banco de dados do usuário.

    Returns:
        dict com: columns, rows, row_count, execution_time_ms, error
    """
    from sqlalchemy import text

    # Segurança: bloquear comandos destrutivos
    sql_upper = sql.strip().upper()
    forbidden = ['DROP ', 'DELETE ', 'TRUNCATE ', 'ALTER ', 'CREATE ', 'INSERT ', 'UPDATE ']
    for cmd in forbidden:
        if sql_upper.startswith(cmd):
            return {
                'columns': [],
                'rows': [],
                'row_count': 0,
                'execution_time_ms': 0,
                'error': f'Comando "{cmd.strip()}" não é permitido por segurança. Apenas SELECT é aceito.'
            }

    try:
        engine = get_connection_engine(conn_model)
        start_time = time.time()

        with engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows = [list(row) for row in result.fetchmany(limit)]

        execution_time = (time.time() - start_time) * 1000

        return {
            'columns': columns,
            'rows': rows,
            'row_count': len(rows),
            'execution_time_ms': round(execution_time, 2),
            'error': None
        }

    except Exception as e:
        return {
            'columns': [],
            'rows': [],
            'row_count': 0,
            'execution_time_ms': 0,
            'error': str(e)
        }
