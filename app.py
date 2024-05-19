from flask import Flask, render_template, request, url_for, flash, redirect, session
import sqlite3
from werkzeug.exceptions import abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jRv8sL2pFwXhN5aG9zQ3bU7cY6dA1eR4'


# Open the connection between the db and our app
def get_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# Function to get the post id
def get_post(post_id):
    conn = get_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


# Function to get user by username and email
def get_user(username, email):
    conn = get_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND email = ?', (username, email)).fetchone()
    conn.close()
    return user


@app.route("/")
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    # We used the connection to bring all the data from the table
    conn = get_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template("index.html", posts=posts, get_user_by_id=get_user_by_id)



@app.route("/<int:post_id>")
def post(post_id):
    post = get_post(post_id)
    return render_template("post.html", post=post)


@app.route("/create", methods=['GET', 'POST'])
def create():
    if 'username' not in session:
        flash('You need to login to create a post.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash("Title is required!")
        else:
            conn = get_connection()
            conn.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)", (title, content, session['user_id']))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template("create.html")

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)
    if 'username' not in session:
        flash('You need to login to edit a post.')
        return redirect(url_for('login'))

    # Check if the user is the owner of the post or an admin
    if session['user_id'] != post['user_id'] and not session.get('is_admin'):
        flash('You are not authorized to edit this post.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            conn = get_connection()
            conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template("edit.html", post=post)


@app.route('/<int:id>/delete', methods=('GET', 'POST'))
def delete_post(id):
    if 'username' not in session or not session['is_admin']:
        flash('You are not authorized to perform this action.')
        return redirect(url_for('index'))

    # Check if the post exists
    post = get_post(id)
    if post is None:
        flash('Post does not exist.')
        return redirect(url_for('index'))

    # Perform the deletion
    conn = get_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Post deleted successfully.')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        user = get_user(username, email)
        if user:
            session['username'] = username
            session['user_id'] = user['id']

            # Check if the user is an admin
            if user['is_admin'] == 1:
                session['is_admin'] = True
            else:
                session['is_admin'] = False

            flash(f'Logged in as {username} ({email})')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or email. Please try again.')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        # Check if the username or email already exists in the database
        conn = get_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email)).fetchone()
        conn.close()
        if existing_user:
            flash('Username or email already exists. Please choose a different one.')
        else:
            conn = get_connection()
            conn.execute("INSERT INTO users (username, email) VALUES (?, ?)", (username, email))
            conn.commit()
            conn.close()
            flash('You have successfully registered! Please login.')
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    if 'username' not in session:
        flash('You need to login to view your profile.')
        return redirect(url_for('login'))

    # Fetch user data from the database
    user = get_user_by_id(session['user_id'])
    return render_template('profile.html', user=user)


def get_user_by_id(user_id):
    conn = get_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user


if __name__ == '__main__':
    app.run(debug=True)
