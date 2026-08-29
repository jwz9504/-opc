"""create ORM baseline

Revision ID: 0001_orm_baseline
"""
import sqlalchemy as sa

from alembic import op

revision = "0001_orm_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "meetings_orm",
        sa.Column("meeting_id", sa.String(64), primary_key=True),
        sa.Column("owner_id", sa.String(255), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("resume_token", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "artifacts_orm",
        sa.Column("artifact_id", sa.String(255), primary_key=True),
        sa.Column("artifact_type", sa.String(64), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("artifacts_orm")
    op.drop_table("meetings_orm")
