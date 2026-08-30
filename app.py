import os
import json
import streamlit as st

from monday_client import MondayClient
from data_cleaning import (
    monday_items_to_dataframe,
    clean_deals,
    clean_work_orders
)
from metrics import (
    deal_metrics,
    work_order_metrics,
    cross_board_analysis
)
from ai_agent import BIAgent


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Skylark BI Agent",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# CONFIGURATION
# ============================================================

try:
    MONDAY_API_TOKEN = st.secrets.get(
        "MONDAY_API_TOKEN",
        os.getenv("MONDAY_API_TOKEN")
    )

    OPENAI_API_KEY = st.secrets.get(
        "OPENAI_API_KEY",
        os.getenv("OPENAI_API_KEY")
    )

except Exception:
    MONDAY_API_TOKEN = os.getenv(
        "MONDAY_API_TOKEN"
    )

    OPENAI_API_KEY = os.getenv(
        "OPENAI_API_KEY"
    )


# ============================================================
# HEADER
# ============================================================

st.title(
    "📊 Skylark Business Intelligence Agent"
)

st.caption(
    "Founder-level insights powered by live Monday.com data"
)


# ============================================================
# CONFIGURATION CHECK
# ============================================================

if not MONDAY_API_TOKEN:

    st.error(
        "❌ Monday.com API token is not configured."
    )

    st.info(
        "Check your .streamlit/secrets.toml file."
    )

    st.stop()


if not OPENAI_API_KEY:

    st.error(
        "❌ OpenAI API key is not configured."
    )

    st.info(
        "Check your .streamlit/secrets.toml file."
    )

    st.stop()


# ============================================================
# LOAD DATA FROM MONDAY.COM
# ============================================================

@st.cache_data(ttl=60)
def load_data():

    client = MondayClient(
        MONDAY_API_TOKEN
    )

    # Get Deals
    deals_board = client.get_deals()

    # Get Work Orders
    work_orders_board = client.get_work_orders()

    # Convert Monday response to DataFrames
    deals = monday_items_to_dataframe(
        deals_board
    )

    work_orders = monday_items_to_dataframe(
        work_orders_board
    )

    # Clean / normalize data
    deals = clean_deals(
        deals
    )

    work_orders = clean_work_orders(
        work_orders
    )

    return deals, work_orders


# ============================================================
# RETRIEVE DATA
# ============================================================

try:

    deals, work_orders = load_data()

except Exception as e:

    st.error(
        "❌ Unable to retrieve or process data from Monday.com."
    )

    st.code(
        str(e)
    )

    st.warning(
        "If this error is related to a column name, "
        "check the Monday board column mapping."
    )

    st.stop()


# ============================================================
# CALCULATE BUSINESS METRICS
# ============================================================

try:

    deal_summary = deal_metrics(
        deals
    )

    work_order_summary = work_order_metrics(
        work_orders
    )

    cross_board = cross_board_analysis(
        deals,
        work_orders
    )

except Exception as e:

    st.error(
        "❌ Unable to calculate business metrics."
    )

    st.code(
        str(e)
    )

    st.stop()


# ============================================================
# BUSINESS SNAPSHOT
# ============================================================

st.subheader(
    "Business Snapshot"
)

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Open Pipeline",
        f"₹{deal_summary['open_pipeline']:,.0f}"
    )


with col2:

    st.metric(
        "Open Deals",
        deal_summary["open_deals"]
    )


with col3:

    st.metric(
        "Work Orders",
        work_order_summary[
            "total_work_orders"
        ]
    )


with col4:

    st.metric(
        "Total Collected",
        f"₹{work_order_summary['total_collected']:,.0f}"
    )


# ============================================================
# ADDITIONAL BUSINESS INFORMATION
# ============================================================

st.divider()

st.subheader(
    "Business Performance"
)

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Won Deals",
        deal_summary["won_deals"]
    )


with col2:

    st.metric(
        "Lost Deals",
        deal_summary["lost_deals"]
    )


with col3:

    st.metric(
        "Completed Work Orders",
        work_order_summary[
            "completed_orders"
        ]
    )


with col4:

    st.metric(
        "Collection Rate",
        f"{work_order_summary['collection_rate']:.1f}%"
    )


# ============================================================
# PIPELINE BY SECTOR
# ============================================================

st.divider()

st.subheader(
    "Pipeline by Sector"
)

