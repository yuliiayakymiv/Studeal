# Seed data

`make seed` loads these files into the database (on AWS every backend deploy does it). They hold the real Lviv student deals and events. To change them, edit the CSV (or a spreadsheet exported as CSV with the same header row).

| File | Columns |
|---|---|
| `deals.csv` | `venue, title, category, discount, address, valid_until, source_url, image_url, description, university` |
| `events.csv` | `title, venue, starts_at, address, price, source_url, image_url, university, category` |

- `category`: one word in English, e.g. `coffee`, `food`, `coworking`, `sport` for deals; `quiz`, `lecture`, `concert`, `workshop` for events.
- `image_url`: a direct link to a photo (ends in `.jpg`/`.png`/`.webp`), or empty — the site shows a placeholder. Use the venue's own photos (with their OK) or your own; Instagram links stop working after a while, so upload the photo somewhere stable instead.
- `description`: conditions in a sentence ("weekdays 10:00–16:00, show your student ID") or empty.
- `university`: `ucu` for places and events of UCU (canteen, café, gym, UCU events); empty = for all students.
- `image_url`, `description`, `university` (and `category` in `events.csv`) are optional columns: you can leave them out of the file.
- `valid_until`: `2026-12-31` or empty. `starts_at`: `2026-11-20 19:00` (Kyiv time).
- Re-running `make seed` updates existing rows (same `venue + title` / `title + starts_at`) instead of duplicating them.
