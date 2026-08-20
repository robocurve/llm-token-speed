# llm-token-speed

One-chart repo: LLM output speed (tok/s) vs release date with per-intelligence-
level Pareto frontiers. Public-facing figure for robocurve.org.

## Layout

- `src/make_speed_chart.py` — the only script; run from the **repo root**
  (`uv run src/make_speed_chart.py`), paths are root-relative. Deps are inline
  (PEP 723: matplotlib, numpy).
- `data/` — AA API snapshot + Wayback-backfilled historical speeds (see README).
- `plots/` — rendered PNG (180 dpi) + SVG.
- `fonts/` — Space Grotesk (vendored from robocurve/towel-cover; OFL).

## Conventions & gotchas

- Visual grammar follows towel-cover's `make_latency_chart.py`: ink `#161A1D`,
  muted `#6B767D`, hairline bottom spine only, no tick marks, Space Grotesk,
  footer starts with `robocurve.org`.
- Tier accent colors (`#A34E30`, `#B8860B`, `#0679A9` + neutral gray) passed
  colorblind/contrast validation as an all-pairs scatter palette — don't swap
  casually.
- Label positions (`tip_offsets`, `start_offsets`, `rate_pos`) are hand-placed
  per current data; re-check for collisions after any data refresh.
- Never annualize a frontier spanning < 300 days (the `span` gate in the rate
  code) — a 9-week tier annualizes to ×8,762/yr nonsense. Short spans render
  per-month.
- Fonts are loaded from `fonts/` at run time; matplotlib lacks Space Grotesk
  weight 600, warns, and falls back to 500 — harmless (`grep -v findfont`).
- AA's public API only carries speed for currently-served models. Deprecated
  models come from `data/aa_backfilled.json` (Wayback extraction, method in
  `data/aa_wayback_notes.md`). A future refresh should extend the backfill
  rather than re-scrape from scratch.
