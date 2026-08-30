# Skylark Drones — Monday.com Business Intelligence Agent

A conversational Business Intelligence agent that connects to Monday.com and provides founder-level insights across Deals and Work Orders data.

---

## 1. Overview

The Skylark Business Intelligence Agent helps founders and executives answer business questions without manually extracting and cleaning data from multiple Monday.com boards.

The application supports:

- Sales pipeline analysis
- Deal performance
- Sector-level performance
- Work-order execution metrics
- Billing and collection analysis
- Receivables analysis
- Cross-board sales vs execution analysis
- Data-quality reporting
- Leadership updates

The application retrieves business data dynamically from Monday.com. The original source datasets are imported into Monday.com as separate boards and are **not hardcoded into the application**.

---

## 2. Architecture

```text
                         Monday.com
                        /          \
                       /            \
                 Deals Board    Work Orders Board
                       \            /
                        \          /
                         ▼        ▼
                     monday_client.py
                            |
                            ▼
                     data_cleaning.py
                            |
                            ▼
                        metrics.py
                            |
                ┌───────────┴───────────┐
                ▼                       ▼
        Business Metrics       Cross-Board Analysis
                │                       │
                └───────────┬───────────┘
                            ▼
                       ai_agent.py
                            |
                            ▼
                          app.py
                            |
                            ▼
                   Streamlit Interface
                            |
                            ▼
                  Founder-Level Questions
```

### Components

#### `app.py`

Main Streamlit application.

Provides:

- Business snapshot dashboard
- Conversational chat interface
- Leadership update generation
- Data-quality display

#### `monday_client.py`

Handles communication with Monday.com through the API.

The application retrieves:

- Deals board data
- Work Orders board data

The integration is read-only.

#### `data_cleaning.py`

Responsible for data resilience.

It handles:

- Column-name normalization
- Text cleaning
- Missing values
- Sector normalization
- Numeric/currency conversion
- Date conversion
- Standard internal field names

#### `metrics.py`

Calculates:

- Open pipeline
- Open deals
- Won/lost deals
- Pipeline by sector
- Pipeline by stage
- Work-order execution
- Billed value
- Collected value
- Receivables
- Collection rate
- Cross-board sector comparison

#### `ai_agent.py`

Provides conversational business-intelligence responses based on the calculated business metrics.

It also generates leadership updates and contains a fallback mechanism for API availability issues.

#### `prompts.py`

Contains reusable prompt-related configuration used by the application.

---

## 3. Monday.com Configuration

Create two separate boards in Monday.com.

### Board 1 — Deals

Import the supplied Deals dataset into a Monday.com board.

Important fields include:

- Sector / Service
- Deal Value
- Deal Status
- Deal Stage
- Close Date
- Tentative Close Date
- Created Date

### Board 2 — Work Orders

Import the supplied Work Orders dataset into a separate Monday.com board.

Important fields include:

- Sector
- Execution Status
- Billed Value
- Collected Amount
- Amount Receivable
- WO Status
- Billing Status

The exact Monday.com column types should be selected according to the imported data. Text, numeric/currency, date, and status columns can be used where appropriate.

The application uses the Monday.com board IDs configured in `monday_client.py` and retrieves the board data dynamically.

---

## 4. Environment Variables and Secrets

The application requires:

```text
MONDAY_API_TOKEN
OPENAI_API_KEY
```

For local Streamlit execution, create:

```text
.streamlit/secrets.toml
```

with:

```toml
MONDAY_API_TOKEN = "YOUR_MONDAY_API_TOKEN"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
```

Never commit `secrets.toml` to GitHub.

The project includes a `.gitignore` rule to prevent accidental exposure of API credentials.

---

## 5. Installation

Clone the repository and enter the project directory.

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## 6. Running Locally

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in the browser.

The default local address is:

```text
http://localhost:8501
```

---

## 7. Example Founder-Level Questions

The agent can answer questions such as:

```text
How is our pipeline looking?

Which sector has the strongest pipeline?

How are our work orders performing?

Which sectors have strong sales but weaker execution?

What are our collection risks?

What are the main data quality issues?

Prepare a leadership update.
```

The application is designed to provide business context and insights rather than returning only raw numbers.

---

## 8. Data Resilience

The source data contains real-world inconsistencies and incomplete records.

The application therefore:

