"""add report and audit ORM tables

Revision ID: 0003_report_audit
"""
import sqlalchemy as sa

from alembic import op

revision = "0003_report_audit"
down_revision = "0002_extend_orm"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("reports_orm", sa.Column("meeting_id", sa.String(64), primary_key=True), sa.Column("payload", sa.Text(), nullable=False), sa.Column("markdown_path", sa.Text(), nullable=False))
    op.create_table("audit_events_orm", sa.Column("event_id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("meeting_id", sa.String(64), nullable=False), sa.Column("actor_id", sa.String(255), nullable=False), sa.Column("action", sa.String(128), nullable=False), sa.Column("details", sa.Text(), nullable=False))


def downgrade() -> None:
    op.drop_table("audit_events_orm")
    op.drop_table("reports_orm")
