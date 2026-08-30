# Skylark Drones — Monday.com Business Intelligence Agent

## Decision Log

### 1. Key Assumptions

- Monday.com is treated as the source of truth for business data. The agent does not directly read or hardcode the supplied CSV/XLSX files after their import into Monday.com.
- The Deals and Work Orders datasets are maintained as separate Monday.com boards and are accessed through the Monday.com API in read-only mode.
- Deal pipeline is calculated using deals whose normalized status is `Open`.
- Pipeline values are grouped by normalized sector.
- Work-order execution is represented using the available execution-status field. Records with missing status are not silently treated as completed or ongoing.
- Financial metrics use the billed, collected, and receivable values available in the Work Orders board.
- Missing numeric values are not fabricated as zero when calculating data-quality statistics.
- Sector names and common variations are normalized where possible. Unrecognized or missing sector values are retained as `Unknown` rather than being silently discarded.
- Because the source data is messy, calculated metrics may be affected by missing or incomplete records. These limitations are surfaced to the user.

### 2. Technical Approach and Trade-offs

I implemented the prototype using Python and Streamlit, with Monday.com accessed dynamically through its API.

The architecture separates responsibilities into:

- `monday_client.py` — Monday.com authentication and read-only board retrieval.
- `data_cleaning.py` — normalization of column names, text, sectors, numeric values, and dates.
- `metrics.py` — pipeline, work-order, financial, sector, and cross-board calculations.
- `ai_agent.py` — conversational business-intelligence responses and leadership summaries.
- `app.py` — Streamlit conversational interface and business dashboard.

I chose Streamlit because it allowed a functional conversational prototype and dashboard to be developed quickly within the six-hour assignment constraint.

A deliberate trade-off was to calculate core business metrics deterministically in Python before passing the results to the language model. This reduces the risk of the LLM inventing or incorrectly calculating financial figures.

The agent also includes a local fallback response mechanism when the OpenAI API is unavailable because of quota, billing, or rate-limit errors. This ensures that core business questions can still be answered from the calculated Monday.com metrics.

### 3. Data Resilience

The source data contains missing values, inconsistent text, dates, and naming conventions.

The cleaning layer therefore:

- Normalizes column names.
- Handles null, empty, `N/A`, `None`, and similar values.
- Normalizes sector naming conventions.
- Converts financial fields into numeric values where possible.
- Converts date fields into standardized datetime values.
- Preserves missing information instead of fabricating values.
- Reports important data-quality gaps to the user.

For example, the dashboard explicitly reports missing deal values, missing close dates, missing collection values, and missing work-order status.

### 4. Cross-Board Analysis

The agent combines Deals and Work Orders at the sector level.

For each sector, it compares:

- Open sales pipeline from Deals.
- Billed execution value from Work Orders.

A sector is flagged as having potentially strong sales but weaker execution when it has a non-zero pipeline and billed execution is below 50% of its open pipeline.

The 50% threshold is a heuristic chosen for the prototype rather than a claim about Skylark's actual business policy. With more business context, this threshold should be configurable or replaced by a business-approved definition.

### 5. Leadership Updates

I interpreted "leadership updates" as a concise executive summary that converts the underlying metrics into decision-oriented information.

The generated update contains:

1. Executive Summary
2. Pipeline
3. Execution
4. Financial / Collection Picture
5. Risks / Data Quality
6. Recommended Focus Areas

The leadership update is intentionally concise and focuses on trends, risks, and areas requiring attention rather than reproducing the complete underlying dataset.

### 6. Query Understanding

The conversational interface supports founder-level questions about:

- Pipeline health
- Deal performance
- Sector performance
- Work-order execution
- Revenue and collections
- Receivables
- Data quality
- Cross-board sales versus execution
- Leadership updates

The system uses the available structured metrics as context for responses and avoids presenting missing information as confirmed facts.

### 7. What I Would Do Differently With More Time

With additional development time, I would:

- Add more robust semantic query understanding and clarification questions.
- Add configurable date-range filtering such as "this quarter".
- Add historical pipeline and execution trend analysis.
- Improve entity matching between Deals and Work Orders.
- Add more sophisticated sector and customer-name normalization.
- Add automated tests for all data-cleaning and metric calculations.
- Add authentication/role-based access for production use.
- Add monitoring and logging for Monday.com API failures.
- Improve the dashboard with interactive charts and drill-downs.
- Replace heuristic thresholds with business-approved definitions.
- Add caching and incremental data retrieval for larger Monday.com datasets.
