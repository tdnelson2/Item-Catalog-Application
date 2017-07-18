from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem, User

engine = create_engine('sqlite:///restaurantmenuwithusers.db')
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
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

job_categories = ["finance", "office", "art", "science", "retail", "software", "media", "web", "government", "legal", "marketing", "service"]
dummy_jobs = ["Bailiff", "Horticulturalist", "Radio presenter", "Dressmaker", "Social worker", "Anthropologist", "Car dealer", "Tour guide", "Speech therapist", "Bookmaker", "Comedian", "Garden designer", "Plumber"]
description = "Far far away, behind the word mountains, far from the countries Vokalia and Consonantia, there live the blind texts. Separated they live in Bookmarksgrove right at the coast of the Semantics, a large language ocean. A small river named Duden flows by their place and supplies it with the necessary regelialia."


# Jobs
job1 = Job(user_id=1, category="Urban Burger")

session.add(job1)
session.commit()

# Finance Job Posts
job_post = JobPost()

session.add(job_post)
session.commit()


print "added menu items!"