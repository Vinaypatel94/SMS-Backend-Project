from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import LeaveRecord, User, Role, LeaveStatus, user_role_association
from schemas import LeaveRecordCreate, LeaveRecordResponse
from dependencies import leave_apply_required, leave_approve_or_reject_required
from email_service import send_email

router = APIRouter(prefix="/api", tags=["notification"])

# Leave request API


@router.post("/leave_request/", response_model=LeaveRecordResponse)
def apply_leave(
    leave: LeaveRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(leave_apply_required),
):
    try:
        if current_user.id != leave.user_id:
            raise HTTPException(
                status_code=403,
                detail="You can only apply leave for your own account.",
            )

        user = db.query(User).filter(User.id == leave.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        manager = (
            db.query(User)
            .join(user_role_association, User.id == user_role_association.c.user_id)
            .join(Role, Role.id == user_role_association.c.role_id)
            .filter(Role.name == "manager")
            .first()
        )

        if manager is None:
            raise HTTPException(
                status_code=404,
                detail="No manager found to receive leave requests.",
            )

        new_leave = LeaveRecord(**leave.model_dump())
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

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error processing leave request: {str(e)}")


# Leave approved and rejected API
@router.put("/leave_request/{leave_id}/", response_model=LeaveRecordResponse)
def approve_reject_leave(
    leave_id: int,
    status: LeaveStatus,
    db: Session = Depends(get_db),
    _: User = Depends(leave_approve_or_reject_required),
):
    try:
        if status not in [LeaveStatus.APPROVED, LeaveStatus.REJECTED]:
            raise HTTPException(
                status_code=400, detail="Invalid status. Use 'approved' or 'rejected'."
            )

        leave_request = db.query(LeaveRecord).filter(
            LeaveRecord.id == leave_id).first()

        if not leave_request:
            raise HTTPException(
                status_code=404, detail="Leave request not found")

        leave_request.status = status
        db.commit()
        db.refresh(leave_request)

        user = db.query(User).filter(User.id == leave_request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        send_email(user.email, f"Leave Request {status.value.capitalize()}",
                f"Your leave request (ID: {leave_request.id}) has been {status.value}.")

        return leave_request

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")