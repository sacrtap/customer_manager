"""add_pricing_strategies_table

Revision ID: 470022cd851a
Revises: 58f2922f9dc1
Create Date: 2026-03-05 01:37:34.088424

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "470022cd851a"
down_revision: Union[str, None] = "58f2922f9dc1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pricing_strategies",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("applicable_customer_type", sa.String(length=50), nullable=True),
        sa.Column("applicable_tier_levels", sa.String(length=50), nullable=True),
        sa.Column(
            "discount_type", sa.String(length=20), nullable=False, default="percentage"
        ),
        sa.Column(
            "discount_value",
            sa.Numeric(precision=10, scale=4),
            nullable=False,
            default=0,
        ),
        sa.Column("priority", sa.BigInteger(), nullable=False, default=0),
        sa.Column("status", sa.String(length=20), nullable=False, default="active"),
        sa.Column("valid_from", sa.DateTime(), nullable=True),
        sa.Column("valid_to", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pricing_strategies_code"), "pricing_strategies", ["code"], unique=True
    )
    op.create_index(
        op.f("ix_pricing_strategies_name"), "pricing_strategies", ["name"], unique=False
    )
    op.create_index(
        op.f("ix_pricing_strategies_status"),
        "pricing_strategies",
        ["status"],
        unique=False,
    )
    op.create_index(
        "idx_status_priority",
        "pricing_strategies",
        ["status", "priority"],
        unique=False,
    )
    op.create_index(
        "idx_validity", "pricing_strategies", ["valid_from", "valid_to"], unique=False
    )


def downgrade() -> None:
    op.drop_index("idx_validity", table_name="pricing_strategies")
    op.drop_index("idx_status_priority", table_name="pricing_strategies")
    op.drop_index(op.f("ix_pricing_strategies_status"), table_name="pricing_strategies")
    op.drop_index(op.f("ix_pricing_strategies_name"), table_name="pricing_strategies")
    op.drop_index(op.f("ix_pricing_strategies_code"), table_name="pricing_strategies")
    op.drop_table("pricing_strategies")
