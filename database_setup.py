from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists # noqa


Base = declarative_base()

# http://sqlalchemy-utils.readthedocs.io/en/latest/database_helpers.html#create-database # noqa
if not database_exists('postgresql://cataloguser:password@localhost/itemcat'):
    create_database('postgresql://cataloguser:password@localhost/itemcat')


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    password = Column(String(250))
    picture = Column(String(250))
    google_id = Column(String(250))

    @property
    def serialize(self):

        # Returns object data in json
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'google_id': self.google_id,
            'picture': self.picture
        }


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    users_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(Users)

    @property
    def serialize(self):

        # Returns object data in json
        return {
            'id': self.id,
            'name': self.name,
        }


class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    price = Column(String(8))
    picture = Column(String(250))
    users_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(Users)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    @property
    def serialize(self):

        # Returns object data in json
        return {
            'id': self.id,
            'name': self.name,
            'descripton': self.description,
            'price': self.price,
            'picture': self.picture,
        }


engine = create_engine('postgresql://cataloguser:password@localhost/itemcat')
Base.metadata.create_all(engine)
