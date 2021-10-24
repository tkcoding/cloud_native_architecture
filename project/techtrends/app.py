import sqlite3
import logging
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


# database connection tracking
conn_track = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global conn_track
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    # cursor_obj = connection.cursor()
    # cursor_obj.execute('SELECT * FROM posts')
    conn_track += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application
@app.route('/')
def index():
    app.logger.debug('Mainpage request successful')
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
      logging.debug("Article ID : {} does not exists.".format(post_id))
      return render_template('404.html'), 404
    else:
      logging.debug('Article ID : {} retrieved successfully'.format(post_id))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.debug('About us accessed.')
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
            logging.debug('Create {} successfully!'.format(title))
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def healthz():
    try:
        connection = get_db_connection()
        connection.cursor()
        connection.execute('SELECT * FROM posts')
        connection.close()
        response = app.response_class(
                response=json.dumps({"result":"OK - healthy"}),
                status=200,
                mimetype='application/json'
        )
        return response
    except Exception:
        response = app.response_class(
                response=json.dumps({"result":"ERROR - unhealthy"}),
                status=500,
                mimetype='application/json'
        )
        return response


@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    post_count = len(posts)
    response = {"db_connection_count":connection_count,"post_count":post_count}

    return response

# start the application on port 3111
if __name__ == "__main__":
    logname = 'app.log'
    logging.basicConfig(filename=logname,
                                filemode='a',
                                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                                datefmt='%H:%M:%S',
                                level=logging.DEBUG)
    app.run(host='0.0.0.0',port='3111')


# Path for windows
# \\wsl$\docker-desktop-data\version-pack-data\community\docker\containers\2c944454b8daf31bb664c5eb9f117da005bba875b2d1ab21a33be2c9a6aad75d
