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
	return render_template('specific-item.html')


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)