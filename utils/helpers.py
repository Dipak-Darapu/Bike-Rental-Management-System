"""Business rules, validation and small UI helpers."""
import re

import streamlit as st

# Late return penalty: every extra day is charged at 150% of the daily rate
LATE_FEE_MULTIPLIER = 1.5


# ---------- business rules ----------
def rental_days(start, end):
    """Number of chargeable days (minimum 1)."""
    return max(1, (end - start).days)


def calc_base_amount(daily_rate, start, end):
    return round(float(daily_rate) * rental_days(start, end), 2)


def calc_late_fee(daily_rate, expected_return, actual_return):
    """Returns (late_days, late_fee)."""
    late_days = max(0, (actual_return - expected_return).days)
    return late_days, round(float(daily_rate) * LATE_FEE_MULTIPLIER * late_days, 2)


def money(value):
    return f"₹{float(value):,.2f}"


# ---------- validation ----------
def valid_phone(phone):
    return bool(re.fullmatch(r"[6-9]\d{9}", phone))


def valid_email(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))


# ---------- flash messages (survive st.rerun) ----------
def flash(message, kind="success"):
    st.session_state["_flash"] = (kind, message)


def show_flash():
    item = st.session_state.pop("_flash", None)
    if item:
        getattr(st, item[0])(item[1])
