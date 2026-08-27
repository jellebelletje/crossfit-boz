#!/usr/bin/env python3
"""Genereert responsive varianten van de foto's in assets/.

Voor iedere bronfoto komen er WebP- en JPEG-versies op 600px en 1200px breed,
plus 1600px voor de hero. De pagina serveert die via <picture> met srcset, zodat
een telefoon niet langer de desktopversie downloadt.

Bronbestanden blijven staan en dienen als JPEG-fallback op volle breedte.
Varianten krijgen het achtervoegsel -600 / -1200 / -1600.

Draaien vanuit de repo-root:  python3 tools/build-images.py
"""
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# Breedtes per gebruik. Meer varianten dan dit levert nauwelijks winst op en
# maakt de map onoverzichtelijk.
WIDTHS = [600, 900, 1200]
HERO_WIDTHS = [600, 900, 1600]

# De ronde portretjes bij de testimonials zijn al 160px; die hoeven niets.
SKIP = {"logo.png", "lid-cihan.jpg", "lid-joyce.jpg", "lid-mike.jpg", "lid-jelmar.jpg"}

# Mappen met werkbestanden, geen sitefoto's.
SKIP_DIRS = {"shortlist", "coaches-website-backup"}

JPEG_Q = 78
WEBP_Q = 72


def variants_for(name: str) -> list[int]:
    return HERO_WIDTHS if name.startswith("hero") else WIDTHS


def is_variant(name: str) -> bool:
    stem = pathlib.Path(name).stem
    return any(stem.endswith(f"-{w}") for w in set(WIDTHS + HERO_WIDTHS + [800]))


def main() -> int:
    if not ASSETS.is_dir():
        print("assets/ niet gevonden", file=sys.stderr)
        return 1

    # Alleen foto's die de pagina echt gebruikt. Anders krijgen werkbestanden als
    # "hero copy.jpg" ook varianten, en die horen nergens.
    import re
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    referenced = {
        pathlib.Path(m).name
        for m in re.findall(r'(?:src|srcset)="([^"]*)"', html)
        for m in re.findall(r'assets/([^\s",]+)', m)
    }

    made = skipped = 0
    for src in sorted(ASSETS.iterdir()):
        if not src.is_file() or src.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        if src.name in SKIP or is_variant(src.name):
            continue
        if any(part in SKIP_DIRS for part in src.parts):
            continue
        if src.name not in referenced:
            continue

        im = Image.open(src).convert("RGB")
        w, h = im.size

        for target in variants_for(src.stem):
            if target >= w:
                # Nooit opschalen: dat kost bytes en levert geen detail op.
                skipped += 1
                continue
            ratio = target / w
            resized = im.resize((target, round(h * ratio)), Image.LANCZOS)

            jpg = ASSETS / f"{src.stem}-{target}.jpg"
            webp = ASSETS / f"{src.stem}-{target}.webp"
            resized.save(jpg, "JPEG", quality=JPEG_Q, optimize=True, progressive=True)
            resized.save(webp, "WEBP", quality=WEBP_Q, method=6)
            made += 2

        # Ook een WebP op volle breedte, als fallback-formaat voor grote schermen.
        full_webp = ASSETS / f"{src.stem}.webp"
        im.save(full_webp, "WEBP", quality=WEBP_Q, method=6)
        made += 1

    print(f"{made} varianten geschreven, {skipped} overgeslagen (bron te klein)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
