import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import SkinCatalog, db, app


DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "cs2_skins_seed.json"


def main() -> None:
    seed_file = DEFAULT_PATH
    with seed_file.open("r", encoding="utf-8") as f:
        items = json.load(f)

    allowed_rarities = {"Covert", "Extraordinary"}
    normalized = []
    for item in items:
        rarity = (item.get("rarity") or "").strip()
        if rarity not in allowed_rarities:
            continue
        normalized.append(
            {
                "game": "cs2",
                "weapon": item["weapon"].strip(),
                "skin_name": item["skin_name"].strip(),
                "rarity": rarity,
            }
        )

    inserted = 0
    updated = 0
    deleted = 0

    desired_keys = {(i["game"], i["weapon"], i["skin_name"]) for i in normalized}

    with app.app_context():
        existing_rows = SkinCatalog.query.all()
        for row in existing_rows:
            key = (row.game, row.weapon, row.skin_name)
            if key not in desired_keys:
                db.session.delete(row)
                deleted += 1

        for item in normalized:
            existing = SkinCatalog.query.filter_by(
                game=item["game"], weapon=item["weapon"], skin_name=item["skin_name"]
            ).first()
            if existing:
                existing.rarity = item["rarity"]
                existing.collection = None
                existing.image_url = None
                updated += 1
                continue

            db.session.add(
                SkinCatalog(
                    game=item["game"],
                    weapon=item["weapon"],
                    skin_name=item["skin_name"],
                    rarity=item["rarity"],
                    collection=None,
                    image_url=None,
                )
            )
            inserted += 1

        db.session.commit()

    print(
        f"Seed complete: inserted={inserted}, updated={updated}, deleted={deleted}, total_input={len(normalized)}"
    )


if __name__ == "__main__":
    main()
