# ⚡ Column Volatility Analyzer

A premium web-based utility designed to analyze database schemas (DDL) and generate SQL queries that measure the **rate of change** (volatility) for every column in a table.

This tool is specifically built for data engineers working with **staged tables** or **versioned records**, where understanding how often specific attributes change is critical for data modeling and observability.

---

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
# → The app will be available at http://127.0.0.1:5050
```

---

## 📊 How It Works

### The Volatility Score
The generated SQL calculates a score for each column based on the unique values relative to the total number of record versions for a given Primary Key.

$$score = \text{AVG}\left( \frac{\text{unique\_values\_per\_PK} - 1}{\text{total\_versions\_per\_PK} - 1} \right)$$

| Score | Category | Meaning |
|:---:|:---:|:--- |
| `0.00` | 🟩 **Stable** | Column never changes across versions (e.g., birth_date). |
| `0.01 - 0.79` | 🟨 **Volatile** | Column changes occasionally (e.g., weight_kg, status). |
| `1.00` | 🟥 **Dynamic** | Column changes on every single version (e.g., updated_at). |

*Note: Records with only 1 version are automatically excluded to avoid division by zero.*

---

## 🔍 Primary Key Detection

The analyzer automatically identifies Primary Keys from your DDL using a prioritized rule system:

1.  **Explicit PK Suffix**: Any column ending with `_PK` (e.g., `patient_PK`).
2.  **DDL Constraints**: Columns marked as `PRIMARY KEY` (inline or table-level).
3.  **Surrogate Patterns**: Columns named exactly `id` or ending with `_id` (e.g., `user_id`).

---

## 🛠 Supported SQL Dialects

The tool generates safe SQL using dialect-specific functions to handle potential division-by-zero errors.

| Dialect | Division Function | Targeted Platform |
|:--- |:--- |:--- |
| **Snowflake** | `DIV0NULL(a, b)` | Snowflake Data Cloud |
| **Databricks** | `TRY_DIVIDE(a, b)` | Databricks / Spark SQL |

---

## 💻 Tech Stack

- **Backend**: Python 3.11+ / Flask
- **Frontend**: HTML5 & Vanilla CSS (Modern Dark Mode with Glassmorphism)
- **Typography**: Inter & JetBrains Mono (via Google Fonts)
- **Regex**: Robust DDL parsing engine

---

## 📖 Example

**Input DDL:**
```sql
CREATE TABLE clinical_trials.patient_vitals (
  patient_PK     STRING NOT NULL,
  reading_time   TIMESTAMP,
  heart_rate     INT,
  systolic_bp    INT,
  diastolic_bp   INT,
  ingestion_id   STRING
);
```

**Generated Logic (Summary):**
The tool generates a CTE-based query that:
1. Groups records by the detected Primary Key (`patient_PK`).
2. Counts distinct values for all other columns.
3. Calculates the average volatility score.
4. Unpivots the results and categorizes them by severity.

---

<footer>
Column Volatility Analyzer · Boehringer Ingelheim Data Engineering
</footer>
