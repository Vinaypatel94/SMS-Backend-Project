from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table, Date, Time, DECIMAL
from sqlalchemy.orm import relationship
import enum
from database import Base


# ==============================
# Association Tables
# ==============================

role_permission_association = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

user_role_association = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


# ==============================
# ENUMS
# ==============================

class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    ON_LEAVE = "on_leave"


class LeaveType(str, enum.Enum):
    SICK_LEAVE = "sick_leave"
    VACATION = "vacation"
    UNPAID_LEAVE = "unpaid_leave"


class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# ==============================
# USER TABLE
# ==============================

class User(Base):

    __tablename__ = "users"
    __table_args__ = {"mysql_engine": "InnoDB"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(100))
    age = Column(Integer)

    email = Column(String(150), unique=True, index=True)
    phone_no = Column(String(20), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)

    hashed_password = Column(String(255), nullable=False)

    roles = relationship(
        "Role",
        secondary=user_role_association,
        back_populates="users"
    )

    attendances = relationship(
        "Attendance",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    leave_records = relationship(
        "LeaveRecord",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# ==============================
# ROLE TABLE
# ==============================

class Role(Base):

    __tablename__ = "roles"
    __table_args__ = {"mysql_engine": "InnoDB"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, index=True)

    users = relationship(
        "User",
        secondary=user_role_association,
        back_populates="roles"
    )

    permissions = relationship(
        "Permission",
        secondary=role_permission_association,
        back_populates="roles"
    )


# ==============================
# PERMISSION TABLE
# ==============================

class Permission(Base):

    __tablename__ = "permissions"
    __table_args__ = {"mysql_engine": "InnoDB"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, index=True)

    roles = relationship(
        "Role",
        secondary=role_permission_association,
        back_populates="permissions"
    )


# ==============================
# ATTENDANCE TABLE
# ==============================

class Attendance(Base):

    __tablename__ = "attendances"
    __table_args__ = {"mysql_engine": "InnoDB"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    date = Column(Date, nullable=False)
    check_in = Column(Time)
    check_out = Column(Time)

    total_hours = Column(DECIMAL(5, 2), default=0)
    overtime_hours = Column(DECIMAL(5, 2), default=0)

    status = Column(
        Enum(AttendanceStatus, name="attendance_status"),
        nullable=False
    )

    user = relationship("User", back_populates="attendances")


# ==============================
# LEAVE RECORD TABLE
# ==============================

class LeaveRecord(Base):

    __tablename__ = "leave_records"
    __table_args__ = {"mysql_engine": "InnoDB"}

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    leave_type = Column(
        Enum(LeaveType, name="leave_type"),
        nullable=False
    )

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    status = Column(
        Enum(LeaveStatus, name="leave_status"),
        default=LeaveStatus.PENDING,
        nullable=False
    )

    user = relationship("User", back_populates="leave_records")