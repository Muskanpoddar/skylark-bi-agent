import json
import re

from openai import OpenAI


class BIAgent:

    def __init__(self, api_key=None):

        self.api_key = api_key

        if api_key:
            self.client = OpenAI(
                api_key=api_key
            )
        else:
            self.client = None

    # ========================================================
    # MAIN ANSWER FUNCTION
    # ========================================================

    def answer(self, question, context):

        # Try OpenAI first
        if self.client:

            try:

                response = self.client.responses.create(
                    model="gpt-4.1-mini",

                    instructions="""
You are Skylark Business Intelligence Agent.

You help founders understand business performance.

Use ONLY the business data supplied to you.

Never invent numbers.

Clearly distinguish:
- sales pipeline
- deal value
- billed revenue
- collected amount
- receivables

If data is missing, mention the limitation.

Give concise, executive-friendly answers.

For leadership updates use:
1. Executive Summary
2. Pipeline
3. Execution
4. Financial / Collection Picture
5. Risks / Data Quality
6. Recommended Focus
""",

                    input=f"""
USER QUESTION:
{question}

BUSINESS DATA:
{context}
"""
                )

                return response.output_text

            except Exception as e:

                # If API credits/rate limit fail,
                # use local fallback.
                error_text = str(e).lower()

                if (
                    "429" in error_text
                    or "credit" in error_text
                    or "quota" in error_text
                    or "billing" in error_text
                ):

                    return self.local_answer(
                        question,
                        context
                    )

                raise e

        # No API key / credits
        return self.local_answer(
            question,
            context
        )

    # ========================================================
    # LOCAL BUSINESS INTELLIGENCE ENGINE
    # ========================================================

    def local_answer(self, question, context):

        try:
            data = json.loads(context)
        except Exception:
            data = {}

        deals = data.get(
            "deals",
            {}
        )

        work_orders = data.get(
            "work_orders",
            {}
        )

        comparison = data.get(
            "cross_board_sector_comparison",
            {}
        )

        data_quality = data.get(
            "data_quality",
            {}
        )

        q = question.lower().strip()

        # ====================================================
        # LEADERSHIP UPDATE
        # ====================================================

        if (
            "leadership" in q
            or "executive" in q
            or "management update" in q
        ):

            return self.leadership_update(
                deals,
                work_orders,
                comparison,
                data_quality
            )

        # ====================================================
        # PIPELINE
        # ====================================================

                # ====================================================
        # LEADERSHIP UPDATE
        # ====================================================

        if (
            "leadership" in q
            or "executive" in q
            or "management update" in q
        ):

            return self.leadership_update(
                deals,
                work_orders,
                comparison,
                data_quality
            )


        # ====================================================
        # DATA QUALITY
        # ====================================================

        if (
            "data quality" in q
            or "missing" in q
            or "incomplete" in q
            or "data issue" in q
        ):

            return self.data_quality_answer(
                data_quality
            )


        # ====================================================
        # SECTOR ANALYSIS
        # IMPORTANT: THIS MUST COME BEFORE PIPELINE
        # ====================================================

        if (
            "sector" in q
            or "energy" in q
            or "mining" in q
            or "defence" in q
            or "defense" in q
            or "agriculture" in q
            or "infrastructure" in q
        ):

            return self.sector_answer(
                deals,
                work_orders,
                comparison
            )


        # ====================================================
        # WORK ORDERS / OPERATIONS
        # ====================================================

        if (
            "work order" in q
            or "execution" in q
            or "operational" in q
            or "operations" in q
        ):

            return self.operations_answer(
                work_orders
            )


        # ====================================================
        # COLLECTION / REVENUE
        # ====================================================

        if (
            "collection" in q
            or "collected" in q
            or "receivable" in q
            or "billed" in q
            or "revenue" in q
        ):

            return self.financial_answer(
                work_orders
            )


        # ====================================================
        # PIPELINE
        # ====================================================

        if (
            "pipeline" in q
            or "sales" in q
            or "deal" in q
        ):

            return self.pipeline_answer(
                deals,
                comparison
            )


        # ====================================================
        # DEFAULT
        # ====================================================

        return self.general_answer(
            deals,
            work_orders
        )

        # ====================================================
        # SECTOR
        # ====================================================

        if "sector" in q:

            return self.sector_answer(
                deals,
                work_orders,
                comparison
            )

        # ====================================================
        # WORK ORDERS / OPERATIONS
        # ====================================================

        if (
            "work order" in q
            or "execution" in q
            or "operational" in q
            or "operations" in q
        ):

            return self.operations_answer(
                work_orders
            )

        # ====================================================
        # COLLECTION / REVENUE
        # ====================================================

        if (
            "collection" in q
            or "collected" in q
            or "receivable" in q
            or "billed" in q
            or "revenue" in q
        ):

            return self.financial_answer(
                work_orders
            )

        # ====================================================
        # DATA QUALITY
        # ====================================================

        if (
            "data quality" in q
            or "missing" in q
            or "incomplete" in q
            or "data issue" in q
        ):

            return self.data_quality_answer(
                data_quality
            )

        # ====================================================
        # DEFAULT
        # ====================================================

        return self.general_answer(
            deals,
            work_orders
        )

    # ========================================================
    # PIPELINE ANSWER
    # ========================================================

    def pipeline_answer(
        self,
        deals,
        comparison
    ):

        pipeline = deals.get(
            "open_pipeline",
            0
        )

        open_deals = deals.get(
            "open_deals",
            0
        )

        won = deals.get(
            "won_deals",
            0
        )

        lost = deals.get(
            "lost_deals",
            0
        )

        sector_data = deals.get(
            "pipeline_by_sector",
            {}
        )

        lines = []

        lines.append(
            "### Pipeline Overview"
        )

        lines.append(
            f"**Open pipeline:** "
            f"₹{pipeline:,.0f}"
        )

        lines.append(
            f"**Open deals:** {open_deals}"
        )

        lines.append(
            f"**Won deals:** {won}"
        )

        lines.append(
            f"**Lost deals:** {lost}"
        )

        if sector_data:

            strongest = max(
                sector_data,
                key=sector_data.get
            )

            strongest_value = sector_data[
                strongest
            ]

            lines.append("")

            lines.append(
                f"**Strongest pipeline sector:** "
                f"{strongest} "
                f"(₹{strongest_value:,.0f})"
            )

        lines.append("")

        lines.append(
            "### Insight"
        )

        if open_deals > 0:

            lines.append(
                "The current pipeline contains "
                f"{open_deals} open opportunities with "
                f"₹{pipeline:,.0f} of open value."
            )

        else:

            lines.append(
                "There are currently no open deals "
                "recorded in the dataset."
            )

        return "\n".join(lines)

    # ========================================================
    # SECTOR ANSWER
    # ========================================================

    def sector_answer(
        self,
        deals,
        work_orders,
        comparison
    ):

        pipeline = deals.get(
            "pipeline_by_sector",
            {}
        )

        billed = work_orders.get(
            "billed_by_sector",
            {}
        )

        if not pipeline and not billed:

            return (
                "I don't have sufficient sector data "
                "to compare performance."
            )

        sectors = set(
            pipeline.keys()
        ).union(
            billed.keys()
        )

        rows = []

        for sector in sectors:

            pipeline_value = float(
                pipeline.get(
                    sector,
                    0
                )
            )

            billed_value = float(
                billed.get(
                    sector,
                    0
                )
            )

            rows.append(
                (
                    sector,
                    pipeline_value,
                    billed_value
                )
            )

        # Highest pipeline first
        rows.sort(
            key=lambda x: x[1],
            reverse=True
        )

        answer = [
            "### Sector Performance",
            "",
            "| Sector | Open Pipeline | Billed |",
            "|---|---:|---:|"
        ]

        for sector, pipeline_value, billed_value in rows:

            answer.append(
                f"| {sector} | "
                f"₹{pipeline_value:,.0f} | "
                f"₹{billed_value:,.0f} |"
            )

        answer.append("")

        # ----------------------------------------------------
        # Identify strongest sales sector
        # ----------------------------------------------------

        pipeline_rows = [
            row
            for row in rows
            if row[1] > 0
        ]

        if pipeline_rows:

            strongest_sales = max(
                pipeline_rows,
                key=lambda x: x[1]
            )

            answer.append(
                f"**Strongest sales pipeline:** "
                f"{strongest_sales[0]} "
                f"with ₹{strongest_sales[1]:,.0f}."
            )

        # ----------------------------------------------------
        # Identify weaker execution relative to sales
        # ----------------------------------------------------

        if len(rows) > 1:

            max_pipeline = max(
                row[1]
                for row in rows
            )

            max_billed = max(
                row[2]
                for row in rows
            )

            weak_execution_candidates = []

            for sector, pipe, bill in rows:

                pipeline_score = (
                    pipe / max_pipeline
                    if max_pipeline > 0
                    else 0
                )

                execution_score = (
                    bill / max_billed
                    if max_billed > 0
                    else 0
                )

                # Strong sales + comparatively weaker execution
                if (
                    pipeline_score >= 0.5
                    and execution_score < pipeline_score
                ):

                    weak_execution_candidates.append(
                        (
                            sector,
                            pipe,
                            bill,
                            pipeline_score,
                            execution_score
                        )
                    )

            if weak_execution_candidates:

                weak_execution_candidates.sort(
                    key=lambda x:
                    x[3] - x[4],
                    reverse=True
                )

                answer.append("")

                answer.append(
                    "### Sales vs Execution"
                )

                answer.append(
                    "The following sectors show relatively "
                    "strong pipeline value but weaker billed "
                    "execution compared with their pipeline:"
                )

                for (
                    sector,
                    pipe,
                    bill,
                    pipeline_score,
                    execution_score
                ) in weak_execution_candidates:

                    answer.append(
                        f"- **{sector}** — "
                        f"₹{pipe:,.0f} open pipeline vs "
                        f"₹{bill:,.0f} billed."
                    )

            else:

                answer.append("")

                answer.append(
                    "### Sales vs Execution"
                )

                answer.append(
                    "No clear sector with both strong sales "
                    "pipeline and materially weaker billed "
                    "execution was identified from the "
                    "available data."
                )

        return "\n".join(answer)
    # ========================================================
    # OPERATIONS ANSWER
    # ========================================================

    def operations_answer(
        self,
        work_orders
    ):

        total = work_orders.get(
            "total_work_orders",
            0
        )

        completed = work_orders.get(
            "completed_orders",
            0
        )

        ongoing = work_orders.get(
            "ongoing_orders",
            0
        )

        not_started = work_orders.get(
            "not_started_orders",
            0
        )

        return f"""
### Operational Performance

**Total work orders:** {total}

**Completed:** {completed}

**Ongoing:** {ongoing}

**Not started / pending:** {not_started}

The current dataset indicates that {completed} of
{total} work orders are recorded as completed.

The operational picture should be interpreted alongside
the missing-status data below, since incomplete records
may affect the reported counts.
"""

    # ========================================================
    # FINANCIAL ANSWER
    # ========================================================

    def financial_answer(
        self,
        work_orders
    ):

        billed = work_orders.get(
            "total_billed",
            0
        )

        collected = work_orders.get(
            "total_collected",
            0
        )

        receivable = work_orders.get(
            "total_receivable",
            0
        )

        rate = work_orders.get(
            "collection_rate",
            0
        )

        return f"""
### Financial / Collection Picture

**Total billed:** ₹{billed:,.0f}

**Total collected:** ₹{collected:,.0f}

**Receivables:** ₹{receivable:,.0f}

**Collection rate:** {rate:.1f}%

The collection rate indicates that approximately
{rate:.1f}% of the recorded billed value has been
collected.

Receivables of ₹{receivable:,.0f} represent the
recorded outstanding amount and may warrant follow-up.
"""

    # ========================================================
    # DATA QUALITY ANSWER
    # ========================================================

    def data_quality_answer(
        self,
        quality
    ):

        return f"""
### Data Quality Assessment

The agent identified the following incomplete records:

- **Missing deal values:** {quality.get("deals_missing_values", 0)}
- **Missing deal close dates:** {quality.get("deals_missing_close_dates", 0)}
- **Missing deal sectors:** {quality.get("deals_missing_sectors", 0)}
- **Missing collection values:** {quality.get("work_orders_missing_collection", 0)}
- **Missing work-order status:** {quality.get("work_orders_missing_status", 0)}
- **Missing execution status:** {quality.get("work_orders_missing_execution_status", 0)}

These gaps should be considered when interpreting
pipeline, execution and financial metrics.

The system does not treat missing values as confirmed
zero values.
"""

    # ========================================================
    # LEADERSHIP UPDATE
    # ========================================================

    def leadership_update(
        self,
        deals,
        work_orders,
        comparison,
        quality
    ):

        pipeline = deals.get(
            "open_pipeline",
            0
        )

        open_deals = deals.get(
            "open_deals",
            0
        )

        total_work_orders = work_orders.get(
            "total_work_orders",
            0
        )

        completed = work_orders.get(
            "completed_orders",
            0
        )

        billed = work_orders.get(
            "total_billed",
            0
        )

        collected = work_orders.get(
            "total_collected",
            0
        )

        receivable = work_orders.get(
            "total_receivable",
            0
        )

        collection_rate = work_orders.get(
            "collection_rate",
            0
        )

        sector_data = deals.get(
            "pipeline_by_sector",
            {}
        )

        if sector_data:

            strongest_sector = max(
                sector_data,
                key=sector_data.get
            )

            strongest_value = sector_data[
                strongest_sector
            ]

        else:

            strongest_sector = "Unknown"
            strongest_value = 0

        return f"""
# Leadership Update

## Executive Summary

The business currently has **₹{pipeline:,.0f}**
of open sales pipeline across **{open_deals} open deals**.

On the execution side, **{completed} of
{total_work_orders} work orders** are recorded as
completed.

## Pipeline

The strongest identified pipeline sector is
**{strongest_sector}**, with approximately
**₹{strongest_value:,.0f}** in open pipeline.

## Execution

There are **{total_work_orders} work orders** in the
current dataset, of which **{completed} are completed**.

## Financial / Collection Picture

Recorded billed value is **₹{billed:,.0f}**.

Recorded collections are **₹{collected:,.0f}**,
giving a collection rate of **{collection_rate:.1f}%**.

Recorded receivables are **₹{receivable:,.0f}**.

## Risks / Data Quality

There are **{quality.get("deals_missing_values", 0)}**
deals with missing values and
**{quality.get("deals_missing_close_dates", 0)}**
deals with missing close dates.

There are also
**{quality.get("work_orders_missing_collection", 0)}**
work orders with missing collection values.

These gaps should be considered before making
high-confidence decisions.

## Recommended Focus

1. Prioritize conversion of the highest-value open
   pipeline opportunities.

2. Review receivables and collection follow-ups.

3. Monitor incomplete work-order and deal records.

4. Compare sector-level pipeline against execution
   performance to identify areas where sales momentum
   is not yet translating into delivery.
"""

    # ========================================================
    # GENERAL ANSWER
    # ========================================================

    def general_answer(
        self,
        deals,
        work_orders
    ):

        return f"""
### Business Snapshot

Here is the current picture from Monday.com:

- **Open pipeline:** ₹{deals.get("open_pipeline", 0):,.0f}
- **Open deals:** {deals.get("open_deals", 0)}
- **Work orders:** {work_orders.get("total_work_orders", 0)}
- **Completed work orders:** {work_orders.get("completed_orders", 0)}
- **Total billed:** ₹{work_orders.get("total_billed", 0):,.0f}
- **Total collected:** ₹{work_orders.get("total_collected", 0):,.0f}
- **Receivables:** ₹{work_orders.get("total_receivable", 0):,.0f}
- **Collection rate:** {work_orders.get("collection_rate", 0):.1f}%

You can ask me about pipeline, sectors, work orders,
collections, revenue, data quality, or leadership updates.
"""