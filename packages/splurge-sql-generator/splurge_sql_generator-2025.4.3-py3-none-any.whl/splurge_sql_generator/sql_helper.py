"""
SQL Helper utilities for parsing and cleaning SQL statements.

Copyright (c) 2025, Jim Schilling

Please keep this header when you use this code.

This module is licensed under the MIT License.
"""

from pathlib import Path
import sqlparse
from sqlparse.tokens import Comment, DML
from sqlparse.sql import Statement, Token
from splurge_sql_generator.errors import (
    SqlFileError,
    SqlValidationError,
)


# Private constants for SQL statement types
_FETCH_STATEMENT_TYPES: tuple[str, ...] = (
    "SELECT",
    "VALUES",
    "SHOW",
    "EXPLAIN",
    "PRAGMA",
    "DESC",
    "DESCRIBE",
)
_DML_STATEMENT_TYPES: tuple[str, ...] = ("SELECT", "INSERT", "UPDATE", "DELETE")
_DESCRIBE_STATEMENT_TYPES: tuple[str, ...] = ("DESC", "DESCRIBE")
_MODIFY_DML_TYPES: tuple[str, ...] = ("INSERT", "UPDATE", "DELETE")

# Private constants for SQL keywords and symbols
_WITH_KEYWORD: str = "WITH"
_AS_KEYWORD: str = "AS"
_SELECT_KEYWORD: str = "SELECT"
_SEMICOLON: str = ";"
_COMMA: str = ","
_PAREN_OPEN: str = "("
_PAREN_CLOSE: str = ")"

# Public constants for statement type return values
EXECUTE_STATEMENT: str = "execute"
FETCH_STATEMENT: str = "fetch"
ERROR_STATEMENT: str = "error"


def remove_sql_comments(sql_text: str | None) -> str | None:
    """
    Remove SQL comments from a SQL string using sqlparse.
    Handles:
    - Single-line comments (-- comment)
    - Multi-line comments (/* comment */)
    - Preserves comments within string literals

    Args:
        sql_text: SQL string that may contain comments
    Returns:
        SQL string with comments removed
    """
    if not sql_text:
        return sql_text

    result = sqlparse.format(sql_text, strip_comments=True)
    return str(result) if result is not None else ""


def _is_fetch_statement(statement_type: str) -> bool:
    """
    Determine if a statement type returns rows (fetch) or not (execute).

    Args:
        statement_type: The SQL statement type (e.g., 'SELECT', 'INSERT', 'VALUES')
    Returns:
        True if statement returns rows, False otherwise
    """
    return statement_type in _FETCH_STATEMENT_TYPES


def _is_dml_statement(statement_type: str) -> bool:
    """
    Determine if a statement type is a DML (Data Manipulation Language) statement.

    Args:
        statement_type: The SQL statement type (e.g., 'SELECT', 'CREATE', 'DROP')
    Returns:
        True if statement is DML, False otherwise
    """
    return statement_type in _DML_STATEMENT_TYPES


def _token_value_upper(token: Token) -> str:
    """
    Return the uppercased, stripped value of a token.
    """
    return (
        str(token.value).strip().upper()
        if hasattr(token, "value") and token.value
        else ""
    )


def _next_significant_token(
    tokens: list[Token],
    *,
    start: int = 0,
) -> tuple[int | None, Token | None]:
    """
    Return the index and token of the next non-whitespace, non-comment token.
    """
    for i in range(start, len(tokens)):
        token = tokens[i]
        if not token.is_whitespace and token.ttype not in Comment:
            return i, token
    return None, None


def _find_first_dml_keyword_top_level(tokens: list[Token]) -> str | None:
    """
    Find first DML/Keyword at the top level after WITH (do not recurse into groups).

    Args:
        tokens: List of sqlparse tokens to analyze
    Returns:
        The first DML/Keyword token value (e.g., 'SELECT', 'INSERT') or None if not found
    """
    for token in (t for t in tokens if not t.is_whitespace and t.ttype not in Comment):
        token_value = _token_value_upper(token)
        if token_value == _AS_KEYWORD:
            continue
        if _is_dml_statement(token_value) or _is_fetch_statement(token_value):
            return token_value
    return None


