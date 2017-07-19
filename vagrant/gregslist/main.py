from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, JobCategory, StuffCategory, SpaceCategory, JobPost, StuffPost, SpacePost
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json


# Connect to Database and create database session
engine = create_engine('sqlite:///gregslist.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

# Show all posts
@app.route('/')
@app.route('/gregslist/')
def mainPage():
	job_categories = session.query(JobCategory).order_by(asc(JobCategory.name))
	return render_template('index.html', job_categories=job_categories)

@app.route('/gregslist/<int:category_id>/job-category/')
def showJobCategory(category_id):
	job_categories = session.query(JobCategory).order_by(asc(JobCategory.name))
	job_posts = session.query(JobPost).filter_by(category_id=category_id).order_by(JobPost.title)
	return render_template('specific-category.html', 
							categories=job_categories, 
							this_category_id=category_id,
							posts=job_posts)


@app.route('/gregslist/<int:post_id>/post/')
def showJobPost(post_id):
	post = session.query(JobPost).filter_by(id=post_id).one()
	return render_template('specific-item.html', post=post)

@app.route('/gregslist/<int:post_id>/delete/', methods=['GET', 'POST'])
def deletePost(post_id):
	post = session.query(JobPost).filter_by(id=post_id).one()
	if request.method == 'POST':
		session.delete(post)
		flash('"%s" has been deleted' % post.title)
		session.commit()
		return redirect(url_for('mainPage'))
	else:
		return render_template('delete-item.html', post=post)

# @app.route('/gregslist/<int:post_id>/edit/')
# def editPost(post_id):
# 	post = session.query(JobPost).filter_by(id=post_id).one()
# 	if request.method == 'POST':
# 	else:
# 		return render_template('edit-item.html', post=post)


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)