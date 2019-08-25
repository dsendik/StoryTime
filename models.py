from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, Base):
    __tablename__ = 'Users'
    username = Column(String(100), primary_key=True)
    password = Column(String(100), unique=False)
    message = Column(String(5000), unique=False)


class Message(UserMixin, Base):
    __tablename__ = 'Messages'
    ROWID = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), ForeignKey('Users.username'))
    message_content = Column(String(5000), unique=False)
    image = Column(String(1000), unique=False)
    storyID = Column(Integer, ForeignKey('Stories.storyID'))

class Sketch(UserMixin, Base):
    __tablename__ = 'Sketches'
    ROWID = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), ForeignKey('Users.username'))
    sketch_url = Column(String(1000), unique=False)
    storyID = Column(Integer, ForeignKey('Stories.storyID'))


class Story(UserMixin, Base):
    __tablename__ = 'Stories'
    storyID = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), ForeignKey('Users.username'))
    storyPrompt = Column(String(1000), unique=False)
    message_content = Column(String(5000), ForeignKey('Messages.message_content'))
    score = Column(Integer, unique=False)
    image = Column(String(1000), unique=False)

def set_password(self, password):
    self.password_hash = generate_password_hash(password)

def check_password(self, password):
    return check_password_hash(self.password_hash, password)
