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


class JobCategory(Base):
    __tablename__ = 'job_category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


class StuffCategory(Base):
    __tablename__ = 'stuff_category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


class SpaceCategory(Base):
    __tablename__ = 'space_category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

class JobPost(Base):
    __tablename__ = 'job_post'

    id = Column(Integer, primary_key = True)
    title = Column(String(80), nullable = False)
    description = Column(String(250))
    pay = Column(String(10))
    hours = Column(String(5))
    category_id = Column(Integer, ForeignKey('job_category.id'))
    category = relationship(JobCategory)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

class StuffPost(Base):
    __tablename__ = 'stuff_post'

    id = Column(Integer, primary_key = True)
    title =Column(String(80), nullable = False)
    description = Column(String(250))
    price = Column(String(10))
    category_id = Column(Integer,ForeignKey('stuff_category.id'))
    category = relationship(StuffCategory)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

class SpacePost(Base):
    __tablename__ = 'space_post'

    id = Column(Integer, primary_key = True)
    title =Column(String(80), nullable = False)
    description = Column(String(250))
    price = Column(String(30))
    street = Column(String(250))
    city = Column(String(80))
    state = Column(String(40))
    zip = Column(String(10))
    category_id = Column(Integer,ForeignKey('space_category.id'))
    category = relationship(SpaceCategory)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)



engine = create_engine('sqlite:///gregslist.db')


Base.metadata.create_all(engine)
