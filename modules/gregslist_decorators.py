from flask import flash, redirect
from flask import session as login_session
from functools import wraps
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import (Base,
                            JobCategory,
                            StuffCategory,
                            SpaceCategory,
                            JobPost,
                            StuffPost,
                            SpacePost)

# Connect to Database and create database session
engine = create_engine('postgresql://timnelson:password@localhost/mydb')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


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

# Decorators

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
