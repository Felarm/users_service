"""create user table

Revision ID: e8b16f96b3f7
Revises: 
Create Date: 2026-05-07 15:35:13.549347

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from config import settings

# revision identifiers, used by Alembic.
revision: str = 'e8b16f96b3f7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


async def create_db():
    admin_url = settings.db_url[:-len(settings.DB_NAME)] + "postgres"
    db_creation_engine = sa.ext.asyncio.create_async_engine(url=admin_url, isolation_level="AUTOCOMMIT")
    async with db_creation_engine.begin() as conn:
        try:
            await conn.execute(sa.text(f"CREATE DATABASE {settings.DB_NAME}"))
        except sa.exc.ProgrammingError:
            pass
    await db_creation_engine.dispose()


def upgrade() -> None:
    """Upgrade schema."""
    # await create_db()
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, autoincrement=True),
        sa.Column("username", sa.String(255), unique=True, nullable=False),
        sa.Column("tg_id", sa.Integer, unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(1024), nullable=False),
        sa.Column("first_name", sa.String(255), nullable=True),
        sa.Column("last_name", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP, server_default=sa.text("now()"), nullable=False),
        sa.Column("is_admin", sa.Boolean, server_default="false", default=False),
        sa.Column("is_active", sa.Boolean, server_default="true", default=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tg_id"),
        sa.UniqueConstraint("username"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
