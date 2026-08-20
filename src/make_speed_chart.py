# /// script
# dependencies = ["matplotlib", "numpy"]
# ///
"""Output speed (median tok/s) vs release date, colored by AA Intelligence
Index tier, in the towel-cover visual grammar (Space Grotesk, hairline
bottom spine, direct labels, muted ink).

Data: Artificial Analysis API v2 snapshot (aa_api_models.json).
Caveat drawn on-chart: deprecated models carry no live speed medians, so
pre-2026 frontier models are absent and high tiers only span 2026.
"""

import json
from datetime import date
from pathlib import Path

import matplotlib
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np

INK = "#161A1D"
MUTED = "#6B767D"
HAIRLINE = "#D8DEE2"
GRIDLINE = "#EDF1F3"
NEUTRAL = "#9AA6AC"

TIERS = [  # (label, lo, hi, color, is_accent)
    ("GPT-3.5 Turbo", 0, 20, NEUTRAL, False),
    ("o1", 20, 35, "#A34E30", True),
    ("GPT-5", 35, 50, "#B8860B", True),
    ("Fable 5", 50, 999, "#0679A9", True),
]

for f in Path("fonts").glob("*.ttf"):
    fm.fontManager.addfont(str(f))
matplotlib.rcParams["font.family"] = "Space Grotesk"
matplotlib.rcParams["svg.fonttype"] = "none"

models = json.load(open("data/aa_api_models.json"))["data"]
rows = []
for m in models:
    ii = (m.get("evaluations") or {}).get("artificial_analysis_intelligence_index")
    spd = m.get("median_output_tokens_per_second")
    rd = m.get("release_date")
    if ii is None or not spd or not rd:
        continue
    rows.append({"name": m["name"], "date": date.fromisoformat(rd), "ii": ii,
                 "spd": spd, "backfilled": False})
for r in json.load(open("data/aa_backfilled.json")):
    rows.append({"name": r["name"], "date": date.fromisoformat(r["date"]),
                 "ii": r["ii"], "spd": r["spd"], "backfilled": True})

fig, ax = plt.subplots(figsize=(12.8, 7.4))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
ax.set_yscale("log")

