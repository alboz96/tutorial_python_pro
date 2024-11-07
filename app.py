from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_scores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key_here'  # Necessario per gestire le sessioni
db = SQLAlchemy(app)


# Modello per l'utente
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


# Modello per i punteggi
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)


# Usa l'app context per creare il database
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    # Recupera il punteggio migliore
    best_score = Score.query.filter_by(username=session['username']).order_by(Score.score.desc()).first()
    return render_template('quiz.html', best_score=best_score)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/submit', methods=['POST'])
def submit():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    score = 0

    # Verifica le risposte dell'utente per ciascuna domanda
    if request.form['question1'] == 'tensorflow':  # Risposta corretta
        score += 1
    if request.form['question2'] == 'opencv':  # Risposta corretta
        score += 1
    if request.form['question3'] == 'nltk':  # Risposta corretta
        score += 1
    if request.form['question4'] == 'data_analysis':  # Risposta corretta
        score += 1

    # Calcola il punteggio in percentuale
    total_questions = 4  # Escludiamo la domanda di testo opzionale
    score_percentage = (score / total_questions) * 100

    # Salva il punteggio dell'utente nel database
    new_score = Score(username=username, score=int(score_percentage))
    db.session.add(new_score)
    db.session.commit()

    # Recupera il punteggio migliore
    # Get the best score for the current user
    best_score = Score.query.filter_by(username=session['username']).order_by(Score.score.desc()).first()

    return render_template('quiz.html', score=int(score_percentage), best_score=best_score)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)