pipeline_by_sector = (
    deal_summary[
        "pipeline_by_sector"
    ]
)

if pipeline_by_sector:

    for sector, value in pipeline_by_sector.items():

        st.write(
            f"**{sector}** — ₹{value:,.0f}"
        )

else:

    st.info(
        "No sector pipeline data is available."
    )


# ============================================================
# ASK THE AI AGENT
# ============================================================

st.divider()

st.subheader(
    "💬 Ask the Business Intelligence Agent"
)

st.caption(
    "Ask questions about pipeline, revenue, sectors, "
    "work orders, collections, or business performance."
)


question = st.chat_input(
    "Ask a founder-level business question..."
)


# ============================================================
# AI CONTEXT
# ============================================================

context = {

    "deals": deal_summary,

    "work_orders": work_order_summary,

    "cross_board_sector_comparison": (
        cross_board
    ),

    "data_quality": {

        "deals_missing_values":
            deal_summary[
                "missing_deal_values"
            ],

        "deals_missing_close_dates":
            deal_summary.get(
                "missing_close_dates",
                0
            ),

        "deals_missing_sectors":
            deal_summary.get(
                "missing_sectors",
                0
            ),

        "work_orders_missing_collection":
            work_order_summary[
                "missing_collection_values"
            ],

        "work_orders_missing_status":
            work_order_summary[
                "missing_wo_status"
            ],

        "work_orders_missing_execution_status":
            work_order_summary.get(
                "missing_execution_status",
                0
            )
    }
}


# ============================================================
# ANSWER USER QUESTION
# ============================================================

if question:

    with st.chat_message("user"):

        st.write(
            question
        )

    with st.chat_message("assistant"):

        with st.spinner(
            "🔎 Analyzing live Monday.com data..."
        ):

            try:

                agent = BIAgent(
                    OPENAI_API_KEY
                )

                answer = agent.answer(
                    question,
                    json.dumps(
                        context,
                        indent=2,
                        default=str
                    )
                )

                st.markdown(
                    answer
                )

            except Exception as e:

                st.error(
                    "❌ The AI agent encountered an error."
                )

                st.code(
                    str(e)
                )


# ============================================================
# LEADERSHIP UPDATE
# ============================================================

st.divider()

st.subheader(
    "📋 Leadership Update"
)

st.write(
    "Generate a concise executive-level summary "
    "from the current Monday.com data."
)


if st.button(
    "Generate Leadership Update"
):

    with st.spinner(
        "Preparing executive summary..."
    ):

        try:

            agent = BIAgent(
                OPENAI_API_KEY
            )

            leadership_question = """
Prepare a concise leadership update based only
on the provided business metrics.

Structure the answer as:

## Executive Summary

Give the most important overall business takeaway.

## Pipeline

Discuss open pipeline, deal volume, sector performance,
and stage distribution where available.

## Execution

Discuss work order volume, completion, and ongoing work.

## Financial / Collection Picture

Discuss billed value, collected value, receivables,
and collection rate where available.

## Risks / Data Quality

Mention missing or incomplete data that could affect
decision-making.

## Recommended Focus

Give 2-4 practical areas leadership should focus on.

Do not invent numbers.
Do not assume missing values are zero.
Clearly mention limitations.
"""

            update = agent.answer(
                leadership_question,
                json.dumps(
                    context,
                    indent=2,
                    default=str
                )
            )

            st.markdown(
                update
            )

        except Exception as e:

            st.error(
                "❌ Unable to generate leadership update."
            )

            st.code(
                str(e)
            )


# ============================================================
# DATA QUALITY
# ============================================================

st.divider()

st.subheader(
    "⚠️ Data Quality"
)

dq1, dq2, dq3, dq4 = st.columns(4)


with dq1:

    st.metric(
        "Missing Deal Values",
        deal_summary[
            "missing_deal_values"
        ]
    )


with dq2:

    st.metric(
        "Missing Close Dates",
        deal_summary.get(
            "missing_close_dates",
            0
        )
    )


with dq3:

    st.metric(
        "Missing Collections",
        work_order_summary[
            "missing_collection_values"
        ]
    )


with dq4:

    st.metric(
        "Missing WO Status",
        work_order_summary[
            "missing_wo_status"
        ]
    )


st.caption(
    "Data is retrieved dynamically from Monday.com. "
    "Missing or incomplete values are surfaced rather "
    "than silently fabricated."
)