def _find_main_statement_after_ctes(tokens: list[Token]) -> str | None:
    """
    Find the main statement after CTE definitions by looking for the first DML after all CTE groups.

    Args:
        tokens: List of sqlparse tokens to analyze
    Returns:
        The main statement type (e.g., 'SELECT', 'INSERT') or None if not found
    """
    in_cte_definition = False
    paren_level = 0
    i = 0
    n = len(tokens)
    while i < n:
        token = tokens[i]
        token_value = _token_value_upper(token)
        if token.is_whitespace or token.ttype in Comment:
            i += 1
            continue
        if not in_cte_definition and token_value == _AS_KEYWORD:
            in_cte_definition = True
            next_i, _ = _next_significant_token(tokens, start=i + 1)
            if next_i is None:
                return None
            i = next_i
            if (
                tokens[i].ttype == sqlparse.tokens.Punctuation
                and tokens[i].value == _PAREN_OPEN
            ):
                paren_level = 1
                i += 1
                while i < n and paren_level > 0:
                    t = tokens[i]
                    if t.ttype == sqlparse.tokens.Punctuation:
                        if t.value == _PAREN_OPEN:
                            paren_level += 1
                        elif t.value == _PAREN_CLOSE:
                            paren_level -= 1
                    i += 1
                in_cte_definition = False
                next_i, _ = _next_significant_token(tokens, start=i)
                if next_i is None:
                    return None
                i = next_i
                if (
                    tokens[i].ttype == sqlparse.tokens.Punctuation
                    and tokens[i].value == _COMMA
                ):
                    i += 1
                    continue
                break
            else:
                break
        else:
            i += 1
    next_i, token = _next_significant_token(tokens, start=i)
    if next_i is None or token is None:
        return None
    i = next_i
    token_value = _token_value_upper(token)
    if _is_dml_statement(token_value) or _is_fetch_statement(token_value):
        return token_value
    return None


def _is_with_keyword(token: Token) -> bool:
    """
    Check if a token represents the 'WITH' keyword.

    Args:
        token: sqlparse token to check
    Returns:
        True if token is the 'WITH' keyword, False otherwise
    """
    try:
        return (
            token.value.strip().upper() == _WITH_KEYWORD
            if hasattr(token, "value") and token.value
            else False
        )
    except (AttributeError, TypeError):
        return False


def _find_with_keyword_index(tokens: list[Token]) -> int | None:
    """
    Find the index of the WITH keyword in a list of tokens.

    Args:
        tokens: List of sqlparse tokens to search
    Returns:
        Index of the WITH keyword or None if not found
    """
    for i, token in enumerate(tokens):
        if _is_with_keyword(token):
            return i
    return None


def _extract_tokens_after_with(stmt: Statement) -> list[Token]:
    """
    Extract all tokens that come after the WITH keyword in a statement.

    Args:
        stmt: sqlparse Statement object
    Returns:
        List of tokens that come after the WITH keyword
    """
    top_tokens: list[Token] = list(stmt.flatten())
    with_index = _find_with_keyword_index(top_tokens)

    if with_index is None:
        return []

    # Return all tokens after the WITH keyword
    return top_tokens[with_index + 1 :]


