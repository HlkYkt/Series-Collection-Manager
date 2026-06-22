from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'arel_proje_sirri_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///series_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    series_list = db.relationship('Series', backref='owner', lazy=True)

class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50))
    seasons_watched = db.Column(db.Integer, default=1)
    status = db.Column(db.String(50))
    comments = db.Column(db.Text, default="")
    favorite_season = db.Column(db.Integer, default=0)
    recommendation = db.Column(db.String(30), default="")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/')
def index():
    
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        
        if username and password:
            user_exists = User.query.filter_by(username=username).first()
            if not user_exists:
                new_user = User(username=username, password=password)
                db.session.add(new_user)
                db.session.commit()
                
                session['username'] = username
                session['user_id'] = new_user.id
                return redirect(url_for('dashboard'))
        return redirect(url_for('register'))
        
    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        title = request.form.get('title')
        genre = request.form.get('genre')
        seasons_watched = request.form.get('seasons_watched', 1)
        status = request.form.get('status', 'Watching')
        
        new_series = Series(
            title=title, 
            genre=genre, 
            seasons_watched=int(seasons_watched), 
            status=status,
            comments="",
            favorite_season=0,
            recommendation="",
            user_id=user_id
        )
        db.session.add(new_series)
        db.session.commit()
        return redirect(url_for('dashboard'))
        
    user_series = Series.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', username=session['username'], series_list=user_series)

@app.route('/increment_season/<int:id>')
def increment_season(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    series = Series.query.get_or_404(id)
    series.seasons_watched += 1
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/edit_series/<int:id>', methods=['POST'])
def edit_series(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    series = Series.query.get_or_404(id)
    series.title = request.form.get('title')
    series.genre = request.form.get('genre')
    series.seasons_watched = int(request.form.get('seasons_watched'))
    series.status = request.form.get('status')
    series.comments = request.form.get('comments')
    series.recommendation = request.form.get('recommendation')
    
    fav_season = request.form.get('favorite_season')
    series.favorite_season = int(fav_season) if fav_season and fav_season.isdigit() else 0
    
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:id>')
def delete_series(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    series = Series.query.get_or_404(id)
    db.session.delete(series)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)
