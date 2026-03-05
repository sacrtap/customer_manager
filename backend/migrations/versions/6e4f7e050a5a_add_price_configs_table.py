"""add_price_configs_table

Revision ID: 6e4f7e050a5a
Revises: 470022cd851a
Create Date: 2026-03-05 02:11:03.940097

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6e4f7e050a5a"
down_revision: Union[str, None] = "470022cd851a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "price_configs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False, comment="代码"),
        sa.Column("name", sa.String(length=200), nullable=False, comment="名称"),
        sa.Column("description", sa.Text(), nullable=True, comment="描述"),
        sa.Column(
            "base_price", sa.Float(), nullable=False, default=0.0, comment="基准价格"
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            default="active",
            comment="状态 (active/disabled)",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            default=sa.func.now(),
            nullable=False,
            comment="创建时间",
        ),
        sa.Column(
            "created_by",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False,
            comment="创建人 ID",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            onupdate=sa.func.now(),
            nullable=True,
            comment="更新时间",
        ),
        sa.Column(
            "updated_by",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=True,
            comment="更新人 ID",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_price_config_code", "price_configs", ["code"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_price_config_code", table_name="price_configs")
    op.drop_table("price_configs")
