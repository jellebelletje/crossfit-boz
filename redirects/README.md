# Redirects van de oude site naar de nieuwe one-pager

De oude WordPress-site had dertien losse pagina's. De nieuwe site is één pagina,
dus alles moet naar een anker op de homepage.

## Belangrijk: GitHub Pages kan geen 301 sturen

Er is geen serverconfiguratie op GitHub Pages, dus een echte permanente redirect
is daar niet mogelijk. De stubs die `gen-github-pages-stubs.py` genereert zijn een
200 met `meta refresh` plus een `canonical`. Zoekmachines behandelen dat meestal
als een redirect, maar het **is** er geen: linkwaarde gaat deels verloren en de
oude URL blijft technisch bestaan.

Voor echte 301's is een van deze nodig:

| Host | Bestand |
|---|---|
| nginx (wat het domein nu draait) | `nginx.conf` |
| Apache | `.htaccess` |
| Netlify / Cloudflare Pages | `_redirects` |
| Cloudflare vóór GitHub Pages | Bulk Redirects, gevoed met `map.tsv` |

De laatste optie is waarschijnlijk het handigst als de site op GitHub Pages blijft:
het domein loopt dan via Cloudflare en die stuurt de 301 vóórdat het verzoek Pages
bereikt.

## De mapping

Zie `map.tsv` (oud pad, nieuw doel, reden). Een paar keuzes die uitleg verdienen:

- **`/binnenkort-beschikbaar/` → `/#rooster`** — in de oude navigatie heette dit
  item "Rooster" en het wees naar een lege placeholder. De nieuwe pagina heeft een
  echt rooster, dus die link klopt nu eindelijk.
- **`/is-crossfit-iets-voor-mij/` → `/#faq`** — de kop van de nieuwe FAQ is
  letterlijk dezelfde vraag.
- **`/fitness/` en `/trainers/` → `/#circuittraining` en `/#founder`** — dit waren
  onafgemaakte templatepagina's, nog gevuld met lorem ipsum en een verzonnen
  trainer ("Maria Morales"). Ze staan wel in de sitemap en zijn dus indexeerbaar.
  Redirecten is hier het minimum; ze horen ook uit de oude index verwijderd te
  worden.
- **`/lessen/90-days-challenge/` → `/#tarieven`** — dat aanbod bestaat niet meer.

## Fragmenten

Een `#anchor` wordt door de browser bewaard, niet door de server verstuurd. De
regels hierboven zetten het fragment expliciet in de `Location`-header, dus dat
werkt. Let bij nginx op `NE` / geen extra encoding, anders wordt `#` als `%23`
doorgegeven en landt de bezoeker bovenaan de pagina.

## Na het omzetten controleren

```bash
for p in /wat-is-crossfit/ /lessen/ /tarieven/ /contact/; do
  curl -sI "https://crossfitbergenopzoom.nl$p" | head -2
done
```

Verwacht `HTTP/1.1 301` met een `location:` die het anker bevat.
