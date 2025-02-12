from sqlalchemy import Column, String, Integer
from database import Base

class User(Base):
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer, index=True)
    email = Column(String, unique=True, index=True)
    phone_no = Column(Integer, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String,index=True)
    role = Column(String, index=True, default="staff") #default role
    

# class Role(Base):
    
#     __tablename__ = "roles"
    
#     role_id = Column(Integer, primary_key=True, index=True)
#     role_name = Column(String, unique=True, index=True)
    

# class Permession(Base):
    
#     __tablename__ = "permission"
    
#     permession_id = Column(Integer, primary_key=True, index=True)
#     permession_name = Column(String, unique=True, index=True)