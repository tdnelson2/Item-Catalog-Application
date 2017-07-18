from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
  """a table for storing information about each user"""
  __tablename__ = 'user'
  id = Column(Integer, primary_key=True)
  name = Column(String(250))
  email = Column(String(250))
  picture = Column(String(250))


class Job(Base):
    __tablename__ = 'job'

    id = Column(Integer, primary_key=True)
    category = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


class Stuff(Base):
    __tablename__ = 'stuff'

    id = Column(Integer, primary_key=True)
    category = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


class Space(Base):
    __tablename__ = 'space'

    id = Column(Integer, primary_key=True)
    category = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

class JobPost(Base):
    __tablename__ = 'job_post'

    id = Column(Integer, primary_key = True)
    title =Column(String(80), nullable = False)
    description = Column(String(250))
    pay = Column(String(8))
    hours = Column(String(8))
    job_id = Column(Integer,ForeignKey('job.id'))
    category = relationship(Job)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

class StuffPost(Base):
    __tablename__ = 'stuff_post'

    id = Column(Integer, primary_key = True)
    title =Column(String(80), nullable = False)
    description = Column(String(250))
    price = Column(String(8))
    stuff_id = Column(Integer,ForeignKey('stuff.id'))
    category = relationship(Stuff)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

class SpacePost(Base):
    __tablename__ = 'space_post'

    id = Column(Integer, primary_key = True)
    title =Column(String(80), nullable = False)
    description = Column(String(250))
    price = Column(String(8))
    space_id = Column(Integer,ForeignKey('space.id'))
    category = relationship(Space)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)



engine = create_engine('sqlite:///gregslist.db')


Base.metadata.create_all(engine)
