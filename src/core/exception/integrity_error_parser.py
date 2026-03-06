from typing import Dict

from sqlalchemy.exc import IntegrityError


PG_ERROR_MAP: Dict[str, str] = {
    "23505": "Unique constraint violated (duplicate value)",  # unique_violation
    "23503": "Foreign key constraint violated (invalid reference)",  # foreign_key_violation
    "23502": "Not null constraint violated (missing required value)",  # not_null_violation
    "22001": "Value too long for column",  # string_data_right_truncation
    "22007": "Invalid datetime format",  # invalid_datetime_format
    "22003": "Numeric value out of range",  # numeric_value_out_of_range
    "22P02": "Invalid text representation (wrong data type)",  # invalid_text_representation
}


def parse_integrity_error(e: IntegrityError) -> str:
    """
    Convert PostgreSQL SQLSTATE code into a human-readable message
    for returning via API.
    """
    code = getattr(e.orig, "sqlstate", None)
    return PG_ERROR_MAP.get(code, "Database integrity error")  # type: ignore
