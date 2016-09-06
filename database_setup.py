import datetime
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, DateTime


Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(250), nullable=False)
    email = Column(String(250), unique=True, nullable=False)
    picture = Column(String(250))
    registered = Column(DateTime, default=datetime.datetime.utcnow)

    @classmethod
    def get_id_by_email(cls, session, email):
        try:
            user = session.query(cls).filter_by(email=email).one()
            return user.id
        except:
            return None

    @classmethod
    def by_id(cls, session, id):
        try:
            user = session.query(cls).filter_by(id=id).one()
            return user
        except:
            return None

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(250), nullable=False)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }



class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(250), nullable=False)
    description = Column(Text, nullable=False)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'cat_id': self.category_id,
            'description': self.description,
            'id': self.id,
            'name': self.name
        }


engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
