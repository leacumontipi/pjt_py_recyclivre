import sqlite3
import click
from flask import Flask, flash, current_app, g, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash
from pathlib import Path

app = Flask(__name__)

#INIT DATABASE BEFORE PROJECT
#Read db file and transform db data as object
def get_db():
    db = sqlite3.connect(
        'db',
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row
    return db

#If the db file doesn't exist, an empty file will exist
db_file = Path('db')
if(not db_file.exists()):
    db = get_db()
    db.executescript(Path('db.sql').read_text())

#MAIN APP
@app.route("/")
def index():
    return render_template('index.html')

#LOGIN GET, render login template
@app.get('/login')
def login_get():
    return render_template('login.html')

#LOGIN POST, take data from login's form, check if username and password is correct
@app.post('/login')
def login_post():
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None
    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username)
    ).fetchone()

    if user is None:
        error = 'Incorrect username.'
    elif not check_password_hash(user['password'], password):
        error = 'Incorrect password.'

    if error is None:
        session.clear()
        session['user_id'] = user['id']
        return redirect(url_for('index'))

    flash(error)

#LOGOUT
@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))


#INIT DATABSE


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

#Initialize database with db.sql file
def init_db():
    db = get_db()

    with current_app.open_resource('db.sql') as f:
        db.executescript(f.read().decode('utf8'))
<<<<<<< HEAD


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
 
#show the user profile for that user
@app.route('/user/<username>')
def show_user_profile(karima):
    return f'User {escape(username)}'

@app.route('/post/<int:post_id>')
def show_post(post_id):
    #show the post with the given id, the id is an integer
    return f'Post {post_id}' 
# Comportement de redirection
@app.route('/projects/')
def projects():
    return 'The project page'       
=======
>>>>>>> 3586ab656758308291f1434ec111535b4cb50162
