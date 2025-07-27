from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
import sqlite3

SQLALCHEMY_DATABASE_URL = 'sqlite:///../database.sqlite'

engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args={"check_same_thread": False})

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection): 
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind = engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()