from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserLogin, Token, UserResponse
from auth import authenticator
from dependencies import protected_user
from typing import List

router = APIRouter()

router = APIRouter(prefix="/api", tags=["auth"]) 

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.username == user.username).first()
        if not db_user or not authenticator.verify_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = authenticator.create_access_token(
            data={"sub": db_user.username})
        return {"access_token": access_token, "token_type": "bearer"}
     
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"login error:{str(e)}")
    
    finally:
        db.close()


@router.get("/user/{username}", response_model=UserResponse)
def get_user_by_username(username: str, current_user: User = Depends(protected_user), db: Session = Depends(get_db)):
    try:  
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error fatching  user record{str(e)}")
    
    