#!/usr/bin/env python3
"""Genereert HTML-stubs voor GitHub Pages.

GitHub Pages kan geen echte 301 sturen: er is geen serverconfiguratie. Deze stubs
zijn het dichtstbijzijnde alternatief - een 200 met een meta-refresh en een
canonical. Zoekmachines behandelen dat meestal als een redirect, maar het IS er
geen. Draait de site achter nginx, Apache, Netlify of Cloudflare, gebruik dan de
configs hiernaast; die geven een echte 301.

Draaien vanuit de repo-root:  python3 redirects/gen-github-pages-stubs.py
"""
import os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
rows = [l.rstrip("\n").split("\t") for l in open(ROOT/"redirects/map.tsv", encoding="utf-8") if l.strip()]

TPL = """<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<title>Verplaatst naar de homepage</title>
<link rel="canonical" href="https://crossfitbergenopzoom.nl{target}">
<meta name="robots" content="noindex, follow">
<meta http-equiv="refresh" content="0; url=https://crossfitbergenopzoom.nl{target}">
<script>location.replace("https://crossfitbergenopzoom.nl{target}");</script>
</head>
<body style="background:#0A0A0A;color:#FAFAFA;font-family:system-ui,sans-serif;padding:3rem">
<p>Deze pagina staat nu op de homepage.
<a href="https://crossfitbergenopzoom.nl{target}" style="color:#F5D300">Ga verder →</a></p>
</body>
</html>
"""

made = []
for old, new, *_ in rows:
    if old.rstrip("/") in ("", "/feed", "/comments/feed"):
        continue
    d = ROOT / old.strip("/")
    d.mkdir(parents=True, exist_ok=True)
    (d/"index.html").write_text(TPL.format(target=new), encoding="utf-8")
    made.append(str(d.relative_to(ROOT)) + "/index.html")

print(f"{len(made)} stubs geschreven:")
for m in made:
    print("  ", m)
