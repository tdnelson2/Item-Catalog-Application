from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   jsonify,
                   url_for,
                   flash)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import (Base,
                            User,
                            JobCategory,
                            StuffCategory,
                            SpaceCategory,
                            JobPost,
                            StuffPost,
                            SpacePost)
from flask import session as login_session
import json
import requests
# from functools import wraps
from modules.login import login
from modules.gregslist_decorators import (get_post_table,
                                          add_entries_from_all_categories,
                                          add_categories,
                                          add_specific_category,
                                          add_posts,
                                          add_specific_post,
                                          login_required,
                                          owner_filter,
                                          ownership_required)


# Connect to Database and create database session
engine = create_engine('sqlite:///gregslist.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

app.register_blueprint(login)


# ##########################################################
# """
# CRUD: CATEGORY AND POST PAGES
#  ^
# read only
# """
# ##########################################################


@app.route('/')
@app.route('/gregslist/')
@add_entries_from_all_categories
def mainPage(job_categories, stuff_categories, space_categories):
    """
    A page with links to all Job, Stuff and Space categories
    """
    login_session['current_url'] = request.url
    super_categories = {"jobs": job_categories,
                        "stuff": stuff_categories,
                        "space": space_categories}
    return render_template('index.html',
                           super_categories=super_categories)


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
@add_specific_post
@owner_filter
@ownership_required
def deletePost(super_category, category, post_id, post_entry):
    """
    A confirmation page for deleting a post
    """
    login_session['current_url'] = request.url
    if request.method == 'POST':
        current_session = session.object_session(post_entry)
        current_session.delete(post_entry)
        flash('[info]"%s" has been deleted' % post_entry.title)
        current_session.commit()
        return redirect(url_for('showPosts',
                                super_category=super_category,
                                category=category))
    else:
        return render_template('delete-item.html', post=post_entry)


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
        current_session = session.object_session(post_entry)
        updated_post = make_entry(super_category, request, category_entry)
        try:
            # delete the existing entry
            current_session.delete(post_entry)
            # give the new entry the same id as the previous one
            updated_post.id = post_id
            # add the new one in place of the old one
            current_session.add(updated_post)
            current_session.commit()
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
            params = {"pay": post_entry.pay, "hours": post_entry.hours}
        if super_category == "stuff":
            params = {"price": post_entry.price}
        if super_category == "space":
            params = {"price": post_entry.price, "street": post_entry.street,
                      "city": post_entry.city, "state": post_entry.state,
                      "zip": post_entry.zip}
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
            params = {"pay": "", "hours": ""}
        if super_category == "stuff":
            params = {"price": ""}
        if super_category == "space":
            params = {"price": "", "street": "",
                      "city": "", "state": "", "zip": ""}
        return render_template('create-or-edit.html',
                               super_category=super_category,
                               title="",
                               description="",
                               params=params)


##########################################################
"""
JSON RESPONSE
"""
##########################################################


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
    return jsonify(Categories=[{"Jobs": jobs},
                               {"Stuff": stuff},
                               {"Space": space}])


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
HELPER FUNCTIONS
"""
##########################################################

def make_entry(super_category, request, category_entry):
    """
    Used by newPostForm and editPost to create a new
    post based on the unique requirements of each
    super-category. The function determines which
    super-category is being requested then
    creates a new entry, filling it
    with data collected from the form.
    """
    title = request.form['title']
    description = request.form['description']
    user_id = login_session['user_id']
    category_id = category_entry.id
    if super_category == 'jobs':
        pay = request.form['pay']
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
        price = request.form['price']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        zip = request.form['zip']
        return SpacePost(title=title,
                         description=description,
                         price=price,
                         street=street,
                         city=city,
                         state=state,
                         zip=zip,
                         category_id=category_id,
                         user_id=user_id)


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


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
