#   
#   Mainumby Database.
#   Based almost entirely on what's in Guampa.
#   Uses the Object Relational Mapper implementation of SQLAlchemy.
#
########################################################################
#
#   This file is part of the HLTDI L^3 project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyright (C) 2015, 2016 HLTDI <gasser@cs.indiana.edu>
#   
#   This program is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 3 of
#   the License, or (at your option) any later version.
#   
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#   
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# =========================================================================

# 2015.07.11
# -- Created

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from flask import _app_ctx_stack
import datetime

DATABASE = 'sqlite:///mainumby.db'

Base = declarative_base()

def make_engine():
    return create_engine(DATABASE, echo=False)

def make_session():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'db_session'):
        engine = make_engine()
        Session = sessionmaker(bind=engine)
        top.db_session = Session()
    return top.db_session

def initialize_db(engine=None):
    if not engine:
        engine = make_engine()
    Base.metadata.create_all(engine)

### ORM mapped classes

class User(Base):
    """A user of the system."""
    
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    fullname = Column(String)
    email = Column(String)
    pwhash = Column(String)

    def __init__(self, username, fullname, email, pwhash):
        self.username = username
        self.fullname = fullname
        self.email = email
        self.pwhash = pwhash

    def __repr__(self):
       return "<User({}, '{}', '{}')>".format(self.id, self.username, self.fullname)

#class Document(Base):
#    """A document uploaded by a user, eventually segmented into sentences."""
#    
#    __tablename__ = 'documents'
#
#    id = Column(Integer, primary_key=True)
#    title = Column(String)
#    userid = Column(Integer, ForeignKey('users.id'))
#
#    def __init__(self, title, userid):
#        self.title = title
#        self.userid = userid
#
#    def __repr__(self):
#       return "<Document({}, '{}')>".format(self.id, self.title)

class Sentence(Base):
    """A sentence to be (or already) translated."""
    
    __tablename__ = 'sentences'

    id = Column(Integer, primary_key=True)
    text = Column(String)
    userid = Column(Integer, ForeignKey('users.id'))

    def __init__(self, text, userid):
        self.text = text
        self.userid = userid

    def __repr__(self):
        text = self.text[:25] + '...' if len(self.text) > 25 else self.text
        return "<Sentence({}, '{}')>".format(self.id, text)

class Segment(Base):
    """A segment of a sentence being translated."""
    
    __tablename__ = 'segments'

    id = Column(Integer, primary_key=True)
    text = Column(String)
    sentenceid = Column(Integer, ForeignKey('sentences.id'))
    sentence = relationship("Sentence", backref=backref("segments", order_by=id))

    def __init__(self, text, sentenceid):
        self.text = text
        self.sentenceid = docid

    def __repr__(self):
        text = self.text[:25] + '...' if len(self.text) > 25 else self.text
        return "<Segment({}, '{}')>".format(self.id, text)

class Translation(Base):
    """A translation of a Sentence."""
    
    __tablename__ = 'translations'

    id = Column(Integer, primary_key=True)
    text = Column(String)
    sentenceid = Column(Integer, ForeignKey('sentences.id'))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    userid = Column(Integer, ForeignKey('users.id'))

    def __init__(self, text, userid, sentenceid):
        self.text = text
        self.sentenceid = sentenceid
        self.userid = userid

    def __repr__(self):
        text = self.text[:25] + '...' if len(self.text) > 25 else self.text
        return "<Translation({}, '{}', {})>".format(self.id, text, self.sentenceid)

class Comment(Base):
    """A User's comment on a Translation of a Sentence. Should maybe also have translationid
    as a column?"""
    
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    text = Column(String)
    sentenceid = Column(Integer, ForeignKey('sentences.id'))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    userid = Column(Integer, ForeignKey('users.id'))
    sentence = relationship("Sentence", backref=backref("comments", order_by=id))

    def __init__(self, text, userid, sentenceid):
        self.text = text
        self.userid = userid
        self.sentenceid = sentenceid

    def __repr__(self):
        text = self.text[:25] + '...' if len(self.text) > 25 else self.text
        return "<Comment({}, '{}', {})>".format(self.id, text, self.sentenceid)

# Here are some users
u1 = ['mary', "Mary Jones", "maryj@gmail.com", "345abc"]
u2 = ['almaz', "Almaz Beqele", "almaz@yahoo.com", "xxx###"]
u3 = ['fatuma', "Fatuma Ali", "fali11@me.com", "f%$--"]

# Here's an example document
doc1 = """This is an example of a document.
It has a few English sentences in it.
And that's pretty much it.
If you expected more, I'm sorry.
"""

# Here are some translations
t1 = "Este es un ejemplo de un documento."
t2 = "Tiene un par oraciones ingleses."
t3 = "Y nada mas."
t4 = "Si esperabas mas, lo siento."

# Create all the tables (do this only the first time).
#Base.metadata.create_all(engine)

#ed = User(name='ed', fullname='Ed Jones', password='edspassword')
#mary = User(name='mary', fullname='Mary Smith', password='maryspassword')

# Create a session
#session = Session()

