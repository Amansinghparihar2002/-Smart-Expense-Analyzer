# charts.py
# All visualizations for Smart Expense Analyzer — upgraded with better colors,
# labels, readability, and two additional chart types.

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np

# ── Global theme ────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "font.family":    "DejaVu Sans",
    "axes.spines.top":    False,
    "axes.spines.right":  False,
})

# Consistent brand palette (colorblind-friendly)
PALETTE = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52",
    "#8172B2", "#937860", "#DA8BC3", "#8C8C8C",
]


# ── 1. Horizontal Bar Chart ─────────────────────────────────────────────────
def plot_category_bar(df):
    """
    Horizontal bar chart: total spend per category, sorted descending.
    Value labels shown inside/outside bars.
    """
    cat_spend = (
        df.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=True)   # ascending → largest at top of chart
    )

    n      = len(cat_spend)
    colors = PALETTE[:n] if n <= len(PALETTE) else sns.color_palette("tab10", n)

    fig, ax = plt.subplots(figsize=(9, max(4, n * 0.7)))

    bars = ax.barh(
        cat_spend.index,
        cat_spend.values,
        color=colors,
        edgecolor="white",
        linewidth=0.8,
        height=0.6,
    )

    # Value labels
    max_val = cat_spend.max()
    for bar, val in zip(bars, cat_spend.values):
        label_x = val + max_val * 0.01
        ax.text(
            label_x, bar.get_y() + bar.get_height() / 2,
            f"₹{val:,.0f}",
            va="center", ha="left", fontsize=9, color="#333333",
        )

    ax.set_xlabel("Total Spend (₹)", fontsize=11, labelpad=8)
    ax.set_title("Spending by Category", fontsize=14, fontweight="bold", pad=14)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M" if x >= 1e6 else f"₹{x:,.0f}"))
    ax.set_xlim(0, max_val * 1.22)
    ax.tick_params(axis="y", labelsize=10)

    plt.tight_layout()
    return fig


# ── 2. Donut Chart (upgraded from plain pie) ────────────────────────────────
def plot_category_pie(df):
    """
    Donut chart with % labels and a central summary label.
    """
    cat_spend = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    n         = len(cat_spend)
    colors    = PALETTE[:n] if n <= len(PALETTE) else sns.color_palette("tab10", n)
    total     = cat_spend.sum()

    fig, ax = plt.subplots(figsize=(7, 7))

    wedges, texts, autotexts = ax.pie(
        cat_spend.values,
        labels=None,                         # we draw a legend instead
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        wedgeprops={"edgecolor": "white", "linewidth": 2, "width": 0.55},
        pctdistance=0.78,
    )

    for at in autotexts:
        at.set_fontsize(9)
        at.set_fontweight("bold")
        at.set_color("white")

    # Centre text
    ax.text(0, 0.08, "Total", ha="center", va="center", fontsize=11, color="#555")
    ax.text(0, -0.15, f"₹{total/1e6:.1f}M" if total >= 1e6 else f"₹{total:,.0f}",
            ha="center", va="center", fontsize=13, fontweight="bold", color="#222")

    # Legend
    legend_patches = [
        mpatches.Patch(color=colors[i], label=f"{cat}  ({cat_spend[cat]/total*100:.1f}%)")
        for i, cat in enumerate(cat_spend.index)
    ]
    ax.legend(
        handles=legend_patches, loc="lower center",
        bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=9, frameon=False,
    )

    ax.set_title("Spending Distribution", fontsize=14, fontweight="bold", pad=14)
    plt.tight_layout()
    return fig


