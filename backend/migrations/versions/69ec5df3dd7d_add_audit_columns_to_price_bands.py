"""add_audit_columns_to_price_bands

Revision ID: 69ec5df3dd7d
Revises: a1b2c3d4e5f6
Create Date: 2026-03-05 02:14:00.873260

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "69ec5df3dd7d"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "price_bands",
        sa.Column(
            "created_by",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False,
            comment="创建人 ID",
        ),
    )
    op.add_column(
        "price_bands",
        sa.Column(
            "updated_by",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=True,
            comment="更新人 ID",
        ),
    )


def downgrade() -> None:
    op.drop_column("price_bands", "updated_by")
    op.drop_column("price_bands", "created_by")
