"""extend ORM persistence tables

Revision ID: 0002_extend_orm
"""
import sqlalchemy as sa

from alembic import op

revision = "0002_extend_orm"
down_revision = "0001_orm_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("meeting_states_orm", sa.Column("meeting_id", sa.String(64), primary_key=True), sa.Column("payload", sa.Text(), nullable=False))
    op.create_table("request_keys_orm", sa.Column("request_key", sa.String(255), primary_key=True), sa.Column("meeting_id", sa.String(64), nullable=False))


def downgrade() -> None:
    op.drop_table("request_keys_orm")
    op.drop_table("meeting_states_orm")
