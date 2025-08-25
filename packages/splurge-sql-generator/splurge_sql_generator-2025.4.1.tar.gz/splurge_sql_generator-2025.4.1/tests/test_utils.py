"""
Test utilities for splurge-sql-generator tests.

This module provides common helper functions and fixtures used across multiple test files.
"""

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator


@contextmanager
def temp_sql_files(
    sql_content: str,
    schema_content: str | None = None,
    *,
    sql_suffix: str = ".sql"
) -> Generator[tuple[str, str | None], None, None]:
    """
    Context manager for creating temporary SQL and schema files.
    
    Args:
        sql_content: Content for the SQL file
        schema_content: Content for the schema file (optional)
        sql_suffix: Suffix for the SQL file (default: ".sql")
        
    Yields:
        Tuple of (sql_file_path, schema_file_path)
        schema_file_path will be None if schema_content is None
        
    Example:
        with temp_sql_files(sql, schema) as (sql_file, schema_file):
            code = generator.generate_class(sql_file)
    """
    # Create SQL file
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=sql_suffix) as f:
        f.write(sql_content)
        sql_fname = f.name
    
    schema_fname = None
    if schema_content is not None:
        # Create schema file
        schema_fname = Path(sql_fname).with_suffix('.schema')
        with open(schema_fname, "w", encoding="utf-8") as f:
            f.write(schema_content)
    
    try:
        yield sql_fname, schema_fname
    finally:
        # Cleanup
        if os.path.exists(sql_fname):
            os.remove(sql_fname)
        if schema_fname and os.path.exists(schema_fname):
            os.remove(schema_fname)


@contextmanager
def temp_multiple_sql_files(
    sql_files: list[tuple[str, str]]
) -> Generator[list[tuple[str, str]], None, None]:
    """
    Context manager for creating multiple temporary SQL and schema files.
    
    Args:
        sql_files: List of (sql_content, schema_content) tuples
        
    Yields:
        List of (sql_file_path, schema_file_path) tuples
        
    Example:
        files = [("# ClassA\\n#get_a\\nSELECT 1;", "CREATE TABLE a (id INT);")]
        with temp_multiple_sql_files(files) as file_paths:
            result = generator.generate_multiple_classes([f[0] for f in file_paths])
    """
    file_paths = []
    
    try:
        for sql_content, schema_content in sql_files:
            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".sql") as f:
                f.write(sql_content)
                sql_fname = f.name
            
            schema_fname = Path(sql_fname).with_suffix('.schema')
            with open(schema_fname, "w", encoding="utf-8") as f:
                f.write(schema_content)
            
            file_paths.append((sql_fname, schema_fname))
        
        yield file_paths
        
    finally:
        # Cleanup all files
        for sql_fname, schema_fname in file_paths:
            if os.path.exists(sql_fname):
                os.remove(sql_fname)
            if os.path.exists(schema_fname):
                os.remove(schema_fname)


def create_sql_with_schema(tmp_path, filename: str, sql_content: str, schema_content: str | None = None) -> tuple[Path, Path]:
    """
    Helper function to create SQL file with corresponding schema file.
    
    Args:
        tmp_path: pytest tmp_path fixture
        filename: Name of the SQL file (e.g., "test.sql")
        sql_content: Content for the SQL file
        schema_content: Content for the schema file (optional, uses create_basic_schema if None)
        
    Returns:
        Tuple of (sql_file_path, schema_file_path)
        
    Example:
        sql_file, schema_file = create_sql_with_schema(tmp_path, "test.sql", "# TestClass\\nSELECT 1;")
    """
    sql_file = tmp_path / filename
    sql_file.write_text(sql_content)
    
    # Create schema file
    schema_file = tmp_path / f"{Path(filename).stem}.schema"
    if schema_content is None:
        schema_content = create_basic_schema()
    schema_file.write_text(schema_content)
    
    return sql_file, schema_file


def create_basic_schema(table_name: str = "users") -> str:
    """
    Create a basic schema for testing.
    
    Args:
        table_name: Name of the table (default: "users")
        
    Returns:
        Basic CREATE TABLE statement
    """
    return f"""CREATE TABLE {table_name} (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE
);
"""


def create_dummy_schema(table_name: str = "dummy") -> str:
    """
    Create a minimal dummy schema for testing.
    
    Args:
        table_name: Name of the table (default: "dummy")
        
    Returns:
        Minimal CREATE TABLE statement
    """
    return f"""CREATE TABLE {table_name} (
    id INTEGER PRIMARY KEY
);
"""


def create_complex_schema() -> str:
    """
    Create a complex schema with multiple tables for testing joins and complex queries.
    
    Returns:
        Multi-table CREATE TABLE statements
    """
    return """CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    status TEXT NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    order_date DATE,
    total_amount DECIMAL(10,2)
);

CREATE TABLE order_details (
    id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_name TEXT,
    quantity INTEGER,
    price DECIMAL(10,2)
);
"""


def assert_generated_code_structure(code: str, class_name: str, method_names: list[str]) -> None:
    """
    Assert that generated code has the expected structure.
    
    Args:
        code: Generated Python code
        class_name: Expected class name
        method_names: List of expected method names
        
    Raises:
        AssertionError: If structure doesn't match expectations
    """
    assert f"class {class_name}" in code, f"Class {class_name} not found in generated code"
    
    for method_name in method_names:
        assert f"def {method_name}(" in code, f"Method {method_name} not found in generated code"
        assert "@classmethod" in code, "Generated methods should be class methods"
    
    # Check for required imports
    required_imports = [
        "Any",  # Check if Any is imported (could be in various forms)
        "from sqlalchemy import text",
        "Connection",  # Check if Connection is imported
        "Row",  # Check if Row is imported
        "import logging"
    ]
    
    for import_stmt in required_imports:
        assert import_stmt in code, f"Required import missing: {import_stmt}"


def assert_method_parameters(code: str, method_name: str, expected_params: list[str]) -> None:
    """
    Assert that a method has the expected parameters with Any type annotations.
    
    Args:
        code: Generated Python code
        method_name: Name of the method to check
        expected_params: List of expected parameter names (excluding 'connection')
        
    Raises:
        AssertionError: If parameters don't match expectations
    """
    # All methods should have connection parameter
    assert f"def {method_name}(" in code
    assert "connection: Connection" in code
    
    # Check for expected parameters with Any type
    for param in expected_params:
        assert f"{param}: Any" in code, f"Parameter {param}: Any not found for method {method_name}"
