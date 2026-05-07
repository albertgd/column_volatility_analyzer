# ⚡ Column Volatility Analyzer

Paste any `CREATE TABLE` DDL → instantly get a **BigQuery / Standard SQL** query that measures how often each column changes across record versions.

## Quick Start

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install flask

# 3. Run the app
python app.py
# → Open http://127.0.0.1:5050
```

## How It Works

### Volatility Score
```
score = AVG( (unique_values_per_PK - 1) / (total_versions_per_PK - 1) )
```
| Score | Meaning | Category |
|-------|---------|----------|
| `0.0` | Column **never changes** | 🟩 Stable |
| `0.5` | Column changes **often** | 🟨 Volatile |
| `1.0` | Column **changes always** | 🟥 Dynamic |

Records with only 1 version are excluded (division by zero).

---

## Primary Key Detection Rules

Applied in priority order — first match wins:

| Priority | Rule | Example |
|----------|------|---------|
| **1** | Column name ends with `_PK` (case-insensitive) | `patient_PK`, `ORDER_PK` |
| **2** | `PRIMARY KEY` declared inline or as table constraint | `id INT PRIMARY KEY` |
| **3** | Column named `id` or ending in `_id` | `user_id`, `order_id` |

---

## SQL Dialects

| Dialect | Division function |
|---------|-------------------|
| **BigQuery** | `SAFE_DIVIDE(a, b)` — returns NULL instead of error |
| **Standard SQL** | `(a) / NULLIF(b, 0)` — ANSI compatible |

---

## Example Input / Output

**Input DDL:**
```sql
CREATE TABLE my_dataset.patient_records (
  patient_PK     STRING NOT NULL,
  visit_date     DATE,
  diagnosis_code STRING,
  weight_kg      FLOAT64,
  updated_at     TIMESTAMP
);
```

**Generated SQL:**
```sql
WITH PK_Stats AS (
    SELECT
        patient_PK,
        COUNT(*)                       AS total_versions,
        COUNT(DISTINCT visit_date)     AS unique_1,
        COUNT(DISTINCT diagnosis_code) AS unique_2,
        COUNT(DISTINCT weight_kg)      AS unique_3,
        COUNT(DISTINCT updated_at)     AS unique_4
    FROM patient_records
    GROUP BY patient_PK
),
ColumnVolatility AS (
    SELECT
        AVG(SAFE_DIVIDE(unique_1 - 1, total_versions - 1)) AS vol_score_visit_date,
        AVG(SAFE_DIVIDE(unique_2 - 1, total_versions - 1)) AS vol_score_diagnosis_code,
        AVG(SAFE_DIVIDE(unique_3 - 1, total_versions - 1)) AS vol_score_weight_kg,
        AVG(SAFE_DIVIDE(unique_4 - 1, total_versions - 1)) AS vol_score_updated_at
    FROM PK_Stats
    WHERE total_versions > 1
),
UnpivotedResults AS (
    SELECT 'visit_date' AS column_name, vol_score_visit_date AS volatility_score FROM ColumnVolatility
    UNION ALL
    SELECT 'diagnosis_code' AS column_name, vol_score_diagnosis_code AS volatility_score FROM ColumnVolatility
    -- ... more columns ...
)
SELECT 
    column_name,
    volatility_score,
    CASE 
        WHEN volatility_score <= 0.01 THEN '🟩 Stable (Almost no change)'
        WHEN volatility_score < 0.80  THEN '🟨 Volatile (Changes often)'
        ELSE '🟥 Dynamic (Changes always)'
    END AS volatility_category
FROM UnpivotedResults
ORDER BY volatility_score DESC;
```
