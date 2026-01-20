import os
import re
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv

# Načtení .env souboru
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database URL - podporuje PostgreSQL, MySQL i SQLite
# PostgreSQL: postgresql://user:password@host:port/database
# MySQL: mysql://user:password@host:port/database
# SQLite: sqlite:///tasks.db
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'sqlite:///tasks.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ============ MODELY ============

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(20), default='medium')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ============ VALIDACE ============

def validate_username(username):
    """Validace uživatelského jména - pouze bezpečné znaky"""
    if not username or len(username) < 3:
        return False, "Uživatelské jméno musí mít alespoň 3 znaky"
    if len(username) > 80:
        return False, "Uživatelské jméno může mít maximálně 80 znaků"
    # safe_characters - povoleny pouze alfanumerické znaky a podtržítko
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Uživatelské jméno může obsahovat pouze písmena, čísla a podtržítko"
    return True, ""

def validate_password(password):
    """Validace hesla"""
    if not password or len(password) < 4:
        return False, "Heslo musí mít alespoň 4 znaky"
    return True, ""

def validate_task_title(title):
    """Validace názvu úkolu"""
    if not title or len(title.strip()) == 0:
        return False, "Název úkolu je povinný"
    if len(title) > 200:
        return False, "Název úkolu může mít maximálně 200 znaků"
    return True, ""

def validate_priority(priority):
    """Validace priority"""
    valid_priorities = ['low', 'medium', 'high']
    if priority not in valid_priorities:
        return False, "Neplatná priorita"
    return True, ""

# ============ DEKORÁTORY ============

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Pro přístup se musíš přihlásit', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============ ROUTY ============

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validace
        valid, msg = validate_username(username)
        if not valid:
            flash(msg, 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Úspěšně přihlášen!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Neplatné přihlašovací údaje', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validace uživatelského jména
        valid, msg = validate_username(username)
        if not valid:
            flash(msg, 'error')
            return render_template('register.html')
        
        # Validace hesla
        valid, msg = validate_password(password)
        if not valid:
            flash(msg, 'error')
            return render_template('register.html')
        
        # Kontrola existence
        if User.query.filter_by(username=username).first():
            flash('Uživatelské jméno již existuje', 'error')
            return render_template('register.html')
        
        user = User(username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        
        flash('Registrace úspěšná! Nyní se přihlas.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Byl jsi odhlášen', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = db.session.get(User, session['user_id'])
    tasks = Task.query.filter_by(user_id=user.id).all()
    
    total = len(tasks)
    completed = len([t for t in tasks if t.completed])
    pending = total - completed
    
    return render_template('dashboard.html', 
                         user=user,
                         tasks=tasks, 
                         total=total, 
                         completed=completed, 
                         pending=pending)

@app.route('/add-task', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')
        
        # Validace názvu
        valid, msg = validate_task_title(title)
        if not valid:
            flash(msg, 'error')
            return render_template('add_task.html')
        
        # Validace priority
        valid, msg = validate_priority(priority)
        if not valid:
            flash(msg, 'error')
            return render_template('add_task.html')
        
        task = Task(
            title=title,
            description=description,
            priority=priority,
            user_id=session['user_id']
        )
        db.session.add(task)
        db.session.commit()
        
        flash('Úkol byl přidán!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_task.html')

@app.route('/edit-task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = db.session.get(Task, task_id)
    
    if not task or task.user_id != session['user_id']:
        flash('Úkol nenalezen', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')
        
        # Validace názvu
        valid, msg = validate_task_title(title)
        if not valid:
            flash(msg, 'error')
            return render_template('edit_task.html', task=task)
        
        # Validace priority
        valid, msg = validate_priority(priority)
        if not valid:
            flash(msg, 'error')
            return render_template('edit_task.html', task=task)
        
        task.title = title
        task.description = description
        task.priority = priority
        db.session.commit()
        
        flash('Úkol byl upraven!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_task.html', task=task)

@app.route('/toggle-task/<int:task_id>')
@login_required
def toggle_task(task_id):
    task = db.session.get(Task, task_id)
    
    if task and task.user_id == session['user_id']:
        task.completed = not task.completed
        db.session.commit()
        status = 'dokončen' if task.completed else 'obnoven'
        flash(f'Úkol byl {status}!', 'success')
    
    return redirect(url_for('dashboard'))

@app.route('/delete-task/<int:task_id>')
@login_required
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    
    if task and task.user_id == session['user_id']:
        db.session.delete(task)
        db.session.commit()
        flash('Úkol byl smazán!', 'success')
    
    return redirect(url_for('dashboard'))

# ============ SPUŠTĚNÍ ============

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
