from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import LeaveRecord, User, Role, user_role_association
from schemas import LeaveRecordCreate, LeaveRecordResponse
from dependencies import admin_or_manager_required, protected_user
from email_service import send_email


router = APIRouter()

router = APIRouter(prefix="/api", tags=["notification "])

# Leave request API


@router.post("/leave_request/", response_model=LeaveRecordResponse, dependencies=[Depends(protected_user)])
def apply_leave(leave: LeaveRecordCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == leave.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    manager = (
        db.query(User)
        .join(user_role_association, User.id == user_role_association.c.user_id)
        .join(Role, Role.id == user_role_association.c.role_id)
        .filter(Role.name == "manager")
        .first())

    try:
        new_leave = LeaveRecord(**leave.dict())
        db.add(new_leave)
        db.commit()
        db.refresh(new_leave)

        leave_id = new_leave.id
        leave_type = new_leave.leave_type
        start_date = new_leave.start_date
        end_date = new_leave.end_date

        send_email(user.email, "Leave Request Submitted",
                   f"Your leave request (ID: {leave_id}) has been submitted:")

        send_email(manager.email, "New Leave Request",
                   f"A new leave request ID{leave_id} has been submitted by {user.name}\n\n user id  {user.id}\n  {leave_type} \n start date: {start_date}\n end date: {end_date}")

        return new_leave

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error processing leave request: {str(e)}")

    finally:
        db.close()


# Leave approved and rejected API
@router.put("/leave_request/{leave_id}/", response_model=LeaveRecordResponse, dependencies=[Depends(admin_or_manager_required)])
def approve_reject_leave(leave_id: int, status: str, db: Session = Depends(get_db)):
    try:

        leave_request = db.query(LeaveRecord).filter(
            LeaveRecord.id == leave_id).first()

        if not leave_request:
            raise HTTPException(
                status_code=404, detail="Leave request not found")

        if status not in ["approved", "rejected"]:
            raise HTTPException(
                status_code=400, detail="Invalid status. Use 'approved' or 'rejected'.")

        leave_request.status = status
        db.commit()
        db.refresh(leave_request)

        user = db.query(User).filter(User.id == leave_request.user_id).first()
        send_email(user.email, f"Leave Request {status.capitalize()}",
                f"Your leave request (ID: {leave_request.id}) has been {status}.")

        return leave_request
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, details=f"Error prosessing request{str(e)}")
    
    finally:
        db.close()