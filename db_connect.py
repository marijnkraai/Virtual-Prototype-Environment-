from sqlalchemy import create_engine
from db_config import DATABASE_URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pyodbc

# Setup db
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()      


