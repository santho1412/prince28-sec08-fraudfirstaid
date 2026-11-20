"""add metadata gin index

Revision ID: f2598cbeaee3
Revises: afe23be4c384
Create Date: 2026-11-20

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f2598cbeaee3"
down_revision: str | Sequence[str] | None = "afe23be4c384"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create a GIN index on document metadata."""
    op.create_index(
        "ix_documents_metadata_gin",
        "documents",
        ["metadata"],
        unique=False,
        postgresql_using="gin",
    )


def downgrade() -> None:
    """Remove the metadata GIN index."""
    op.drop_index(
        "ix_documents_metadata_gin",
        table_name="documents",
    )
