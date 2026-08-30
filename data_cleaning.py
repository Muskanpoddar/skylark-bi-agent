import pandas as pd
import numpy as np
import re


# ============================================================
# MISSING VALUE DEFINITIONS
# ============================================================

MISSING_VALUES = {
    "",
    "-",
    "--",
    "na",
    "n/a",
    "nan",
    "none",
    "null",
    "unknown"
}


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(value):

    if pd.isna(value):
        return None

    value = str(value).strip()

    if value.lower() in MISSING_VALUES:
        return None

    return value


# ============================================================
# COLUMN NAME NORMALIZATION
# ============================================================

def normalize_column_name(column):

    column = str(column).strip()

    column = re.sub(
        r"\s+",
        " ",
        column
    )

    return column


def normalize_columns(df):

    df = df.copy()

    df.columns = [
        normalize_column_name(c)
        for c in df.columns
    ]

    return df


# ============================================================
# SECTOR NORMALIZATION
# ============================================================

def normalize_sector(value):

    value = clean_text(value)

    if not value:
        return "Unknown"

    value = value.strip().lower()

    mapping = {

        "energy": "Energy",
        "energy sector": "Energy",

        "mining": "Mining",
        "mining sector": "Mining",

        "defence": "Defence",
        "defense": "Defence",

        "agriculture": "Agriculture",
        "agri": "Agriculture",

        "infrastructure": "Infrastructure",

        "renewable": "Renewables",
        "renewables": "Renewables",

        "railway": "Railways",
        "railways": "Railways",

        "construction": "Construction",

        "powerline": "Powerline",
        "power line": "Powerline",

        "others": "Others",
        "other": "Others"
    }

    return mapping.get(
        value,
        value.title()
    )


# ============================================================
# NUMERIC CLEANING
# ============================================================

def clean_numeric(series):

    def convert(value):

        if pd.isna(value):
            return np.nan

        value = str(value).strip()

        if value.lower() in MISSING_VALUES:
            return np.nan

        # Remove currency symbols, commas and spaces
        value = re.sub(
            r"[₹,$ ]",
            "",
            value
        )

        # Handle parentheses as negative values
        if value.startswith("(") and value.endswith(")"):
            value = "-" + value[1:-1]

        try:
            return float(value)

        except (ValueError, TypeError):
            return np.nan

    return series.apply(convert)


# ============================================================
# DATE CLEANING
# ============================================================

def clean_date(series):

    return pd.to_datetime(
        series,
        errors="coerce"
    )


# ============================================================
# FIND COLUMN
# ============================================================

def find_column(df, possible_names):

    normalized = {
        normalize_column_name(column).lower():
            column
        for column in df.columns
    }

    # Exact matching
    for name in possible_names:

        key = normalize_column_name(
            name
        ).lower()

        if key in normalized:
            return normalized[key]

    # Fuzzy matching
    for column in df.columns:

        column_lower = (
            normalize_column_name(
                column
            ).lower()
        )

        for name in possible_names:

            name_lower = (
                normalize_column_name(
                    name
                ).lower()
            )

            if (
                name_lower in column_lower
                or column_lower in name_lower
            ):
                return column

    return None


# ============================================================
# CLEAN DEALS
# ============================================================

