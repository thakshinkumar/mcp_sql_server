from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pyodbc
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (where main.py is 4 levels deep)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=str(env_path))

# Optional OpenAI import (only if API key is available)
OPENAI_AVAILABLE = False
try:
    if os.getenv("OPENAI_API_KEY"):
        from openai import OpenAI
        OPENAI_AVAILABLE = True
except ImportError:
    pass

app = FastAPI()

# Lazy-loaded OpenAI client
_client = None

def get_client():
    """Get or create the OpenAI client on first use."""
    global _client
    if _client is None and OPENAI_AVAILABLE:
        from openai import OpenAI
        _client = OpenAI()
    return _client


class QueryRequest(BaseModel):
    query: str


# DB connection
def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"
        "DATABASE=testdb;"
        "Trusted_Connection=yes;"
    )


def get_current_database(conn) -> str:
    cursor = conn.cursor()
    cursor.execute("SELECT DB_NAME()")
    row = cursor.fetchone()
    return row[0] if row and row[0] else None


def use_database(conn, db_name: str):
    if db_name:
        cursor = conn.cursor()
        cursor.execute(f"USE [{db_name}]")
        conn.commit()


def table_exists(conn, table_name: str) -> bool:
    if not table_name:
        return False
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' "
        "AND TABLE_NAME = ?", table_name
    )
    return cursor.fetchone() is not None


