from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Attendance, LeaveRecord, User, Role, user_role_association
from schemas import AttendanceCreate, LeaveRecordCreate, AttendanceResponse, LeaveRecordResponse, AttendanceUpdate, LeaveRecordUpdate
from typing import List
from dependencies import admin_or_manager_required, protected_user

router = APIRouter()

router = APIRouter(prefix="/api", tags=["attendance"])


@router.post("/attendances/", response_model=AttendanceResponse, dependencies=[Depends(admin_or_manager_required)])
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


@router.get("/attendances/{user_id}", response_model=List[AttendanceResponse], dependencies=[Depends(admin_or_manager_required)])
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


@router.get("/leave_records/{user_id}", response_model=List[LeaveRecordResponse], dependencies=[Depends(admin_or_manager_required)])
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
            status_code=500, detail=f"erro fatching record{str(e)}")


@router.put("/leave_record/{leave_id}", response_model=LeaveRecordResponse, dependencies=[Depends(admin_or_manager_required)])
def update_leave(leave_id: int, leave_update: LeaveRecordUpdate, db: Session = Depends(get_db)):
    leave = db.query(LeaveRecord).filter(LeaveRecord.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="leave record not found")

    try:
        update_data = leave_update.model_dump(
            exclude_unset=True)  # Use model_dump for Pydantic v2
        for key, value in update_data.items():
            setattr(leave, key, value)

        db.commit()
        db.refresh(leave)
        return leave

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error updating leave record")


@router.delete("/leave_record/{leave_id}", dependencies=[Depends(admin_or_manager_required)])
def delete_leave(leave_id: int, db: Session = Depends(get_db)):
    try:
        leave = db.query(LeaveRecord).filter(
            LeaveRecord.id == leave_id).first()
        if not leave:
            raise HTTPException(
                status_code=404, detail="leave record not found")

        db.delete(leave)
        db.commit()
        return {"message": "leave record deleted successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f" deleting leave record:{str(e)}")
