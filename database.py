from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# DATABASE_URL = "sqlite:///./SMS.db" 
DATABASE_URL = "mysql+pymysql://root:12345@localhost:3306/sms_db"

# Set up the database engine
engine = create_engine(DATABASE_URL)

# Create a session maker for handling DB connections
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()  

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()