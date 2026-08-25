# insights.py
# Smart financial insights — percentage-based, savings tips,
# warnings, health score, category summary, and monthly summary

import pandas as pd


# ---------------------------------------------------------------------------
# BENCHMARK: Application-defined spending guidelines
# These are NOT universal financial rules.
# They are used by this application to identify unusually high spending.
# ---------------------------------------------------------------------------
IDEAL_LIMITS = {
    "food": 30,
    "entertainment": 10,
    "travel": 15,
    "bills": 35,
    "fuel": 10,
    "grocery": 20,
}

# Categories not listed above use this guideline
DEFAULT_LIMIT = 40


# ---------------------------------------------------------------------------
# HELPER: Get category percentages
# ---------------------------------------------------------------------------
def _category_percentages(df):
    """
    Returns a Series:
        category -> percentage of total spending
    """

    cat_totals = df.groupby("category")["amount"].sum()
    total = cat_totals.sum()

    if total == 0:
        return pd.Series(dtype=float)

    return (cat_totals / total * 100).round(1)


# ---------------------------------------------------------------------------
# CATEGORY SUMMARY
# ---------------------------------------------------------------------------
def get_category_summary(df):
    """
    Returns detailed category-level spending information.

    Each record contains:
    - category
    - total spending
    - transaction count
    - average transaction
    - percentage of total spending
    """

    if df.empty:
        return []

    category_summary = (
        df.groupby("category")["amount"]
        .agg(["sum", "count", "mean"])
        .reset_index()
    )

    # Rename columns to clearer names
    category_summary = category_summary.rename(
        columns={
            "sum": "total_spend",
            "count": "transactions",
            "mean": "avg_transaction",
        }
    )

    total_spend = category_summary["total_spend"].sum()

    if total_spend > 0:
        category_summary["percentage"] = (
            category_summary["total_spend"] / total_spend * 100
        ).round(1)
    else:
        category_summary["percentage"] = 0

    # Highest spending categories first
    category_summary = category_summary.sort_values(
        "total_spend",
        ascending=False
    )

    return category_summary.to_dict("records")


# ---------------------------------------------------------------------------
# MONTHLY SUMMARY
# ---------------------------------------------------------------------------
def get_monthly_summary(df):
    """
    Returns monthly spending information.

    Requires the 'month_year' column created by add_time_features().
    """

    if df.empty or "month_year" not in df.columns:
        return []

    monthly_summary = (
        df.groupby("month_year")["amount"]
        .agg(["sum", "count", "mean"])
        .reset_index()
    )

    monthly_summary = monthly_summary.rename(
        columns={
            "sum": "total_spend",
            "count": "transactions",
            "mean": "avg_transaction",
        }
    )

    monthly_summary = monthly_summary.sort_values("month_year")

    return monthly_summary.to_dict("records")


