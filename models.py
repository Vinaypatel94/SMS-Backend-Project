
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table, Date, DateTime, Time, DECIMAL
from sqlalchemy.orm import relationship
import datetime
import enum
from database import Base


# Many-to-Many between Roles and Permissions
role_permission_association = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey(
        "permissions.id"), primary_key=True),
)

# Many-to-Many between Users and Roles
user_role_association = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
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

    roles = relationship(
        "Role", secondary=user_role_association, back_populates="users")

    attendances = relationship(
        "Attendance", back_populates="user", cascade="all, delete")
    leave_records = relationship(
        "LeaveRecord", back_populates="user", cascade="all, delete")


class Role(Base):

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    users = relationship(
        "User", secondary=user_role_association, back_populates="roles")
    permissions = relationship(
        "Permission", secondary=role_permission_association, back_populates="roles")


class Permission(Base):

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    roles = relationship(
        "Role", secondary=role_permission_association, back_populates="permissions")



class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    ON_LEAVE = "on_leave"


class LeaveType(str, enum.Enum):
    SICK_LEAVE = "sick_leave"
    VACATION = "vacation"
    UNPAID_LEAVE = "unpaid_leave"

# SMS Attendance models
class Attendance(Base):

    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, nullable=False)
    check_in = Column(Time, nullable=True)
    check_out = Column(Time, nullable=True)
    total_hours = Column(DECIMAL(5, 2), nullable=True)
    overtime_hours = Column(DECIMAL(5, 2), nullable=True)

    status = Column(Enum(AttendanceStatus), nullable=False)


    user = relationship("User", back_populates="attendances")


class LeaveRecord(Base):

    __tablename__ = "leave_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    leave_type = Column(Enum(LeaveType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="LEAVE_PENDING")


    user = relationship("User", back_populates="leave_records")
