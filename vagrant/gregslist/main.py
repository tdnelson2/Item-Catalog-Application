from flask import Flask, render_template, request,\
				  redirect, jsonify, url_for, flash
from flask import make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, JobCategory, StuffCategory,\
						   SpaceCategory, JobPost, StuffPost, SpacePost
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from functools import wraps

# https://console.developers.google.com/apis/credentials?project=greglist-174419
GOOGLE_CLIENT_ID = json.loads(
	open('client_secret.json', 'r').read())['web']['client_id']

# https://developers.facebook.com/apps/555177401540603/settings/
FACEBOOK_APP_ID = json.loads(
	open('fb_client_secrets.json', 'r').read())['web']['app_id']


# Connect to Database and create database session
engine = create_engine('sqlite:///gregslist.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

##########################################################
"""
DECORATORS
"""
##########################################################

# Decorator helper funcs
def get_category_table(category):
	if category == "jobs":
		return JobCategory
	if category == "stuff":
		return StuffCategory
	if category == "space":
		return SpaceCategory

def get_post_table(category):
	if category == "jobs":
		return JobPost
	if category == "stuff":
		return StuffPost
	if category == "space":
		return SpacePost

def add_entries_from_all_categories(func):
	"""
	A decorator to add all JobCategory, StuffCategory,
	and SpaceCategory entries to the fuction's arguments
	"""
	@wraps(func)
	def wrap(*args, **kwargs):
		kwargs['job_categories'] =   session.query(JobCategory).\
									 order_by(asc(JobCategory.name))
		kwargs['stuff_categories'] = session.query(StuffCategory).\
									 order_by(asc(StuffCategory.name))
		kwargs['space_categories'] = session.query(SpaceCategory).\
									 order_by(asc(SpaceCategory.name))
		return func(*args, **kwargs)
	return wrap


def add_categories(func):
	"""
	A decorator to add Jobs, Stuff, or Space categories
	to the fuction's arguments as needed
	"""
	@wraps(func)
	def wrap(*args, **kwargs):
		if 'super_category' in kwargs:
			sup = kwargs['super_category']
			table = get_category_table(sup)
			if table:
				try:
					categories = session.query(table).\
								 order_by(asc(table.name))
					kwargs['categories'] = categories
				except:
					msg = ("[warning]There was a problem "
						   "retrieving the %s categories")
					flash(msg % sup)
					return redirect(login_session['current_url'])
		if not 'categories' in kwargs:
			flash("[warning]There was a problem retrieving the categories")
			return redirect(login_session['current_url'])
		return func(*args, **kwargs)
	return wrap

def add_specific_category(func):
	"""
	A decorator to add the specific Jobs, Stuff, or Space
	category to the fuction's arguments as needed
	"""
	@wraps(func)
	def wrap(*args, **kwargs):
		if 'super_category' in kwargs and 'category' in kwargs:
			cat = kwargs['category']
			cat_table = get_category_table(kwargs['super_category'])
			if cat_table:
				try:
					category = session.query(cat_table).\
							   filter_by(name=cat).one()
					kwargs['category_entry'] = category
				except:
					msg = ("[warning]There was a problem "
						   "retrieving the %s category")
					flash(msg % cat)
					return redirect(login_session['current_url'])
		if not 'category_entry' in kwargs:
			flash("[warning]There was a problem retrieving the category")
			return redirect(login_session['current_url'])
		return func(*args, **kwargs)
	return wrap

def add_posts(func):
	"""
	A decorator to add Job, Stuff, or Space
	posts to the fuction's arguments as needed.

	super_category, category, category_entry
	must be present in order for this to work.
	category_entry can be added by making
	sure the add_specific_category decorator
	proceeds this one.
	"""
	@wraps(func)
	def wrap(*args, **kwargs):

		if (
			'super_category' in kwargs
			and
			'category' in kwargs
			and
			'category_entry' in kwargs
			):
				sup = kwargs['super_category']
				cat = kwargs['category']
				category_entry = kwargs['category_entry']
				post_table = get_post_table(sup)
				if post_table:
					try:
						posts = session.query(post_table).\
								filter_by(category_id=category_entry.id).\
								order_by(asc(post_table.title))
						kwargs['post_entries'] = posts
					except:
						msg = ("[warning]There was a problem "
							   "retrieving posts from %s/%s")
						flash(msg % (cat, sup))
						return redirect(login_session['current_url'])
		if not 'post_entries' in kwargs:
			flash("[warning]There was a problem retrieving the posts")
			return redirect(login_session['current_url'])
		return func(*args, **kwargs)
	return wrap

def add_specific_post(func):
	"""
	A decorator to add a specific post
	entry to the function's arguments.

	super_category and post_id must be in the
	function's arguments in order for this to work.
	"""
	@wraps(func)
	def wrap(*args, **kwargs):
		if ('post_id' in kwargs
			and
			'super_category' in kwargs
			):
				id = kwargs['post_id']
				sup = kwargs['super_category']
				post_table = get_post_table(sup)
				if post_table:
					try:
						kwargs['post_entry'] = session.query(post_table).\
											   filter_by(id=id).one()
					except:
						print '[warning]Specific post could not be found'
		if not 'post_entry' in kwargs:
			flash('[warning]Specific post could not be found')
			return redirect(url_for('mainPage'))
		return func(*args, **kwargs)
	return wrap



def login_required(func):
	"""
	A decorator to confirm login or redirect as needed
	"""
	@wraps(func)
	def wrap(*args, **kwargs):
		print args

		if 'logged_in' in login_session:
			return func(*args, **kwargs)
		else:
			flash("[warning]You need to login first")
			return redirect(login_session['current_url'])
	return wrap

def owner_filter(func):
	"""
	A decorator to confirm if user created the post
	so page can 'edit'/'delete' buttons as needed.

	In order for this to work, the add_specific_post
	decorator must come before this. By doing so
	we ensure post_entry is in the function's arguments.
	"""

	@wraps(func)
	def wrap(*args, **kwargs):
		# if all tests fail, current user is not owner
		kwargs['is_owner'] = False
		if 'post_entry' in kwargs:
			post = kwargs['post_entry']
			if ('user_id' in login_session
				and
				post.user_id == login_session['user_id']):
					# current user created this post
					kwargs["is_owner"] = True

		return func(*args, **kwargs)
	return wrap

def ownership_required(func):
	"""
	A decorator to confirm authorization
	and redirect as needed.

	In order for this to work, the owner_filter decorator
	must come before this. In addition, this
	decorator requires that super_category,
	category and post_entry is in the arguments.
	"""
	@wraps(func)
	def wrap(*args, **kwargs):
		if (
			'is_owner' in kwargs
			and
			kwargs['is_owner']
			and
			'super_category' in kwargs
			and
			'category' in kwargs
			and
			'post_entry' in kwargs
			):
				# is_owner is no longer needed
				del kwargs['is_owner']
				# all tests passed, proceed to page
				return func(*args, **kwargs)
		flash("[warning]You do not own this post")
		# test failed, redirect to last known page
		return redirect(login_session['current_url'])
	return wrap


##########################################################
"""
OAUTH AND LOGIN PAGES
"""
##########################################################


@app.route('/gregslist/login/')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
					for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state,
							GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID,
							FACEBOOK_APP_ID=FACEBOOK_APP_ID)


