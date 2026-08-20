# Artificial Analysis Wayback speed extraction — notes

Source: Wayback Machine snapshots of `artificialanalysis.ai/models` (one per month,
2024-01 through 2026-01). Output: `aa_wayback_speeds.json` with structure
`{"<YYYYMMDD>": {"<model name>": <median output tokens/sec>, ...}, ...}`.

## Coverage

**All 25 months recovered (25/25). 420 distinct model names total.**

| Snapshot | Models | Notes |
|---|---|---|
| 20240120 | 21 | avg (not median) — see caveats |
| 20240219 | 21 | |
| 20240319 | 27 | |
| 20240406 | 28 | |
| 20240516 | 37 | |
| 20240628 | 38 | |
| 20240718 | 50 | |
| 20240816 | 58 | |
| 20240901 | 60 | |
| 20241005 | 65 | |
| 20241105 | 76 | |
| 20241208 | 83 | |
| 20250105 | 82 | |
| 20250204 | 90 | |
| 20250303 | 90 | (one 0.0-speed entry dropped) |
| 20250414 | 121 | |
| 20250505 | 135 | |
| 20250602 | 151 | |
| 20250701 | 157 | |
| 20250802 | 162 | |
| 20250902 | 160 | |
| 20251002 | 203 | |
| 20251103 | 221 | |
| 20251204 | 233 | |
| 20260101 | 245 | |

Download hiccups: 20250902/20251002/20251103/20260101 failed on the first curl pass
(connection errors from web.archive.org); all succeeded on retry (20260101 needed
https + `--retry 3`).

## Extraction method (same pipeline for every month)

Contrary to the initial assumption, **every era 2024-01 through 2026-01 uses Next.js
app-router flight payloads** (`self.__next_f.push([1,"..."])` script chunks) — there
is no `__NEXT_DATA__` era among these snapshots. Pipeline (see `extract.py`):

1. Regex-extract all pushed string chunks, `json.loads` each, concatenate into one blob.
2. Build a UUID -> model-name map from objects `{"id":"<uuid>","name":...}`. In late-2025
   snapshots (2025-10 onward) model-object keys are alphabetized so `"id"` is not the
   first key; a fallback finds `"id":"<uuid>"` and parses the enclosing JSON object.
3. Collect measurement objects and take the speed field, by era:
   - **2024-01 only:** objects `{"model_id":..., "avg_throughput_tokens_per_second":N}`
     (no median field existed yet).
   - **2024-02 → 2025-03:** `median_throughput_tokens_per_second` from objects keyed by
     `model_id`, **excluding** objects containing `interval_start_date` (those are the
     over-time chart's historical daily/weekly points, not the snapshot-date value).
   - **2025-04 → 2026-01:** `median_output_speed` from objects
     `{"prompt_length_type":"medium", "model_id":..., "median_output_speed":N}` —
     "medium" is the site's headline benchmark (verified: in 2025-03, which carries
     both forms, the no-prompt-type value equals the `medium` value exactly for all
     90 models).
4. Where a model appears twice in a page (two chart sections in 2024 snapshots), the
   duplicated values are bit-identical (max diff 0.0); the median of duplicates is taken.
5. Values <= 0 are dropped (one 0.0 entry in 2025-03).

## Validation (spot checks vs known ballparks)

- GPT-4o: 75.2 (2024-05), 86.8 (2024-07), 105.6 (2024-09) — in 60-110 range. OK
- Claude 3 Sonnet 61.4 (2024-05); Claude 3.5 Sonnet (Oct '24) 56.3 (2024-11) — in 50-80. OK
- GPT-5 (high) 128.3, (medium) 188.4 (2025-09) — slightly above the 50-120 hint but
  consistent with AA's published late-2025 GPT-5 speeds. OK
- Gemini 2.5 Flash: 253.9 (2025-08), 277.8 Reasoning (2026-01) — in 200-400. OK
- High outliers (500-960 tok/s, from 2024-09 onward) are Cerebras/Groq/SambaNova-served
  open models and Gemini Flash-Lite — genuine, not extraction errors.

## Caveats

- **2024-01-20 values are `avg_throughput_tokens_per_second`, not median** — the median
  field did not exist yet in that page's data model. Avg vs median differ by roughly
  5-15% for these distributions; treat that month accordingly.
- Values are the site-wide headline number per model (median across the hosts/providers
  AA benchmarked at the time), for the standard ("medium", ~1k-token) prompt length.
  Reasoning-model speeds are output-phase tokens/sec as AA measures them.
- Model naming drifts across months (e.g. "Claude 3.5 Sonnet" later becomes
  "Claude 3.5 Sonnet (June '24)"; late 2025 adds "(Reasoning)"/"(Non-reasoning)" and
  effort suffixes like "(high)"). Names are kept exactly as shown per snapshot; any
  longitudinal join needs its own name normalization.
- Snapshot pages render a few models in the visible chart but the flight payload
  carries the full benchmarked model list — counts here reflect the payload, which is
  broader than what a screenshot of the page would show.
