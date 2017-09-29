from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, JobCategory, StuffCategory, \
                           SpaceCategory, JobPost, StuffPost, SpacePost

from random import randint

from gregslist_raw_dummy_data import description, job_categories, dummy_jobs, \
                                     stuff_categories, dummy_stuff, \
                                     space_categories, dummy_space

engine = create_engine('postgresql://ubuntu:password@localhost/mydb')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create dummy user
admin_user = User(name="Robo Admin", email="robo_admin@gregslist.com",
             picture='static/images/robo_admin.jpg')
session.add(admin_user)
session.commit()

this_user = session.query(User).\
            filter_by(email="robo_admin@gregslist.com").one()

# Create jobs categories and job posts

for job_cat in job_categories:
    category = JobCategory(name=job_cat, user_id=this_user.id)

    session.add(category)
    session.commit()

    new_cat = session.query(JobCategory).filter_by(name=job_cat).one()

    print new_cat.name

    for job in dummy_jobs:
        title = job + " " + job_cat + " worker"
        pay = "$" + str(randint(7,100)) + ".00"
        hours = str(randint(5,40))
        job_post = JobPost(title=title,
                           description=description,
                           pay=pay,
                           hours=hours,
                           category_id=new_cat.id,
                           user_id=this_user.id)

        session.add(job_post)
        session.commit()


print "\n\njobs added!\n\n"

# Create stuff categories and stuff posts

for stuff_cat in stuff_categories:
    category = StuffCategory(name=stuff_cat, user_id=this_user.id)

    session.add(category)
    session.commit()

    new_cat = session.query(StuffCategory).filter_by(name=stuff_cat).one()

    print new_cat.name

    for thing in dummy_stuff:
        price = "$" + str(randint(1,500)) + ".00"
        stuff_post = StuffPost(title=thing,
                           description=description,
                           price=price,
                           category_id=new_cat.id,
                           user_id=this_user.id)

        session.add(stuff_post)
        session.commit()


print "\n\nstuff added!\n\n"

# Create space categories and space posts

for space_cat in space_categories:
    category = SpaceCategory(name=space_cat, user_id=this_user.id)

    session.add(category)
    session.commit()

    new_cat = session.query(SpaceCategory).filter_by(name=space_cat).one()

    print new_cat.name

    for space in dummy_space:
        price = "$" + str(randint(100,1000000000)) + ".00"
        space_post = SpacePost(title=space,
                           description=description,
                           price=price,
                           street="6666 NW 23rd",
                           city="Portland",
                           state="OR",
                           zip="97210",
                           category_id=new_cat.id,
                           user_id=this_user.id)

        session.add(space_post)
        session.commit()


print "\n\nspace added!\n\n"


