from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Role, Permission
from schemas import UserCreate, UserResponse
from dependencies import admin_required, admin_or_manager_required
from typing import List
from auth import authenticator

router = APIRouter(prefix="/admin", tags=["admin"]) 


@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=400, detail="Username already registered")

    hashed_password = authenticator.hash_password(user.password)
    new_user = User(
        name=user.name,
        age=user.age,
        phone_no=user.phone_no,
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )

    # fatch and assign roles to the user
    if user.role:
        roles = db.query(Role).filter(Role.name.in_(user.role)).all()
        if not roles:
            raise HTTPException(status_code=404, detail="roles not found")
        new_user.roles = roles

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}


@router.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(admin_or_manager_required)):
    users = db.query(User).all()

    users_response = [
        {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "email": user.email,
            "phone_no": user.phone_no,
            "age": user.age,
            "roles": [
                {
                    "id": role.id,
                    "name": role.name,
                    "permissions": [{"id": perm.id, "name": perm.name} for perm in role.permissions]
                }
                for role in user.roles
            ]
        }
        for user in users
    ]
    return users_response


# update user information only admin
@router.put("/users/{username}", response_model=UserResponse, dependencies=[Depends(admin_or_manager_required)])
def update_user(username: str, user_update: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = user_update.name
    user.age = user_update.age
    user.phone_no = user_update.phone_no
    user.email = user_update.email
    user.role = user_update.role

    # Update roles
    if user_update.role:
        roles = db.query(Role).filter(Role.name.in_(user_update.role)).all()
        user.roles = roles

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{username}")
def delete_user(username: str, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted"}
