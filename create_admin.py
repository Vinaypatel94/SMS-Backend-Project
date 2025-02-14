# create_admin.py

from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Role
from auth import authenticator

def create_super_admin():
    db: Session = SessionLocal()

    # Create 'admin' role if not exists
    admin_role = db.query(Role).filter_by(name="admin").first()
    if not admin_role:
        admin_role = Role(name="admin")
        db.add(admin_role)
        db.commit()
        print("Admin role created.")

    # Check if Super Admin already exists
    existing_admin = db.query(User).filter_by(username="admin").first()
    if existing_admin:
        print("Super Admin already exists.")
        return

    # Create super admin user
    hashed_password = authenticator.hash_password("admin123")
    super_admin = User(
        name="Super Admin",
        username="admin",
        email="admin@gmail.com",
        phone_no="1234567890",
        age=35,
        hashed_password=hashed_password,
        roles=[admin_role]
    )

    db.add(super_admin)
    db.commit()
    db.refresh(super_admin)
    print(f"Super Admin created with username: {super_admin.username}")

if __name__ == "__main__":
    create_super_admin()