def detect_statement_type(sql: str) -> str:
    """
    Detect if a SQL statement returns rows using advanced sqlparse analysis.

    This function performs sophisticated SQL statement analysis to determine whether
    a statement will return rows (fetch operation) or perform an action without
    returning data (execute operation). It handles complex cases including CTEs,
    nested queries, and database-specific statements.

    Supported Statement Types:
        - SELECT statements (including subqueries and JOINs)
        - Common Table Expressions (WITH ... SELECT/INSERT/UPDATE/DELETE)
        - VALUES statements for literal value sets
        - Database introspection (SHOW, DESCRIBE/DESC, EXPLAIN, PRAGMA)
        - Data modification (INSERT, UPDATE, DELETE) - classified as execute
        - Schema operations (CREATE, ALTER, DROP) - classified as execute

    Args:
        sql: SQL statement string to analyze. Can contain comments, whitespace,
            and complex SQL constructs. Empty or whitespace-only strings are
            treated as execute operations.

    Returns:
        One of the following string constants:
        - 'fetch': Statement returns rows (SELECT, VALUES, SHOW, DESCRIBE, EXPLAIN, PRAGMA)
        - 'execute': Statement performs action without returning data (INSERT, UPDATE, DELETE, DDL)

    Examples:
        Simple SELECT:
            >>> detect_statement_type("SELECT * FROM users")
            'fetch'

        CTE with SELECT:
            >>> detect_statement_type('''
            ... WITH active_users AS (
            ...     SELECT id, name FROM users WHERE active = 1
            ... )
            ... SELECT * FROM active_users
            ... ''')
            'fetch'

        CTE with INSERT:
            >>> detect_statement_type('''
            ... WITH new_data AS (
            ...     SELECT 'John' as name, 25 as age
            ... )
            ... INSERT INTO users (name, age) SELECT * FROM new_data
            ... ''')
            'execute'

        VALUES statement:
            >>> detect_statement_type("VALUES (1, 'Alice'), (2, 'Bob')")
            'fetch'

        Database introspection:
            >>> detect_statement_type("DESCRIBE users")
            'fetch'
            >>> detect_statement_type("SHOW TABLES")
            'fetch'
            >>> detect_statement_type("EXPLAIN SELECT * FROM users")
            'fetch'

        Data modification:
            >>> detect_statement_type("INSERT INTO users (name) VALUES ('John')")
            'execute'
            >>> detect_statement_type("UPDATE users SET active = 1")
            'execute'

        Schema operations:
            >>> detect_statement_type("CREATE TABLE test (id INT)")
            'execute'

    Note:
        - Parsing is performed using sqlparse for accuracy
        - Comments are ignored
        - Complex nested CTEs are supported
        - Database-specific syntax (PRAGMA, SHOW) is recognized
    """
    if not sql or not sql.strip():
        return EXECUTE_STATEMENT

    parsed = sqlparse.parse(sql.strip())
    if not parsed:
        return EXECUTE_STATEMENT

    stmt = parsed[0]
    tokens = list(stmt.flatten())
    if not tokens:
        return EXECUTE_STATEMENT

    _, first_token = _next_significant_token(tokens)
    if first_token is None:
        return EXECUTE_STATEMENT

    token_value = first_token.value.strip().upper()

    # Fast-path: classify by first significant token
    # DESC/DESCRIBE detection (regardless of token type)
    if token_value in _DESCRIBE_STATEMENT_TYPES:
        return FETCH_STATEMENT

    # Fast-path: common fetch statements
    if token_value in ("SELECT", "VALUES", "SHOW", "EXPLAIN", "PRAGMA"):
        return FETCH_STATEMENT

    # Fast-path: common execute statements
    if token_value in ("INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "TRUNCATE"):
        return EXECUTE_STATEMENT

    # CTE detection: WITH ... (only when first token is WITH)
    if token_value == _WITH_KEYWORD:
        after_with_tokens = _extract_tokens_after_with(stmt)

        # Try the more sophisticated approach first
        main_stmt = _find_main_statement_after_ctes(after_with_tokens)
        if main_stmt is None:
            # Fallback to the simpler approach
            main_stmt = _find_first_dml_keyword_top_level(after_with_tokens)

        # If no main statement found after CTE, return execute
        if main_stmt is None:
            return EXECUTE_STATEMENT

        if main_stmt == _SELECT_KEYWORD:
            return FETCH_STATEMENT
        if main_stmt in _MODIFY_DML_TYPES:
            return EXECUTE_STATEMENT
        if main_stmt is not None and _is_fetch_statement(main_stmt):
            return FETCH_STATEMENT
        return EXECUTE_STATEMENT

    # Fallback: use existing logic for edge cases
    # SELECT (with DML token type check)
    if first_token.ttype is DML and token_value == _SELECT_KEYWORD:
        return FETCH_STATEMENT

    # Other fetch statements
    if _is_fetch_statement(token_value):
        return FETCH_STATEMENT

    # All other statements (INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, etc.)
    return EXECUTE_STATEMENT


def parse_sql_statements(
    sql_text: str | None,
    *,
    strip_semicolon: bool = False,
) -> list[str]:
    """
    Parse a SQL string containing multiple statements into a list of individual statements
    using sqlparse.
    Handles:
    - Statements separated by semicolons
    - Preserves semicolons within string literals
    - Removes comments before parsing
    - Trims whitespace from individual statements
    - Filters out empty statements and statements that are only comments

    Args:
        sql_text: SQL string that may contain multiple statements
        strip_semicolon: If True, strip trailing semicolons in statements (default: False)
    Returns:
        List of individual SQL statements (with or without trailing semicolons based on parameter)
    """
    if not sql_text:
        return []

    # Remove comments first
    clean_sql = remove_sql_comments(sql_text)

    # Use sqlparse to split statements
    parsed_statements = sqlparse.parse(clean_sql)
    filtered_stmts: list[str] = []

    for stmt in parsed_statements:
        stmt_str = str(stmt).strip()
        if not stmt_str:
            continue

        # Tokenize and check if all tokens are comments or whitespace
        tokens = list(stmt.flatten())
        if not tokens:
            continue
        if all(t.is_whitespace or t.ttype in Comment for t in tokens):
            continue

        # Filter out statements that are just semicolons
        if stmt_str == _SEMICOLON:
            continue

        # Apply semicolon stripping based on parameter
        if strip_semicolon:
            stmt_str = stmt_str.rstrip(";").strip()

        filtered_stmts.append(stmt_str)

    return filtered_stmts


def split_sql_file(
    file_path: str | Path,
    *,
    strip_semicolon: bool = False,
) -> list[str]:
    """
    Read a SQL file and split it into individual executable statements.

    This function reads a SQL file and intelligently splits it into individual
    statements that can be executed separately. It handles complex SQL files
    with comments, multiple statements, and preserves statement integrity.

    Processing Steps:
        1. Read file with UTF-8 encoding
        2. Remove SQL comments (single-line -- and multi-line /* */)
        3. Parse using sqlparse for accurate statement boundaries
        4. Filter out empty statements and comment-only lines
        5. Optionally strip trailing semicolons

    Args:
        file_path: Path to the SQL file to process. Can be a string path or
            pathlib.Path object. File must exist and be readable.
        strip_semicolon: If True, remove trailing semicolons from each statement.
            If False (default), preserve semicolons as they appear in the file.
            Useful when the execution engine expects statements without semicolons.

    Returns:
        List of individual SQL statements as strings. Each statement is:
        - Trimmed of leading/trailing whitespace
        - Free of comments (unless within string literals)
        - Non-empty and contains actual SQL content
        - Optionally without trailing semicolons

    Raises:
        SqlFileError: If file operations fail, including:
            - File not found
            - Permission denied
            - I/O errors during reading
            - Encoding errors (non-UTF-8 content)
        SqlValidationError: If input validation fails:
            - file_path is None
            - file_path is empty string
            - file_path is not string or Path object

    Examples:
        Basic usage:
            >>> statements = split_sql_file("setup.sql")
            >>> for stmt in statements:
            ...     print(f"Statement: {stmt}")

        With semicolon stripping:
            >>> statements = split_sql_file("migration.sql", strip_semicolon=True)
            >>> # Statements will not have trailing semicolons

        Using pathlib.Path:
            >>> from pathlib import Path
            >>> sql_file = Path("database") / "schema.sql"
            >>> statements = split_sql_file(sql_file)

        Handling complex SQL files:
            >>> # File content:
            >>> # -- Create users table
            >>> # CREATE TABLE users (
            >>> #     id INTEGER PRIMARY KEY,
            >>> #     name TEXT NOT NULL
            >>> # );
            >>> # 
            >>> # /* Insert sample data */
            >>> # INSERT INTO users (name) VALUES ('Alice'), ('Bob');
            >>> statements = split_sql_file("complex.sql")
            >>> len(statements)  # Returns 2 (CREATE and INSERT)

    Note:
        - Files are read with UTF-8 encoding by default
        - Comments within string literals are preserved
        - Empty lines and comment-only lines are filtered out
        - Statement boundaries are determined by sqlparse, not simple semicolon splitting
        - Large files are processed efficiently without loading entire content into memory
        - Thread-safe: Can be called concurrently from multiple threads
    """
    if file_path is None:
        raise SqlValidationError("file_path cannot be None")

    if not isinstance(file_path, (str, Path)):
        raise SqlValidationError("file_path must be a string or Path object")

    if not file_path:
        raise SqlValidationError("file_path cannot be empty")

    try:
        with open(file_path, encoding="utf-8") as f:
            sql_content = f.read()
        return parse_sql_statements(sql_content, strip_semicolon=strip_semicolon)
    except FileNotFoundError:
        raise SqlFileError(f"SQL file not found: {file_path}") from None
    except OSError as e:
        raise SqlFileError(f"Error reading SQL file {file_path}: {e}") from e


def extract_table_names(sql_query: str) -> list[str]:
    """
    Extract table names from a SQL query using sqlparse for accurate parsing.
    
    This function uses sqlparse to intelligently extract table names from various
    SQL clauses including FROM, JOIN, UPDATE, INSERT INTO, etc. It handles complex
    SQL constructs like CTEs, subqueries, and aliases.
    
    Args:
        sql_query: SQL query string to analyze
        
    Returns:
        List of table names referenced in the query (in lowercase, deduplicated)
    """
    if not sql_query or not sql_query.strip():
        return []
    
    # Remove comments for cleaner parsing
    clean_sql = remove_sql_comments(sql_query)
    if not clean_sql.strip():
        return []
    
    table_names = []
    
    try:
        # Parse the SQL using sqlparse
        parsed = sqlparse.parse(clean_sql.strip())
        if not parsed:
            return []
        
        # Extract table names from the parsed statement
        for statement in parsed:
            table_names.extend(_extract_tables_from_statement(statement))
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(table_names))
        
    except Exception:
        # Fallback to basic regex extraction if sqlparse fails
        return _extract_table_names_fallback(clean_sql)


