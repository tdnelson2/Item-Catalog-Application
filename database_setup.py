from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class A_User(Base):
  """a table for storing information about each user"""
  __tablename__ = 'a_user'
  id = Column(Integer, primary_key=True)
  name = Column(String(250))
  email = Column(String(250))
  picture = Column(String(250))


class JobCategory(Base):
    __tablename__ = 'job_category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('a_user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'user_id' : self.user_id
        }


class StuffCategory(Base):
    __tablename__ = 'stuff_category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('a_user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'user_id' : self.user_id
        }


class SpaceCategory(Base):
    __tablename__ = 'space_category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('a_user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'user_id' : self.user_id
        }

class JobPost(Base):
    __tablename__ = 'job_post'

    id = Column(Integer, primary_key = True)
    title = Column(String(80), nullable = False)
    description = Column(String(250))
    pay = Column(String(10))
    hours = Column(String(5))
    category_id = Column(Integer, ForeignKey('job_category.id'))
    category = relationship(JobCategory)
    user_id = Column(Integer, ForeignKey('a_user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'title' : self.title,
            'description' : self.description,
            'pay' : self.pay,
            'hours' : self.hours,
            'category_id' : self.category_id,
            'user_id' : self.user_id
        }

class StuffPost(Base):
    __tablename__ = 'stuff_post'

    id = Column(Integer, primary_key = True)
    title =Column(String(80), nullable = False)
    description = Column(String(250))
    price = Column(String(10))
    category_id = Column(Integer,ForeignKey('stuff_category.id'))
    category = relationship(StuffCategory)
    user_id = Column(Integer, ForeignKey('a_user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'title' : self.title,
            'description' : self.description,
            'price' : self.price,
            'category_id' : self.category_id,
            'user_id' : self.user_id
        }

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

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'title' : self.title,
            'description' : self.description,
            'price' : self.price,
            'street' : self.street,
            'city' : self.city,
            'state' : self.state,
            'zip' : self.zip,
            'category_id' : self.category_id,
            'user_id' : self.user_id
        }



engine = create_engine('postgresql://timnelson:password@localhost/mydb')


Base.metadata.create_all(engine)
