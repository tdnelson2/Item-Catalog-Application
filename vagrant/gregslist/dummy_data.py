from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, JobCategory, StuffCategory, SpaceCategory, JobPost, StuffPost, SpacePost

from random import randint

engine = create_engine('sqlite:///gregslist.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
admin_user = User(name="Robo Admin", email="robo_admin@gregslist.com",
             picture='static/images/robo_admin.jpg')
session.add(admin_user)
session.commit()

this_user = session.query(User).filter_by(email="robo_admin@gregslist.com").one()

job_categories = ["finance", "office", "art", "science", "retail", "software", "media", "web", "government", "legal", "marketing", "service"]
dummy_jobs = ["Bailiff", "Horticulturalist", "Radio presenter", "Dressmaker", "Social worker", "Anthropologist", "Car dealer", "Tour guide", "Speech therapist", "Bookmaker", "Comedian", "Garden designer", "Plumber"]
description = "Far far away, behind the word mountains, far from the countries Vokalia and Consonantia, there live the blind texts. Separated they live in Bookmarksgrove right at the coast of the Semantics, a large language ocean. A small river named Duden flows by their place and supplies it with the necessary regelialia."

for job_cat in job_categories:
    category = JobCategory(name=job_cat, user_id=this_user.id)

    session.add(category)
    session.commit()

    new_cat = session.query(JobCategory).filter_by(name=job_cat).one()

    for job in dummy_jobs:
        title = job + " " + job_cat + " worker"
        pay_in_cents = str(randint(800,10000))
        hours_in_minutes = randint(5,40) * 60
        job_post = JobPost(title=title,
                           description=description,
                           pay_in_cents=pay_in_cents,
                           hours_in_minutes=hours_in_minutes,
                           category=new_cat.id,
                           user_id=this_user.id)

        session.add(job_post)
        session.commit()


print "added menu items!"