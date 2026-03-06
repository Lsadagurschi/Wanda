import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask
from src.extensions import db, login_manager, bcrypt
from src.models.user import User


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
    # Corrigir URL do Postgres no Heroku/Railway (postgres:// -> postgresql://)
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = _db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 280,
        'pool_pre_ping': True
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

    app.register_blueprint(landing_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(connections_bp)
    app.register_blueprint(query_bp)

    # Criar tabelas
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')
