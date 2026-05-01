from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from models import Attendance, LeaveRecord, LeaveStatus, User, Role, user_role_association
from schemas import AttendanceCreate, LeaveRecordCreate, AttendanceResponse, LeaveRecordResponse, AttendanceUpdate, LeaveRecordUpdate
from typing import List
from dependencies import admin_or_manager_required, protected_user

router = APIRouter()

router = APIRouter(prefix="/api", tags=["attendance"])


def _has_permission(user: User, permission_name: str) -> bool:
    return any(
        permission.name == permission_name
        for role in user.roles
        for permission in role.permissions
    )


@router.post("/attendance/", response_model=AttendanceResponse, dependencies=[Depends(admin_or_manager_required)])
def create_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == attendance.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        """ Once validated, the data is converted into an Attendance model and saved to the database.
        unpacks JSON data into an SQLAlchemy model"""

        new_attendance = Attendance(**attendance.dict())
        db.add(new_attendance)
        db.commit()
        db.refresh(new_attendance)
        return new_attendance

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"error creating attendance record{str(e)}")



@router.get("/attendance/{user_id}", response_model=List[AttendanceResponse], dependencies=[Depends(admin_or_manager_required)])
def get_user_attendance(user_id: int, db: Session = Depends(get_db)):
    try:
        attendances = db.query(Attendance).filter(
            Attendance.user_id == user_id).all()
        if not attendances:
            raise HTTPException(
                status_code=404, detail="No attendance records found")
        return attendances

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"error get attendance record{str(e)}")



@router.delete("/attendance/{attendance_id}", dependencies=[Depends(admin_or_manager_required)])
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):

    try:
        attendance = db.query(Attendance).filter(
            Attendance.id == attendance_id).first()
        if not attendance:
            raise HTTPException(
                status_code=404, detail="Attendance record not found")
        db.delete(attendance)
        db.commit()
        return {"message": "Attendance record deleted successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"error deleting attendance record{str(e)}")

    finally:
        db.close()



@router.put("/attendance/{attendance_id}", response_model=AttendanceResponse, dependencies=[Depends(admin_or_manager_required)])
def update_attendance(attendance_id: int, attendance_update: AttendanceUpdate, db: Session = Depends(get_db)):
    try:
        attendance = db.query(Attendance).filter(
            Attendance.id == attendance_id).first()
        if not attendance:
            raise HTTPException(
                status_code=404, detail="Attendance record not found")

        for key, value in attendance_update.dict(exclude_unset=True).items():
            setattr(attendance, key, value)

        db.commit()
        db.refresh(attendance)
        return attendance

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"error updating attendance record{str(e)}")


@router.get("/leave_record/{user_id}", response_model=List[LeaveRecordResponse], dependencies=[Depends(admin_or_manager_required)])
def get_user_leaves(user_id: int, db: Session = Depends(get_db)):
    try:
        leaves = db.query(LeaveRecord).filter(
            LeaveRecord.user_id == user_id).all()
        if not leaves:
            raise HTTPException(
                status_code=404, detail="No leave records found")
        return leaves

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"error fatching record{str(e)}")



@router.put("/leave_record/{leave_id}", response_model=LeaveRecordResponse)
def update_leave(
    leave_id: int,
    leave_update: LeaveRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(protected_user),
):
    leave = db.query(LeaveRecord).filter(LeaveRecord.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="leave record not found")

    try:
        is_owner = leave.user_id == current_user.id
        can_manage_leave = _has_permission(current_user, "update_leave")
        can_apply_leave = _has_permission(current_user, "create_leave")

        if not can_manage_leave:
            if not (is_owner and can_apply_leave):
                raise HTTPException(
                    status_code=403,
                    detail="You do not have permission to update this leave record.",
                )
            if leave.status != LeaveStatus.PENDING:
                raise HTTPException(
                    status_code=400,
                    detail="You can only update pending leave records.",
                )

        if leave.status != LeaveStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail="Only pending leave records can be updated.",
            )

        update_data = leave_update.model_dump(
            exclude_unset=True)  # Use model_dump for Pydantic v2

        if not can_manage_leave and "status" in update_data:
            raise HTTPException(
                status_code=403,
                detail="You cannot change leave status.",
            )

        for key, value in update_data.items():
            setattr(leave, key, value)

        db.commit()
        db.refresh(leave)
        return leave

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error updating leave record: {str(e)}")


@router.delete("/leave_record/{leave_id}")
def delete_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(protected_user),
):
    try:
        leave = db.query(LeaveRecord).filter(
            LeaveRecord.id == leave_id).first()
        if not leave:
            raise HTTPException(
                status_code=404, detail="leave record not found")

        is_owner = leave.user_id == current_user.id
        can_manage_leave = _has_permission(current_user, "delete_leave")
        can_apply_leave = _has_permission(current_user, "create_leave")

        if not can_manage_leave:
            if not (is_owner and can_apply_leave):
                raise HTTPException(
                    status_code=403,
                    detail="You do not have permission to delete this leave record.",
                )
            if leave.status != LeaveStatus.PENDING:
                raise HTTPException(
                    status_code=400,
                    detail="You can only delete pending leave records.",
                )

        if leave.status != LeaveStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail="Only pending leave records can be deleted.",
            )

        db.delete(leave)
        db.commit()
        return {"message": "leave record deleted successfully"}

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f" deleting leave record:{str(e)}")
