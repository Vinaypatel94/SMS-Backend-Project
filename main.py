from fastapi import FastAPI
from database import Base, engine
from routes import users, admin, attendance, notification

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(attendance.router)
app.include_router(notification.router)