@app.route('/gregslist/gconnect', methods=['POST'])
def gconnect():
	# Validate state token
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Obtain authorization code
	code = request.data

	try:
		# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(
			json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid.
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
		   % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	# If there was an error in the access token info, abort.
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is used for the intended user.
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(
			json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is valid for this app.
	if result['issued_to'] != GOOGLE_CLIENT_ID:
		response = make_response(
			json.dumps("Token's client ID does not match app's."), 401)
		print "Token's client ID does not match app's."
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_access_token = login_session.get('access_token')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_access_token is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps(
				   'Current user is already connected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the session for later use.
	login_session['access_token'] = credentials.access_token
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['logged_in'] = True
	login_session['provider'] = 'google'
	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']


	user_id = getUserID(login_session['email'])
	if not user_id:
		user_id = createUser(login_session)
	login_session['user_id'] = user_id
	msg = "[success]you are now logged in as %s"
	flash(msg % login_session['username'])
	return render_template('login-success.html',
							username=login_session['username'],
							img_url=login_session['picture'])


@app.route('/gregslist/gdisconnect/')
@login_required
def gdisconnect():
	access_token = None
	if 'access_token' in login_session:
		access_token = login_session['access_token']
	if access_token is None:
		print 'Access Token is None'
		response = make_response(json.dumps(
			'Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
			% login_session['access_token'])
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	print 'result is '
	print result
	if result['status'] == '200':
		del login_session['logged_in']
		del login_session['access_token']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		del login_session['provider']
		flash("[info]You have been logged out")
		return redirect(url_for('mainPage'))
	else:
		flash("[warning]Failed to revoke token for given user")
		return redirect(url_for('mainPage'))

# Facebook login
@app.route('/gregslist/fbconnect', methods=['POST'])
def fbconnect():
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	access_token = request.data
	print "access token received %s " % access_token


	app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
		'web']['app_id']
	app_secret = json.loads(
		open('fb_client_secrets.json', 'r').read())['web']['app_secret']
	url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % ( # NOQA
		app_id, app_secret, access_token)
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]


	# Use token to get user info from API
	userinfo_url = "https://graph.facebook.com/v2.8/me"
	'''
		Due to the formatting for the result
		from the server token exchange we have to
		split the token first on commas and
		select the first index which gives us the
		key : value for the server access token
		then we split it on colons to pull out
		the actual token value and replace the
		remaining quotes with nothing so that it
		can be used directly in the graph api calls
	'''
	token = result.split(',')[0].split(':')[1].replace('"', '')

	url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token # NOQA
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]
	# print "url sent for API access:%s"% url
	# print "API JSON result: %s" % result
	data = json.loads(result)
	login_session['logged_in'] = True
	login_session['provider'] = 'facebook'
	login_session['username'] = data["name"]
	login_session['email'] = data["email"]
	login_session['facebook_id'] = data["id"]

	# The token must be stored in the login_session in order to properly logout
	login_session['access_token'] = token

	# Get user picture
	url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token # NOQA
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]
	data = json.loads(result)

	login_session['picture'] = data["data"]["url"]

	# see if user exists
	user_id = getUserID(login_session['email'])
	if not user_id:
		user_id = createUser(login_session)
	login_session['user_id'] = user_id

	flash("[success]Now logged in as %s" % login_session['username'])

	return render_template('login-success.html',
							username=login_session['username'],
							img_url=login_session['picture'])


