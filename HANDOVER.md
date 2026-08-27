# Handover — crossfitbergenopzoom.nl

Last updated 2026-08-27. Read this before touching anything; several traps here
have already caused near-misses.

## What this is

A single-page static site for CrossFit Bergen op Zoom, replacing the WordPress site
that used to live at the same domain. **It is live in production.** Every push to
`main` deploys to the real business website within about a minute.

| | |
|---|---|
| Live | https://crossfitbergenopzoom.nl |
| Repo | https://github.com/jellebelletje/crossfit-boz (public) |
| Host | SiteGround, Apache behind nginx |
| Deploy | GitHub Actions → rsync over SSH, port 18765 |
| GitHub Pages | **Disabled.** Was a preview mirror, retired |

Everything is in `index.html` — markup and an inline `<style>`. There is no build
step for the page itself.

## Read this before you deploy

**Pushing to `main` publishes to a live business site.** There is no staging. The
workflow runs `rsync --delete` against `public_html`.

Four things have already gone wrong here. All four were caught by reading command
output, not by anything failing safely. Assume a fifth exists.

1. **The destination once resolved to `/`.** A discovery step was written but never
   staged, so an unset `SG_PATH` became an empty string and the rsync target was
   `user@host:/`. Guards now refuse any path that is empty, `/`, `$HOME`, or does
   not end in `public_html`.
2. **There are two sites on this SiteGround account.** `~/www/crossfit-bergenopzoom.nl`
   (hyphen) and `~/www/crossfitbergenopzoom.nl` (no hyphen). `ls | head -1` returns
   the hyphenated one, because `-` sorts before letters. The workflow now matches
   `$SITE_DOMAIN` by name and the guard rechecks it.
3. **rsync does not read `.gitignore`.** An early version staged from the working
   directory and would have published 2.2 GB, including `reference-images/` — the
   Powermama and ZilverFitness partner image banks. Staging is now `git archive HEAD`,
   so only committed files ship, with a 30 MB ceiling as a backstop.
4. **A status-code check is not a deploy check.** The first real deploy put every file
   in place correctly while `/` still served the old WordPress homepage from
   SiteGround's Dynamic Cache. The verification now asserts the new content is
   actually in the response.

**Never excluded from `--delete`:** `.well-known/` is Let's Encrypt's renewal path. If
it is deleted, HTTPS keeps working and then silently fails to renew weeks later.

## The pipeline

`.github/workflows/deploy.yml`, on push to `main` plus a manual button.

1. Stage via `git archive HEAD` into `_site/`, copy `redirects/.htaccess` to
   `_site/.htaccess`, drop `redirects/`, `.github/`, `tools/`, `.gitignore`
2. Write the SSH key from secrets, `ssh-keyscan` the host
3. Resolve the document root (see trap 2)
4. `rsync -az --delete`, excluding `.well-known/`, `.htpasswd`, `cgi-bin/`
5. Verify the live site: status, actual content, real 301s, WordPress gone

Secrets: `SG_HOST`, `SG_USER`, `SG_SSH_KEY`. **`SG_PATH` is deliberately unset** —
the workflow resolves it. The key must have **no passphrase**; SiteGround's UI forces
one, so the key was generated locally and its public half imported.

## Open items

**Dynamic Cache is still enabled.** It served a stale WordPress homepage after a
successful deploy once already. Site Tools → Speed → Caching shows only a flush icon,
no toggle. Unresolved question: does `site-tools-client` exist over SSH? If so, wire
an automatic flush into the workflow and the manual step disappears.

```
ssh -p 18765 -i ~/.ssh/siteground_key USER@HOST 'which site-tools-client'
```

**Powermama and ZilverFitness use composites, not photography of this box.** Real
participants from each programme's image bank, backgrounds rebuilt from the CFBoZ
shoot. They carry `SAMENGESTELD BEELD` in their IPTC captions and a
`rechten controleren` keyword. A shoot of those two sessions retires them.

**The roster is hand-maintained.** Transcribed from the Sportbit drop-in planner for a
typical June week. It will drift. Sportbit has no public roster page — that was checked,
the SPA route table has no such route.

**Two testimonial portraits are 160px.** Displayed at 96px, so slightly soft on retina.
The originals were overwritten during processing and are gone.

## Conventions that matter

**Copy is Peter's and goes in verbatim.** Do not tighten, rewrite or "improve" it,
including the one-word FAQ answers and the sentence fragments used for emphasis.
Design serves the text. Every copy change so far has been verified mechanically by
diffing rendered text against source.

**No em dashes anywhere.** Deliberate. Use commas, colons or full stops. En dashes in
the roster time ranges are correct and stay.

**Never assign an age or a programme to anyone from a photograph.** This went wrong
once: frames were captioned "60-plus" and "ZilverFitness" on the strength of grey hair,
and two reached the live page. One labelled the owner as both over sixty and someone
needing the workout adapted. Describe what someone is *doing*. See
`assets/shortlist/INDEX.md`.

**Images.** `tools/build-images.py` generates WebP and JPEG at 600/900/1200 for every
photo the page references. Every `<img>` is a `<picture>` with `srcset`, `sizes`, and
explicit `width`/`height`. A phone loads about 1.2 MB, down from 6.2 MB. Re-run the
script after adding a photo, then add the variants to the `srcset`.

**Redirects.** `redirects/.htaccess` ships as the live `.htaccess`. It carries
compression, cache headers, the 404 `ErrorDocument`, and 301s for all thirteen old
WordPress URLs. Mapping and reasoning in `redirects/map.tsv`.

## Page structure

`#waarom` `#community` `#wie` `#programmas` → eight programme detail sections
(`#crossfit` `#hyrox` `#powermama` `#zilverfitness` `#circuittraining` `#metcon`
`#crossfit-kids` `#private-coaching`) → `#coaching` `#faq` `#verhalen` `#dropin`
`#tarieven` `#private` `#rooster` `#founder` `#start`

Programme cards link to their detail section. Detail sections link out to Sportbit,
except Private Coaching which links to `#private` for the packages.

## Verifying a deploy by hand

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128.0 Safari/537.36"
curl -s -A "$UA" https://crossfitbergenopzoom.nl/ | grep -c wp-content     # expect 0
curl -sI -A "$UA" https://crossfitbergenopzoom.nl/tarieven/ | head -1      # expect 301
curl -s -o /dev/null -w '%{http_code}\n' -A "$UA" https://crossfitbergenopzoom.nl/wp-login.php  # expect 404
```

SiteGround answers datacentre clients with **202** rather than 200. Send a browser
user-agent or you will misread a healthy site as broken.
