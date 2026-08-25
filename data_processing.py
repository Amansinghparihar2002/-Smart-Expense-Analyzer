# data_processing.py
# Handles all data cleaning, transformation, and filtering tasks

import pandas as pd


def clean_data(df):
    """
    Cleans the raw CSV data.
    Steps:
    - Lowercase all column names
    - Rename 'exp type' to 'category'
    - Convert date to datetime, amount to numeric
    - Drop rows with missing key values
    """
    # Step 1: Lowercase column names and strip whitespace
    df = df.copy()
    df.columns = df.columns.str.lower().str.strip()

    # Step 2: Rename 'exp type' to 'category' if present
    if "exp type" in df.columns:
        df = df.rename(columns={"exp type": "category"})

    # Step 3: Validate required columns
    required_columns = {"date", "category", "amount"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Step 4: Parse date column (handles formats like '29-Oct-14')
    df["date"] = pd.to_datetime(
    df["date"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

    # Step 5: Parse amount column (strip commas if any)
    df["amount"] = pd.to_numeric(
        df["amount"].astype(str).str.replace(",", ""), errors="coerce"
    )

    # Step 6: Drop rows with nulls in key columns
    df = df.dropna(subset=["date", "category", "amount"])

    # Step 7: Clean up category strings
    df["category"] = df["category"].str.strip().str.title()

    return df


def add_time_features(df):
    """
    Adds time-based columns derived from the date column.
    - month      : integer month (1–12)
    - year       : 4-digit year
    - month_year : string like '2014-10' for sorting
    - month_label: string like 'Oct 2014' for display
    """
    df = df.copy()

    df["month"]       = df["date"].dt.month
    df["year"]        = df["date"].dt.year
    df["month_year"]  = df["date"].dt.to_period("M").astype(str)
    df["month_label"] = df["date"].dt.strftime("%b %Y")

    return df


def apply_filters(df, selected_categories, date_range):
    """
    Filters the dataframe based on sidebar selections.

    Parameters:
    - df                : cleaned dataframe with time features
    - selected_categories: list of category strings to keep
    - date_range        : tuple of (start_date, end_date) as date objects

    Returns the filtered dataframe.
    """
    filtered = df.copy()

    # Filter by selected categories (if not all selected)
    if selected_categories:
        filtered = filtered[filtered["category"].isin(selected_categories)]

    # Filter by date range
    start_date, end_date = date_range
    filtered = filtered[
        (filtered["date"].dt.date >= start_date) &
        (filtered["date"].dt.date <= end_date)
    ]

    return filtered
