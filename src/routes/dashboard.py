from flask import Blueprint, render_template, redirect, url_for, jsonify, request, flash
from flask_login import login_required, current_user
from src.extensions import db
from src.models.connection import DatabaseConnection
from src.models.query import Query
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    connections = DatabaseConnection.query.filter_by(user_id=current_user.id, is_active=True).all()
    recent_queries = Query.query.filter_by(user_id=current_user.id)\
        .order_by(Query.created_at.desc()).limit(10).all()
    saved_queries = Query.query.filter_by(user_id=current_user.id, is_saved=True)\
        .order_by(Query.created_at.desc()).limit(5).all()

    # Estatísticas
    total_queries = Query.query.filter_by(user_id=current_user.id).count()
    positive_feedback = Query.query.filter_by(user_id=current_user.id, feedback=1).count()
    last_week = datetime.utcnow() - timedelta(days=7)
    week_queries = Query.query.filter(
        Query.user_id == current_user.id,
        Query.created_at >= last_week
    ).count()

    stats = {
        'total_queries': total_queries,
        'connections': len(connections),
        'positive_feedback': positive_feedback,
        'week_queries': week_queries
    }

    return render_template('dashboard/index.html',
                           connections=connections,
                           recent_queries=recent_queries,
                           saved_queries=saved_queries,
                           stats=stats)


@dashboard_bp.route('/dashboard/saved-queries')
@login_required
def saved_queries():
    queries = Query.query.filter_by(user_id=current_user.id, is_saved=True)\
        .order_by(Query.created_at.desc()).all()
    return render_template('dashboard/saved_queries.html', queries=queries)


@dashboard_bp.route('/dashboard/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    queries = Query.query.filter_by(user_id=current_user.id)\
        .order_by(Query.created_at.desc())\
        .paginate(page=page, per_page=20)
    return render_template('dashboard/history.html', queries=queries)


@dashboard_bp.route('/api/query/<int:query_id>/save', methods=['POST'])
@login_required
def save_query(query_id):
    query = Query.query.filter_by(id=query_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    query.is_saved = True
    query.title = data.get('title', f'Consulta {query_id}')
    db.session.commit()
    return jsonify({'success': True})


@dashboard_bp.route('/api/query/<int:query_id>/feedback', methods=['POST'])
@login_required
def query_feedback(query_id):
    query = Query.query.filter_by(id=query_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    query.feedback = data.get('feedback', 0)
    query.feedback_comment = data.get('comment', '')
    db.session.commit()
    return jsonify({'success': True})


@dashboard_bp.route('/api/query/<int:query_id>', methods=['GET'])
@login_required
def get_query(query_id):
    query = Query.query.filter_by(id=query_id, user_id=current_user.id).first_or_404()
    return jsonify({
        'id': query.id,
        'natural_language': query.natural_language,
        'sql_generated': query.sql_generated,
        'result': query.get_result(),
        'row_count': query.row_count,
        'execution_time_ms': query.execution_time_ms,
        'feedback': query.feedback,
        'title': query.title,
        'created_at': query.created_at.isoformat()
    })