def clean_deals(df):

    df = normalize_columns(df)

    df = df.dropna(
        how="all"
    )

    # --------------------------------------------------------
    # Clean text fields
    # --------------------------------------------------------

    for column in df.columns:

        if df[column].dtype == "object":

            df[column] = df[column].apply(
                clean_text
            )

    # --------------------------------------------------------
    # Sector
    # --------------------------------------------------------

    sector_column = find_column(
        df,
        [
            "Sector/service",
            "Sector Service",
            "Sector",
            "Sector / Service"
        ]
    )

    if sector_column:

        df[sector_column] = df[
            sector_column
        ].apply(
            normalize_sector
        )

        # IMPORTANT:
        # Create a standard internal sector column.
        df["__sector"] = df[
            sector_column
        ]

    else:

        df["__sector"] = "Unknown"

    # --------------------------------------------------------
    # Deal Value
    # --------------------------------------------------------

    value_column = find_column(
        df,
        [
            "Masked Deal value",
            "Masked Deal Value",
            "Deal Value",
            "Deal value"
        ]
    )

    if value_column:

        df[value_column] = clean_numeric(
            df[value_column]
        )

        # Standard internal name
        df["__deal_value"] = df[
            value_column
        ]

    else:

        df["__deal_value"] = np.nan

    # --------------------------------------------------------
    # Dates
    # --------------------------------------------------------

    date_candidates = {

        "__close_date": [
            "Close Date (A)",
            "Close Date"
        ],

        "__tentative_close_date": [
            "Tentative Close Date"
        ],

        "__created_date": [
            "Created Date"
        ]
    }

    for internal_name, candidates in date_candidates.items():

        column = find_column(
            df,
            candidates
        )

        if column:

            df[internal_name] = clean_date(
                df[column]
            )

        else:

            df[internal_name] = pd.NaT

    # --------------------------------------------------------
    # Deal Status
    # --------------------------------------------------------

    status_column = find_column(
        df,
        [
            "Deal Status",
            "Status"
        ]
    )

    if status_column:

        df["__deal_status"] = (
            df[status_column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    else:

        df["__deal_status"] = ""

    # --------------------------------------------------------
    # Deal Stage
    # --------------------------------------------------------

    stage_column = find_column(
        df,
        [
            "Deal Stage",
            "Stage"
        ]
    )

    if stage_column:

        df["__deal_stage"] = (
            df[stage_column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    else:

        df["__deal_stage"] = ""

    return df


# ============================================================
# CLEAN WORK ORDERS
# ============================================================

def clean_work_orders(df):

    df = normalize_columns(df)

    df = df.dropna(
        how="all"
    )

    # --------------------------------------------------------
    # Clean text fields
    # --------------------------------------------------------

    for column in df.columns:

        if df[column].dtype == "object":

            df[column] = df[column].apply(
                clean_text
            )

    # --------------------------------------------------------
    # Sector
    # --------------------------------------------------------

    sector_column = find_column(
        df,
        [
            "Sector"
        ]
    )

    if sector_column:

        df[sector_column] = df[
            sector_column
        ].apply(
            normalize_sector
        )

        df["__sector"] = df[
            sector_column
        ]

    else:

        df["__sector"] = "Unknown"

    # --------------------------------------------------------
    # Execution Status
    # --------------------------------------------------------

    execution_column = find_column(
        df,
        [
            "Execution Status"
        ]
    )

    if execution_column:

        df["__execution_status"] = (
            df[execution_column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    else:

        df["__execution_status"] = ""

    # --------------------------------------------------------
    # Billing
    # --------------------------------------------------------

    billed_column = find_column(
        df,
        [
            "Billed Value in Rupees (Incl. of GST.) (Masked)",
            "Billed Value in Rupees",
            "Billed Value"
        ]
    )

    collected_column = find_column(
        df,
        [
            "Collected Amount in Rupees (Incl. GST.) (Masked)",
            "Collected Amount",
            "Collected Value"
        ]
    )

    receivable_column = find_column(
        df,
        [
            "Amount Receivable (Masked)",
            "Amount Receivable",
            "Receivable"
        ]
    )

    if billed_column:

        df["__billed"] = clean_numeric(
            df[billed_column]
        )

    else:

        df["__billed"] = np.nan

    if collected_column:

        df["__collected"] = clean_numeric(
            df[collected_column]
        )

    else:

        df["__collected"] = np.nan

    if receivable_column:

        df["__receivable"] = clean_numeric(
            df[receivable_column]
        )

    else:

        df["__receivable"] = np.nan

    # --------------------------------------------------------
    # WO Status
    # --------------------------------------------------------

    wo_status_column = find_column(
        df,
        [
            "WO Status (billed)",
            "WO Status",
            "WO status"
        ]
    )

    if wo_status_column:

        df["__wo_status"] = (
            df[wo_status_column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    else:

        df["__wo_status"] = ""

    # --------------------------------------------------------
    # Billing Status
    # --------------------------------------------------------

    billing_status_column = find_column(
        df,
        [
            "Billing Status"
        ]
    )

    if billing_status_column:

        df[billing_status_column] = (
            df[billing_status_column]
            .astype("string")
            .str.strip()
            .replace(
                {
                    "BIlled": "Billed",
                    "billed": "Billed",
                    "BILLED": "Billed"
                }
            )
        )

    return df


# ============================================================
# MONDAY ITEMS → DATAFRAME
# ============================================================

def monday_items_to_dataframe(board):

    return pd.DataFrame(
        board["items"]
    )