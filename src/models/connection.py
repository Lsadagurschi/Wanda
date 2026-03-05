from src.extensions import db
from datetime import datetime
import json


class DatabaseConnection(db.Model):
    __tablename__ = 'database_connections'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    db_type = db.Column(db.String(20), nullable=False)  # postgresql, mysql, sqlite, mssql
    host = db.Column(db.String(255))
    port = db.Column(db.Integer)
    database = db.Column(db.String(255))
    username = db.Column(db.String(255))
    password_enc = db.Column(db.Text)  # encrypted password
    connection_string = db.Column(db.Text)  # optional direct connection string
    schema_cache = db.Column(db.Text)  # JSON with table/column info
    is_active = db.Column(db.Boolean, default=True)
    last_tested = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    queries = db.relationship('Query', backref='connection', lazy=True)

    def get_schema(self):
        if self.schema_cache:
            return json.loads(self.schema_cache)
        return {}

    def set_schema(self, schema_dict):
        self.schema_cache = json.dumps(schema_dict)

    def __repr__(self):
        return f'<Connection {self.name} ({self.db_type})>'