def extract_table_name_from_sql(sql_query: str) -> str:
    """Extract table name from common SQL Server statements."""
    import re

    if not sql_query:
        return None

    sql = sql_query.strip()
    patterns = [
        r"^\s*CREATE\s+TABLE\s+([^\s(;]+)",
        r"^\s*DROP\s+TABLE\s+([^\s(;]+)",
        r"^\s*ALTER\s+TABLE\s+([^\s(;]+)",
        r"^\s*TRUNCATE\s+TABLE\s+([^\s(;]+)",
        r"^\s*UPDATE\s+([^\s(;]+)",
        r"^\s*DELETE\s+FROM\s+([^\s(;]+)",
        r"^\s*SELECT\b.+?\bFROM\s+([^\s(;]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, sql, flags=re.IGNORECASE)
        if match:
            raw_name = match.group(1).strip()
            # Handle schema-qualified names and bracket quoting.
            base_name = raw_name.split(".")[-1].strip("[]")
            return base_name if base_name else None

    return None


def get_table_columns(table_name: str) -> list:
    """Fetch actual table columns from INFORMATION_SCHEMA."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = f"""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
        """
        cursor.execute(query)
        columns = cursor.fetchall()
        conn.close()
        return columns
    except:
        return []


def strip_go(sql_text: str) -> str:
    """Remove SSMS-style GO batch separators (not valid T-SQL)."""
    import re

    if not sql_text:
        return sql_text
    # Remove lines that are only "GO" (case-insensitive), optionally preceded/followed by whitespace.
    return re.sub(r"(?im)^[ \t]*GO[ \t]*;?[ \t]*\r?\n?", "", sql_text).strip()


def split_sql_statements(sql_text: str) -> list[str]:
    """Split a SQL batch into statements by semicolons, ignoring semicolons inside strings."""
    if not sql_text:
        return []

    sql_text = strip_go(sql_text)
    stmts: list[str] = []
    buf: list[str] = []
    in_single = False
    in_double = False

    i = 0
    while i < len(sql_text):
        ch = sql_text[i]

        if ch == "'" and not in_double:
            # Handle escaped single quote: ''
            if in_single and i + 1 < len(sql_text) and sql_text[i + 1] == "'":
                buf.append("''")
                i += 2
                continue
            in_single = not in_single
            buf.append(ch)
            i += 1
            continue

        if ch == '"' and not in_single:
            in_double = not in_double
            buf.append(ch)
            i += 1
            continue

        if ch == ";" and not in_single and not in_double:
            stmt = "".join(buf).strip()
            if stmt:
                stmts.append(stmt)
            buf = []
            i += 1
            continue

        buf.append(ch)
        i += 1

    tail = "".join(buf).strip()
    if tail:
        stmts.append(tail)
    return stmts


def database_exists(conn, db_name: str) -> bool:
    if not db_name:
        return False
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM sys.databases WHERE name = ?", db_name)
    return cur.fetchone() is not None


def validate_statement(conn, statement: str) -> tuple[bool, str]:
    """Allowlist-based validator with basic schema checks."""
    import re

    if not statement or not statement.strip():
        return False, "Empty SQL statement"

    s = statement.strip()
    s_upper = s.upper()

    # Block multi-statement chains in a single statement (should have been split already).
    if ";" in s:
        return False, "Multiple statements detected"

    # Hard blocks (safety)
    blocked = ["MERGE ", "GRANT ", "REVOKE ", "DENY ", "BACKUP ", "RESTORE ", "KILL ", "SHUTDOWN "]
    if any(tok in s_upper for tok in blocked):
        return False, "Statement type not allowed"

    # Allow USE <db>
    if s_upper.startswith("USE "):
        m = re.match(r"(?is)^\s*USE\s+(\[?[A-Za-z0-9_]+\]?)\s*$", s)
        if not m:
            return False, "Invalid USE syntax"
        db = m.group(1).strip("[]")
        if not database_exists(conn, db):
            return False, f"Database '{db}' does not exist"
        return True, ""

    # Allow CREATE/DROP DATABASE
    if s_upper.startswith("CREATE DATABASE"):
        m = re.match(r"(?is)^\s*CREATE\s+DATABASE\s+(\[?[A-Za-z0-9_]+\]?)\s*$", s)
        if not m:
            return False, "Invalid CREATE DATABASE syntax"
        return True, ""

    if s_upper.startswith("DROP DATABASE"):
        m = re.match(r"(?is)^\s*DROP\s+DATABASE\s+(\[?[A-Za-z0-9_]+\]?)\s*$", s)
        if not m:
            return False, "Invalid DROP DATABASE syntax"
        return True, ""

    # Allow EXEC only for safe built-ins we use (rename/comments).
    if s_upper.startswith("EXEC") or s_upper.startswith("EXECUTE"):
        allowed_exec = ["SP_RENAME", "SYS.SP_ADDEXTENDEDPROPERTY", "SYS.SP_UPDATEEXTENDEDPROPERTY"]
        if not any(a in s_upper for a in allowed_exec):
            return False, "EXEC is not allowed (except sp_rename / sp_addextendedproperty)"
        return True, ""

    # Table ops
    if any(s_upper.startswith(k) for k in ["CREATE TABLE", "DROP TABLE", "ALTER TABLE", "TRUNCATE TABLE"]):
        tbl = extract_table_name_from_sql(s)
        if not tbl:
            return False, "Could not determine target table"

        if s_upper.startswith("CREATE TABLE"):
            if table_exists(conn, tbl):
                return False, f"Table '{tbl}' already exists"
            return True, ""

        if s_upper.startswith("DROP TABLE") or s_upper.startswith("TRUNCATE TABLE"):
            if not table_exists(conn, tbl):
                return False, f"Table '{tbl}' does not exist"
            return True, ""

        # ALTER TABLE: basic column existence checks
        if not table_exists(conn, tbl):
            return False, f"Table '{tbl}' does not exist"

        cols = {str(r[0]).lower() for r in get_table_columns(tbl)}
        m_add = re.search(r"(?is)\bADD\b\s+(\[?[A-Za-z0-9_]+\]?)\b", s)
        if m_add:
            col = m_add.group(1).strip("[]").lower()
            if col in cols:
                return False, f"Column '{col}' already exists on '{tbl}'"
            return True, ""

        m_dropcol = re.search(r"(?is)\bDROP\b\s+COLUMN\b\s+(\[?[A-Za-z0-9_]+\]?)\b", s)
        if m_dropcol:
            col = m_dropcol.group(1).strip("[]").lower()
            if col not in cols:
                return False, f"Column '{col}' does not exist on '{tbl}'"
            return True, ""

        # ALTER COLUMN: ensure column exists
        m_altercol = re.search(r"(?is)\bALTER\b\s+COLUMN\b\s+(\[?[A-Za-z0-9_]+\]?)\b", s)
        if m_altercol:
            col = m_altercol.group(1).strip("[]").lower()
            if col not in cols:
                return False, f"Column '{col}' does not exist on '{tbl}'"
            return True, ""

        return True, ""

    # SELECT (only allow SELECT * FROM <table> for now)
    if s_upper.startswith("SELECT"):
        tbl = extract_table_name_from_sql(s)
        if tbl and not table_exists(conn, tbl):
            return False, f"Table '{tbl}' does not exist"
        return True, ""

    # INSERT
    if s_upper.startswith("INSERT INTO"):
        import re
        m = re.match(r"(?is)^\s*INSERT\s+INTO\s+([^\s(]+)\s*(\(([^)]*)\))?\s+VALUES\s*\(", s)
        if not m:
            return False, "Invalid INSERT syntax"
        raw_tbl = m.group(1)
        tbl = raw_tbl.split(".")[-1].strip("[]")
        if not table_exists(conn, tbl):
            return False, f"Table '{tbl}' does not exist"
        cols_live = {str(r[0]).lower() for r in get_table_columns(tbl)}
        cols_part = m.group(3)
        if cols_part:
            cols_req = [c.strip().strip("[]").lower() for c in cols_part.split(",") if c.strip()]
            missing = [c for c in cols_req if c not in cols_live]
            if missing:
                return False, f"Insert columns not found on '{tbl}': {', '.join(missing)}"
        return True, ""

    # UPDATE
    if s_upper.startswith("UPDATE "):
        import re
        m = re.match(r"(?is)^\s*UPDATE\s+([^\s]+)\s+SET\s+(.+)$", s)
        if not m:
            return False, "Invalid UPDATE syntax"
        raw_tbl = m.group(1)
        tbl = raw_tbl.split(".")[-1].strip("[]")
        if not table_exists(conn, tbl):
            return False, f"Table '{tbl}' does not exist"
        cols_live = {str(r[0]).lower() for r in get_table_columns(tbl)}
        set_part = m.group(2)
        # Validate SET columns
        set_cols = re.findall(r"(?is)(?:^|,)\s*(\[?[A-Za-z0-9_]+\]?)\s*=", set_part)
        if not set_cols:
            return False, "UPDATE must include SET column=value"
        missing = [c.strip("[]").lower() for c in set_cols if c.strip("[]").lower() not in cols_live]
        if missing:
            return False, f"Update columns not found on '{tbl}': {', '.join(missing)}"
        return True, ""

    # DELETE
    if s_upper.startswith("DELETE FROM"):
        tbl = extract_table_name_from_sql(s)
        if tbl and not table_exists(conn, tbl):
            return False, f"Table '{tbl}' does not exist"
        return True, ""

    return False, "Unsupported SQL statement"


def extract_table_name(query: str) -> str:
    """Extract table name from natural language query."""
    import re
    reserved_or_noise = {
        "the", "a", "an", "with", "and", "or", "from", "in", "to", "into",
        "table", "tables", "column", "columns", "database", "db", "where",
        "set", "values", "value", "add", "drop", "alter", "create", "rename",
        "highest", "lowest", "ascending", "descending", "largest", "smallest",
        "top", "bottom", "first", "last", "oldest", "youngest", "max", "min",
        "ordered",
    }
    
    # Match patterns: "table users", "from users", "users table", "called users"
    # Avoid matching articles like "the"
    patterns = [
        r'(?:table|from|in)\s+(?!the\s|an?\s)(\w+)',  # Avoid "the" or "a/an" after from/in/table
        r'(?!the\s|an?\s)(\w+)\s+table',  # Avoid "the table" or "a table"
        r'called\s+(\w+)',
        r'rename\s+(?:table\s+)?\w+\s+to\s+(\w+)(?:\s|$)',
        r'(?:alter|drop|truncate|describe|create)\s+(?:table\s+)?(?!the\s|an?\s)(\w+)',  # Avoid articles
        r'show\s+all\s+(?!the\s|an?\s)(\w+)',  # Match "show all users", "show all products", etc.
    ]
    
    query_lower = query.lower()
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            table_name = match.group(1)
            # Additional check: reject articles/keywords/noise tokens
            if table_name not in reserved_or_noise:
                return table_name
    
    return None


def infer_table_name(query: str, default: str = None) -> str:
    """Infer table name from broader NL patterns."""
    import re

    q = (query or "").lower().strip()
    table_name = extract_table_name(q)
    if table_name:
        return table_name

    aggregate_patterns = [
        r'(?:count(?:\s+total\s+number\s+of)?|number\s+of)\s+(\w+)',
        r'(?:maximum|max(?:imum)?|minimum|min(?:imum)?|average|avg|sum)\s+(\w+)\s+(?:of|among)\s+(\w+)',
    ]
    for pat in aggregate_patterns:
        m = re.search(pat, q)
        if m:
            candidate = m.group(m.lastindex)
            if candidate not in {"age", "salary", "price", "count", "total", "number"}:
                return candidate

    # Handle "top/first/limit N <table>" while avoiding sort words.
    m = re.search(r'(?:top|first|limit)\s+\d+\s+(\w+)', q)
    if m:
        candidate = m.group(1)
        sort_noise = {
            "highest", "lowest", "ascending", "descending", "largest", "smallest",
            "oldest", "youngest", "max", "min", "first", "last", "top", "bottom",
        }
        if candidate not in sort_noise:
            return candidate

    candidates = [
        r'(?:from|into|in)\s+(\w+)',
        r'(?:update|delete|select|show|display|list|count|find|get|fetch|remove)\s+(\w+)',
        r'(\w+)\s+records',
        r'(\w+)\s+rows',
        r'(?:youngest|oldest)\s+(\w+)',
    ]
    noise = {
        "all", "the", "a", "an", "new", "record", "records", "row", "rows", "user",
        "top", "first", "limit", "highest", "lowest", "ascending", "descending",
        "largest", "smallest", "oldest", "youngest", "max", "min", "bottom", "last",
        "ordered", "total", "number", "maximum", "minimum", "average",
    }
    for pat in candidates:
        m = re.search(pat, q)
        if m:
            t = m.group(1)
            if t not in noise and not t.isdigit():
                return t
    return default


def extract_columns_from_query(query: str) -> list:
    """Extract column definitions from natural language query."""
    import re
    
    query_lower = query.lower()
    columns = []
    
    # Mapping of keywords to data types
    datatype_map = {
        'id': 'INT PRIMARY KEY',
        'name': 'VARCHAR(100)',
        'email': 'VARCHAR(255)',
        'password': 'VARCHAR(255)',
        'phone': 'VARCHAR(20)',
        'address': 'VARCHAR(500)',
        'salary': 'DECIMAL(10,2)',
        'price': 'DECIMAL(10,2)',
        'age': 'INT',
        'date': 'DATE',
        'timestamp': 'DATETIME',
        'description': 'VARCHAR(500)',
        'status': 'VARCHAR(50)',
    }
    
    # Check for each possible column
    for col_name, col_type in datatype_map.items():
        if col_name in query_lower:
            columns.append((col_name, col_type))
    
    return columns


def nl_to_sql_mock(nl_query: str) -> str:
    """DDL-focused SQL generation with rule-based mapping."""
    query_lower = nl_query.lower()
    import re

    number_words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }

    def sql_value(raw: str) -> str:
        raw = (raw or "").strip()
        if re.fullmatch(r"-?\d+(?:\.\d+)?", raw):
            return raw
        return "'" + raw.replace("'", "''") + "'"

    def extract_limit(text: str) -> int | None:
        digit_match = re.search(r'(?:top|first|limit)\s+(\d+)', text)
        if digit_match:
            return int(digit_match.group(1))

        word_match = re.search(r'\b(?:the\s+)?(one|two|three|four|five|six|seven|eight|nine|ten)\b', text)
        if word_match and any(term in text for term in ["youngest", "oldest", "highest", "lowest", "first", "top"]):
            return number_words[word_match.group(1)]

        return None

    def parse_simple_where(text: str, live_cols: set[str] | None = None) -> str:
        parts = []
        t = text.lower().strip()

        if t.startswith("whose "):
            t = t[6:]

        multi_name_match = re.search(r'(\w+)\s+(?:is|equals)\s+([a-zA-Z0-9_@.\-]+)\s+or\s+([a-zA-Z0-9_@.\-]+)', t)
        if multi_name_match:
            col = multi_name_match.group(1).lower()
            if not live_cols or col in live_cols:
                return f" WHERE {col} = {sql_value(multi_name_match.group(2))} OR {col} = {sql_value(multi_name_match.group(3))}"

        patterns = [
            (r'(\w+)\s+is\s+not\s+equal\s+to\s+(\d+)', lambda m: f"{m.group(1)} <> {m.group(2)}"),
            (r'(\w+)\s+is\s+not\s+equal\s+to\s+([a-zA-Z0-9_@.\-]+)', lambda m: f"{m.group(1)} <> {sql_value(m.group(2))}"),
            (r'(\w+)\s+is\s+not\s+([a-zA-Z0-9_@.\-]+)', lambda m: f"{m.group(1)} <> {sql_value(m.group(2))}"),
            (r'(\w+)\s+between\s+(\d+)\s+and\s+(\d+)', lambda m: f"{m.group(1)} BETWEEN {m.group(2)} AND {m.group(3)}"),
            (r'(\w+)\s+(?:>=|greater than or equal to)\s+(\d+)', lambda m: f"{m.group(1)} >= {m.group(2)}"),
            (r'(\w+)\s+(?:<=|less than or equal to)\s+(\d+)', lambda m: f"{m.group(1)} <= {m.group(2)}"),
            (r'(\w+)\s+(?:>|greater than|above)\s+(\d+)', lambda m: f"{m.group(1)} > {m.group(2)}"),
            (r'(\w+)\s+(?:<|less than|below)\s+(\d+)', lambda m: f"{m.group(1)} < {m.group(2)}"),
            (r'(\w+)\s+contains\s+the\s+letter\s+([a-zA-Z0-9_@.\-]+)', lambda m: f"{m.group(1)} LIKE '%{m.group(2)}%'"),
            (r'(\w+)\s+(?:contains|like)\s+([a-zA-Z0-9_@.\-]+)', lambda m: f"{m.group(1)} LIKE '%{m.group(2)}%'"),
            (r'(\w+)\s+starts with\s+([a-zA-Z0-9_@.\-]+)', lambda m: f"{m.group(1)} LIKE '{m.group(2)}%'"),
            (r'(\w+)\s+ends with\s+([a-zA-Z0-9_@.\-]+)', lambda m: f"{m.group(1)} LIKE '%{m.group(2)}'"),
        ]
        for pat, builder in patterns:
            for m in re.finditer(pat, t):
                col = m.group(1).lower()
                if live_cols and col not in live_cols:
                    continue
                parts.append(builder(m))

        if not parts:
            comparator_matches = list(
                re.finditer(
                    r'(\w+)\s+(?:is\s+)?(?:greater than or equal to|less than or equal to|greater than|less than|above|below|not equal to|equal to|equals|is)\s+([a-zA-Z0-9_@.\-]+)',
                    t,
                )
            )
            for m in comparator_matches:
                col = m.group(1).lower()
                value = m.group(2)
                if live_cols and col not in live_cols:
                    continue
                if value in {"greater", "less", "above", "below", "not"}:
                    continue

        if not parts:
            equality_pattern = r'(\w+)\s+(?:=|is|equals)\s+([a-zA-Z0-9_@.\-]+)'
            for m in re.finditer(equality_pattern, t):
                col = m.group(1).lower()
                value = m.group(2).lower()
                if live_cols and col not in live_cols:
                    continue
                if value in {"greater", "less", "above", "below", "not", "equal"}:
                    continue
                parts.append(f"{col} = {sql_value(m.group(2))}")

        if not parts:
            return ""

        joiner = " OR " if " or " in t else " AND "
        return " WHERE " + joiner.join(dict.fromkeys(parts))
    
    # ===== CREATE DATABASE =====
    if ('create' in query_lower or 'make' in query_lower or 'new' in query_lower) and 'database' in query_lower:
        # Extract database name from various patterns
        # Patterns: "create database xyz", "make database xyz", "new database xyz", "named xyz", "called xyz"
        db_match = re.search(r'(?:create|make|new)(?:\s+a)?\s+(?:new\s+)?(?:database|db)\s+(?:called|named|as)?\s*(\w+)', query_lower)
        if db_match:
            db_name = db_match.group(1)
            return f"CREATE DATABASE {db_name};"
        return "CREATE DATABASE newdatabase;"
    
    # ===== DROP DATABASE =====
    if ('drop' in query_lower or 'delete' in query_lower or 'remove' in query_lower) and 'database' in query_lower:
        # Extract database name from various patterns
        db_match = re.search(r'(?:drop|delete|remove)\s+(?:the\s+)?(?:database|db)\s+(?:called|named)?\s*(\w+)', query_lower)
        if db_match:
            db_name = db_match.group(1)
            return f"DROP DATABASE {db_name};"
        return "DROP DATABASE newdatabase;"
    
    # ===== RULE 1: SHOW / DESCRIBE TABLE STRUCTURE =====
    if any(phrase in query_lower for phrase in ['describe', 'show structure', 'show schema', 'columns in', 'show columns', 'table structure']):
        table_name = infer_table_name(query_lower)
        if table_name:
            return f"SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' ORDER BY ORDINAL_POSITION;"
        return "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';"
    
    # ===== RULE 2: LIST ALL TABLES =====
    if any(phrase in query_lower for phrase in ['show all tables', 'list tables', 'database tables', 'list all tables']):
        return "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';"
    
    # ===== RULE 2.5: SHOW ALL DATA FROM TABLE =====
    # Supports:
    # - "show all users"
    # - "display all records from users table"
    # - "list all rows in users"
    # Do not match if the query also requests filtering/sorting/limits/aggregations.
    simple_show_all = any(phrase in query_lower for phrase in ["show all", "display all", "list all"])
    has_advanced_select_intent = any(
        phrase in query_lower
        for phrase in [
            "where",
            "with ",
            "having",
            "sort by",
            "sorted by",
            "order by",
            "ascending",
            "descending",
            "latest",
            "top ",
            "first ",
            "limit ",
            "count",
            "average",
            "avg",
            "sum",
            "min",
            "max",
        ]
    )
    if simple_show_all and not has_advanced_select_intent and any(
        marker in query_lower for marker in ["record", "records", "row", "rows", "from", "in", "table"]
    ):
        table_name = infer_table_name(query_lower)
        if table_name and table_name != "tables":
            return f"SELECT * FROM {table_name};"

    # ===== RULE 2.6: ADVANCED SELECT (conditions/sorting/limit/aggregations/patterns) =====
    if any(k in query_lower for k in ["show", "display", "list", "get", "find", "fetch", "count", "average", "avg", "sum", "min", "max"]):
        table_name = infer_table_name(query_lower, "users")
        if table_name and table_name != "tables":
            live_cols = {str(r[0]).lower() for r in get_table_columns(table_name)}
            select_expr = "*"
            if "count" in query_lower:
                select_expr = "COUNT(*) AS count"
            elif any(word in query_lower for word in ["maximum", "max"]):
                metric = "age" if "age" in live_cols else "id"
                select_expr = f"MAX({metric}) AS max_{metric}"
            elif any(word in query_lower for word in ["minimum", "min"]):
                metric = "age" if "age" in live_cols else "id"
                select_expr = f"MIN({metric}) AS min_{metric}"
            elif "average" in query_lower or "avg" in query_lower:
                metric = "age" if "age" in live_cols else ("salary" if "salary" in live_cols else None)
                select_expr = f"AVG({metric}) AS average_{metric}" if metric else "AVG(1) AS average_value"
            elif "sum" in query_lower:
                metric = "salary" if "salary" in live_cols else ("age" if "age" in live_cols else None)
                select_expr = f"SUM({metric}) AS sum_{metric}" if metric else "SUM(1) AS sum_value"

            top_clause = ""
            limit_value = extract_limit(query_lower)
            if limit_value and select_expr == "*":
                top_clause = f"TOP {limit_value} "

            where_clause = ""
            where_source = query_lower
            where_match = re.search(r'(?:where|with|having)\s+(.+)', query_lower)
            if where_match:
                where_source = where_match.group(1)
            elif "whose " in query_lower:
                where_source = query_lower.split("whose ", 1)[1]
            where_clause = parse_simple_where(where_source, live_cols)

            order_clause = ""
            sort_col = None
            sort_direction = None

            order_match = re.search(
                r'(?:order by|sort by|sorted by)\s+(\w+)(?:\s+(asc|ascending|desc|descending))?',
                query_lower
            )
            if not order_match:
                order_match = re.search(r'(\w+)\s+(?:in\s+)?(asc|ascending|desc|descending)\s+order', query_lower)
            if order_match:
                sort_col = order_match.group(1).lower()
                direction = order_match.group(2) or "ASC"
                sort_direction = "DESC" if direction.lower().startswith("desc") else "ASC"

            if not sort_col:
                if any(phrase in query_lower for phrase in ["from highest to lowest", "highest to lowest", "descending", "highest first", "largest first"]):
                    sort_direction = "DESC"
                elif any(phrase in query_lower for phrase in ["from lowest to highest", "lowest to highest", "ascending", "lowest first", "smallest first"]):
                    sort_direction = "ASC"
                elif "oldest" in query_lower:
                    sort_col = "age"
                    sort_direction = "DESC"
                elif "youngest" in query_lower:
                    sort_col = "age"
                    sort_direction = "ASC"

                if not sort_col:
                    if "age" in query_lower:
                        sort_col = "age"
                    elif "id" in query_lower:
                        sort_col = "id"
                    elif "name" in query_lower:
                        sort_col = "name"

                if not sort_col and ("latest" in query_lower and ("created_at" in live_cols)):
                    sort_col = "created_at"
                    sort_direction = "DESC"

            if sort_col and (not live_cols or sort_col in live_cols):
                order_clause = f" ORDER BY {sort_col} {sort_direction or 'ASC'}"

            return f"SELECT {top_clause}{select_expr} FROM {table_name}{where_clause}{order_clause};"
    
    # ===== RULE 10: CHECK IF TABLE EXISTS =====
    if 'exist' in query_lower or 'check if' in query_lower:
        table_name = infer_table_name(query_lower)
        if table_name:
            return f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}' AND TABLE_TYPE = 'BASE TABLE';"
    
    # ===== RULE 9: RENAME TABLE =====
    if "rename" in query_lower or ("change" in query_lower and "name" in query_lower and "table" in query_lower):
        # Supported patterns:
        # - "rename table users to app_users"
        # - "rename users to app_users"
        # - "change table name users to app_users"
        rename_patterns = [
            r'rename\s+(?:table\s+)?(\w+)\s+to\s+(\w+)',
            r'change\s+(?:the\s+)?table\s+name\s+(?:from\s+)?(\w+)\s+to\s+(\w+)',
        ]
        for pat in rename_patterns:
            match = re.search(pat, query_lower)
            if match:
                old_name = match.group(1)
                new_name = match.group(2)
                return f"EXEC sp_rename '{old_name}', '{new_name}';"
    
    # ===== RULE 5: TRUNCATE TABLE =====
    if (
        'truncate' in query_lower
        or ('clear' in query_lower and 'table' in query_lower and 'data' in query_lower)
        or ('empty' in query_lower and 'table' in query_lower)
    ):
        table_name = extract_table_name(query_lower)
        if table_name:
            return f"TRUNCATE TABLE {table_name};"

    # ===== RULE 5.5: COMMENT ON TABLE (SQL Server style) =====
    # SQL Server does not support "COMMENT ON TABLE ... IS ...".
    # Use extended properties instead.
    if "comment" in query_lower and "table" in query_lower:
        table_name = None
        # Prefer explicit comment-target patterns first.
        target_match = re.search(r'(?:to|for|on)\s+(?:the\s+)?(\w+)\s+table\b', query_lower)
        if target_match:
            table_name = target_match.group(1)
        if not table_name:
            target_match = re.search(r'table\s+(\w+)\b', query_lower)
            if target_match:
                table_name = target_match.group(1)
        if not table_name:
            table_name = infer_table_name(query_lower)
        if table_name:
            comment_text = None
            # Prefer quoted comment text.
            quoted = re.search(r"'([^']+)'|\"([^\"]+)\"", nl_query)
            if quoted:
                comment_text = (quoted.group(1) or quoted.group(2) or "").strip()
            else:
                # Fallback to phrase after "comment ...".
                comment_match = re.search(r'comment(?:\s+on\s+table\s+\w+)?(?:\s+(?:is|as))?\s+(.+)$', nl_query, flags=re.IGNORECASE)
                if comment_match:
                    comment_text = comment_match.group(1).strip()
                    comment_text = re.sub(
                        r'\s+(?:to|for|on)\s+(?:the\s+)?\w+\s+table\s*$',
                        '',
                        comment_text,
                        flags=re.IGNORECASE,
                    ).strip()
            if not comment_text:
                comment_text = "Table description"
            comment_text = comment_text.replace("'", "''")
            return (
                f"EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'{comment_text}', "
                f"@level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'{table_name}';"
            )
    
    # ===== RULE 4.55: UPDATE ROW DATA (different phrasings) =====
    if any(k in query_lower for k in ["update ", "set ", "change ", "modify "]) and "table" not in query_lower:
        table_name = infer_table_name(query_lower, "users")
        live_cols = {str(r[0]).lower() for r in get_table_columns(table_name)}
        set_source = query_lower
        m_set_source = re.search(r'\bset\b\s+(.+?)(?:\bwhere\b|$)', query_lower)
        if m_set_source:
            set_source = m_set_source.group(1)
        set_pairs = []
        for col in live_cols:
            m = re.search(rf'{col}\s+(?:to|=|as|is)\s+([a-zA-Z0-9_@.\-]+)', set_source)
            if m:
                set_pairs.append(f"{col} = {sql_value(m.group(1))}")
        if not set_pairs:
            # Generic fallback when schema cache is empty/not reachable.
            m_set = re.search(r'(\w+)\s+(?:to|=)\s+([a-zA-Z0-9_@.\-]+)', set_source)
            if m_set:
                set_pairs.append(f"{m_set.group(1).lower()} = {sql_value(m_set.group(2))}")
        # Common fallback: "change age of Ravi to 30"
        fallback = re.search(r'change\s+(\w+)\s+(?:of|for)\s+(\w+)\s+to\s+([a-zA-Z0-9_@.\-]+)', query_lower)
        if fallback:
            col, who, val = fallback.group(1).lower(), fallback.group(2), fallback.group(3)
            if not live_cols or col in live_cols:
                set_pairs = [f"{col} = {sql_value(val)}"]
                if not live_cols or "name" in live_cols:
                    return f"UPDATE {table_name} SET {', '.join(set_pairs)} WHERE name = {sql_value(who)};"
        if set_pairs:
            where_clause = ""
            if "where" in query_lower:
                where_clause = parse_simple_where(query_lower.split("where", 1)[1], live_cols)
            else:
                # "for user X" style
                who = re.search(r'(?:for|of)\s+(?:user\s+)?([a-zA-Z0-9_@.\-]+)', query_lower)
                if who and (not live_cols or "name" in live_cols):
                    where_clause = f" WHERE name = {sql_value(who.group(1))}"
            if not where_clause:
                where_clause = " WHERE 1=1"
            return f"UPDATE {table_name} SET {', '.join(set_pairs)}{where_clause};"

    # ===== RULE 4.5: DELETE ROWS WITH CONDITIONS (edge cases) =====
    if any(word in query_lower for word in ["delete", "remove"]) and (
        "where" in query_lower
        or "named" in query_lower
        or "older than" in query_lower
        or "starts with" in query_lower
        or "ends with" in query_lower
        or "contains" in query_lower
    ):
        table_name = infer_table_name(query_lower, "users")
        live_cols = {str(r[0]).lower() for r in get_table_columns(table_name)}
        where_clause = ""
        if "where" in query_lower:
            where_clause = parse_simple_where(query_lower.split("where", 1)[1], live_cols)
        else:
            named = re.search(r'named\s+([a-zA-Z0-9_@.\-]+)', query_lower)
            if named and (not live_cols or "name" in live_cols):
                where_clause = f" WHERE name = {sql_value(named.group(1))}"
            older = re.search(r'older than\s+(\d+)', query_lower)
            if older and (not live_cols or "age" in live_cols):
                where_clause = f" WHERE age > {older.group(1)}"
        if where_clause:
            return f"DELETE FROM {table_name}{where_clause};"

    # ===== RULE 4: DROP TABLE vs DELETE FROM =====
    if ('drop' in query_lower or 'delete' in query_lower or 'remove' in query_lower):
        # Check for table operations (DROP TABLE or DELETE FROM)
        if 'table' in query_lower and 'column' not in query_lower and 'database' not in query_lower:
            table_name = infer_table_name(query_lower)
            
            # Distinguish between DROP TABLE and DELETE FROM
            # "delete the employees table" → DROP TABLE (remove table)
            # "delete all from employees" or "delete data from employees" → DELETE FROM (remove rows)
            if 'delete' in query_lower and ('all' in query_lower or 'data' in query_lower or 'from' in query_lower or 'rows' in query_lower):
                # DELETE FROM (remove all rows, keep table)
                return f"DELETE FROM {table_name};"
            else:
                # DROP TABLE (remove entire table)
                return f"DROP TABLE {table_name};"
        
        # Check for data deletion operations (DELETE FROM without "table" keyword)
        elif 'delete' in query_lower and ('all' in query_lower or 'data' in query_lower or 'from' in query_lower or 'rows' in query_lower) and 'column' not in query_lower and 'database' not in query_lower:
            table_name = infer_table_name(query_lower)
            return f"DELETE FROM {table_name};"

    # ===== RULE 4.6: INSERT ROW DATA =====
    # Examples:
    # - "add a new user with name Arjun and age 26"
    # - "insert a user named Meena with age 23 into users table"
    # - "insert into users name Ravi age 22"
    if (
        any(phrase in query_lower for phrase in ["add new user", "add a new user", "insert user", "insert into", "add user"])
        or ("insert" in query_lower and "into" in query_lower)
    ):
        table_name = "users"
        table_match = re.search(r'(?:into|to)\s+(\w+)', query_lower)
        if table_match and table_match.group(1) not in ["a", "an", "the", "new", "user"]:
            table_name = table_match.group(1)

        # Parse common attributes
        name_match = re.search(
            r'(?:name|named)\s+(?:is\s+)?([a-zA-Z][a-zA-Z\s\-]*?)(?=\s+(?:with|and|age|into)\b|$)',
            nl_query,
            flags=re.IGNORECASE,
        )
        age_match = re.search(r'age\s+(?:is\s+)?(\d+)', query_lower)

        # Adapt to live schema (if table/columns changed in SSMS)
        live_cols = {str(row[0]).lower() for row in get_table_columns(table_name)} if table_name else set()

        columns = []
        values = []
        if name_match:
            name_value = name_match.group(1).strip().split(" and ")[0].strip()
            name_value_escaped = name_value.replace("'", "''")
            if not live_cols or "name" in live_cols:
                columns.append("name")
                values.append("'" + name_value_escaped + "'")
        if age_match:
            if not live_cols or "age" in live_cols:
                columns.append("age")
                values.append(age_match.group(1))

        if columns:
            return f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});"

        # Generic fallback if fields are not extractable
        return f"INSERT INTO {table_name} DEFAULT VALUES;"
    
    # ===== RULE 7: ALTER TABLE - DROP COLUMN =====
    if ('drop' in query_lower or 'remove' in query_lower or 'delete' in query_lower) and 'column' in query_lower:
        table_name = extract_table_name(query_lower)
        # Extract column name (word after "column")
        col_match = re.search(r'(?:column|field)\s+(\w+)', query_lower)
        col_name = col_match.group(1) if col_match else None
        
        if not col_name:
            # Try to get first non-table word
            words = query_lower.split()
            for i, word in enumerate(words):
                if word in ['from', 'in'] and i + 1 < len(words):
                    col_name = words[i + 1]
                    break
        
        if table_name and col_name:
            return f"ALTER TABLE {table_name} DROP COLUMN {col_name};"
    
    # ===== RULE 6: ALTER TABLE - ADD COLUMN =====
    if 'add' in query_lower and ('column' in query_lower or 'field' in query_lower or 'to' in query_lower):
        # Make sure it's not "add user to table" (which is data operation)
        if 'user' not in query_lower or ('column' in query_lower or 'field' in query_lower):
            table_name = extract_table_name(query_lower)
            
            # Try to extract column name and type more robustly
            col_match = re.search(r'add\s+(?:a\s+)?(?:column\s+)?(\w+)', query_lower)
            if col_match:
                col_name = col_match.group(1)
            else:
                col_match = re.search(r'add\s+(\w+)', query_lower)
                col_name = col_match.group(1) if col_match else None
            
            if table_name and col_name:
                # Determine column type
                col_type = 'VARCHAR(100)'
                if 'int' in query_lower or col_name == 'age' or col_name == 'id':
                    col_type = 'INT'
                elif 'decimal' in query_lower or 'price' in query_lower or 'salary' in query_lower or col_name == 'salary' or col_name == 'price':
                    col_type = 'DECIMAL(10,2)'
                elif 'date' in query_lower or col_name == 'date':
                    col_type = 'DATE'
                elif col_name in ['email', 'password']:
                    col_type = 'VARCHAR(255)'
                elif col_name in ['phone']:
                    col_type = 'VARCHAR(20)'
                elif col_name in ['address', 'description']:
                    col_type = 'VARCHAR(500)'
                
                return f"ALTER TABLE {table_name} ADD {col_name} {col_type};"
    
    # ===== RULE 8: ALTER TABLE - MODIFY COLUMN =====
    if 'modify' in query_lower or 'change' in query_lower or 'alter column' in query_lower:
        table_name = extract_table_name(query_lower)
        
        # Extract column name
        col_match = re.search(r'(?:modify|change)\s+(?:column\s+)?(\w+)', query_lower)
        col_name = col_match.group(1) if col_match else None
        
        if table_name and col_name:
            # Determine new data type
            col_type = 'VARCHAR(255)'
            if 'int' in query_lower:
                col_type = 'INT'
            elif 'decimal' in query_lower or 'price' in query_lower:
                col_type = 'DECIMAL(10,2)'
            elif 'date' in query_lower:
                col_type = 'DATE'
            
            return f"ALTER TABLE {table_name} ALTER COLUMN {col_name} {col_type};"
    
    # ===== RULE 3: CREATE TABLE =====
    if ('create' in query_lower or 'make' in query_lower or 'new' in query_lower) and 'table' in query_lower and 'database' not in query_lower:
        # Extract table name more robustly
        # Patterns: "create table xyz", "make table xyz", "new table xyz", "named xyz"
        table_match = re.search(r'(?:create|make|new)(?:\s+a)?\s+(?:new\s+)?table\s+(?:called|named|as)?\s*(\w+)', query_lower)
        if table_match:
            table_name = table_match.group(1)
        else:
            table_name = extract_table_name(query_lower)
        
        # Guard against malformed names from phrases like "create table with ..."
        if not table_name or table_name in {"with", "where", "and", "or"}:
            table_name = 'new_table'
        
        # Extract columns from query
        columns = extract_columns_from_query(query_lower)
        
        if columns:
            col_definitions = [f"{col[0]} {col[1]}" for col in columns]
            col_str = ", ".join(col_definitions)
        else:
            col_str = "id INT PRIMARY KEY, name VARCHAR(100)"
        
        return f"CREATE TABLE {table_name} ({col_str});"
    
    # ===== RULE 11: CREATE VIEW (basic support) =====
    if "create" in query_lower and "view" in query_lower:
        view_match = re.search(r'create\s+(?:a\s+)?view\s+(\w+)', query_lower)
        source_match = re.search(r'from\s+(\w+)', query_lower)
        if view_match:
            view_name = view_match.group(1)
            source_table = source_match.group(1) if source_match else "users"
            return f"CREATE VIEW {view_name} AS SELECT * FROM {source_table};"

    # ===== RULE 12: DROP VIEW =====
    if "drop" in query_lower and "view" in query_lower:
        view_match = re.search(r'drop\s+(?:the\s+)?view\s+(\w+)', query_lower)
        if view_match:
            return f"DROP VIEW {view_match.group(1)};"

    # Default: Return sentinel comment (caller should not execute)
    return "-- UNSUPPORTED_NL_QUERY"


def clean_sql_output(sql: str) -> str:
    """Clean up generated SQL by removing unnecessary articles and common syntax issues."""
    import re

    if not sql:
        return sql

    sql = sql.strip()

    # Strip fenced code blocks if an LLM ever returns them.
    if sql.startswith("```"):
        sql = re.sub(r"^```[a-zA-Z]*\s*", "", sql)
        sql = re.sub(r"\s*```$", "", sql)

    # Remove articles after DDL verbs (case-insensitive, handles extra spaces):
    # - "CREATE a TABLE ..." -> "CREATE TABLE ..."
    # - "DROP the DATABASE ..." -> "DROP DATABASE ..."
    # - "ALTER TABLE ... ADD a email ..." -> "ALTER TABLE ... ADD email ..."
    sql = re.sub(
        r"\b(CREATE|DROP|ALTER|ADD|MODIFY|TRUNCATE)\s+(a|an|the)\s+",
        r"\1 ",
        sql,
        flags=re.IGNORECASE,
    )

    # Also handle rare ordering mistakes like: "... a TABLE ..." / "... the DATABASE ..."
    sql = re.sub(
        r"\s+(a|an|the)\s+(DATABASE|TABLE|COLUMN)\b",
        r" \2",
        sql,
        flags=re.IGNORECASE,
    )

    # If a CTE starts with WITH, SQL Server requires a leading semicolon if it's not
    # the first token in the batch.
    # e.g. "SELECT 1 WITH cte AS (...) ..." -> ";WITH cte AS (...)".
    for m in re.finditer(r"\bWITH\s+\w+\s+AS\s*\(", sql, flags=re.IGNORECASE):
        # Find last non-whitespace character before this WITH
        j = m.start() - 1
        while j >= 0 and sql[j].isspace():
            j -= 1
        if j >= 0 and sql[j] != ";":
            sql = sql[: m.start()] + "; " + sql[m.start() :]
            break

    # Clean up whitespace (keep semicolons intact).
    sql = re.sub(r"\s+", " ", sql).strip()
    return sql


def is_sql_query(query: str) -> bool:
    """Check if the query is already SQL by looking for SQL keywords and structure.
    
    SQL vs Natural Language Detection:
    - Natural Language: lowercase keywords mixed with regular words
      Example: "create a database called companydb"
    - Actual SQL: uppercase keywords with SQL syntax
      Example: "CREATE DATABASE companydb;" or "SELECT * FROM users;"
    """
    stripped_query = query.strip()
    query_upper = stripped_query.upper()
    
    # SQL keywords that typically start a statement
    sql_keywords = [
        "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP",
        "TRUNCATE", "EXEC", "WITH", "FROM", "WHERE", "JOIN", "GROUP BY", 
        "ORDER BY", "HAVING", "UNION", "EXCEPT", "INTERSECT", "BEGIN", 
        "COMMIT", "ROLLBACK", "DECLARE"
    ]
    
    # Check if it starts with a SQL keyword
    starts_with_sql = any(query_upper.startswith(keyword) for keyword in sql_keywords)
    
    if not starts_with_sql:
        return False
    
    # If starts with SQL keyword, apply additional heuristics to distinguish SQL from NL
    # 1. If starts with LOWERCASE SQL keyword, it's probably natural language
    stripped_lower = stripped_query.lstrip()
    first_word = stripped_lower.split()[0].upper() if stripped_lower else ""
    
    # Check if first word of original query is lowercase
    first_word_lower = stripped_lower.split()[0] if stripped_lower else ""
    if first_word_lower and first_word_lower[0].islower():
        # Starts with lowercase keyword - probably natural language
        return False
    
    # 2. Check for natural language patterns mixed with keywords
    # Natural language often has articles, prepositions, etc.
    natural_language_indicators = ['a ', 'an ', 'the ', 'called ', 'named ', 'to ', 'in ', 'of ']
    
    # If it has SQL structure indicators, it's probably real SQL
    sql_indicators = [';', '(', ')', 'FROM', 'WHERE', '=', ',']
    has_sql_indicators = any(indicator in query_upper for indicator in sql_indicators)
    
    if has_sql_indicators:
        # More likely to be actual SQL
        return True
    
    # If it has natural language patterns, it's probably NL
    for indicator in natural_language_indicators:
        if indicator in query_upper:
            # Has natural language patterns - probably NL
            return False
    
    # Default: if starts with uppercase SQL keyword and has structure, treat as SQL
    return True


# 🔥 AI converts NL → SQL (uses API if available, otherwise mock mode)
def nl_to_sql(nl_query: str) -> str:
    if OPENAI_AVAILABLE:
        # Use real OpenAI
        prompt = f"""
        You are a SQL Server NL→SQL generator. Convert natural language into SQL Server statements.
        
        **CRITICAL: Generate ONLY valid SQL Server syntax.**
        - Output ONLY SQL code (no explanations).
        - Do NOT output `GO` (SSMS-only batch separator).
        - If multiple steps are required (e.g., create db + use + create table + insert + select), output multiple statements separated by semicolons `;`.
        - Avoid unsafe statements (MERGE/GRANT/etc.). Use only: CREATE/DROP/ALTER/TRUNCATE/RENAME, SELECT, INSERT, UPDATE, DELETE, USE.
        - NEVER include articles (a, an, the) as SQL object type tokens (e.g., never `CREATE a TABLE`).
        
        STRICT RULE-BASED MAPPINGS:
        
        0. CREATE DATABASE (NO articles in output):
           Input: "create a database called companydb"
           Output: CREATE DATABASE companydb;
           ❌ WRONG: CREATE a DATABASE companydb;
           
        0. DROP DATABASE (NO articles in output):
           Input: "drop the database olddb"
           Output: DROP DATABASE olddb;
           ❌ WRONG: DROP the DATABASE olddb;
        
        1. DESCRIBE/SHOW TABLE STRUCTURE:
           "describe users" → SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'users' ORDER BY ORDINAL_POSITION;
        
        2. LIST ALL TABLES:
           "show all tables" → SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';
        
        3. CREATE TABLE (NO articles):
           "create a table with id, name" → CREATE TABLE new_table (id INT PRIMARY KEY, name VARCHAR(100));
           
        4. DROP TABLE (NO articles):
           "drop the users table" → DROP TABLE users;
           "delete the users table" → DROP TABLE users;
           
        4.5. DELETE FROM (remove all rows):
           "delete all data from users" → DELETE FROM users;
           "delete all from users table" → DELETE FROM users;
           "delete rows from users" → DELETE FROM users;

        4.6. INSERT INTO (add rows):
           "add a new user with name Arjun and age 26" → INSERT INTO users (name, age) VALUES ('Arjun', 26);
           "insert into users name Ravi age 22" → INSERT INTO users (name, age) VALUES ('Ravi', 22);

        5. TRUNCATE TABLE:
           "empty users table" → TRUNCATE TABLE users;

        6. RENAME TABLE:
           "rename users to app_users" → EXEC sp_rename 'users', 'app_users';

        7. COMMENT ON TABLE (SQL Server):
           "add comment 'customer master table' to users table" → EXEC sys.sp_addextendedproperty ...
        
        RULES:
        - Extract table and column names accurately
        - Use INFORMATION_SCHEMA for schema queries
        - Support INSERT INTO for row creation when user asks to add/create a record
        - Support SQL Server table comments via sp_addextendedproperty
        - Return ONLY valid SQL, no text, no explanations
        - NO articles (a, an, the) in the SQL output
        
        Query: {nl_query}
        """

        response = get_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a SQL Server NL2SQL expert. Generate ONLY valid SQL Server syntax. Support DDL plus SELECT/INSERT/UPDATE/DELETE for data operations. NEVER include articles (a, an, the) as SQL object type tokens. Return only SQL code, no text, no explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        sql = response.choices[0].message.content.strip()
        # Clean up the SQL to remove articles
        sql = clean_sql_output(sql)
        
        # Ensure it's SQL by checking if it starts with SQL keywords
        if not is_sql_query(sql):
            # If not SQL, fall back to mock (mock already returns clean SQL)
            sql = nl_to_sql_mock(nl_query)
        return sql
    else:
        # Use mock mode (already returns clean SQL)
        return nl_to_sql_mock(nl_query)


# API
@app.post("/api/query/text")
def execute_query(request: QueryRequest):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if is_sql_query(request.query):
            sql_query_raw = request.query
        else:
            sql_query_raw = nl_to_sql(request.query)

        # Cleanup (also strips accidental markdown fences, fixes articles, etc.)
        sql_query_clean = clean_sql_output(sql_query_raw)
        sql_query_clean = strip_go(sql_query_clean)

        print("Generated SQL:", sql_query_clean)

        # Do not execute sentinel/comment-only outputs from NL2SQL.
        stripped = sql_query_clean.strip()
        if not stripped or stripped.startswith("--"):
            return {
                "sql": sql_query_clean,
                "result": "-- Unsupported query. Supported: CREATE/DROP DATABASE, LIST TABLES, DESCRIBE TABLE, CREATE/DROP/ALTER/TRUNCATE/RENAME TABLE, COMMENT ON TABLE (via extended properties), CREATE/DROP VIEW, SELECT/INSERT/UPDATE/DELETE on tables with filters/sorting/aggregations.",
            }

        statements = split_sql_statements(sql_query_clean)
        if not statements:
            return {"sql": sql_query_clean, "result": "-- No executable SQL statements found"}

        results: list[dict] = []

        def execute_one(stmt: str):
            stmt_upper = stmt.strip().upper()
            original_autocommit = conn.autocommit
            try:
                # Autocommit for database / table DDL, USE, and safe EXEC helpers.
                if any(
                    stmt_upper.startswith(prefix)
                    for prefix in [
                        "CREATE DATABASE",
                        "DROP DATABASE",
                        "CREATE TABLE",
                        "DROP TABLE",
                        "ALTER TABLE",
                        "TRUNCATE TABLE",
                        "USE ",
                        "EXEC ",
                        "EXECUTE ",
                        "CREATE VIEW",
                        "DROP VIEW",
                    ]
                ):
                    conn.autocommit = True

                cursor.execute(stmt)

                if stmt_upper.startswith("SELECT"):
                    columns = [col[0] for col in cursor.description] if cursor.description else []
                    rows = cursor.fetchall() if columns else []
                    return [dict(zip(columns, row)) for row in rows]

                # For non-SELECT with autocommit False, commit explicitly.
                if not conn.autocommit:
                    conn.commit()
                return "OK"
            except Exception as e:
                if not conn.autocommit:
                    conn.rollback()
                raise e
            finally:
                conn.autocommit = original_autocommit

        # Validate + execute sequentially (supports multi-step workflows).
        for stmt in statements:
            ok, reason = validate_statement(conn, stmt)
            if not ok:
                blocked_entry = {"sql": stmt, "result": f"-- Blocked: {reason}"}
                if len(statements) == 1 and not results:
                    return {"sql": sql_query_clean, "result": f"-- Validation failed: {reason}"}
                return {
                    "sql": sql_query_clean,
                    "result": f"-- Validation failed: {reason}",
                    "statements": results + [blocked_entry],
                }

            try:
                res = execute_one(stmt)
                results.append({"sql": stmt, "result": res})
            except Exception as e:
                error_msg = f"Execution Error: {str(e)}"
                print(f"ERROR: {error_msg}")
                error_entry = {"sql": stmt, "result": f"-- {error_msg}"}
                if len(statements) == 1 and not results:
                    return {"sql": sql_query_clean, "result": f"-- {error_msg}"}
                return {
                    "sql": sql_query_clean,
                    "result": f"-- {error_msg}",
                    "statements": results + [error_entry],
                }

        if len(results) == 1:
            return {"sql": sql_query_clean, "result": results[0]["result"]}

        return {"sql": sql_query_clean, "result": results[-1]["result"], "statements": results}

    except HTTPException:
        # Re-raise HTTPExceptions
        raise
    except Exception as e:
        error_msg = f"Unexpected Error: {str(e)}"
        print(f"ERROR: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

    finally:
        try:
            conn.close()
        except:
            pass
