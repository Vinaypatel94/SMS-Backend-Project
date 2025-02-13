from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserLogin, Token, UserResponse
from auth import authenticator
from dependencies import protected_user
from typing import List

router = APIRouter()

@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = authenticator.hash_password(user.password)
    new_user = User(
        name=user.name,
        age=user.age,
        phone_no=user.phone_no,
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not authenticator.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = authenticator.create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/user/{username}", response_model=UserResponse)
def get_user_by_username(username: str, current_user: User = Depends(protected_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# @router.get("/users", response_model=List[UserResponse])
# def get_all_users(current_user: User = Depends(protected_user), db: Session = Depends(get_db)):
#     users = db.query(User).all()
#     return users

# # protected route
# @router.get("/protected")
# def protected_route(current_user: User = Depends(protected_user)):
#     return {"message": f"Welcome {current_user.username}!"}