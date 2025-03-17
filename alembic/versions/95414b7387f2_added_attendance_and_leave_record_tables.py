"""Added attendance and leave_record tables

Revision ID: 95414b7387f2
Revises: 7de84d36ef28
Create Date: 2025-02-19 05:38:52.451256

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95414b7387f2'
down_revision: Union[str, None] = '7de84d36ef28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # create attendances table
    op.create_table("attendances",
                    sa.Column("id", sa.Integer(), primary_key=True, index=True),
                    sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), index=True),
                    sa.Column("date", sa.Date, nullable=False, index=True),
                    sa.Column("check_in", sa.Time, nullable=True, index=True),
                    sa.Column("check_out", sa.Time, nullable=True, index=True),
                    sa.Column("total_hours", sa.Interval, nullable=True, index=True),
                    sa.Column("overtime_hours", sa.Interval,nullable=True, index=True),
                    sa.Column("status", sa.String(length=30), index=True) 
                    )
    
    # create leave_record table
    op.create_table("leave_records",
                    sa.Column("id", sa.Integer, primary_key=True, index=True),
                    sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), index=True),
                    sa.Column("leave_type", sa.String(length=40), index=True),
                    sa.Column("start_date", sa.Time, index=True),
                    sa.Column("end_date", sa.Time, index=True),
                    sa.Column("status", sa.String(length=40), index=True)
                    
                    )


def downgrade() -> None:
    op.drop_table("attendances")
    op.drop_table("leave_records")
    
