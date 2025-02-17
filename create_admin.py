# create_admin.py

from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Role, Permission
from auth import authenticator


def create_super_admin():
    db: Session = SessionLocal()

    # Define the roles
    role_permissions_map = {
        "admin": ["create_user", "update_user", "delete_user", "view_user"],
        "manager": ["update_user", "view_user"],
        "hr": ["update_user", "view_user"],
        "employee": ["view_user"]
         
         }

    # Fetch existing roles
    existing_roles = {role.name for role in db.query(Role).all()}
    new_roles = [Role(name=role) for role in role_permissions_map.keys() if role not in existing_roles]

    new_roles = [Role(name=role) for role in role_permissions_map.keys() if role not in existing_roles]

    if new_roles:
        db.add_all(new_roles)
        db.commit()
        print(f"Created roles: {[role.name for role in new_roles]}")
    else:
        print("All roles already exist.")

    # Permission
    all_permission_names = set(perm for perms in role_permissions_map.values() for perm in perms)

    # Fetch existing permissions
    existing_permissions = {perm.name for perm in db.query(Permission).all()}
    new_permissions = [Permission(name=perm) for perm in all_permission_names if perm not in existing_permissions]
    
    if new_permissions:
        db.add_all(new_permissions)
        db.commit()
        print(f"Created permissions: {[perm.name for perm in new_permissions]}")

    # Fetch all permissions
    all_permissions ={prem.name: prem for prem in  db.query(Permission).all()}

    # Assign permissions to roles
    for role_name, permission_names in role_permissions_map.items():
        role = db.query(Role).filter_by(name=role_name).first()
        if role:
            role.permissions = [all_permissions[perm] for perm in permission_names]
            db.commit()
            print(f"Updated {role_name} role with permissions: {permission_names}")

    # # Create 'admin' role if not exists
    # admin_role = db.query(Role).filter_by(name="admin").first()
    # if not admin_role:
    #     admin_role = Role(name="admin")
    #     admin_role.permissions.extend(all_permissions)
    #     db.add(admin_role)
    #     db.commit()
    #     db.refresh(admin_role)
    #     print("Admin role created and assigned all permissions.")

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
        roles=[db.query(Role).filter_by(name="admin").first()]
    )

    db.add(super_admin)
    db.commit()
    db.refresh(super_admin)
    print(f"Super Admin created with username: {super_admin.username}")


if __name__ == "__main__":
    create_super_admin()
