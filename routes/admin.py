from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import User, Role
from schemas import UserCreate, UserResponse
from dependencies import admin_required, admin_or_manager_required
from typing import List
from auth import authenticator

router = APIRouter(prefix="/admin", tags=["admin"]) 


# ========================= REGISTER USER =========================
@router.post("/register", status_code=201)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    # Username check
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=400,
            detail="Username already taken. Please choose another username."
        )

    # Phone check
    if db.query(User).filter(User.phone_no == user.phone_no).first():
        raise HTTPException(
            status_code=400,
            detail="This phone number is already registered. Try logging in or use another number."
        )

    # Email check
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=400,
            detail="This email is already registered. Please use a different email."
        )

    hashed_password = authenticator.hash_password(user.password)

    new_user = User(
        name=user.name,
        age=user.age,
        phone_no=user.phone_no,
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )

    # Assign roles
    if user.role:
        roles = db.query(Role).filter(Role.name.in_(user.role)).all()
        if not roles:
            raise HTTPException(status_code=404, detail="Roles not found")
        new_user.roles = roles

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="User already exists with same credentials."
        )

    return {"message": "User registered successfully"}


# ========================= GET USERS =========================
@router.get("/users", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_or_manager_required)
):
    users = db.query(User).all()

    return [
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
                    "permissions": [
                        {"id": perm.id, "name": perm.name}
                        for perm in role.permissions
                    ],
                }
                for role in user.roles
            ],
        }
        for user in users
    ]


# ========================= UPDATE USER =========================
@router.put("/users/{username}", response_model=UserResponse)
def update_user(
    username: str,
    user_update: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_or_manager_required)
):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Phone check (exclude current user)
    if db.query(User).filter(
        User.phone_no == user_update.phone_no,
        User.username != username
    ).first():
        raise HTTPException(
            status_code=400,
            detail="This phone number is already in use."
        )

    # Email check
    if db.query(User).filter(
        User.email == user_update.email,
        User.username != username
    ).first():
        raise HTTPException(
            status_code=400,
            detail="This email is already in use."
        )

    # Username change check (optional)
    if user_update.username != username:
        if db.query(User).filter(User.username == user_update.username).first():
            raise HTTPException(
                status_code=400,
                detail="Username already taken."
            )
        user.username = user_update.username

    # Update fields
    user.name = user_update.name
    user.age = user_update.age
    user.phone_no = user_update.phone_no
    user.email = user_update.email

    # Update roles
    if user_update.role:
        roles = db.query(Role).filter(Role.name.in_(user_update.role)).all()
        user.roles = roles

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Update failed due to duplicate data."
        )

    return user


# ========================= DELETE USER =========================
@router.delete("/users/{username}")
def delete_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}