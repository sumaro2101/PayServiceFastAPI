"""add coupons

Revision ID: d5e180680631
Revises: 25938cbce120
Create Date: 2024-10-19 17:25:34.347800

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d5e180680631"
down_revision: Union[str, None] = "25938cbce120"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "coupons",
        sa.Column("number", sa.String(), nullable=False),
        sa.Column("discount", sa.Float(), nullable=False),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column(
            "create_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("end_at", sa.DateTime(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("number"),
    )
    op.create_table(
        "coupon_user_association",
        sa.Column("coupon_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["coupon_id"],
            ["coupons.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("coupon_id", "user_id", name="idx_unique_coupon_user"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("coupon_user_association")
    op.drop_table("coupons")
    # ### end Alembic commands ###