# fb logout
@app.route('/gregslist/fbdisconnect/')
@login_required
def fbdisconnect():
	facebook_id = login_session['facebook_id']
	# The access token must me included to successfully logout
	access_token = login_session['access_token']
	url = ('https://graph.facebook.com/%s/permissions?access_token=%s' %
		  (facebook_id, access_token))
	h = httplib2.Http()
	result = h.request(url, 'DELETE')[1]
	if result == '{"success":true}':
		del login_session['logged_in']
		del login_session['user_id']
		del login_session['provider']
		del login_session['username']
		del login_session['email']
		del login_session['facebook_id']
		flash("[info]You have been logged out")
		return redirect(url_for('mainPage'))
	else:
		flash("[warning]Failed to revoke token for given user")
		return redirect(url_for('mainPage'))


##########################################################
"""
CRUD: CATEGORY AND POST PAGES
 ^
read only
"""
##########################################################


@app.route('/')
@app.route('/gregslist/')
@add_entries_from_all_categories
def mainPage(job_categories, stuff_categories, space_categories):
	"""
	A page with links to all Job, Stuff and Space categories
	"""
	login_session['current_url'] = request.url
	super_categories = {"jobs" : job_categories,
						"stuff" : stuff_categories,
						"space" : space_categories}
	return render_template('index.html',
							super_categories=super_categories)


@app.route('/gregslist/JSON/')
@add_entries_from_all_categories
def mainJSON(job_categories, stuff_categories, space_categories):
	"""
	JSON of all categories contained in
	Job, Stuff, and Space super-categories
	"""
	jobs = [entry.serialize for entry in job_categories]
	stuff = [entry.serialize for entry in stuff_categories]
	space = [entry.serialize for entry in space_categories]
	return jsonify(Categories=[{"Jobs" : jobs}, {"Stuff" : stuff}, {"Space" : space}])


@app.route('/gregslist/<super_category>/<category>/')
@add_categories
@add_specific_category
@add_posts
def showPosts(super_category, category,
			  categories, category_entry, post_entries):
	"""
	A page with links to all post
	contained in a specific category
	"""
	return render_template('specific-category.html',
							posts=post_entries,
							category_entry=category_entry,
							categories=categories,
							super_category=super_category)

@app.route('/gregslist/<super_category>/<category>/JSON/')
@add_specific_category
@add_posts
def postsJSON(super_category, category, category_entry, post_entries):
	"""
	Will display JSON that corresponds to the
	URL path components: ex: /gregslist/stuff/boats/JSON
	will return all posts contained in the boats
	category of the stuff super-category
	"""
	return jsonify(Posts=[entry.serialize for entry in post_entries])




