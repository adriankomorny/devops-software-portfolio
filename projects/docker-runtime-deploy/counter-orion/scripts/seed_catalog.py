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

    inserted = 0
    updated = 0

    with app.app_context():
        for item in items:
            game = (item.get("game") or "cs2").strip().lower()
            weapon = item["weapon"].strip()
            skin_name = item["skin_name"].strip()
            rarity = item["rarity"].strip()
            collection = (item.get("collection") or "").strip() or None
            image_url = (item.get("image_url") or "").strip() or None

            existing = SkinCatalog.query.filter_by(game=game, weapon=weapon, skin_name=skin_name).first()
            if existing:
                existing.rarity = rarity
                existing.collection = collection
                existing.image_url = image_url
                updated += 1
                continue

            db.session.add(
                SkinCatalog(
                    game=game,
                    weapon=weapon,
                    skin_name=skin_name,
                    rarity=rarity,
                    collection=collection,
                    image_url=image_url,
                )
            )
            inserted += 1

        db.session.commit()

    print(f"Seed complete: inserted={inserted}, updated={updated}, total_input={len(items)}")


if __name__ == "__main__":
    main()
