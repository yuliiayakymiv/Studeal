# Seed data

`make seed` loads these files into the database. **The rows here are placeholders** — replace them with the real deals and events (export the team's Google Sheet: File → Download → CSV, keep the header row).

| File | Columns |
|---|---|
| `deals.csv` | `venue, title, category, discount, address, valid_until, source_url, image_url` |
| `events.csv` | `title, venue, starts_at, address, price, source_url` |

- `category`: one word in English, e.g. `coffee`, `food`, `coworking`, `sport`, `cinema`, `culture`.
- `image_url`: a direct link to a photo (ends in `.jpg`/`.png`/`.webp`), or empty — the site shows a placeholder. Use the venue's own photos (with their OK) or your own; Instagram links stop working after a while, so upload the photo somewhere stable instead.
- `valid_until`: `2026-12-31` or empty. `starts_at`: `2026-11-20 19:00` (Kyiv time).
- Re-running `make seed` updates existing rows (same `venue + title` / `title + starts_at`) instead of duplicating them.
