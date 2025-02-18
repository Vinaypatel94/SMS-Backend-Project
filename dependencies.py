from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import authenticator


def protected_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    scheme, token = authorization.split()
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = authenticator.decode_token(token)
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def admin_required(current_user: User = Depends(protected_user)):
    if not any(role.name == "admin" for role in current_user.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform this action"
        )
    return current_user


def admin_or_manager_required(current_user: User = Depends(protected_user)):
    role_names = [role.name for role in current_user.roles]
    if not any(role in ["admin", "manager", "hr"] for role in role_names):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and managers or hr can access this resource"
        )
    return current_user 
