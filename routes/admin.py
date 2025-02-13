from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserResponse
from dependencies import admin_required
from typing import List

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    return db.query(User).all()

# update user information only admin
@router.put("/users/{username}", response_model=UserResponse, dependencies=[Depends(admin_required)])
def update_user(username: str, user_update: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = user_update.name
    user.age = user_update.age
    user.phone_no = user_update.phone_no
    user.email = user_update.email
    user.role = user_update.role

    db.commit()
    db.refresh(user)

    return {"message":"update data sucessfully"}


@router.delete("/users/{username}")
def delete_user(username: str, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}
