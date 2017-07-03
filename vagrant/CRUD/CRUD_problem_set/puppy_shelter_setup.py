#!/usr/bin/env python
#
# database_setup.py -- a database for storing info related to puppies in a shelter
#
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, BLOB, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()

# classes

class Shelter(Base):
    """a table class for Shelter"""
    __tablename__ = 'shelter'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    address = Column(String(80), nullable=False)
    city = Column(String(80), nullable=False)
    state = Column(String(2), nullable=False)
    zipCode = Column(Integer, nullable=False)
    website = Column(String(80), nullable=False)

class Puppy(Base):
    """a table for each Puppy"""
    __tablename__ = 'puppy'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    dateOfBirth = Column(Date, nullable=False)
    gender = Column(String(6), nullable=False)
    weight = Column(Float, nullable=False)
    shelter_id = Column(Integer, ForeignKey('shelter.id'))
    picture = Column(String(500), nullable=False)

###### insert at end of file ######

engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.create_all(engine)
