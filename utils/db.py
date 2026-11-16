"""Database helper functions (MySQL connection, queries, transactions)."""
import os
from contextlib import contextmanager
from decimal import Decimal

import mysql.connector
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "bike_rental"),
    )


def check_connection():
    """Returns (True, '') if MySQL is reachable, else (False, error_message)."""
    try:
        conn = get_connection()
        conn.close()
        return True, ""
    except mysql.connector.Error as e:
        return False, str(e)


def _clean(params):
    """Convert numpy / pandas scalars to plain Python types for MySQL."""
    cleaned = []
    for p in params or ():
        if hasattr(p, "item") and not isinstance(p, (str, bytes)):
            p = p.item()
        cleaned.append(p)
    return tuple(cleaned)


def fetch_df(sql, params=None):
    """Run a SELECT and return a pandas DataFrame (DECIMAL columns become float)."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, _clean(params))
        rows = cur.fetchall()
        columns = cur.column_names
        cur.close()
    finally:
        conn.close()

    df = pd.DataFrame(rows, columns=columns)
    for col in df.columns:
        if df[col].map(lambda v: isinstance(v, Decimal)).any():
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def fetch_value(sql, params=None):
    """Return the first column of the first row (0 if NULL / no rows)."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, _clean(params))
        row = cur.fetchone()
        cur.close()
    finally:
        conn.close()
    if row is None or row[0] is None:
        return 0
    value = row[0]
    return float(value) if isinstance(value, Decimal) else value


@contextmanager
def transaction():
    """Use for multi-step writes: commits on success, rolls back on any error."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
        cur.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute(sql, params=None):
    """Run a single INSERT / UPDATE / DELETE. Returns the last inserted id."""
    with transaction() as cur:
        cur.execute(sql, _clean(params))
        return cur.lastrowid
