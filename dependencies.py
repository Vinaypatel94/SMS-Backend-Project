from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import authenticator


def protected_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    parts = authorization.strip().split(" ", 1)
    if len(parts) != 2:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, token = parts
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
    data = authenticator.decode_token(token)
    user = db.query(User).filter(User.id == data["user_id"]).first()
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


def _require_any_permission(current_user: User, required_permissions: set[str]) -> User:
    user_permissions = {
        permission.name
        for role in current_user.roles
        for permission in role.permissions
    }
    if user_permissions.intersection(required_permissions):
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have required permission for this action.",
    )


def leave_apply_required(current_user: User = Depends(protected_user)) -> User:
    return _require_any_permission(current_user, {"create_leave"})


def leave_approve_required(current_user: User = Depends(protected_user)) -> User:
    return _require_any_permission(current_user, {"approve_leave"})


def leave_reject_required(current_user: User = Depends(protected_user)) -> User:
    return _require_any_permission(current_user, {"reject_leave"})


def leave_approve_or_reject_required(current_user: User = Depends(protected_user)) -> User:
    return _require_any_permission(current_user, {"approve_leave", "reject_leave"})
