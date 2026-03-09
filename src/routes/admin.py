from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from src.extensions import db
from src.models.user import User, Department, Subscription, Payment
from src.models.connection import DatabaseConnection
from src.models.query import Query
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator que exige que o usuário seja admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acesso restrito a administradores.', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Dashboard administrativo com métricas gerais."""
    # Métricas de usuários
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    new_this_month = User.query.filter(
        User.created_at >= datetime.utcnow().replace(day=1)
    ).count()

    # Distribuição por plano
    plan_counts = db.session.query(
        User.plan, func.count(User.id)
    ).group_by(User.plan).all()
    plans_data = {p: c for p, c in plan_counts}

    # Receita do mês
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    monthly_revenue = db.session.query(
        func.sum(Payment.amount)
    ).filter(
        Payment.status == 'paid',
        Payment.paid_at >= month_start
    ).scalar() or 0

    # Receita total
    total_revenue = db.session.query(
        func.sum(Payment.amount)
    ).filter(Payment.status == 'paid').scalar() or 0

    # Últimos 5 usuários cadastrados
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    # Últimos 5 pagamentos
    recent_payments = Payment.query.order_by(Payment.created_at.desc()).limit(5).all()

    # Total de consultas realizadas
    total_queries = Query.query.count()

    # Departamentos
    total_departments = Department.query.count()

    return render_template('admin/index.html',
        total_users=total_users,
        active_users=active_users,
        new_this_month=new_this_month,
        plans_data=plans_data,
        monthly_revenue=monthly_revenue,
        total_revenue=total_revenue,
        recent_users=recent_users,
        recent_payments=recent_payments,
        total_queries=total_queries,
        total_departments=total_departments
    )


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Lista todos os usuários com filtros."""
    page = request.args.get('page', 1, type=int)
    plan_filter = request.args.get('plan', '')
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    dept_filter = request.args.get('department', '')

    query = User.query

    if search:
        query = query.filter(
            (User.name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.company.ilike(f'%{search}%'))
        )
    if plan_filter:
        query = query.filter_by(plan=plan_filter)
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    if dept_filter:
        query = query.filter_by(department_id=int(dept_filter))

    users_paginated = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    departments = Department.query.filter_by(is_active=True).all()

    return render_template('admin/users.html',
        users=users_paginated,
        departments=departments,
        plan_filter=plan_filter,
        status_filter=status_filter,
        search=search,
        dept_filter=dept_filter
    )


@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """Detalhes completos de um usuário."""
    user = User.query.get_or_404(user_id)
    subscriptions = Subscription.query.filter_by(user_id=user_id).order_by(
        Subscription.created_at.desc()
    ).all()
    payments = Payment.query.filter_by(user_id=user_id).order_by(
        Payment.created_at.desc()
    ).all()
    connections = DatabaseConnection.query.filter_by(user_id=user_id).all()
    queries = Query.query.filter_by(user_id=user_id).order_by(
        Query.created_at.desc()
    ).limit(20).all()
    departments = Department.query.filter_by(is_active=True).all()

    return render_template('admin/user_detail.html',
        user=user,
        subscriptions=subscriptions,
        payments=payments,
        connections=connections,
        queries=queries,
        departments=departments
    )


@admin_bp.route('/users/<int:user_id>/edit', methods=['POST'])
@login_required
@admin_required
def user_edit(user_id):
    """Edita dados de um usuário."""
    user = User.query.get_or_404(user_id)

    user.name = request.form.get('name', user.name)
    user.email = request.form.get('email', user.email)
    user.plan = request.form.get('plan', user.plan)
    user.company = request.form.get('company', user.company)
    user.profession = request.form.get('profession', user.profession)
    user.is_active = request.form.get('is_active') == 'on'
    user.is_admin = request.form.get('is_admin') == 'on'

    dept_id = request.form.get('department_id')
    user.department_id = int(dept_id) if dept_id else None

    db.session.commit()
    flash(f'Usuário {user.name} atualizado com sucesso.', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def user_toggle(user_id):
    """Ativa ou desativa um usuário."""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'ativado' if user.is_active else 'desativado'
    return jsonify({'success': True, 'status': status, 'is_active': user.is_active})


@admin_bp.route('/users/<int:user_id>/subscription/add', methods=['POST'])
@login_required
@admin_required
def add_subscription(user_id):
    """Adiciona uma assinatura manualmente a um usuário."""
    user = User.query.get_or_404(user_id)

    plan = request.form.get('plan')
    price = float(request.form.get('price', 0))
    billing_cycle = request.form.get('billing_cycle', 'monthly')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    notes = request.form.get('notes', '')

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else datetime.utcnow()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None

    # Cancela assinaturas ativas anteriores
    Subscription.query.filter_by(user_id=user_id, status='active').update({'status': 'cancelled'})

    sub = Subscription(
        user_id=user_id,
        plan=plan,
        status='active',
        start_date=start_date,
        end_date=end_date,
        price=price,
        billing_cycle=billing_cycle,
        notes=notes
    )
    db.session.add(sub)

    # Atualiza o plano do usuário
    user.plan = plan
    db.session.commit()

    flash(f'Assinatura {plan} adicionada com sucesso.', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/payments')
@login_required
@admin_required
def payments():
    """Lista todos os pagamentos com filtros."""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')

    query = Payment.query.join(User)

    if search:
        query = query.filter(
            (User.name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    if status_filter:
        query = query.filter(Payment.status == status_filter)

    payments_paginated = query.order_by(Payment.created_at.desc()).paginate(
        page=page, per_page=25, error_out=False
    )

    # Totais por status
    totals = db.session.query(
        Payment.status, func.sum(Payment.amount), func.count(Payment.id)
    ).group_by(Payment.status).all()

    return render_template('admin/payments.html',
        payments=payments_paginated,
        totals=totals,
        status_filter=status_filter,
        search=search
    )


@admin_bp.route('/payments/add', methods=['POST'])
@login_required
@admin_required
def add_payment():
    """Registra um pagamento manualmente."""
    user_id = request.form.get('user_id', type=int)
    amount = float(request.form.get('amount', 0))
    status = request.form.get('status', 'paid')
    payment_method = request.form.get('payment_method', '')
    description = request.form.get('description', '')
    transaction_id = request.form.get('transaction_id', '')

    payment = Payment(
        user_id=user_id,
        amount=amount,
        status=status,
        payment_method=payment_method,
        description=description,
        transaction_id=transaction_id,
        paid_at=datetime.utcnow() if status == 'paid' else None
    )
    db.session.add(payment)
    db.session.commit()

    flash('Pagamento registrado com sucesso.', 'success')
    return redirect(url_for('admin.payments'))


# ─── Departamentos ────────────────────────────────────────────────────────────

@admin_bp.route('/departments')
@login_required
@admin_required
def departments():
    """Lista todos os departamentos/áreas."""
    depts = Department.query.order_by(Department.name).all()
    # Conta usuários por departamento
    dept_user_counts = db.session.query(
        User.department_id, func.count(User.id)
    ).group_by(User.department_id).all()
    counts = {d: c for d, c in dept_user_counts}

    return render_template('admin/departments.html',
        departments=depts,
        counts=counts
    )


@admin_bp.route('/departments/create', methods=['POST'])
@login_required
@admin_required
def department_create():
    """Cria um novo departamento."""
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    icon = request.form.get('icon', 'briefcase')
    color = request.form.get('color', 'purple')

    if not name:
        flash('O nome do departamento é obrigatório.', 'error')
        return redirect(url_for('admin.departments'))

    if Department.query.filter_by(name=name).first():
        flash(f'Já existe um departamento com o nome "{name}".', 'error')
        return redirect(url_for('admin.departments'))

    dept = Department(name=name, description=description, icon=icon, color=color)
    db.session.add(dept)
    db.session.commit()

    flash(f'Departamento "{name}" criado com sucesso.', 'success')
    return redirect(url_for('admin.departments'))


@admin_bp.route('/departments/<int:dept_id>/edit', methods=['POST'])
@login_required
@admin_required
def department_edit(dept_id):
    """Edita um departamento."""
    dept = Department.query.get_or_404(dept_id)
    dept.name = request.form.get('name', dept.name).strip()
    dept.description = request.form.get('description', dept.description).strip()
    dept.icon = request.form.get('icon', dept.icon)
    dept.color = request.form.get('color', dept.color)
    dept.is_active = request.form.get('is_active') == 'on'
    db.session.commit()

    flash(f'Departamento "{dept.name}" atualizado.', 'success')
    return redirect(url_for('admin.departments'))


@admin_bp.route('/departments/<int:dept_id>/delete', methods=['POST'])
@login_required
@admin_required
def department_delete(dept_id):
    """Remove um departamento (apenas se não houver usuários vinculados)."""
    dept = Department.query.get_or_404(dept_id)
    user_count = User.query.filter_by(department_id=dept_id).count()

    if user_count > 0:
        flash(f'Não é possível excluir: {user_count} usuário(s) vinculado(s) a este departamento.', 'error')
    else:
        db.session.delete(dept)
        db.session.commit()
        flash(f'Departamento "{dept.name}" removido.', 'success')

    return redirect(url_for('admin.departments'))


# ─── API JSON para gráficos ───────────────────────────────────────────────────

@admin_bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """Retorna estatísticas em JSON para gráficos do dashboard."""
    # Novos usuários por mês (últimos 6 meses)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_signups = db.session.query(
        func.strftime('%Y-%m', User.created_at).label('month'),
        func.count(User.id).label('count')
    ).filter(User.created_at >= six_months_ago).group_by('month').all()

    # Receita por mês (últimos 6 meses)
    monthly_revenue = db.session.query(
        func.strftime('%Y-%m', Payment.paid_at).label('month'),
        func.sum(Payment.amount).label('total')
    ).filter(
        Payment.status == 'paid',
        Payment.paid_at >= six_months_ago
    ).group_by('month').all()

    return jsonify({
        'monthly_signups': [{'month': m, 'count': c} for m, c in monthly_signups],
        'monthly_revenue': [{'month': m, 'total': float(t or 0)} for m, t in monthly_revenue],
    })


@admin_bp.route('/setup-admin/<token>')
def setup_admin(token):
    """Rota de setup para ativar o primeiro admin via token seguro.
    
    O token é definido pela variável de ambiente ADMIN_SETUP_TOKEN.
    Uso: /admin/setup-admin/<token>?email=seu@email.com
    """
    import os
    from flask import request
    
    setup_token = os.environ.get('ADMIN_SETUP_TOKEN', '')
    if not setup_token or token != setup_token:
        return jsonify({'error': 'Token inválido ou não configurado.'}), 403
    
    email = request.args.get('email', '')
    if not email:
        return jsonify({'error': 'Parâmetro email obrigatório. Ex: ?email=seu@email.com'}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        # Listar usuários existentes para ajudar
        users = User.query.with_entities(User.id, User.name, User.email, User.is_admin).all()
        return jsonify({
            'error': f'Usuário {email} não encontrado.',
            'usuarios_existentes': [{'id': u.id, 'nome': u.name, 'email': u.email, 'is_admin': u.is_admin} for u in users]
        }), 404
    
    user.is_admin = True
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'✅ Usuário {user.name} ({user.email}) agora é administrador!',
        'admin_url': '/admin'
    })
