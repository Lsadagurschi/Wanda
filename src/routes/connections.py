from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from src.extensions import db
from src.models.connection import DatabaseConnection
from src.services.db_connector import test_connection, extract_schema
from datetime import datetime

connections_bp = Blueprint('connections', __name__)


@connections_bp.route('/dashboard/connections')
@login_required
def index():
    conns = DatabaseConnection.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard/connections.html', connections=conns)


@connections_bp.route('/api/connections', methods=['GET'])
@login_required
def list_connections():
    conns = DatabaseConnection.query.filter_by(user_id=current_user.id, is_active=True).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'db_type': c.db_type,
        'host': c.host,
        'database': c.database,
        'last_tested': c.last_tested.isoformat() if c.last_tested else None
    } for c in conns])


@connections_bp.route('/api/connections', methods=['POST'])
@login_required
def create_connection():
    data = request.get_json()

    conn = DatabaseConnection(
        user_id=current_user.id,
        name=data.get('name'),
        db_type=data.get('db_type', 'postgresql'),
        host=data.get('host'),
        port=data.get('port'),
        database=data.get('database'),
        username=data.get('username'),
        password_enc=data.get('password'),  # Em produção: criptografar
        connection_string=data.get('connection_string')
    )

    # Testar conexão antes de salvar
    test_result = test_connection(conn)
    if not test_result['success']:
        return jsonify({'success': False, 'error': test_result['message']}), 400

    conn.last_tested = datetime.utcnow()

    # Extrair schema
    try:
        schema = extract_schema(conn)
        conn.set_schema(schema)
    except Exception as e:
        pass  # Schema opcional

    db.session.add(conn)
    db.session.commit()

    return jsonify({'success': True, 'id': conn.id, 'message': 'Conexão criada com sucesso!'})


@connections_bp.route('/api/connections/<int:conn_id>/test', methods=['POST'])
@login_required
def test_conn(conn_id):
    conn = DatabaseConnection.query.filter_by(id=conn_id, user_id=current_user.id).first_or_404()
    result = test_connection(conn)
    if result['success']:
        conn.last_tested = datetime.utcnow()
        db.session.commit()
    return jsonify(result)


@connections_bp.route('/api/connections/<int:conn_id>/schema', methods=['GET'])
@login_required
def get_schema(conn_id):
    conn = DatabaseConnection.query.filter_by(id=conn_id, user_id=current_user.id).first_or_404()
    try:
        schema = extract_schema(conn)
        conn.set_schema(schema)
        db.session.commit()
        return jsonify({'success': True, 'schema': schema})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@connections_bp.route('/api/connections/<int:conn_id>', methods=['DELETE'])
@login_required
def delete_connection(conn_id):
    conn = DatabaseConnection.query.filter_by(id=conn_id, user_id=current_user.id).first_or_404()
    conn.is_active = False
    db.session.commit()
    return jsonify({'success': True})
