from src.extensions import db, bcrypt
from flask_login import UserMixin
from datetime import datetime


class Department(db.Model):
    """Departamentos/Áreas criados pelo admin para segmentar usuários."""
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='briefcase')  # ícone Heroicons
    color = db.Column(db.String(20), default='purple')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', backref='department', lazy=True)

    def __repr__(self):
        return f'<Department {self.name}>'


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # Campos de perfil profissional
    company = db.Column(db.String(150))
    area = db.Column(db.String(100))       # Área/departamento informada no cadastro
    profession = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    # Plano e status
    plan = db.Column(db.String(20), default='free')  # free, starter, pro, enterprise
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relacionamentos
    connections = db.relationship('DatabaseConnection', backref='user', lazy=True, cascade='all, delete-orphan')
    queries = db.relationship('Query', backref='user', lazy=True, cascade='all, delete-orphan')
    subscriptions = db.relationship('Subscription', backref='user', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def active_subscription(self):
        """Retorna a assinatura ativa mais recente."""
        return Subscription.query.filter_by(
            user_id=self.id, status='active'
        ).order_by(Subscription.start_date.desc()).first()

    @property
    def plan_display(self):
        plans = {
            'free': 'Gratuito',
            'starter': 'Starter',
            'pro': 'Pro',
            'business': 'Business',
            'enterprise': 'Enterprise'
        }
        return plans.get(self.plan, self.plan.capitalize())

    @property
    def plan_badge_color(self):
        colors = {
            'free': 'gray',
            'starter': 'blue',
            'pro': 'purple',
            'business': 'indigo',
            'enterprise': 'yellow'
        }
        return colors.get(self.plan, 'gray')

    def __repr__(self):
        return f'<User {self.email}>'


class Subscription(db.Model):
    """Histórico de assinaturas de cada usuário."""
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, cancelled, expired, trial
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    price = db.Column(db.Float, default=0.0)
    billing_cycle = db.Column(db.String(20), default='monthly')  # monthly, annual
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_active(self):
        if self.status != 'active':
            return False
        if self.end_date and self.end_date < datetime.utcnow():
            return False
        return True

    @property
    def days_remaining(self):
        if not self.end_date:
            return None
        delta = self.end_date - datetime.utcnow()
        return max(0, delta.days)

    def __repr__(self):
        return f'<Subscription {self.user_id} - {self.plan}>'


class Payment(db.Model):
    """Histórico de pagamentos."""
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='BRL')
    status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    payment_method = db.Column(db.String(50))  # credit_card, pix, boleto
    transaction_id = db.Column(db.String(255))
    description = db.Column(db.String(255))
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subscription = db.relationship('Subscription', backref='payments')

    @property
    def status_display(self):
        labels = {
            'pending': 'Pendente',
            'paid': 'Pago',
            'failed': 'Falhou',
            'refunded': 'Reembolsado'
        }
        return labels.get(self.status, self.status)

    @property
    def status_color(self):
        colors = {
            'pending': 'yellow',
            'paid': 'green',
            'failed': 'red',
            'refunded': 'gray'
        }
        return colors.get(self.status, 'gray')

    def __repr__(self):
        return f'<Payment {self.user_id} - R${self.amount}>'
