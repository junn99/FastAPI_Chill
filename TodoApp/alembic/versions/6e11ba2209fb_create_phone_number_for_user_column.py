"""Create phone number for user column

Revision ID: 6e11ba2209fb
Revises: 
Create Date: 2025-02-20 16:19:15.948431

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e11ba2209fb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 데이터베이스 업그레이드
# 전화번호의 새 열을 갖게 함 
def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', 
                                     sa.String(),
                                     nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'phone_number')
