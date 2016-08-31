import datetime
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, DateTime


Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    created = Column(DateTime, default=datetime.datetime.utcnow)

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    description = Column(Text)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
