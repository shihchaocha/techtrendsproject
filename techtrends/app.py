import sqlite3
import logging
import os
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from datetime import datetime

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config['DB_count'] = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    try:
        if os.path.exists("database.db"):
            connection = sqlite3.connect("database.db")
        else:
            raise RuntimeError('Cannot find database.db')
    except sqlite3.OperationalError:
        logging.error('Please run python init_db.py first!')
    connection.row_factory = sqlite3.Row
    app.config['DB_count'] = app.config['DB_count']+1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logging.error('Article %s does not exist!',post_id)
        return render_template("404.html"), 404
    else:
        logging.debug('Article %s (%s) has been retrieved!',post["title"], post_id)
        return render_template("post.html", post=post)


# Define the About Us page
@app.route('/about')
def about():
    logging.debug("The about page is rendered!")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logging.debug('Article with title %s has been created!', title)
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route("/healthz")
def healthz():
    try:
        connection = get_db_connection()
        connection.cursor()
        connection.execute("SELECT * FROM posts")
        connection.close()
        return {"result": "OK - healthy"}
    except Exception:
        return {"result": "ERROR - unhealthy"}, 500

@app.route("/metrics")
def metrics():
    connection = get_db_connection()
    posts = connection.execute("SELECT * FROM posts").fetchall()
    connection.close()
    post_count = len(posts)
    data = {"db_connection_count": app.config['DB_count'], "post_count": post_count}
    return data

def initialize_logging():
    log_level = os.getenv("LOGLEVEL", "DEBUG").upper()
    log_level = (
        getattr(logging, log_level)
        if log_level in ["CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING",]
        else logging.DEBUG
    )

    logging.basicConfig(
        format='%(levelname)s:%(name)s:%(asctime)s, %(message)s',
                level=log_level,
    )

# start the application on port 3111
if __name__ == "__main__":
    initialize_logging()
    app.run(host='0.0.0.0', port='3111')
