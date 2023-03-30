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

#to use insert
#print(generate_password_hash("admin"))

#MAIN APP
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/success")
def success():
    return render_template('success.html')

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
    #Need to specify selecting password and user's id because select * doesn't take user's id
    user = db.execute(
        'SELECT rowid, password FROM user WHERE username = ?', (username,)
    ).fetchone()

    if user is None:
        error = 'Incorrect username.'
    elif not check_password_hash(user['password'], password):
        error = 'Incorrect password.'
    if error is not None:
        flash(error)
    #if there's no error, redirect to the index page
    if error is None:
        session.clear()
        session['user_id'] = user['rowid']
        return redirect(url_for('success'))

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
                return redirect(url_for("login_get"))

        flash(error)
    return render_template('register.html')

# Get all books from logged user
@app.route('/books')
def get_books():
    db = get_db()
    books = db.execute(
        "SELECT book.rowid, * FROM book JOIN user ON book.user_id = user.rowid WHERE user.rowid = ?", (session['user_id'],)
    ).fetchall()
    db.commit()
    return render_template('list_books.html', books=books)

#Get every books
@app.route('/all_books')
def get_all_books():
    db = get_db()
    books = db.execute(
        'SELECT book.rowid, book.*, user.username as username, COUNT(like_book.book_id) AS liked '
        'FROM book LEFT JOIN like_book ON book.rowid = like_book.book_id INNER JOIN user ON user.rowid = book.user_id GROUP BY book.rowid'
    ).fetchall()
    db.commit()
    return render_template('all_books.html', books=books)

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
##Create book for an admin
@app.route("/createBook",methods = ["POST","GET"])
def createBook():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        price = request.form["price"]
        summary = request.form["summary"]
        user_id = session['user_id']
        edition = request.form["edition"]
        db = get_db()
        db.execute("INSERT INTO book(title,author, price, summary,edition,user_id) values(?,?,?,?,?,?)", (title,author,price,summary,edition,user_id) )
        db.commit()
        return redirect(url_for("get_books"))
    return render_template("create_book.html")

# get book's information by its id
def get_book(id):
    book = get_db().execute(
        'SELECT book.rowid, book.*, user.rowid as userid, user.username as username, COUNT(like_book.book_id) AS liked '
        ' FROM book JOIN user ON book.user_id = user.rowid'
        ' JOIN like_book ON book.rowid = like_book.book_id'
        ' WHERE book.rowid = ?',
        (id,)
    ).fetchone()
    return book


# readonly book's details
@app.route('/book/<int:id>', methods=['GET'])
def view_one_book(id):
    book = get_book(id)
    return render_template('view_book.html', book=book)


# Update the book's information
@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    book = get_book(id)
    if request.method =='POST':
        title = request.form['title']
        author = request.form['author']
        edition = request.form['edition']
        summary = request.form['summary']
        price = request.form['price']
        error = None

        if not title:
            error = 'Title is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('UPDATE book SET title = ?, author = ?, edition = ?, summary =?, price = ? WHERE rowid = ?', (title,author,edition, summary, price, id))
            db.commit()
            return redirect(url_for('get_books'))
    return render_template('update_book.html', book=book)

#Delete a book
@app.route('/delete/<int:id>', methods=('GET',))
def delete(id):
    db = get_db()
    db.execute('DELETE FROM book WHERE rowid = ?', (id,))
    db.commit()
    return redirect(url_for('get_books'))

#Like function
#Count how many times the user already liked the book
def get_liked_book(userid, bookid):
    liked_book = get_db().execute(
        'SELECT COUNT(like_book.user_id) AS nb_already_liked FROM like_book WHERE like_book.user_id = ? AND like_book.book_id = ?',
        (userid, bookid)
    ).fetchone()
    return liked_book

#Check if the current user already liked the post
@app.route('/like/<int:id>', methods=('POST',))
def like(id):
    user_id = session['user_id']
    book = get_liked_book(user_id, id)

    #If the user never liked the actual post, then he can like,
    #howervise the book's likes won't update
    if book['nb_already_liked'] == 0:
        db = get_db()
        db.execute("INSERT INTO like_book(book_id,user_id) values(?,?)", (id,user_id) )
        db.commit()
    return redirect(url_for('get_all_books'))







