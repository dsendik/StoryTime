from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlite3


engine = create_engine('sqlite:////Users/Dan/PycharmProjects/TwitterChat/chatDB.db', convert_unicode=True)
db_session = sessionmaker(bind=engine)
Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)