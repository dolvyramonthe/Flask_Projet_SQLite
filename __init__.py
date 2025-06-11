import os
import sqlite3
from contextlib import closing
from flask import Flask, render_template, request, redirect, url_for, session, abort
from werkzeug.security import generate_password_hash, check_password_hash

# Initialisation de l'application Flask
app = Flask(__name__)

# Configuration sécurisée
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['DATABASE_PATH'] = 'database.db'
app.config['ADMIN_USERNAME'] = os.environ.get('ADMIN_USERNAME', 'admin')
app.config['ADMIN_PASSWORD_HASH'] = generate_password_hash(
    os.environ.get('ADMIN_PASSWORD', 'default_password')
)

# Fonction pour obtenir une connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
    return conn

# Fonction utilitaire pour vérifier l'authentification
def est_authentifie():
    return session.get('authentifie', False)

# Middleware pour vérifier l'authentification sur les routes protégées
def authentification_requise(f):
    def wrapper(*args, **kwargs):
        if not est_authentifie():
            return redirect(url_for('authentification'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# Routes de l'application
@app.route('/')
def accueil():
    return render_template('hello.html')

@app.route('/lecture')
@authentification_requise
def lecture():
    return render_template('lecture.html')

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if (username == app.config['ADMIN_USERNAME'] and 
            check_password_hash(app.config['ADMIN_PASSWORD_HASH'], password)):
            session['authentifie'] = True
            return redirect(url_for('lecture'))
        
        return render_template('formulaire_authentification.html', 
                            error=True)
    
    return render_template('formulaire_authentification.html', 
                         error=False)

@app.route('/fiche_client/<int:post_id>')
@authentification_requise
def lire_fiche(post_id):
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
            data = cursor.fetchall()
            
            if not data:
                abort(404)
                
            return render_template('read_data.html', data=data)
    except sqlite3.Error as e:
        app.logger.error(f"Erreur base de données: {e}")
        abort(500)

@app.route('/consultation/')
@authentification_requise
def consulter_bdd():
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM clients;')
            data = cursor.fetchall()
            return render_template('read_data.html', data=data)
    except sqlite3.Error as e:
        app.logger.error(f"Erreur base de données: {e}")
        abort(500)

@app.route('/enregistrer_client', methods=['GET'])
@authentification_requise
def afficher_formulaire_client():
    return render_template('formulaire.html')

@app.route('/enregistrer_client', methods=['POST'])
@authentification_requise
def enregistrer_client():
    nom = request.form.get('nom', '').strip()
    prenom = request.form.get('prenom', '').strip()
    
    if not nom or not prenom:
        abort(400, "Le nom et prénom sont obligatoires")
    
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)',
                (1002938, nom, prenom, "ICI")
            )
            conn.commit()
            
        return redirect(url_for('consulter_bdd'))
    except sqlite3.Error as e:
        app.logger.error(f"Erreur lors de l'enregistrement: {e}")
        abort(500)

# Point d'entrée de l'application
if __name__ == "__main__":
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
