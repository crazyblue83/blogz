#!/usr/bin/env python

__author__ = "student"
__version__ = "1.0"
# June 2017
# Flask Blog App re: LaunchCode LC-101
# Rubric: http://education.launchcode.org/web-fundmentals/assignments/blogz/


from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:apples@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'super_secret_key'
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner, date=None):
        self.title = title
        self.body = body
        self.owner = owner
        if date is None:
            date = datetime.utcnow()
        self.date = date


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.args:
        user_id = request.args.get('username')
        username = User.query.get(user_id)
        return render_template('index.html', title="Users", username=username)
    
    elif request.args:
        user_id = request.args.get('owner_id')
        userId = Blog.query.get(user_id)
    
    return render_template('solouser.html', title="Entries", userId=userId)

    usernames = User.query.order_by(User.id.desc()).all()
    return render_template('index.html', title="Blogz!", usernames=usernames)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            # it could be "return redirect(/newpost)"
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/blog', methods=['GET'])
def blog():
    if request.args:
        blog_id = request.args.get('id')
        entry = Blog.query.get(blog_id)
        return render_template('soloentry.html', title="Entry", entry=entry)
    #if request.args:
        #users = request.args.get('owner_id')
        #userId = Blog.query.get('users')
    #return render_template('solouser.html', title="Entries", userId=userId)

    # show all blog posts
    entries = Blog.query.order_by(Blog.date.desc()).all()
    return render_template('blog.html', title="Blogz!", entries=entries)

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        entry_name = request.form['title']
        new_body = request.form['entry']
        username = session['username']

        user = User.query.filter_by(username=username).first()
        owner_id = user.id
        new_entry = Blog(entry_name, new_body, owner_id)

        db.session.add(new_entry)
        db.session.commit()
        return redirect('/blog')

    return render_template('newpost.html', title="New Post")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    username = ''
    title = 'Sign Up'

    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        if not username:
            flash("That's not a valid username.")

        elif (len(username) <= 3) or (" " in username):
            flash("That's not a valid username")
            username = ''

        elif (not password) or (len(password) <= 3) or (len(password) > 20) or (" " in password):
            flash("That's not a valid password")

        elif (not verify_password) or (password != verify_password):
            flash("Passwords do not match.")

        elif existing_user and (username == existing_user.username):
            flash("The username <strong>{0}</strong> is already registered".format(username), 'danger')

        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            # session['password'] = password
            return redirect('/newpost')

    return render_template('signup.html', title=title, username=username)


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


if __name__ == '__main__':
    app.run()
