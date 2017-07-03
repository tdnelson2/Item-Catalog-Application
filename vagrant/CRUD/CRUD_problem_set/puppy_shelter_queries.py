#!/usr/bin/env python
#
# database_setup.py -- queries for searching within the shelterpuppies database
#
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from puppy_shelter_setup import Base, Shelter, Puppy
from sqlalchemy import func
engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


print "1. Query all of the puppies and return the results in ascending alphabetical order"

for puppy in session.query(Puppy).order_by(Puppy.name.asc()).all():
    print puppy.name


print "2. Query all of the puppies that are less than 6 months old organized by the youngest first"

today = datetime.date.today()
SixMonthsAgo = today - datetime.timedelta(days = 182)

for puppy in session.query(Puppy).\
    filter(Puppy.dateOfBirth > SixMonthsAgo ).\
    order_by(Puppy.dateOfBirth.desc()):
    print puppy.name
    print puppy.dateOfBirth
    print ""

print "3. Query all puppies by ascending weight"

for puppy in session.query(Puppy).\
    order_by(Puppy.weight).all():
    print puppy.name
    print puppy.weight
    print ""

print "4. Query all puppies grouped by the shelter in which they are staying"

for item in session.query(Shelter, func.count(Puppy.id)).\
    join(Puppy).group_by(Shelter.id).all():
    print item[0].id, item[0].name, item[1]
    print ""