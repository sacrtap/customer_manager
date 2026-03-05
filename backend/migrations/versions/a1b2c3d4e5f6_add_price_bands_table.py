"""add_price_bands_table

Revision ID: a1b2c3d4e5f6
Revises: 6e4f7e050a5a
Create Date: 2026-03-05 02:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "6e4f7e050a5a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "price_bands",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False, comment="区间名称"),
        sa.Column("code", sa.String(length=50), nullable=False, comment="区间代码"),
        sa.Column("description", sa.Text(), nullable=True, comment="描述"),
        sa.Column(
            "price_config_id",
            sa.BigInteger(),
            sa.ForeignKey("price_configs.id", ondelete="CASCADE"),
            nullable=True,
            comment="关联的价格配置 ID",
        ),
        sa.Column(
            "min_quantity",
            sa.Numeric(precision=12, scale=2),
            nullable=True,
            comment="最小数量（包含）",
        ),
        sa.Column(
            "max_quantity",
            sa.Numeric(precision=12, scale=2),
            nullable=True,
            comment="最大数量（包含）",
        ),
        sa.Column(
            "min_amount",
            sa.Numeric(precision=12, scale=2),
            nullable=True,
            comment="最小金额（包含）",
        ),
        sa.Column(
            "max_amount",
            sa.Numeric(precision=12, scale=2),
            nullable=True,
            comment="最大金额（包含）",
        ),
        sa.Column(
            "unit_price",
            sa.Numeric(precision=12, scale=2),
            nullable=True,
            comment="单价",
        ),
        sa.Column(
            "discount_rate",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
            comment="折扣率（百分比）",
        ),
        sa.Column(
            "final_price",
            sa.Numeric(precision=12, scale=2),
            nullable=True,
            comment="最终价格",
        ),
        sa.Column(
            "priority",
            sa.BigInteger(),
            nullable=False,
            default=0,
            comment="优先级（数字越大优先级越高）",
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, default=True, comment="是否启用"
        ),
        sa.Column("valid_from", sa.DateTime(), nullable=True, comment="生效日期"),
        sa.Column("valid_until", sa.DateTime(), nullable=True, comment="失效日期"),
        sa.Column("metadata_json", sa.JSON(), nullable=True, comment="元数据"),
        sa.Column("created_at", sa.DateTime(), nullable=False, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(), nullable=True, comment="更新时间"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_price_band_code"),
        sa.UniqueConstraint("price_config_id", "code", name="uq_price_config_band"),
    )
    op.create_index(op.f("ix_price_bands_code"), "price_bands", ["code"], unique=True)
    op.create_index(op.f("ix_price_bands_name"), "price_bands", ["name"], unique=False)
    op.create_index(
        op.f("ix_price_bands_is_active"), "price_bands", ["is_active"], unique=False
    )
    op.create_index(
        op.f("ix_price_bands_priority"), "price_bands", ["priority"], unique=False
    )
    op.create_index(
        "idx_price_config_bands",
        "price_bands",
        ["price_config_id", "priority"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_price_config_bands", table_name="price_bands")
    op.drop_index(op.f("ix_price_bands_priority"), table_name="price_bands")
    op.drop_index(op.f("ix_price_bands_is_active"), table_name="price_bands")
    op.drop_index(op.f("ix_price_bands_name"), table_name="price_bands")
    op.drop_index(op.f("ix_price_bands_code"), table_name="price_bands")
    op.drop_table("price_bands")
