"""Table processing and export utilities."""

from __future__ import annotations

import csv
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from kreuzberg._types import TableData


def export_table_to_csv(table: TableData, separator: str = ",") -> str:
    r"""Export a TableData object to CSV/TSV format.

    Args:
        table: TableData object containing DataFrame
        separator: Field separator ("," for CSV, "\t" for TSV)

    Returns:
        String representation in CSV/TSV format
    """
    if "df" not in table or table["df"] is None:
        return ""

    # Use pandas to_csv() direct string return instead of StringIO
    csv_output = table["df"].to_csv(sep=separator, index=False, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    return str(csv_output).strip()


def export_table_to_tsv(table: TableData) -> str:
    """Export a TableData object to TSV format.

    Args:
        table: TableData object containing DataFrame

    Returns:
        String representation in TSV format
    """
    return export_table_to_csv(table, separator="\t")


def enhance_table_markdown(table: TableData) -> str:
    """Generate enhanced markdown table with better formatting.

    Args:
        table: TableData object

    Returns:
        Enhanced markdown table string
    """
    if "df" not in table or table["df"] is None:
        return table.get("text", "")

    df = table["df"]

    if df.empty:
        return table.get("text", "")

    # Create enhanced markdown with proper alignment
    lines = []

    # Header row
    headers = [str(col).strip() for col in df.columns]
    lines.append("| " + " | ".join(headers) + " |")

    # Separator row with alignment hints
    lines.append(_generate_separator_row(df))

    # Analyze float columns to determine formatting strategy
    float_col_formatting = _analyze_float_columns(df)

    # Data rows with proper formatting
    for _, row in df.iterrows():
        formatted_row = _format_table_row(row, df, float_col_formatting)
        lines.append("| " + " | ".join(formatted_row) + " |")

    return "\n".join(lines)


def _generate_separator_row(df: Any) -> str:
    """Generate separator row with proper alignment hints."""
    separators = []
    for col in df.columns:
        # Check if column contains mostly numbers for right alignment
        if df[col].dtype in ["int64", "float64"] or _is_numeric_column(df[col]):
            separators.append("---:")  # Right align numbers
        else:
            separators.append("---")  # Left align text
    return "| " + " | ".join(separators) + " |"


def _analyze_float_columns(df: Any) -> dict[str, str]:
    """Analyze float columns to determine formatting strategy."""
    float_col_formatting = {}
    for col in df.columns:
        if str(df[col].dtype) == "float64":
            non_null_values = df[col].dropna()
            if len(non_null_values) > 0:
                # If all non-null values are whole numbers, format as integers
                all_integers = all(val.is_integer() for val in non_null_values)
                float_col_formatting[col] = "int" if all_integers else "float"
            else:
                float_col_formatting[col] = "int"
    return float_col_formatting


def _format_table_row(row: Any, df: Any, float_col_formatting: dict[str, str]) -> list[str]:
    """Format a single table row with proper value formatting."""
    formatted_row = []
    for col_name, value in row.items():
        if value is None or (isinstance(value, float) and str(value) == "nan"):
            formatted_row.append("")
        elif str(df[col_name].dtype) in ["int64", "int32"]:
            # For integer columns, format as integers
            formatted_row.append(str(int(value)))
        elif isinstance(value, float):
            # For float columns, use the determined formatting strategy
            if col_name in float_col_formatting and float_col_formatting[col_name] == "int":
                formatted_row.append(str(int(value)))
            else:
                formatted_row.append(f"{value:.2f}")
        else:
            # Clean up text values
            clean_value = str(value).strip().replace("|", "\\|")  # Escape pipes
            formatted_row.append(clean_value)
    return formatted_row


def _is_numeric_column(series: Any) -> bool:
    """Check if a pandas Series contains mostly numeric values."""
    if len(series) == 0:
        return False

    try:
        # Check if already numeric dtype first (fastest path)
        if str(series.dtype) in {"int64", "float64", "int32", "float32"}:
            return True

        # Sample-based approach for large series (>1000 rows)
        sample_size = min(100, len(series))
        if len(series) > 1000:
            sample_series = series.dropna().sample(n=sample_size, random_state=42)
        else:
            sample_series = series.dropna()

        if len(sample_series) == 0:
            return False

        # Optimized numeric conversion - avoid exception overhead
        numeric_count = 0
        for val in sample_series:
            val_str = str(val).replace(",", "").replace("$", "").replace("%", "")
            # Quick check: if it contains only digits, decimal point, minus, plus, or e
            if val_str and all(c in "0123456789.-+eE" for c in val_str):
                try:
                    float(val_str)
                    numeric_count += 1
                except (ValueError, TypeError):
                    pass

        # Consider numeric if >70% of sampled values are numeric
        return (numeric_count / len(sample_series)) > 0.7

    except (ValueError, TypeError, ZeroDivisionError):
        return False


def generate_table_summary(tables: list[TableData]) -> dict[str, Any]:
    """Generate summary statistics for extracted tables.

    Args:
        tables: List of TableData objects

    Returns:
        Dictionary with table statistics
    """
    if not tables:
        return {
            "table_count": 0,
            "total_rows": 0,
            "total_columns": 0,
            "pages_with_tables": 0,
        }

    total_rows = 0
    total_columns = 0
    pages_with_tables = set()
    tables_by_page = {}

    for table in tables:
        if "df" in table and table["df"] is not None:
            df = table["df"]
            total_rows += len(df)
            total_columns += len(df.columns)

        if "page_number" in table:
            page_num = table["page_number"]
            pages_with_tables.add(page_num)

            if page_num not in tables_by_page:
                tables_by_page[page_num] = 0
            tables_by_page[page_num] += 1

    return {
        "table_count": len(tables),
        "total_rows": total_rows,
        "total_columns": total_columns,
        "pages_with_tables": len(pages_with_tables),
        "avg_rows_per_table": total_rows / len(tables) if tables else 0,
        "avg_columns_per_table": total_columns / len(tables) if tables else 0,
        "tables_by_page": dict(tables_by_page),
    }


def extract_table_structure_info(table: TableData) -> dict[str, Any]:
    """Extract structural information from a table.

    Args:
        table: TableData object

    Returns:
        Dictionary with structural information
    """
    info = {
        "has_headers": False,
        "row_count": 0,
        "column_count": 0,
        "numeric_columns": 0,
        "text_columns": 0,
        "empty_cells": 0,
        "data_density": 0.0,
    }

    if "df" not in table or table["df"] is None:
        return info

    df = table["df"]

    if df.empty:
        return info

    info["row_count"] = len(df)
    info["column_count"] = len(df.columns)
    info["has_headers"] = len(df.columns) > 0

    # Analyze column types
    for col in df.columns:
        if _is_numeric_column(df[col]):
            info["numeric_columns"] += 1
        else:
            info["text_columns"] += 1

    # Calculate data density
    total_cells = len(df) * len(df.columns)
    if total_cells > 0:
        empty_cells = df.isnull().sum().sum()
        info["empty_cells"] = int(empty_cells)
        info["data_density"] = (total_cells - empty_cells) / total_cells

    return info