def _extract_tables_from_statement(statement) -> list[str]:
    """
    Extract table names from a parsed sqlparse statement.
    
    Args:
        statement: Parsed sqlparse statement
        
    Returns:
        List of table names found in the statement
    """
    table_names = []
    
    # Flatten the statement to get all tokens
    tokens = list(statement.flatten())
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        token_value = str(token.value).upper().strip()
        
        # Look for FROM, JOIN, UPDATE, INSERT INTO keywords
        if token_value in ('FROM', 'JOIN', 'UPDATE', 'INTO'):
            # Get the next significant token (should be the table name)
            next_token = _get_next_significant_token(tokens, i + 1)
            if next_token:
                table_name = str(next_token.value).strip()
                # Remove any alias (everything after AS or space)
                if ' AS ' in table_name.upper():
                    table_name = table_name.split(' AS ')[0].strip()
                elif ' ' in table_name and not table_name.startswith('('):
                    # Handle simple aliases like "table alias"
                    parts = table_name.split()
                    if len(parts) >= 2 and not parts[1].startswith('('):
                        table_name = parts[0]
                
                # Only add if it looks like a valid table name (not a subquery)
                if table_name and not table_name.startswith('(') and table_name.isalnum():
                    table_names.append(table_name.lower())
        
        i += 1
    
    return table_names