# ---------------------------------------------------------------------------
# MAIN INSIGHT GENERATOR
# ---------------------------------------------------------------------------
def generate_insights(df):
    """
    Returns a list of insight dictionaries.

    Each dictionary contains:
    - type   : info | warning | success | tip
    - message: human-readable insight
    """

    insights = []

    if df.empty:
        insights.append({
            "type": "warning",
            "message": "No data available for insights."
        })
        return insights

    total_spend = df["amount"].sum()
    total_txns = len(df)
    avg_amount = df["amount"].mean()

    cat_pct = _category_percentages(df)

    # -----------------------------------------------------------------------
    # 1. SUMMARY STATISTICS
    # -----------------------------------------------------------------------

    insights.append({
        "type": "info",
        "message": (
            f"💸 Total spending across {total_txns:,} transactions: "
            f"₹{total_spend:,.0f}"
        )
    })

    insights.append({
        "type": "info",
        "message": (
            f"📊 Average transaction value: "
            f"₹{avg_amount:,.0f}"
        )
    })

    # -----------------------------------------------------------------------
    # 2. CATEGORY BREAKDOWN
    # -----------------------------------------------------------------------

    if not cat_pct.empty:

        top_cat = cat_pct.idxmax()
        top_pct = cat_pct.max()

        low_cat = cat_pct.idxmin()
        low_pct = cat_pct.min()

        insights.append({
            "type": "info",
            "message": (
                f"🏆 You spend the most on **{top_cat}** — "
                f"that's {top_pct}% of your total spending."
            )
        })

        insights.append({
            "type": "info",
            "message": (
                f"📉 Lowest spending category: **{low_cat}** "
                f"at {low_pct}% of total spending."
            )
        })

    # -----------------------------------------------------------------------
    # 3. OVERSPENDING WARNINGS
    # -----------------------------------------------------------------------

    for cat, pct in cat_pct.items():

        limit = IDEAL_LIMITS.get(
            cat.lower(),
            DEFAULT_LIMIT
        )

        if pct > limit:

            excess = round(pct - limit, 1)

            insights.append({
                "type": "warning",
                "message": (
                    f"⚠️ Overspending Alert: **{cat}** represents "
                    f"{pct}% of your spending. "
                    f"This is {excess} percentage points above "
                    f"the application's {limit}% guideline."
                )
            })

    # -----------------------------------------------------------------------
    # 4. SAVINGS SUGGESTIONS
    # -----------------------------------------------------------------------

    category_totals = df.groupby("category")["amount"].sum()

    for cat, pct in cat_pct.items():

        limit = IDEAL_LIMITS.get(
            cat.lower(),
            DEFAULT_LIMIT
        )

        if pct > limit:

            cat_total = category_totals[cat]

            ideal_amount = total_spend * (limit / 100)

            potential = max(
                0,
                cat_total - ideal_amount
            )

            insights.append({
                "type": "tip",
                "message": (
                    f"💡 Savings Tip: Reducing **{cat}** toward "
                    f"the application's {limit}% guideline could "
                    f"potentially reduce spending by approximately "
                    f"₹{potential:,.0f}."
                )
            })

    # -----------------------------------------------------------------------
    # 5. SPENDING BALANCE
    # -----------------------------------------------------------------------

    if not cat_pct.empty:

        spread = cat_pct.max() - cat_pct.min()

        if spread > 50:

            insights.append({
                "type": "warning",
                "message": (
                    f"⚖️ Unbalanced Spending Detected: "
                    f"The gap between your highest and lowest "
                    f"category is {spread:.1f} percentage points."
                )
            })

        else:

            insights.append({
                "type": "success",
                "message": (
                    "✅ Balanced Spending: Your expenses are "
                    "relatively well-distributed across categories."
                )
            })

    # -----------------------------------------------------------------------
    # 6. MONTHLY TREND
    # -----------------------------------------------------------------------

    if (
        "month_year" in df.columns
        and df["month_year"].nunique() > 1
    ):

        monthly = (
            df.groupby("month_year")["amount"]
            .sum()
            .sort_index()
        )

        best_month = monthly.idxmin()
        worst_month = monthly.idxmax()

        insights.append({
            "type": "success",
            "message": (
                f"📅 Your lowest-spend month was **{best_month}** "
                f"(₹{monthly.min():,.0f})."
            )
        })

        insights.append({
            "type": "warning",
            "message": (
                f"📈 Highest-spend month: **{worst_month}** "
                f"(₹{monthly.max():,.0f}). "
                f"Review what drove spending up that month."
            )
        })

    return insights


# ---------------------------------------------------------------------------
# FINANCIAL HEALTH SCORE
# ---------------------------------------------------------------------------
def compute_health_score(df):
    """
    Computes a Financial Health Score from 0–100.

    Scoring:
    - Start at 100
    - Deduct for categories exceeding application guidelines
    - Deduct for spending imbalance
    - Bonus for 5+ spending categories

    Returns:
        score
        label
        color
        reasons
    """

    if df.empty:

        return (
            0,
            "No Data",
            "#888888",
            []
        )

    score = 100
    reasons = []

    cat_pct = _category_percentages(df)

    # -----------------------------------------------------------------------
    # Deduct for overspending
    # -----------------------------------------------------------------------

    for cat, pct in cat_pct.items():

        limit = IDEAL_LIMITS.get(
            cat.lower(),
            DEFAULT_LIMIT
        )

        if pct > limit:

            excess = pct - limit

            penalty = min(
                int(excess * 0.8),
                20
            )

            score -= penalty

            reasons.append(
                f"−{penalty} pts: {cat} exceeds "
                f"application guideline by {excess:.1f}%"
            )

    # -----------------------------------------------------------------------
    # Deduct for imbalance
    # -----------------------------------------------------------------------

    if not cat_pct.empty:

        spread = cat_pct.max() - cat_pct.min()

        if spread > 60:

            score -= 10

            reasons.append(
                "−10 pts: Very unbalanced category distribution"
            )

        elif spread > 40:

            score -= 5

            reasons.append(
                "−5 pts: Moderately unbalanced spending"
            )

    # -----------------------------------------------------------------------
    # Bonus for diverse categories
    # -----------------------------------------------------------------------

    n_cats = len(cat_pct)

    if n_cats >= 5:

        score += 5

        reasons.append(
            "+5 pts: Spending spread across 5+ categories"
        )

    # -----------------------------------------------------------------------
    # Clamp score
    # -----------------------------------------------------------------------

    score = max(
        0,
        min(100, score)
    )

    # -----------------------------------------------------------------------
    # Label
    # -----------------------------------------------------------------------

    if score >= 80:

        label = "Excellent"
        color = "#2ecc71"

    elif score >= 60:

        label = "Good"
        color = "#27ae60"

    elif score >= 40:

        label = "Average"
        color = "#f39c12"

    else:

        label = "Poor"
        color = "#e74c3c"

    return (
        score,
        label,
        color,
        reasons
    )