#!/usr/bin/env python
#
# database_setup.py -- a database for storing various restaurant menus
#
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# classes

class Restaurant(Base):
    """a table class for Restaurant"""
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

class MenuItem(Base):
    """a table for each MenuItem"""
    __tablename__ = 'menu_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)

###### insert at end of file ######

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.create_all(engine)
