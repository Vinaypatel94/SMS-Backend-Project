from fastapi import FastAPI
from database import Base, engine
from routes import users, admin, attendance, notification
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Middleware
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(attendance.router)
app.include_router(notification.router)
