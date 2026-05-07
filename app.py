"""
Column Volatility Analyzer
Parses a DDL and generates a SQL query to measure the rate of change per column.
"""

from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# DDL PARSING
# ─────────────────────────────────────────────────────────────────────────────

def parse_ddl(ddl: str) -> dict:
    """
    Parse a CREATE TABLE DDL statement and return:
      - table_name (str)
      - columns (list of dicts with 'name' and 'dtype')
      - pk_columns (list of column names identified as primary keys)
      - measure_columns (all non-PK columns)

    PK detection rules (applied in order, first match wins):
      1. Column name ends with '_PK' (case-insensitive)         → explicit PK suffix
      2. Column has a PRIMARY KEY constraint inline              → standard SQL PK
      3. Column name is exactly 'id' or ends with '_id'         → surrogate key pattern
    """
    # ── Strip Comments ────────────────────────────────────────────────────────
    # Remove block comments /* ... */
    ddl = re.sub(r'/\*.*?\*/', '', ddl, flags=re.DOTALL)
    # Remove line comments -- ... (but keep newlines)
    ddl = re.sub(r'--.*$', '', ddl, flags=re.MULTILINE)
    
    ddl = ddl.strip()

    # ── Extract table name ────────────────────────────────────────────────────
    tbl_match = re.search(
        r'CREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMP(?:ORARY)?\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?'
        r'(?:[`"\[]?[\w.]+[`"\]]?\.)?' 
        r'[`"\[]?([\w]+)[`"\]]?',
        ddl, re.IGNORECASE
    )
    if not tbl_match:
        raise ValueError("Could not find a CREATE TABLE statement in the DDL.")
    table_name = tbl_match.group(1)

    # ── Extract column block ──────────────────────────────────────────────────
    body_match = re.search(r'\((.*)\)', ddl, re.DOTALL)
    if not body_match:
        raise ValueError("Could not parse the column definitions (no parentheses found).")

    body = body_match.group(1)

    # Split on commas that are NOT inside nested parens
    def split_columns(text):
        parts, depth, current = [], 0, []
        for ch in text:
            if ch in ('(', '[', '{'):
                depth += 1
            elif ch in (')', ']', '}'):
                depth -= 1
            if ch == ',' and depth == 0:
                parts.append(''.join(current).strip())
                current = []
            else:
                current.append(ch)
        if current:
            parts.append(''.join(current).strip())
        return parts

    raw_parts = split_columns(body)

    columns = []
    inline_pk_cols = []

    # Tokens that signal a table-level constraint line, not a column definition
    constraint_keywords = re.compile(
        r'^\s*(PRIMARY\s+KEY|UNIQUE|CHECK|FOREIGN\s+KEY|CONSTRAINT|INDEX|KEY\b)',
        re.IGNORECASE
    )

    for part in raw_parts:
        part = part.strip()
        if not part:
            continue

        # Strip SQL line comments (-- ...) so section-header comments don't
        # block column detection. Keep the cleaned version for matching only;
        # preserve the original for the 'raw' field.
        part_clean = re.sub(r'--[^\n]*', '', part).strip()
        if not part_clean:
            continue

        if constraint_keywords.match(part_clean):
            # Table-level PRIMARY KEY clause: PRIMARY KEY (col1, col2, ...)
            pk_clause = re.search(r'PRIMARY\s+KEY\s*\(([^)]+)\)', part_clean, re.IGNORECASE)
            if pk_clause:
                for c in pk_clause.group(1).split(','):
                    inline_pk_cols.append(c.strip().strip('`"[]'))
            continue

        # Column definition: name  type  [constraints ...]
        # Use the last non-empty line of part_clean (handles multi-line parts
        # where a comment section header precedes the actual column line)
        lines = [l.strip() for l in part_clean.splitlines() if l.strip()]
        if not lines:
            continue
        col_line = lines[-1]   # last line is always the column definition

        col_match = re.match(r'[`"\[]?([\w]+)[`"\]]?\s+([\w][\w\s(),]*?)(?:\s+.*)?$', col_line)
        if not col_match:
            continue

        col_name = col_match.group(1)
        col_type = col_match.group(2).strip()

        has_inline_pk = bool(re.search(r'\bPRIMARY\s+KEY\b', part_clean, re.IGNORECASE))
        if has_inline_pk:
            inline_pk_cols.append(col_name)

        columns.append({'name': col_name, 'dtype': col_type, 'raw': col_line})

    if not columns:
        raise ValueError("No column definitions could be parsed from the DDL.")

    # ── Apply PK detection rules ──────────────────────────────────────────────
    pk_columns = []
    measure_columns = []

    def is_pk(col_name: str) -> tuple[bool, str]:
        """Return (is_pk, reason)."""
        # Rule 1 – explicit _PK suffix
        if re.search(r'_pk$', col_name, re.IGNORECASE):
            return True, "Ends with _PK suffix"
        # Rule 2 – inline PRIMARY KEY constraint
        if col_name in inline_pk_cols:
            return True, "Declared as PRIMARY KEY in DDL"
        # Rule 3 – surrogate id pattern
        if re.match(r'^id$', col_name, re.IGNORECASE) or re.search(r'_id$', col_name, re.IGNORECASE):
            return True, "Surrogate key pattern (*_id / id)"
        return False, ""

    for col in columns:
        flag, reason = is_pk(col['name'])
        col['is_pk'] = flag
        col['pk_reason'] = reason
        if flag:
            pk_columns.append(col['name'])
        else:
            measure_columns.append(col['name'])

    return {
        'table_name': table_name,
        'columns': columns,
        'pk_columns': pk_columns,
        'measure_columns': measure_columns,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SQL GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def generate_volatility_sql(parsed: dict, dialect: str = "snowflake") -> str:
    """
    Generate the column volatility SQL.

    Supports two dialects:
      - snowflake  → uses DIV0NULL(a, b)  — returns NULL when denominator is 0
      - databricks → uses TRY_DIVIDE(a, b) — Spark SQL / Databricks SQL safe divide
    """
    table_name   = parsed['table_name']
    pk_columns   = parsed['pk_columns']
    measure_cols = parsed['measure_columns']

    if not pk_columns:
        raise ValueError(
            "No primary key columns detected. "
            "Make sure at least one column ends with '_PK', is named 'id'/'*_id', "
            "or is declared PRIMARY KEY."
        )
    if not measure_cols:
        raise ValueError("No non-PK columns found to measure volatility on.")

    pk_select   = ',\n        '.join(pk_columns)
    pk_group_by = ', '.join(pk_columns)

    # COUNT(DISTINCT ...) lines in PK_Stats
    count_lines = []
    for i, col in enumerate(measure_cols, start=1):
        count_lines.append(f'        COUNT(DISTINCT {col}) AS unique_{i}')
    count_block = ',\n'.join(count_lines)

    # AVG(SAFE_DIVIDE / NULLIF ...) lines in ColumnVolatility
    avg_lines = []
    for i, col in enumerate(measure_cols, start=1):
        alias = f'vol_score_{col.lower()}'
        if dialect == "snowflake":
            expr = f'DIV0NULL(unique_{i} - 1, total_versions - 1)'
        else:  # databricks / Spark SQL
            expr = f'TRY_DIVIDE(unique_{i} - 1, total_versions - 1)'
        avg_lines.append(f'        AVG({expr}) AS {alias}')
    avg_block = ',\n'.join(avg_lines)

    # UNPIVOT logic using UNION ALL for maximum compatibility
    union_lines = []
    for col in measure_cols:
        alias = f'vol_score_{col.lower()}'
        union_lines.append(f"    SELECT '{col}' AS column_name, {alias} AS volatility_score FROM ColumnVolatility")
    unpivot_block = '\n    UNION ALL\n'.join(union_lines)

    dialect_note = "Snowflake · DIV0NULL" if dialect == "snowflake" else "Databricks SQL · TRY_DIVIDE"

    sql = f"""\
-- ════════════════════════════════════════════════════════════════════════════
-- Column Volatility Analysis  ·  Table: {table_name}  ·  {dialect_note}
-- Score: 0 = never changes  |  1 = changes on every version
-- ════════════════════════════════════════════════════════════════════════════

WITH PK_Stats AS (
    SELECT
        {pk_select},
        COUNT(*)                AS total_versions,
{count_block}
    FROM {table_name}
    GROUP BY {pk_group_by}
),
ColumnVolatility AS (
    SELECT
{avg_block}
    FROM PK_Stats
    WHERE total_versions > 1  -- Exclude single-version PKs to avoid division by zero
),
UnpivotedResults AS (
{unpivot_block}
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
ORDER BY volatility_score DESC;"""

    return sql


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    data    = request.get_json(force=True)
    ddl     = data.get('ddl', '').strip()
    dialect = data.get('dialect', 'snowflake')

    if not ddl:
        return jsonify({'error': 'Please provide a DDL statement.'}), 400

    try:
        parsed = parse_ddl(ddl)
        sql    = generate_volatility_sql(parsed, dialect=dialect)
        return jsonify({'parsed': parsed, 'sql': sql})
    except ValueError as e:
        return jsonify({'error': str(e)}), 422
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5050)
