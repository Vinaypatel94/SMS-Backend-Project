"""Initial table

Revision ID: 7de84d36ef28
Revises: None
Create Date: 2025-02-13 09:52:36.958317

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7de84d36ef28'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # create  user table
    op.create_table("users",
                    sa.Column('id', sa.Integer(), primary_key=True, index=True),
                    sa.Column('name', sa.String(length=30), index=True),
                    sa.Column('age', sa.Integer(), index=True),
                    sa.Column('email', sa.String(length=30), unique=True, index=True),
                    sa.Column('phone_no', sa.String(length=12), unique=True, index=True),
                    sa.Column('username', sa.String(length=30), unique=True, index=True),
                    sa.Column('hashed_password', sa.String(length=255), index=True)
                    )

    # create roles table
    op.create_table('roles',
                    sa.Column("id", sa.Integer, primary_key=True, index=True),
                    sa.Column('name', sa.String(length=35), unique=True, index=True)
                     )

    # create permissions table
    op.create_table('permissions',
                    sa.Column('id', sa.Integer, primary_key=True, index=True),
                    sa.Column('name', sa.String(length=200), unique=True, index=True)
                    )

    # create user_roles association table
    op.create_table('user_roles',
                    sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
                    sa.Column('role_id', sa.Integer, sa.ForeignKey('roles.id'))
                    )

    # create role_permission association table
    op.create_table( 'role_permissions',
                    sa.Column('role_id', sa.Integer, sa.ForeignKey('roles.id'), primary_key=True),
                    sa.Column('permission_id', sa.Integer, sa.ForeignKey('permissions.id'), primary_key=True)
                   )

    
def downgrade() -> None:
    op.drop_table('users')
    op.drop_table('roles')
    op.drop_table('permissions')
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
     
