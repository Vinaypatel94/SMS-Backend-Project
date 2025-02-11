from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    age: int
    email: EmailStr
    phone_no:int
    username: str
    password: str
    role: str
    

class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    phone_no: int
    email: str
    username: str 
    role: str
    
    
class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str