# ── 3. Monthly Trend Line Chart ─────────────────────────────────────────────
def plot_monthly_trend(df):
    """
    Line chart with gradient fill, peak/low annotations, and dual-color zones.
    """
    monthly = (
        df.groupby("month_year")["amount"]
        .sum()
        .reset_index()
        .sort_values("month_year")
    )

    x_idx  = range(len(monthly))
    values = monthly["amount"].values
    labels = monthly["month_year"].values

    fig, ax = plt.subplots(figsize=(11, 5))

    # Area fill
    ax.fill_between(x_idx, values, alpha=0.12, color=PALETTE[0])

    # Line
    ax.plot(x_idx, values, marker="o", linewidth=2.2,
            markersize=6, color=PALETTE[0], zorder=3)

    # Highlight peak and trough
    peak_i  = int(np.argmax(values))
    trough_i = int(np.argmin(values))

    ax.plot(peak_i,   values[peak_i],   "o", color="#e74c3c", markersize=10, zorder=4)
    ax.plot(trough_i, values[trough_i], "o", color="#2ecc71", markersize=10, zorder=4)

    ax.annotate(
        f"Peak\n₹{values[peak_i]:,.0f}",
        xy=(peak_i, values[peak_i]),
        xytext=(peak_i, values[peak_i] * 1.07),
        ha="center", fontsize=8, color="#e74c3c", fontweight="bold",
    )
    ax.annotate(
        f"Low\n₹{values[trough_i]:,.0f}",
        xy=(trough_i, values[trough_i]),
        xytext=(trough_i, values[trough_i] * 0.88),
        ha="center", fontsize=8, color="#2ecc71", fontweight="bold",
    )

    # Average line
    avg = values.mean()
    ax.axhline(avg, linestyle="--", linewidth=1.2, color="#888", alpha=0.7)
    ax.text(len(x_idx) - 0.5, avg * 1.02, f"Avg ₹{avg:,.0f}",
            ha="right", fontsize=8, color="#666")

    # Axes formatting
    ax.set_xticks(list(x_idx))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"₹{v/1e6:.1f}M" if v >= 1e6 else f"₹{v:,.0f}")
    )
    ax.set_title("Monthly Spending Trend", fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel("Month", fontsize=11, labelpad=8)
    ax.set_ylabel("Total Spend (₹)", fontsize=11, labelpad=8)

    plt.tight_layout()
    return fig


# ── 4. NEW — Category Spend vs Budget Guideline (Grouped Bar) ───────────────
def plot_budget_comparison(df):
    """
    Compares actual % spend per category against the recommended guideline %.
    Bars over the guideline are shown in red.
    """
    from insights import IDEAL_LIMITS, DEFAULT_LIMIT

    cat_pct = (
        df.groupby("category")["amount"].sum() /
        df["amount"].sum() * 100
    ).round(1)

    categories = list(cat_pct.index)
    actual     = [cat_pct[c] for c in categories]
    guideline  = [IDEAL_LIMITS.get(c.lower(), DEFAULT_LIMIT) for c in categories]

    x     = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))

    bar_colors = ["#e74c3c" if a > g else "#4C72B0" for a, g in zip(actual, guideline)]

    ax.bar(x - width / 2, actual,    width, label="Actual %",    color=bar_colors,  alpha=0.85, edgecolor="white")
    ax.bar(x + width / 2, guideline, width, label="Guideline %", color="#b0b0b0",   alpha=0.7,  edgecolor="white")

    # Labels on top of bars
    for xi, (a, g) in enumerate(zip(actual, guideline)):
        ax.text(xi - width / 2, a + 0.5, f"{a}%", ha="center", fontsize=8, fontweight="bold")
        ax.text(xi + width / 2, g + 0.5, f"{g}%", ha="center", fontsize=8, color="#555")

    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=20, ha="right", fontsize=10)
    ax.set_ylabel("% of Total Spend", fontsize=11)
    ax.set_title("Actual Spending vs Recommended Guideline", fontsize=14, fontweight="bold", pad=14)
    ax.legend(fontsize=10, frameon=False)

    # Red-bar note
    from matplotlib.patches import Patch
    note = Patch(color="#e74c3c", alpha=0.8, label="Over guideline")
    ok   = Patch(color="#4C72B0", alpha=0.8, label="Within guideline")
    ax.legend(handles=[ok, note, mpatches.Patch(color="#b0b0b0", alpha=0.7, label="Guideline")],
              fontsize=9, frameon=False)

    plt.tight_layout()
    return fig


# ── 5. NEW — Top 10 Transactions Table-style Bar ─────────────────────────────
def plot_top_transactions(df, n=10):
    """
    Horizontal bar of the top-N highest individual transactions.
    """
    top = df.nlargest(n, "amount")[["date", "category", "amount"]].copy()
    top["label"] = top["category"] + " — " + top["date"].dt.strftime("%d %b %Y")

    fig, ax = plt.subplots(figsize=(9, max(4, n * 0.65)))

    colors = [PALETTE[i % len(PALETTE)] for i in range(len(top))]
    ax.barh(top["label"][::-1], top["amount"][::-1], color=colors[::-1],
            edgecolor="white", linewidth=0.8, height=0.6)

    max_val = top["amount"].max()
    for i, (val, lbl) in enumerate(zip(top["amount"][::-1], top["label"][::-1])):
        ax.text(val + max_val * 0.01, i, f"₹{val:,.0f}", va="center", fontsize=9)

    ax.set_xlabel("Amount (₹)", fontsize=11, labelpad=8)
    ax.set_title(f"Top {n} Transactions", fontsize=14, fontweight="bold", pad=14)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    ax.set_xlim(0, max_val * 1.22)
    ax.tick_params(axis="y", labelsize=9)

    plt.tight_layout()
    return fig
