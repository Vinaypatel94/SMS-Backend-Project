from fastapi import FastAPI, Depends, HTTPException, status, Header
from models import User
from database import Base, engine, SessionLocal
from schema import UserCreate, UserLogin, Token, UserResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import List

# FastAPI app
app = FastAPI()

# Secret key for JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWT Authenticator class
class JWTAuthenticator:
    def __init__(self, secret_key: str, algorithm: str, access_token_expire_minutes: int):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return username
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

# Initialize the JWT Authenticator
authenticator = JWTAuthenticator(SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES)

# Dependency to verify JWT and retrieve the user
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

    
# Routes
@app.post("/register")
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
        role=user.role,
    )
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

# login route
@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not authenticator.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = authenticator.create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# protected route
@app.get("/protected")
def protected_route(current_user: User = Depends(protected_user)):
    return {"message": f"Welcome {current_user.username}!"}


@app.get("/users", response_model=List[UserResponse])
def get_all_users(current_user: User = Depends(protected_user), db: Session = Depends(get_db)):
    if current_user.role not in ["manager", "admin"]:  # Restrict access
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers and admins can access this route"
        )
    users = db.query(User).all()
    return users

# @app.get("/user/{username}", response_model=UserResponse)
# def get_user_by_username(username: str, current_user: User = Depends(protected_user), db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.username == username).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user


# create dependencies
def admin_required(current_user: User = Depends(protected_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform this action"
        )
    return current_user   

# crud operation for admin
@app.post("/admin/users", response_model=UserResponse, dependencies=[Depends(admin_required)])
def create_user_by_admin(user: UserCreate, db: Session = Depends(get_db)):
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
        role=user.role if user.role else "staff"  # Default role is staff
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# get specific user by username only admin
@app.get("/admin/users/{username}", response_model=UserResponse, dependencies=[Depends(admin_required)])
def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# update user information only admin
@app.put("/admin/users/{username}", response_model=UserResponse, dependencies=[Depends(admin_required)])
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
    
    return user


# delete user information only admin
@app.delete("/admin/users/{username}", dependencies=[Depends(admin_required)])
def delete_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"message": f"User {username} deleted successfully"}

