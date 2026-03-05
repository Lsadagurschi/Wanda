from src.extensions import db
from datetime import datetime
import json


class Query(db.Model):
    __tablename__ = 'queries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    connection_id = db.Column(db.Integer, db.ForeignKey('database_connections.id'), nullable=True)
    natural_language = db.Column(db.Text, nullable=False)
    sql_generated = db.Column(db.Text)
    result_preview = db.Column(db.Text)  # JSON with first 100 rows
    row_count = db.Column(db.Integer)
    execution_time_ms = db.Column(db.Float)
    feedback = db.Column(db.Integer)  # 1 = positive, -1 = negative, 0 = neutral
    feedback_comment = db.Column(db.Text)
    is_saved = db.Column(db.Boolean, default=False)
    title = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_result(self):
        if self.result_preview:
            return json.loads(self.result_preview)
        return []

    def set_result(self, data):
        self.result_preview = json.dumps(data, default=str)

    def __repr__(self):
        return f'<Query {self.id}: {self.natural_language[:50]}>'
