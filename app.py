import os
import sqlite3
from flask import Flask, session, render_template, redirect, url_for, request
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
DB_FILE = os.getenv('DATABASE_FILE', 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with open('database.sql', 'r') as f:
        sql_script = f.read()
    conn = get_db_connection()
    conn.executescript(sql_script)
    conn.commit()
    conn.close()


def validate_seasons(seasons):
    try:
        val = int(seasons)
        return val >= 0
    except (ValueError, TypeError):
        return False

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username already exists!"
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        return "Invalid credentials!"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        seasons = request.form['seasons_watched']
        status = request.form['status']
        if validate_seasons(seasons):
            conn.execute('INSERT INTO series (user_id, title, genre, seasons_watched, status) VALUES (?, ?, ?, ?, ?)',
                         (session['user_id'], title, genre, int(seasons), status))
            conn.commit()
        return redirect(url_for('dashboard'))
    my_series = conn.execute('SELECT * FROM series WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('dashboard.html', series_list=my_series, username=session['username'])

@app.route('/delete/<int:id>')
def delete_series(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM series WHERE id = ? AND user_id = ?', (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