@app.route('/gregslist/<super_category>/<category>/post/<int:post_id>/')
@add_specific_post
@owner_filter
def showSpecificPost(super_category, post_id, category, post_entry, is_owner):
	"""
	Displays a specific post. The super_category
	determines what data needs to be displayed
	ie pay and hours for JobPosts or Street,
	City, State, Zip for SpacePosts
	"""
	login_session['current_url'] = request.url
	return render_template('specific-item.html',
							post=post_entry,
							is_owner=is_owner,
							super_category=super_category,
							category=category)

@app.route('/gregslist/<super_category>/<category>/post/<int:post_id>/JSON/')
@add_specific_post
def specificPostJSON(super_category, post_id, category, post_entry):
	"""
	Will display JSON that corresponds to the
	specified post
	"""
	return jsonify(Post=post_entry.serialize)

##########################################################
"""
CRUD: USER INPUT PAGES
^ ^^
create, update, delete
"""
##########################################################

@app.route('/gregslist/<super_category>/<category>/delete/<int:post_id>/',
			methods=['GET', 'POST'])
@login_required
@owner_filter
@ownership_required
def deletePost(super_category, category, post_id, post):
	"""
	A confirmation page for deleting a post
	"""
	login_session['current_url'] = request.url
	if request.method == 'POST':
		session.delete(post)
		flash('[info]"%s" has been deleted' % post.title)
		session.commit()
		return redirect(url_for('showPosts',
								 super_category=super_category,
								 category=category))
	else:
		return render_template('delete-item.html', post=post)

@app.route('/gregslist/<super_category>/<category>/edit/<int:post_id>/',
			methods=['GET', 'POST'])
@login_required
@add_specific_post
@owner_filter
@ownership_required
@add_specific_category
def editPost(super_category, category, post_id, post_entry, category_entry):
	"""
	A page for editing a post
	"""
	login_session['current_url'] = request.url
	if request.method == 'POST':
		"""
		Note: technically since make_entry just
		creates a new entry, the U in CRUD is not being
		accomplished in a pure sense. However since Job,
		Stuff and Space tables contain different items,
		and make_entry can handle each accordingly, it seems
		to make more sense to do it this way.
		Plus make_entry is also used in createPost so we
		avoid writing a lot of the same code twice.
		"""
		updated_post = make_entry(super_category, request, category_entry)
		try:
			# delete the existing entry
			session.delete(post_entry)
			# give the new entry the same id as the previous one
			updated_post.id = post_id
			# add the new one in place of the old one
			session.add(updated_post)
			session.commit()
			msg = '[success]update succesful'
			flash(msg)
			return redirect(url_for('showSpecificPost',
								     super_category=super_category,
								     category=category,
								     post_id=post_id))
		except:
			msg = ('[warning]An unknown problem '
				   'prevented "%s" from being updated')
			flash(msg % request.form['title'])
			return redirect(request.url)
	else:
		if super_category == "jobs":
			params = {"pay" : post_entry.pay, "hours" : post_entry.hours}
		if super_category == "stuff":
			params = {"price" : post_entry.price}
		if super_category == "space":
			params = {"price" : post_entry.price, "street" : post_entry.street,
					  "city" : post_entry.city, "state" : post_entry.state,
					  "zip" : post_entry.zip}
		return render_template('create-or-edit.html',
								super_category=super_category,
								title=post_entry.title,
								description=post_entry.description,
								params=params)

@app.route('/gregslist/choose/category/', methods=['GET', 'POST'])
@login_required
def newPostSuperCategorySelect():
	"""
	A view displayed after user clicks 'post something!'.
	It allows them to select which super-category
	in which they want to post.
	"""
	login_session['current_url'] = request.url
	if request.method == 'POST':
		if 'jobs' in request.form:
			return redirect(url_for('newPostCategorySelect',
									 super_category='jobs'))
		if 'stuff' in request.form:
			return redirect(url_for('newPostCategorySelect',
									 super_category='stuff'))
		if 'space' in request.form:
			return redirect(url_for('newPostCategorySelect',
									 super_category='space'))
	else:
		return render_template('super-category-select.html')


@app.route('/gregslist/<super_category>/select-category/',
			methods=['GET', 'POST'])
@login_required
@add_categories
def newPostCategorySelect(super_category, categories):
	"""
	A view displayed after user selects the super-catetory.
	Here they can select in which category they want they're
	new post to appear
	"""
	login_session['current_url'] = request.url
	return render_template('category-select.html',
							super_category=super_category,
							categories=categories,
							link_func='newPostForm')

@app.route('/gregslist/<super_category>/<category>/new/',
			methods=['GET', 'POST'])