legend_labels = {}
frontier_names = set()
for label, lo, hi, color, accent in TIERS:
    pts = sorted((r for r in rows if lo <= r["ii"] < hi),
                 key=lambda r: (r["date"], -r["spd"]))
    legend_labels[label] = label
    if not pts:
        continue
    # Pareto frontier over time: faster than every earlier release in tier
    frontier, best = [], 0.0
    for r in pts:
        if r["spd"] > best:
            frontier.append(r)
            best = r["spd"]
            frontier_names.add(r["name"])
    rest = [r for r in pts if r["name"] not in frontier_names]

    if rest:
        ax.plot(mdates.date2num([r["date"] for r in rest]),
                [r["spd"] for r in rest], "o", ms=3.8, mfc=color, mec="none",
                alpha=0.18 if not accent else 0.28, zorder=2, linestyle="none")
    fx = mdates.date2num([r["date"] for r in frontier])
    fy = np.array([r["spd"] for r in frontier])
    # running-max step line tracing the frontier to today
    sx = np.append(fx, mdates.date2num(date(2026, 8, 20)))
    ax.step(sx, np.append(fy, fy[-1]), where="post", color=color, lw=2.0,
            alpha=0.55 if not accent else 0.8, zorder=3, solid_capstyle="butt")
    ax.plot(fx, fy, "o", ms=8.2 if accent else 6.6, mfc=color, mec="white",
            mew=1.2, zorder=4, linestyle="none")
    # averaged frontier growth: endpoint ratio annualized over the curve's span,
    # annotated directly on the curve
    span = fx[-1] - fx[0]
    if span >= 300:
        rate_text = f"×{(fy[-1] / fy[0]) ** (365.25 / span):.1f}/yr"
    else:
        rate_text = f"×{(fy[-1] / fy[0]) ** (30.4375 / span):.1f}/mo"
    rate_pos = {"GPT-3.5 Turbo": (date(2025, 2, 1), 640, "center"),
                "o1": (date(2025, 9, 15), 330, "center"),
                "GPT-5": (date(2026, 2, 10), 163, "center"),
                "Fable 5": (date(2026, 7, 6), 120, "right")}
    rx, ry, rha = rate_pos[label]
    ax.annotate(rate_text, (mdates.date2num(rx), ry), fontsize=19,
                fontweight="bold", color=color, ha=rha, va="bottom", zorder=5)
    # name the first frontier model visible on the canvas (x-axis starts 2024)
    start_offsets = {"GPT-3.5 Turbo": (14, -24, "left"), "o1": (0, -24, "center"),
                     "GPT-5": (0, -24, "center"), "Fable 5": (-13, -6, "right")}
    first = next((r for r in frontier if r["date"] >= date(2024, 1, 1)), None)
    if first is not None:
        dx, dy, ha = start_offsets[label]
        ax.annotate(first["name"].split(" (")[0],
                    (mdates.date2num(first["date"]), first["spd"]),
                    xytext=(dx, dy), textcoords="offset points", fontweight=500,
                    fontsize=14, color=color, alpha=0.8, ha=ha, zorder=5)
    # name the tier's most recent frontier model
    tip_offsets = {"GPT-3.5 Turbo": (0, 13, "center"), "o1": (0, 13, "center"),
                   "GPT-5": (58, 12, "right"), "Fable 5": (7, -20, "left")}
    dx, dy, ha = tip_offsets[label]
    tip = frontier[-1]
    ax.annotate(tip["name"].split(" (")[0], (fx[-1], fy[-1]),
                xytext=(dx, dy), textcoords="offset points", fontweight=500,
                fontsize=14, color=color, alpha=0.8, ha=ha, zorder=5)

ax.set_ylim(12, 3000)
ax.set_xlim(mdates.date2num(date(2024, 1, 1)), mdates.date2num(date(2026, 10, 15)))
ax.minorticks_off()
ax.set_yticks([20, 50, 100, 200, 500, 1000, 2000])
ax.set_yticklabels(["20", "50", "100", "200", "500", "1,000", "2,000"],
                   fontsize=16, color=MUTED)
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 7)))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
ax.tick_params(axis="x", labelsize=16, colors=MUTED, length=0)
ax.tick_params(axis="y", length=0)
ax.grid(axis="y", color=GRIDLINE, lw=0.6)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(HAIRLINE)
ax.spines["bottom"].set_linewidth(0.75)

ax.set_title("LLM token speed increases by 2–7× per year",
             fontsize=27, fontweight=600, color=INK, loc="left", pad=40)
ax.text(0, 1.045, "Median output speed (tokens/s, log scale) by release date",
        transform=ax.transAxes, fontsize=16, color=MUTED)

# legend outside plot, top right
handles = [plt.Line2D([], [], marker="o", linestyle="none", ms=7,
                      mfc=c, mec="white" if acc else "none",
                      label=legend_labels[lab])
           for lab, _, _, c, acc in TIERS]
ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.005, 0.98),
          frameon=False, fontsize=15, labelcolor='linecolor', handletextpad=0.3,
          title="Intelligence level", title_fontsize=15, alignment="left")

ax.text(0.0, -0.12, "robocurve.org · Data: Artificial Analysis · intelligence levels binned by AA Intelligence Index, named for the model that opened each band",
        transform=ax.transAxes, fontsize=12.5, color=MUTED, ha="left")

fig.tight_layout(pad=0.6)
for ext in ("png", "svg"):
    fig.savefig(f"plots/speed_vs_release.{ext}", dpi=180, bbox_inches="tight",
                pad_inches=0.25, facecolor="white")
print("wrote speed_vs_release.png / .svg,", len(rows), "models")
