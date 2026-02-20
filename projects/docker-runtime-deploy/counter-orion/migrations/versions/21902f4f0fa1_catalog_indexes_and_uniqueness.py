"""catalog indexes and uniqueness

Revision ID: 21902f4f0fa1
Revises: 07e6fa35699e
Create Date: 2026-02-20 16:33:00

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "21902f4f0fa1"
down_revision = "07e6fa35699e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_skins_catalog_weapon", "skins_catalog", ["weapon"], unique=False)
    op.create_index("ix_skins_catalog_rarity", "skins_catalog", ["rarity"], unique=False)
    op.create_index("ix_skins_catalog_skin_name", "skins_catalog", ["skin_name"], unique=False)
    op.create_unique_constraint(
        "uq_skins_catalog_game_weapon_skin",
        "skins_catalog",
        ["game", "weapon", "skin_name"],
    )


def downgrade():
    op.drop_constraint("uq_skins_catalog_game_weapon_skin", "skins_catalog", type_="unique")
    op.drop_index("ix_skins_catalog_skin_name", table_name="skins_catalog")
    op.drop_index("ix_skins_catalog_rarity", table_name="skins_catalog")
    op.drop_index("ix_skins_catalog_weapon", table_name="skins_catalog")
