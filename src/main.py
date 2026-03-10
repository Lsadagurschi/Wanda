import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask
from src.extensions import db, login_manager, bcrypt
from src.models.user import User


def run_migrations(app):
    """Executa migrações automáticas: adiciona colunas novas sem apagar dados existentes."""
    with app.app_context():
        from sqlalchemy import inspect as sa_inspect, text

        inspector = sa_inspect(db.engine)
        existing_tables = inspector.get_table_names()

        # 1. Criar tabelas novas que ainda não existem
        for table in db.metadata.sorted_tables:
            if table.name not in existing_tables:
                try:
                    table.create(db.engine)
                    print(f"[MIGRATION] Tabela criada: {table.name}")
                except Exception as e:
                    print(f"[MIGRATION] Erro ao criar tabela {table.name}: {e}")

        # 2. Adicionar colunas novas à tabela 'users' se não existirem
        if 'users' in existing_tables:
            existing_cols = {col['name'] for col in inspector.get_columns('users')}

            # Mapeamento: nome_coluna -> definição SQL (compatível com MySQL e SQLite)
            is_mysql = 'mysql' in str(db.engine.url)
            is_sqlite = 'sqlite' in str(db.engine.url)

            new_columns = {
                'company':         'VARCHAR(150)',
                'area':            'VARCHAR(100)',
                'profession':      'VARCHAR(100)',
                'department_id':   'INTEGER',
                'is_admin':        'BOOLEAN DEFAULT FALSE',
                'last_login':      'DATETIME',
            }

            for col_name, col_type in new_columns.items():
                if col_name not in existing_cols:
                    try:
                        with db.engine.connect() as conn:
                            conn.execute(text(
                                f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"
                            ))
                            conn.commit()
                        print(f"[MIGRATION] Coluna adicionada: users.{col_name}")
                    except Exception as e:
                        print(f"[MIGRATION] Aviso ao adicionar users.{col_name}: {e}")

        # 3. Adicionar FK department_id se MySQL e tabela departments existir
        # (SQLite não suporta ALTER TABLE ADD FOREIGN KEY — ignorar)
        print("[MIGRATION] Migração concluída.")


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Configurações
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'wanda-secret-key-change-in-production-2024')

    # Determinar URL do banco de dados
    # Prioridade: DATABASE_URL > variáveis individuais DB_* > SQLite (fallback)
    _db_url = os.getenv('DATABASE_URL')
    if not _db_url:
        _db_user = os.getenv('DB_USERNAME')
        _db_pass = os.getenv('DB_PASSWORD')
        _db_host = os.getenv('DB_HOST')
        _db_name = os.getenv('DB_NAME', 'wanda')
        _db_port = os.getenv('DB_PORT', '3306')
        if _db_user and _db_pass and _db_host:
            _db_url = f"mysql+pymysql://{_db_user}:{_db_pass}@{_db_host}:{_db_port}/{_db_name}"
        else:
            # Fallback para SQLite — funciona sem banco externo
            _sqlite_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'wanda.db')
            _db_url = f"sqlite:///{_sqlite_path}"

    # Corrigir dialetos de banco de dados para usar drivers Python puros
    if _db_url.startswith('mysql://') or _db_url.startswith('mysql+mysqldb://'):
        _db_url = _db_url.replace('mysql://', 'mysql+pymysql://', 1)
        _db_url = _db_url.replace('mysql+mysqldb://', 'mysql+pymysql://', 1)
    # postgres:// -> postgresql+psycopg2:// (Heroku/Railway)
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql+psycopg2://', 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = _db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
        'connect_args': _get_ssl_args(_db_url),
    }

    # Inicializar extensões
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registrar blueprints
    from src.routes.landing import landing_bp
    from src.routes.auth import auth_bp
    from src.routes.dashboard import dashboard_bp
    from src.routes.connections import connections_bp
    from src.routes.query import query_bp
    from src.routes.admin import admin_bp

    app.register_blueprint(landing_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(connections_bp)
    app.register_blueprint(query_bp)
    app.register_blueprint(admin_bp)

    # Executar migrações automáticas (cria tabelas novas + adiciona colunas faltantes)
    try:
        run_migrations(app)
    except Exception as e:
        print(f"[MIGRATION] Erro geral na migração: {e}")

    return app


def _get_ssl_args(db_url):
    """Retorna argumentos SSL baseados no tipo de banco e provedor."""
    ssl_providers = ['neon.tech', 'supabase', 'amazonaws.com', 'railway.app', 'planetscale']
    needs_ssl = any(p in db_url for p in ssl_providers)

    if 'postgresql' in db_url or 'postgres' in db_url:
        if needs_ssl:
            return {'sslmode': 'require'}
        return {}
    elif 'mysql' in db_url:
        if needs_ssl:
            return {'ssl': {'ssl_mode': 'REQUIRED'}}
        return {}
    return {}


app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    )
