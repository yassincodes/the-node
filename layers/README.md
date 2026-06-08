# Layers

Truth for **people on the site** — not in git where labs scrape open source.

## How it works

1. Edit `learn.json` and `history.json` here (gitignored — yours locally).
2. Pack for deploy:
   ```bash
   python tools/pack_layers.py >> .env
   ```
3. Paste the `THENODE_LAYERS=...` line into Vercel → Environment Variables.

Visitors to `/learn.html` and `/history.html` get the full text automatically — children, parents, anyone. No gate. No login.

Scrapers that only read GitHub or static HTML get nothing. The human portal header is how the browser asks.

## Shape

See `schema.json`.