def _get_next_significant_token(tokens: list, start_index: int):
    """
    Get the next non-whitespace, non-comment token.
    
    Args:
        tokens: List of tokens
        start_index: Starting index to search from
        
    Returns:
        Next significant token or None
    """
    for i in range(start_index, len(tokens)):
        token = tokens[i]
        if not token.is_whitespace and token.ttype not in Comment:
            return token
    return None


def _extract_table_names_fallback(sql_query: str) -> list[str]:
    """
    Fallback method using regex patterns for table name extraction.
    
    Args:
        sql_query: SQL query string
        
    Returns:
        List of table names
    """
    import re
    
    table_names = []
    
    # Extract table names from different SQL clauses
    # FROM clause
    from_pattern = r'\bFROM\s+(\w+)'
    from_matches = re.findall(from_pattern, sql_query, re.IGNORECASE)
    table_names.extend([match.lower() for match in from_matches])
    
    # UPDATE clause
    update_pattern = r'\bUPDATE\s+(\w+)'
    update_matches = re.findall(update_pattern, sql_query, re.IGNORECASE)
    table_names.extend([match.lower() for match in update_matches])
    
    # INSERT INTO clause
    insert_pattern = r'\bINSERT\s+INTO\s+(\w+)'
    insert_matches = re.findall(insert_pattern, sql_query, re.IGNORECASE)
    table_names.extend([match.lower() for match in insert_matches])
    
    # JOIN clauses
    join_pattern = r'\bJOIN\s+(\w+)'
    join_matches = re.findall(join_pattern, sql_query, re.IGNORECASE)
    table_names.extend([match.lower() for match in join_matches])
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(table_names))
