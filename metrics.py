import pandas as pd


# ============================================================
# SAFE HELPERS
# ============================================================

def safe_sum(series):

    if series is None:
        return 0.0

    return float(
        pd.to_numeric(
            series,
            errors="coerce"
        ).fillna(0).sum()
    )


def get_column(df, column, default=None):
    """
    Safely get a column.
    Returns a default Series if the column doesn't exist.
    """

    if column in df.columns:
        return df[column]

    return pd.Series(
        [default] * len(df),
        index=df.index
    )


# ============================================================
# DEAL METRICS
# ============================================================

def deal_metrics(deals):

    result = {}

    result["total_deals"] = len(deals)

    # --------------------------------------------------------
    # Deal Status
    # --------------------------------------------------------

    status = (
        get_column(
            deals,
            "__deal_status",
            ""
        )
        .fillna("")
        .astype(str)
        .str.lower()
        .str.strip()
    )

    result["open_deals"] = int(
        status.eq("open").sum()
    )

    result["won_deals"] = int(
        status.isin(
            [
                "won",
                "closed won",
                "closed"
            ]
        ).sum()
    )

    result["lost_deals"] = int(
        status.isin(
            [
                "lost",
                "closed lost"
            ]
        ).sum()
    )

    # --------------------------------------------------------
    # Deal Values
    # --------------------------------------------------------

    deal_value = get_column(
        deals,
        "__deal_value",
        None
    )

    deal_value_numeric = pd.to_numeric(
        deal_value,
        errors="coerce"
    )

    open_mask = status.eq("open")

    result["open_pipeline"] = safe_sum(
        deal_value_numeric[open_mask]
    )

    result["total_deal_value"] = safe_sum(
        deal_value_numeric
    )

    # ========================================================
    # PIPELINE BY SECTOR
    # ========================================================

    sector = (
        get_column(
            deals,
            "__sector",
            "Unknown"
        )
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    sector = sector.replace(
        "",
        "Unknown"
    )

    pipeline_data = pd.DataFrame(
        {
            "sector": sector,
            "value": deal_value_numeric.fillna(0)
        }
    )

    # Only OPEN deals contribute to pipeline
    pipeline_data = pipeline_data[
        open_mask
    ]

    sector_pipeline = (
        pipeline_data
        .groupby("sector")["value"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    result["pipeline_by_sector"] = {
        str(k): float(v)
        for k, v in sector_pipeline.items()
    }

    # ========================================================
    # PIPELINE BY STAGE
    # ========================================================

    stage = (
        get_column(
            deals,
            "__deal_stage",
            "Unknown"
        )
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace(
            "",
            "Unknown"
        )
    )

    stage_data = pd.DataFrame(
        {
            "stage": stage,
            "value": deal_value_numeric.fillna(0)
        }
    )

    stage_data = stage_data[
        open_mask
    ]

    stage_pipeline = (
        stage_data
        .groupby("stage")["value"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    result["pipeline_by_stage"] = {
        str(k): float(v)
        for k, v in stage_pipeline.items()
    }

    # ========================================================
    # AVERAGE DEAL SIZE
    # ========================================================

    valid_values = deal_value_numeric.dropna()

    if len(valid_values) > 0:

        result["average_deal_size"] = float(
            valid_values.mean()
        )

    else:

        result["average_deal_size"] = 0.0

    # ========================================================
    # DATA QUALITY
    # ========================================================

    result["missing_deal_values"] = int(
        deal_value_numeric.isna().sum()
    )

    close_date = get_column(
        deals,
        "__tentative_close_date",
        pd.NaT
    )

    result["missing_close_dates"] = int(
        close_date.isna().sum()
    )

    result["missing_sectors"] = int(
        sector.eq("Unknown").sum()
    )

    return result


# ============================================================
# WORK ORDER METRICS
# ============================================================

def work_order_metrics(work_orders):

    result = {}

    result["total_work_orders"] = len(
        work_orders
    )

    # ========================================================
    # EXECUTION STATUS
    # ========================================================

    execution = (
        get_column(
            work_orders,
            "__execution_status",
            ""
        )
        .fillna("")
        .astype(str)
        .str.lower()
        .str.strip()
    )

    result["completed_orders"] = int(
        execution.str.contains(
            "complete",
            na=False
        ).sum()
    )

    result["ongoing_orders"] = int(
        execution.str.contains(
            "ongoing|progress|active",
            regex=True,
            na=False
        ).sum()
    )

    result["not_started_orders"] = int(
        execution.str.contains(
            "not started|yet to start|pending",
            regex=True,
            na=False
        ).sum()
    )

    # ========================================================
    # FINANCIALS
    # ========================================================

    billed = get_column(
        work_orders,
        "__billed",
        None
    )

    collected = get_column(
        work_orders,
        "__collected",
        None
    )

    receivable = get_column(
        work_orders,
        "__receivable",
        None
    )

    billed_numeric = pd.to_numeric(
        billed,
        errors="coerce"
    )

    collected_numeric = pd.to_numeric(
        collected,
        errors="coerce"
    )

    receivable_numeric = pd.to_numeric(
        receivable,
        errors="coerce"
    )

    result["total_billed"] = safe_sum(
        billed_numeric
    )

    result["total_collected"] = safe_sum(
        collected_numeric
    )

    result["total_receivable"] = safe_sum(
        receivable_numeric
    )

    # ========================================================
    # COLLECTION RATE
    # ========================================================

    if result["total_billed"] > 0:

        result["collection_rate"] = (
            result["total_collected"]
            / result["total_billed"]
        ) * 100

    else:

        result["collection_rate"] = 0.0

    # ========================================================
    # SECTOR PERFORMANCE
    # ========================================================

    sector = (
        get_column(
            work_orders,
            "__sector",
            "Unknown"
        )
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace(
            "",
            "Unknown"
        )
    )

    sector_data = pd.DataFrame(
        {
            "sector": sector,
            "billed": billed_numeric.fillna(0)
        }
    )

    sector_revenue = (
        sector_data
        .groupby("sector")["billed"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    result["billed_by_sector"] = {
        str(k): float(v)
        for k, v in sector_revenue.items()
    }

    # ========================================================
    # DATA QUALITY
    # ========================================================

    result["missing_collection_values"] = int(
        collected_numeric.isna().sum()
    )

    wo_status = get_column(
        work_orders,
        "__wo_status",
        ""
    )

    result["missing_wo_status"] = int(
        wo_status
        .fillna("")
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )

    result["missing_execution_status"] = int(
        execution.eq("").sum()
    )

    result["missing_sectors"] = int(
        sector.eq("Unknown").sum()
    )

    return result


# ============================================================
# CROSS BOARD ANALYSIS
# ============================================================

def cross_board_analysis(
    deals,
    work_orders
):

    deal_data = deal_metrics(
        deals
    )

    work_data = work_order_metrics(
        work_orders
    )

    pipeline_by_sector = deal_data[
        "pipeline_by_sector"
    ]

    billed_by_sector = work_data[
        "billed_by_sector"
    ]

    # Get every sector appearing on either board
    sectors = set(
        pipeline_by_sector.keys()
    ).union(
        billed_by_sector.keys()
    )

    comparison = {}

    for sector in sorted(sectors):

        pipeline = float(
            pipeline_by_sector.get(
                sector,
                0
            )
        )

        billed = float(
            billed_by_sector.get(
                sector,
                0
            )
        )

        # ----------------------------------------------------
        # Execution ratio
        #
        # This compares billed execution against
        # the sales pipeline for the sector.
        # ----------------------------------------------------

        if pipeline > 0:

            execution_ratio = (
                billed / pipeline
            ) * 100

        else:

            execution_ratio = None

        # ----------------------------------------------------
        # Identify strong sales / weak execution
        #
        # A sector qualifies when:
        # - It has meaningful open pipeline
        # - Billed execution is below 50% of pipeline
        #
        # This is a heuristic, not a business fact.
        # ----------------------------------------------------

        strong_sales_weak_execution = (
            pipeline > 0
            and (
                execution_ratio is not None
                and execution_ratio < 50
            )
        )

        comparison[sector] = {

            "pipeline": pipeline,

            "billed": billed,

            "execution_ratio": (
                round(
                    execution_ratio,
                    1
                )
                if execution_ratio is not None
                else None
            ),

            "strong_sales_weak_execution":
                strong_sales_weak_execution
        }

    # ========================================================
    # EXPLICIT LIST FOR AI / LEADERSHIP ANALYSIS
    # ========================================================

    weak_execution_sectors = []

    for sector, data in comparison.items():

        if data[
            "strong_sales_weak_execution"
        ]:

            weak_execution_sectors.append(
                {
                    "sector": sector,
                    "pipeline": data["pipeline"],
                    "billed": data["billed"],
                    "execution_ratio": data[
                        "execution_ratio"
                    ]
                }
            )

    # Highest pipeline first
    weak_execution_sectors.sort(
        key=lambda x: x["pipeline"],
        reverse=True
    )

    return {
        "sector_comparison": comparison,

        "strong_sales_weak_execution": (
            weak_execution_sectors
        )
    }