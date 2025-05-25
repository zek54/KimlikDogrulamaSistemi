from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import json
from datetime import datetime, timedelta
import secrets
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Veritabanı bağlantısı için yardımcı fonksiyon
def get_db():
    db = sqlite3.connect('enhanced_users.db')
    db.row_factory = sqlite3.Row
    return db

# Oturum kontrolü için decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Ana sayfa
@app.route('/')
def index():
    return render_template('index.html')

# Giriş sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            
            # Son giriş bilgilerini güncelle
            db.execute(
                'UPDATE users SET last_login = ?, last_ip = ? WHERE id = ?',
                (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), request.remote_addr, user['id'])
            )
            db.commit()
            
            return redirect(url_for('dashboard'))
            
        return render_template('login.html', error="Hatalı kullanıcı adı veya şifre")
    
    return render_template('login.html')

# Kayıt sayfası
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        security_question = request.form.get('security_question')
        security_answer = request.form.get('security_answer')
        
        db = get_db()
        error = None
        
        if not username:
            error = 'Kullanıcı adı gerekli.'
        elif not password:
            error = 'Şifre gerekli.'
        elif db.execute(
            'SELECT id FROM users WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f'Kullanıcı {username} zaten kayıtlı.'
            
        if error is None:
            db.execute(
                'INSERT INTO users (username, email, password, security_question, security_answer, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                (username, email, generate_password_hash(password), security_question, 
                 generate_password_hash(security_answer), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            db.commit()
            return redirect(url_for('login'))
            
        return render_template('register.html', error=error)
        
    return render_template('register.html')

# Kullanıcı paneli
@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    
    login_history = db.execute(
        'SELECT * FROM login_history WHERE user_id = ? ORDER BY login_time DESC LIMIT 5',
        (session['user_id'],)
    ).fetchall()
    
    return render_template('dashboard.html', user=user, login_history=login_history)

# Şifre sıfırlama
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form.get('username')
        answer = request.form.get('security_answer')
        new_password = request.form.get('new_password')
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        
        if user and check_password_hash(user['security_answer'], answer):
            db.execute(
                'UPDATE users SET password = ? WHERE id = ?',
                (generate_password_hash(new_password), user['id'])
            )
            db.commit()
            return redirect(url_for('login'))
            
        return render_template('reset_password.html', error="Hatalı güvenlik sorusu cevabı")
        
    return render_template('reset_password.html')

# Çıkış
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# API Endpoints
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    
    if user and check_password_hash(user['password'], password):
        token = secrets.token_hex(32)
        
        # Token'ı veritabanına kaydet
        db.execute(
            'INSERT INTO sessions (user_id, session_token, expires_at) VALUES (?, ?, ?)',
            (user['id'], token, (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'))
        )
        db.commit()
        
        return jsonify({
            'token': token,
            'user_id': user['id'],
            'username': user['username']
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password', 'security_question', 'security_answer']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
        
    db = get_db()
    if db.execute('SELECT id FROM users WHERE username = ?', (data['username'],)).fetchone():
        return jsonify({'error': 'Username already exists'}), 409
        
    try:
        db.execute(
            'INSERT INTO users (username, email, password, security_question, security_answer, created_at) VALUES (?, ?, ?, ?, ?, ?)',
            (data['username'], data['email'], generate_password_hash(data['password']),
             data['security_question'], generate_password_hash(data['security_answer']),
             datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        db.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    data = request.get_json()
    username = data.get('username')
    answer = data.get('security_answer')
    new_password = data.get('new_password')
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    if not check_password_hash(user['security_answer'], answer):
        return jsonify({'error': 'Invalid security answer'}), 401
        
    try:
        db.execute(
            'UPDATE users SET password = ? WHERE id = ?',
            (generate_password_hash(new_password), user['id'])
        )
        db.commit()
        return jsonify({'message': 'Password reset successful'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 