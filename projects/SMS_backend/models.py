from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime 
from database import Base


# Many-to-Many between Roles and Permissions
role_permission_association = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.role_id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.permission_id"), primary_key=True),
)

# Many-to-Many between Users and Roles
user_role_association = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.role_id"), primary_key=True),
)
class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer, index=True)
    email = Column(String, unique=True, index=True)
    phone_no = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, index=True)
    role = Column(String, index=True, default="staff")  # default role
    
    roles = relationship("Role", secondary=user_role_association, back_populates="users")

class Role(Base):

    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, unique=True, index=True)

    users = relationship("User", secondary=user_role_association, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permission_association, back_populates="roles")


class Permission(Base):

    __tablename__ = "permission"

    permission_id = Column(Integer, primary_key=True, index=True)
    permission_name = Column(String, unique=True, index=True)

    roles = relationship("Role", secondary=role_permission_association, back_populates="permissions")









# # SMS Attendance models
# class AttendanceRecord(Base):
#     __tablename__ = "attendance_records"
#     id = Column(Integer, primary_key=True, index=True)
#     employee_id = Column(Integer, ForeignKey("users.id"))
#     check_in = Column(DateTime, default=datetime.utcnow)
#     check_out = Column(DateTime, nullable=True)
#     total_hours = Column(DECIMAL(5,2), nullable=True)
#     overtime_hours = Column(DECIMAL(5,2), nullable=True)
#     status = Column(String)
#     method = Column(String)
#     recorded_at = Column(DateTime, default=datetime.utcnow)


# class LeaveRecord(Base):
#     __tablename__ = "leave_records"
#     id = Column(Integer, primary_key=True, index=True)
#     employee_id = Column(Integer, ForeignKey("users.id"))
#     leave_date = Column(DateTime)
#     leave_type = Column(String)
#     status = Column(String)
#     applied_at = Column(DateTime, default=datetime.utcnow)