@login_required
@add_specific_category
def newPostForm(super_category, category, category_entry):
	login_session['current_url'] = request.url
	if request.method == 'POST':
		post = make_entry(super_category, request, category_entry)
		try:
			msg = '[success]"%s" successfully added'
			flash(msg % request.form['title'])
			session.add(post)
			session.commit()
			return redirect(url_for('mainPage'))
		except:
			msg = ('[warning]An unknown problem '
				   'prevented "%s" from being added')
			flash(msg % request.form['title'])
			return redirect(request.url)
	else:
		# set the parameters to empty since this is a new post
		if super_category == "jobs":
			params = {"pay" : "", "hours" : ""}
		if super_category == "stuff":
			params = {"price" : ""}
		if super_category == "space":
			params = {"price" : "", "street" : "",
					  "city" : "", "state" : "", "zip" : ""}
		return render_template('create-or-edit.html',
								super_category=super_category,
								title="",
								description="",
								params=params)


def make_entry(super_category, request, category_entry):
	"""
	Used by newPostForm and editPost to create a new
	post based on the unique requirements of each
	super-category. The function determines which
	super-category is being requested then
	creates a new entry, filling it
	with data collected from the form.
	"""
	title =       request.form['title']
	description = request.form['description']
	user_id =     login_session['user_id']
	category_id = category_entry.id
	if super_category == 'jobs':
		pay =   request.form['pay']
		hours = request.form['hours']
		return JobPost(title=title,
					   description=description,
					   pay=pay,
					   hours=hours,
					   category_id=category_id,
					   user_id=user_id)
	elif super_category == 'stuff':
		price = request.form['price']
		return StuffPost(title=title,
						 description=description,
						 price=price,
						 category_id=category_id,
						 user_id=user_id)
	elif super_category == 'space':
		price =  request.form['price']
		street = request.form['street']
		city =   request.form['city']
		state =  request.form['state']
		zip =    request.form['zip']
		return SpacePost(title=title,
						 description=description,
						 price=price,
						 street=street,
						 city=city,
						 state=state,
						 zip=zip,
						 category_id=category_id,
						 user_id=user_id)

##########################################################
"""
HELPER FUNCTIONS
"""
##########################################################

@app.context_processor
def utility_processor():
	"""
	Make several useful functions directly
	accesible by jinja2. That way we can call
	them directly from within each template
	and avoid cluttering up the view functions.
	"""
	def nav_bar():
		return render_template('nav-bar.html')
	def links_and_scripts():
		return render_template('links-and-scripts.html')
	def flashed_message():
		return render_template('flashed-messages.html')
	def categories(super_category, categories, link_func):
		return render_template('categories.html',
							    super_category=super_category,
							    categories=categories,
							    link_func=link_func)
	def categories_mini(super_category, categories, highlight_id):
		return render_template("categories-mini.html",
								super_category=super_category,
								categories=categories,
								highlight_id=highlight_id)
	def job_specific_form(params):
		return render_template('job-specific-form.html', **params)
	def stuff_specific_form(params):
		return render_template('stuff-specific-form.html', **params)
	def space_specific_form(params):
		return render_template('space-specific-form.html', **params)
	def job_specific_items(post):
		return render_template('job-specific-items.html', post=post)
	def stuff_specific_items(post):
		return render_template('stuff-specific-items.html', post=post)
	def space_specific_items(post):
		return render_template('space-specific-items.html', post=post)
	def login_provider():
		"""
		used to set the logout link depending on
		if we're logged in under google or facebook
		"""
		if 'provider' in login_session:
			return login_session['provider']
	return dict(render_flashed_message=flashed_message,
				login_provider=login_provider,
				render_nav_bar=nav_bar,
				render_links_and_scripts=links_and_scripts,
				render_job_specific_form=job_specific_form,
				render_stuff_specific_form=stuff_specific_form,
				render_space_specific_form=space_specific_form,
				render_job_specific_items=job_specific_items,
				render_stuff_specific_items=stuff_specific_items,
				render_space_specific_items=space_specific_items,
				render_categories=categories,
				render_categories_mini=categories_mini)

def createUser(login_session):
	""" add user to the db """
	newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email=login_session['email']).one()
	return user.id

def getUserInfo(user_id):
	"""retive user entry from db"""
	user = session.query(User).filter_by(id=user_id).one()
	return user

def getUserID(email):
	"""retieve user id from db using email as the input"""
	try:
		user = session.query(User).filter_by(email=email).one()
		return user.id
	except:
		return None




if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)
