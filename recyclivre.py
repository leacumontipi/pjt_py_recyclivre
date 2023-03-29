import sqlite3
import click
from flask import Flask, flash, current_app, g, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from pathlib import Path

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

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

#à utiliser pour insert
#print(generate_password_hash("admin"))

#MAIN APP
@app.route("/")
def index():
    return render_template('index.html')

#LOGIN GET, render login template
@app.get('/login')
def login_get():
    return render_template('login.html')

#LOGIN POST, take data from login's form, check if username and password is correct from db
@app.post('/login')
def login_post():
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None
    user = db.execute(
        'SELECT rowid, password FROM user WHERE username = ?', (username,)
    ).fetchone()

    if user is None:
        error = 'Incorrect username.'
    elif not check_password_hash(user['password'], password):
        error = 'Incorrect password.'

    if error is None:
        session.clear()
        session['user_id'] = user['rowid']
        return redirect(url_for('index'))

    flash(error)

#LOGOUT
@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

# User registration
@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        db = get_db()
        error = None
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password, first_name, last_name) VALUES (?, ?, ?, ?)",
                    (username, generate_password_hash(password), first_name, last_name),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("index"))

        flash(error)
    return render_template('register.html')

# Get all books from user
@app.route('/books')
def get_books():
    db = get_db()
    books = db.execute(
        "SELECT * FROM book INNER JOIN user ON book.user_id = user.rowid WHERE user.rowid = ?", (session['user_id'],)
    ).fetchall()
    db.commit()
    return render_template('list-books.html', books=books)

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
# CRUD 
## create Livre par un admin
@app.route("/createBook",methods = ["POST","GET"])
def createLivre():
   
    if request.method == "POST":

        title = request.form["title"]
        author= request.form["author"]
        price =request.form["price"]
        summary= request.form["summary"]
        user_id= session['user_id']
        edition= request.form["edition"]
        db = get_db()
        db.execute("INSERT INTO book(title,author, price, summary,edition,user_id) values(?,?,?,?,?,?)", (title,author,price,summary,edition,user_id) )
        db.commit()
        return redirect(url_for("index.html"))
    
    return render_template("create_book.html")
# update Livre
def get_book(id):
    book = get_db().execute(
        'SELECT book.rowid, title,author, edition,summary , price'
        ' FROM book  JOIN user  ON book.user_id = user.rowid'
        ' WHERE book.rowid = ?',
        (id,)
    ).fetchone()
    return book

@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    book = get_book(id)
    if request.method =='POST':
        title = request.form['title']
        author= request.form ['author']
        edition =request.form ['edition']
        summary =request.form ['summary']
        price = request.form ['price']
        if not title:
            error = 'Title is required.'
            if error is notNone:
                flash(error)
            else:
                db = get_db
                db.execute(
                    'UPDATE book SET title = ?, author = ?, edition = ?, summary =?, price = ?'
                    'WHERE book.rowid = ?',
                    (title,author,edition, summary, price)
                    )
                db.commit()
                return redirect(url_for('index.html'))
    return render_template('update.html', book=book)

#delete Livre
@app.route('/delete/<int:id>', methods=['GET','POST'])
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM book WHERE book.user_id= ?', (id,))
    db.commit()
    return redirect(url_for('index.html'))








