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

# decorators:
# http://exploreflask.com/en/latest/views.html
# @login_required

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
	job_categories = jobCategories(pagefunc='showJobCategory')
	return render_template('index.html', job_categories=job_categories)

@app.route('/gregslist/<int:category_id>/job-category/')
def showJobCategory(category_id):
	job_categories = jobCategories(pagefunc='showJobCategory',
								   mini=True,
								   highlight=category_id)
	job_posts = session.query(JobPost).filter_by(category_id=category_id).order_by(JobPost.title)
	return render_template('specific-category.html', job_categories=job_categories, posts=job_posts)


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

@app.route('/gregslist/<int:post_id>/edit/', methods=['GET', 'POST'])
def editPost(post_id):
	post = session.query(JobPost).filter_by(id=post_id).one()
	if request.method == 'POST':
		post.title = request.form['title']
		post.description = request.form['description']
		flash('"%s" successfully edited' % post.title)
		session.commit()
		return redirect(url_for('mainPage'))
	else:
		return render_template('create-or-edit.html',
								title=post.title,
								description=post.description)

@app.route('/gregslist/choose/category/', methods=['GET', 'POST'])
def newPostCategorySelect():
	print "button pressed"
	print request.form
	if request.method == 'POST':
		if 'jobs' in request.form:
			return redirect(url_for('newPostSubCategorySelect', category='jobs'))
		if 'stuff' in request.form:
			return redirect(url_for('newPostSubCategorySelect', category='stuff'))
		if 'space' in request.form:
			return redirect(url_for('newPostSubCategorySelect', category='space'))
	else:
		return render_template('category-select.html')

@app.route('/gregslist/<category>/choose/sub-category', methods=['GET', 'POST'])
def newPostSubCategorySelect(category):
	if category == 'jobs':
		job_categories = jobCategories(pagefunc='newJobForm')
		return render_template('sub-category-select.html', job_categories=job_categories)

@app.route('/gregslist/<int:category_id>/new/job/', methods=['GET', 'POST'])
def newJobForm(category_id):
	job_category = session.query(JobCategory).filter_by(id=category_id).one()
	if request.method == 'POST':
		title = request.form['title']
		description = request.form['description']
		job_post = JobPost(title=title,
						   description=description,
						   pay="$0.00",
						   hours="200",
						   category_id=category_id,
						   user_id=1)
		flash('"%s" successfully added' % title)
		session.add(job_post)
		session.commit()
		return redirect(url_for('mainPage'))
	else:
		return render_template('create-or-edit.html',
								title="",
								description="")



def jobCategories(pagefunc='showJobCategory', mini=False, highlight=""):
	job_categories = session.query(JobCategory).order_by(asc(JobCategory.name))
	if mini:
		return render_template('job-categories-mini.html',
								job_categories=job_categories,
								pagefunc=pagefunc,
								current_category_id=highlight)
	else:
		return render_template('job-categories.html',
								job_categories=job_categories,
								pagefunc=pagefunc)




if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)
