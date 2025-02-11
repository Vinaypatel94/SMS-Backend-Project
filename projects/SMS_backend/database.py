from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./SMS.db" 

# Set up the database engine
engine = create_engine(DATABASE_URL,connect_args={"check_same_thread": False})

# Create a session maker for handling DB connections
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()  

