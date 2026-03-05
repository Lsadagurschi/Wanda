from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from src.extensions import db
from src.models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember = data.get('remember', False)

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            if request.is_json:
                return jsonify({'success': True, 'redirect': url_for('dashboard.index')})
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'error': 'E-mail ou senha incorretos.'}), 401
            flash('E-mail ou senha incorretos.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        plan = data.get('plan', 'free')

        if not name or not email or not password:
            msg = 'Preencha todos os campos obrigatórios.'
            if request.is_json:
                return jsonify({'success': False, 'error': msg}), 400
            flash(msg, 'error')
            return render_template('auth/register.html')

        if len(password) < 6:
            msg = 'A senha deve ter pelo menos 6 caracteres.'
            if request.is_json:
                return jsonify({'success': False, 'error': msg}), 400
            flash(msg, 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            msg = 'Este e-mail já está cadastrado.'
            if request.is_json:
                return jsonify({'success': False, 'error': msg}), 409
            flash(msg, 'error')
            return render_template('auth/register.html')

        user = User(name=name, email=email, plan=plan)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        if request.is_json:
            return jsonify({'success': True, 'redirect': url_for('dashboard.index')})
        flash(f'Bem-vindo(a), {name}! Sua conta foi criada com sucesso.', 'success')
        return redirect(url_for('dashboard.index'))

    plan = request.args.get('plan', 'free')
    return render_template('auth/register.html', selected_plan=plan)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('landing.index'))
