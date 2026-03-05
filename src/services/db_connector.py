import time
import json
from typing import Optional


def get_connection_engine(conn_model):
    """
    Cria um engine SQLAlchemy para o banco de dados do usuário.
    Suporta: postgresql, mysql, sqlite, mssql
    """
    from sqlalchemy import create_engine

    db_type = conn_model.db_type.lower()

    if conn_model.connection_string:
        url = conn_model.connection_string
    elif db_type == 'sqlite':
        url = f"sqlite:///{conn_model.database}"
    elif db_type == 'postgresql':
        url = (
            f"postgresql+psycopg2://{conn_model.username}:{conn_model.password_enc}"
            f"@{conn_model.host}:{conn_model.port or 5432}/{conn_model.database}"
        )
    elif db_type == 'mysql':
        url = (
            f"mysql+pymysql://{conn_model.username}:{conn_model.password_enc}"
            f"@{conn_model.host}:{conn_model.port or 3306}/{conn_model.database}"
        )
    elif db_type == 'mssql':
        url = (
            f"mssql+pyodbc://{conn_model.username}:{conn_model.password_enc}"
            f"@{conn_model.host}:{conn_model.port or 1433}/{conn_model.database}"
            f"?driver=ODBC+Driver+17+for+SQL+Server"
        )
    else:
        raise ValueError(f"Tipo de banco não suportado: {db_type}")

    return create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 10})


def test_connection(conn_model) -> dict:
    """Testa se a conexão com o banco está funcionando."""
    try:
        engine = get_connection_engine(conn_model)
        with engine.connect() as conn:
            conn.execute(__import__('sqlalchemy').text("SELECT 1"))
        return {'success': True, 'message': 'Conexão estabelecida com sucesso!'}
    except Exception as e:
        return {'success': False, 'message': f'Erro de conexão: {str(e)}'}


def extract_schema(conn_model) -> dict:
    """Extrai o schema (tabelas e colunas) do banco de dados do usuário."""
    from sqlalchemy import inspect, text

    try:
        engine = get_connection_engine(conn_model)
        inspector = inspect(engine)
        schema = {}

        for table_name in inspector.get_table_names():
            columns = []
            for col in inspector.get_columns(table_name):
                columns.append({
                    'name': col['name'],
                    'type': str(col['type']),
                    'nullable': col.get('nullable', True)
                })

            # Tentar obter contagem de linhas
            try:
                with engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
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
