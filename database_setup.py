import datetime
from sqlalchemy import create_engine, ForeignKey, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
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
        except Exception, e:
            print "Get id by email failed"
            print e
            return None

    @classmethod
    def by_id(cls, session, id):
        try:
            user = session.query(cls).filter_by(id=id).one()
            return user
        except Exception, e:
            print "User query by id failed"
            print e
            return None

    @classmethod
    def by_email(cls, email):
        try:
            user = session.query(cls).filter_by(email=email).first()
            return user
        except Exception, e:
            print "Query user by email failed"
            print e
            return None

    @classmethod
    def new(cls, username, email, picture):
        try:
            new_user = User(username=username, email=email, picture=picture)
            session.add(new_user)
            session.commit()
            return new_user
        except Exception, e:
            print "Create new user failed"
            print e
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

    @classmethod
    def all(cls):
        try:
            c = session.query(cls).all()
            return c
        except Exception, e:
            print "Query categories failed"
            print e
            return None

    @classmethod
    def by_id(cls, id):
        try:
            c = session.query(cls).filter_by(id=id).one()
            return c
        except:
            print "Query category by id failed"
            return None

    @classmethod
    def by_name(cls, name):
        try:
            c = session.query(cls).filter_by(name=name.lower()).one()
            return c
        except:
            print "Query category by name failed"
            return None

    @classmethod
    def new(cls, name, user_id):
        try:
            c = cls(name=name.lower(), user_id=user_id)
            session.add(c)
            session.commit()
            return c
        except Exception, e:
            print "Ceate new category failed"
            print e
            return None

    @classmethod
    def delete(cls, category):
        try:
            session.delete(category)
            session.commit()
        except Exception, e:
            print "Delete category failed"
            print e


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

    @classmethod
    def order_by_created_with_limit(cls, limit):
        try:
            items = session.query(cls).order_by(desc(cls.created)).limit(limit)
            return items
        except Exception, e:
            print "Query items fail"
            print e
            return None

    @classmethod
    def by_category_id(cls, category_id):
        try:
            items = session.query(Item).filter_by(category_id=category_id).all()
            return items
        except Exception, e:
            print "Item query by category_id failed"
            print e
            return None

    @classmethod
    def by_cat_id_and_item_id(cls, category_id, item_id):
        try:
            item = session.query(cls).filter_by(category_id=category_id, id=item_id).one()
            return item
        except Exception, e:
            print "Item query failed"
            print e
            return None

    @classmethod
    def by_name_and_cat_id(cls, name, category_id):
        try:
            item = session.query(cls).filter_by(name=name.lower(),
                    category_id=category_id).one()
            return item
        except:
            print "Item category by name failed"
            return None

    @classmethod
    def new(cls, name, category_id, description, user_id):
        try:
            item = Item(name=name.lower(), category_id=category_id,
                        description=description, user_id=user_id)
            session.add(item)
            session.commit()
            return item
        except Exception, e:
            print "Create new item failed"
            print e
            return None

    def update(self, new_name, new_cat_id, new_description):
        if new_name:
            self.name = new_name
        if new_cat_id:
            self.category_id = new_cat_id
        if new_description:
            self.description = new_description
        try:
            session.add(self)
            session.commit
        except Exception, e:
            print "Update item failed"
            print e

    @classmethod
    def delete(cls, item):
        try:
            session.delete(item)
            session.commit()
        except Exception, e:
            print "Delete item failed"
            print e

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