- Handles null and missing values.
- Normalizes common sector-name variations.
- Normalizes column names.
- Converts financial values into numeric values where possible.
- Converts date fields into standardized datetime values.
- Preserves unknown values instead of silently inventing data.
- Reports important data-quality gaps to the user.

Missing information is not automatically treated as confirmed business values.

For example, the dashboard reports:

- Missing deal values
- Missing close dates
- Missing collection values
- Missing work-order status
- Missing execution status

This allows leadership users to understand limitations in the underlying dataset.

---

## 9. Cross-Board Analysis

The application combines information from the Deals and Work Orders boards at the sector level.

For each sector, it compares:

- Open sales pipeline from the Deals board
- Billed execution value from the Work Orders board

The system can identify sectors where sales pipeline is strong but recorded execution is comparatively weak.

The prototype uses a heuristic threshold for this analysis: a sector with non-zero pipeline and billed execution below 50% of its open pipeline is flagged as potentially having strong sales but weaker execution.

This threshold is a prototype assumption and should be configurable or replaced with a business-approved definition in a production implementation.

---

## 10. Leadership Updates

The leadership-update feature converts current business metrics into a concise executive summary.

The generated update contains:

1. Executive Summary
2. Pipeline
3. Execution
4. Financial / Collection Picture
5. Risks / Data Quality
6. Recommended Focus Areas

The purpose is to help leadership quickly understand:

- Current pipeline position
- Operational execution
- Financial collections
- Outstanding receivables
- Data-quality risks
- Areas requiring management attention

The leadership update is generated only from the available business metrics and does not intentionally fabricate missing information.

---

## 11. Error Handling

The application handles common data and API issues gracefully.

Examples include:

- Missing Monday.com configuration
- Missing OpenAI configuration
- Monday.com API retrieval failures
- Missing data fields
- Invalid numeric values
- Invalid or inconsistent dates
- Missing sector information
- OpenAI quota or billing failures

Core business metrics are calculated deterministically before being passed to the language model.

When the OpenAI API is unavailable because of quota, billing, or rate-limit issues, the application can fall back to a local business-intelligence response mechanism for supported questions.

---

## 12. Security

API credentials are stored using Streamlit secrets or environment variables.

API tokens should never be placed directly into application source code.

The following file must remain private:

```text
.streamlit/secrets.toml
```

It is excluded through `.gitignore`.

Before publishing the repository, verify that no API keys or other credentials are present in source files.

---

## 13. Technology Stack

### Python

Used for data processing, business logic, API integration, and the agent layer.

### Streamlit

Used for the conversational web interface and business dashboard.

### Pandas

Used for data cleaning, normalization, aggregation, and analysis.

### NumPy

Used for numerical operations and missing-value handling.

### Requests

Used for HTTP/API communication where required.

### OpenAI API

Used for conversational business-intelligence responses and leadership summaries when API access is available.

### Monday.com API

Used as the dynamic read-only source for Deals and Work Orders data.

---

## 14. Project Structure

```text
skylark-bi-agent/
│
├── .streamlit/
│   └── secrets.toml
│
├── app.py
├── monday_client.py
├── data_cleaning.py
├── metrics.py
├── ai_agent.py
├── prompts.py
├── test_monday.py
├── requirements.txt
├── README.md
├── DECISION_LOG.md
└── .gitignore
```

> Note: `.streamlit/secrets.toml` is required for local configuration but must not be committed to the public repository.

---

## 15. Future Improvements

With additional development time, the system could be extended with:

- Natural-language date filtering such as "this quarter"
- More sophisticated query understanding
- Automatic clarification questions for ambiguous queries
- Historical pipeline trends
- Historical execution trends
- More advanced entity and sector matching
- Configurable business thresholds
- Automated unit and integration tests
- Interactive charts and drill-downs
- Authentication and role-based access
- API monitoring and structured logging
- Incremental data retrieval for larger Monday.com boards
- More advanced forecasting and pipeline-health scoring

---

## 16. Assignment Deliverables

This repository contains the source code and documentation required for the Skylark Drones technical assignment.

### Hosted Prototype

A publicly accessible Streamlit deployment should be provided separately in the submission form.

### Decision Log

See:

```text
DECISION_LOG.md
```

for assumptions, trade-offs, leadership-update interpretation, and future improvements.

### Source Code

The repository contains the complete application source code and configuration documentation.

API credentials are intentionally excluded from the repository.