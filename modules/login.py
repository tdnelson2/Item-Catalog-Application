from flask import Blueprint, request, jsonify, render_template, flash, url_for, redirect
from flask import session
import random
import string
import json
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User

# Connect to Database and create database session
engine = create_engine('postgresql://ubuntu:password@localhost/mydb')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()
path_google_secret = '/var/www/secrets/client_secret.json'
path_fb_secret = '/var/www/secrets/fb_client_secrets.json'

login = Blueprint('login', 'login', url_prefix='/gregslist')

##########################################################
"""
OAUTH AND LOGIN PAGES
Most of the code in this section is taken directly from
the Udacity examples with some minor modifications
"""
##########################################################


# https://console.developers.google.com/apis/credentials?project=greglist-174419
GOOGLE_CLIENT_ID = json.loads(
    open(path_google_secret, 'r').read())['web']['client_id']

# https://developers.facebook.com/apps/555177401540603/settings/
FACEBOOK_APP_ID = json.loads(
    open(path_fb_secret, 'r').read())['web']['app_id']



@login.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    session['state'] = state
    return render_template('login.html', STATE=state,
                           GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID,
                           FACEBOOK_APP_ID=FACEBOOK_APP_ID)


@login.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(path_google_secret, scope='')
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

    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    session['logged_in'] = True
    session['provider'] = 'google'
    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']

    user_id = getUserID(session['email'])
    if not user_id:
        user_id = createUser(session)
    session['user_id'] = user_id
    msg = "[success]you are now logged in as %s"
    flash(msg % session['username'])
    return render_template('login-success.html',
                           username=session['username'],
                           img_url=session['picture'])


@login.route('/gdisconnect/')
def gdisconnect():
    access_token = None
    if 'access_token' in session:
        access_token = session['access_token']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del session['logged_in']
        del session['access_token']
        del session['gplus_id']
        del session['username']
        del session['email']
        del session['picture']
        del session['provider']
        flash("[info]You have been logged out")
        return redirect(url_for('mainPage'))
    else:
        flash("[warning]Failed to revoke token for given user")
        return redirect(url_for('mainPage'))

# Facebook login


@login.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open(path_fb_secret, 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open(path_fb_secret, 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (  # NOQA
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

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    session['logged_in'] = True
    session['provider'] = 'facebook'
    session['username'] = data["name"]
    session['email'] = data["email"]
    session['facebook_id'] = data["id"]

    # The token must be stored in the session in order to properly logout
    session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(session['email'])
    if not user_id:
        user_id = createUser(session)
    session['user_id'] = user_id

    flash("[success]Now logged in as %s" % session['username'])

    return render_template('login-success.html',
                           username=session['username'],
                           img_url=session['picture'])


# fb logout
@login.route('/fbdisconnect/')
def fbdisconnect():
    facebook_id = session['facebook_id']
    # The access token must me included to successfully logout
    access_token = session['access_token']
    url = ('https://graph.facebook.com/%s/permissions?access_token=%s' %
           (facebook_id, access_token))
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    if result == '{"success":true}':
        del session['logged_in']
        del session['user_id']
        del session['provider']
        del session['username']
        del session['email']
        del session['facebook_id']
        flash("[info]You have been logged out")
        return redirect(url_for('mainPage'))
    else:
        flash("[warning]Failed to revoke token for given user")
        return redirect(url_for('mainPage'))

# storing and retrieving user data fromt the db

def createUser(login_session):
    """ add user to the db """
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    db_session.add(newUser)
    db_session.commit()
    user = db_session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """retive user entry from db"""
    user = db_session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """retieve user id from db using email as the input"""
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

