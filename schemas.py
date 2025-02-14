from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class PermissionSchema(BaseModel):
    id: Optional[int]
    name: str


class RoleSchema(BaseModel):
    id: Optional[int]
    name: str
    permissions: List[PermissionSchema] = []


class UserCreate(BaseModel):
    id: Optional[int] = None
    name: str
    age: int
    email: EmailStr
    phone_no: int
    username: str
    password: str
    role: List[str] = []


class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    phone_no: int
    email: str
    username: str
    roles: list[RoleSchema]

    class Config:
        orm_mode = True
