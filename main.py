#!/usr/bin/env python

__author__ = "student"
__version__ = "1.0"
# June 2017
# Flask Blog App re: LaunchCode LC-101
# Rubric: http://education.launchcode.org/web-fundmentals/assignments/build-a-blog/


from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:apples@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    date = db.Column(db.DateTime)

    def __init__(self, title, body, date=None):
        self.title = title
        self.body = body
        if date is None:
            date = datetime.utcnow()
        self.date = date


@app.route('/')
def index():
    return redirect('/blog')


@app.route('/blog', methods=['GET'])
def blog():

    if request.args:
        blog_id = request.args.get('id')
        entry = Blog.query.get(blog_id)
        return render_template('soloentry.html', title="Entry", entry=entry)

    # show all blog posts
    entries = Blog.query.order_by(Blog.date.desc()).all()
    return render_template('blog.html', title="Build A Blog!", entries=entries)


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():

    if request.method == 'POST':
        entry_name = request.form['title']
        new_body = request.form['entry']
        new_entry = Blog(entry_name, new_body)

        db.session.add(new_entry)
        db.session.commit()
        return redirect('/blog')

    return render_template('newpost.html', title="New Post")


if __name__ == '__main__':
    app.run()
