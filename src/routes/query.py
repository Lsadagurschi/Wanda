from flask import Blueprint, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from src.extensions import db
from src.models.connection import DatabaseConnection
from src.models.query import Query
from src.services.nl2sql import natural_language_to_sql, suggest_visualizations
from src.services.db_connector import execute_query
from src.services.export import export_to_csv, export_to_pdf
import io

query_bp = Blueprint('query', __name__)


@query_bp.route('/dashboard/query')
@login_required
def index():
    connections = DatabaseConnection.query.filter_by(user_id=current_user.id, is_active=True).all()
    return render_template('dashboard/query.html', connections=connections)


@query_bp.route('/api/query/ask', methods=['POST'])
@login_required
def ask():
    """Endpoint principal: converte linguagem natural em SQL e executa."""
    data = request.get_json()
    natural_language = data.get('question', '').strip()
    connection_id = data.get('connection_id')
    execute = data.get('execute', True)

    if not natural_language:
        return jsonify({'success': False, 'error': 'Pergunta não pode estar vazia.'}), 400

    # Obter schema do banco
    schema = {}
    db_type = 'generic'
    conn_model = None

    if connection_id:
        conn_model = DatabaseConnection.query.filter_by(
            id=connection_id, user_id=current_user.id, is_active=True
        ).first()
        if conn_model:
            schema = conn_model.get_schema()
            db_type = conn_model.db_type

    # Histórico recente para contexto
    recent = Query.query.filter_by(user_id=current_user.id)\
        .order_by(Query.created_at.desc()).limit(5).all()
    previous = [{'nl': q.natural_language, 'sql': q.sql_generated} for q in recent]

    # Converter NL → SQL via Claude
    nl_result = natural_language_to_sql(natural_language, schema, db_type, previous)

    if nl_result.get('error'):
        return jsonify({'success': False, 'error': nl_result['error']}), 500

    sql = nl_result['sql']
    result_data = {'columns': [], 'rows': [], 'row_count': 0, 'execution_time_ms': 0}
    exec_error = None

    # Executar SQL se solicitado e houver conexão
    if execute and conn_model and sql:
        exec_result = execute_query(conn_model, sql)
        if exec_result.get('error'):
            exec_error = exec_result['error']
        else:
            result_data = exec_result

    # Sugerir visualizações
    viz_suggestions = suggest_visualizations(
        sql,
        result_data.get('columns', []),
        result_data.get('row_count', 0)
    )

    # Salvar no histórico
    query_record = Query(
        user_id=current_user.id,
        connection_id=connection_id,
        natural_language=natural_language,
        sql_generated=sql,
        row_count=result_data.get('row_count', 0),
        execution_time_ms=result_data.get('execution_time_ms', 0)
    )
    if result_data.get('rows'):
        query_record.set_result({
            'columns': result_data['columns'],
            'rows': result_data['rows'][:100]  # Salvar preview de 100 linhas
        })
    db.session.add(query_record)
    db.session.commit()

    return jsonify({
        'success': True,
        'query_id': query_record.id,
        'sql': sql,
        'explanation': nl_result.get('explanation', ''),
        'confidence': nl_result.get('confidence', 0),
        'warnings': nl_result.get('warnings', []),
        'columns': result_data.get('columns', []),
        'rows': result_data.get('rows', []),
        'row_count': result_data.get('row_count', 0),
        'execution_time_ms': result_data.get('execution_time_ms', 0),
        'exec_error': exec_error,
        'visualizations': viz_suggestions
    })


@query_bp.route('/api/query/<int:query_id>/execute', methods=['POST'])
@login_required
def execute_saved(query_id):
    """Re-executa uma query salva."""
    query = Query.query.filter_by(id=query_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    connection_id = data.get('connection_id') or query.connection_id

    if not connection_id:
        return jsonify({'success': False, 'error': 'Nenhuma conexão selecionada.'}), 400

    conn_model = DatabaseConnection.query.filter_by(
        id=connection_id, user_id=current_user.id
    ).first_or_404()

    result = execute_query(conn_model, query.sql_generated)
    return jsonify({'success': True, **result})


@query_bp.route('/api/query/<int:query_id>/export/csv', methods=['GET'])
@login_required
def export_csv(query_id):
    query = Query.query.filter_by(id=query_id, user_id=current_user.id).first_or_404()
    result = query.get_result()
    if not result:
        return jsonify({'error': 'Sem dados para exportar.'}), 400

    columns = result.get('columns', [])
    rows = result.get('rows', [])
    csv_bytes, filename = export_to_csv(columns, rows)

    return send_file(
        io.BytesIO(csv_bytes),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@query_bp.route('/api/query/<int:query_id>/export/pdf', methods=['GET'])
@login_required
def export_pdf(query_id):
    query = Query.query.filter_by(id=query_id, user_id=current_user.id).first_or_404()
    result = query.get_result()
    if not result:
        return jsonify({'error': 'Sem dados para exportar.'}), 400

    columns = result.get('columns', [])
    rows = result.get('rows', [])
    title = query.title or query.natural_language[:80]
    pdf_bytes, filename = export_to_pdf(columns, rows, title=title, sql=query.sql_generated)

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )
