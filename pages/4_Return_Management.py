from datetime import date

import streamlit as st

from utils.db import fetch_df, fetch_value, transaction
from utils.helpers import calc_late_fee, flash, money, show_flash, LATE_FEE_MULTIPLIER

st.set_page_config(page_title="Return Management", page_icon="↩️", layout="wide")
st.title("↩️ Return Management")
show_flash()

active = fetch_df(
    """
    SELECT r.rental_id, r.bike_id, c.name AS customer, b.bike_name, b.registration_no,
           b.daily_rate, r.rental_date, r.expected_return, r.base_amount
    FROM rentals r
    JOIN customers c ON c.customer_id = r.customer_id
    JOIN bikes b     ON b.bike_id     = r.bike_id
    WHERE r.status = 'Active'
    ORDER BY r.expected_return
    """
)

st.subheader("Record a returned bike")
if active.empty:
    st.info("There are no active rentals waiting for return.")
else:
    lookup = active.set_index("rental_id")
    rid = st.selectbox(
        "Select rental",
        active["rental_id"].tolist(),
        format_func=lambda i: (f"#{i} · {lookup.loc[i, 'customer']} · "
                               f"{lookup.loc[i, 'bike_name']} (due {lookup.loc[i, 'expected_return']})"),
    )
    row = lookup.loc[rid]

    rental_date = row["rental_date"]
    expected = row["expected_return"]
    daily_rate = float(row["daily_rate"])
    base = float(row["base_amount"])

    return_date = st.date_input("Actual return date", value=date.today(), min_value=rental_date)
    late_days, late_fee = calc_late_fee(daily_rate, expected, return_date)
    total = base + late_fee
    paid = float(fetch_value("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE rental_id = %s",
                             (int(rid),)))
    balance = max(0.0, total - paid)

    m = st.columns(5)
    m[0].metric("Booked charge", money(base))
    m[1].metric("Late days", late_days)
    m[2].metric("Late fee", money(late_fee))
    m[3].metric("Total payable", money(total))
    m[4].metric("Balance due", money(balance))
    st.caption(f"Late fee rule: each extra day is charged at {LATE_FEE_MULTIPLIER:.0%} of the daily rate. "
               "Early returns are not refunded.")

    p1, p2 = st.columns(2)
    collect = p1.number_input("Collect payment now (₹)", min_value=0.0, max_value=max(balance, 0.0),
                              value=float(balance), step=100.0)
    mode = p2.selectbox("Payment mode", ["UPI", "Cash", "Card"], key="return_mode")
    to_maintenance = st.checkbox("Send this bike for maintenance after return")

    if st.button("Confirm return", type="primary"):
        try:
            with transaction() as cur:
                cur.execute(
                    "UPDATE rentals SET actual_return=%s, late_fee=%s, total_amount=%s, status='Returned' "
                    "WHERE rental_id=%s AND status='Active'",
                    (return_date, late_fee, total, int(rid)),
                )
                if cur.rowcount == 0:
                    raise ValueError("This rental was already returned.")
                cur.execute(
                    "UPDATE bikes SET status=%s WHERE bike_id=%s",
                    ("Maintenance" if to_maintenance else "Available", int(row["bike_id"])),
                )
                if collect > 0:
                    cur.execute(
                        "INSERT INTO payments (rental_id, amount, payment_mode, note) "
                        "VALUES (%s, %s, %s, 'Payment at return')",
                        (int(rid), collect, mode),
                    )
            flash(f"Rental #{rid} returned. Total {money(total)}, balance now "
                  f"{money(max(0.0, balance - collect))}.")
            st.rerun()
        except Exception as e:
            st.error(f"Could not record return: {e}")

st.divider()
st.subheader("Recent returns")
recent = fetch_df(
    """
    SELECT r.rental_id AS id, c.name AS customer, b.bike_name AS bike,
           r.expected_return, r.actual_return, r.late_fee, r.total_amount
    FROM rentals r
    JOIN customers c ON c.customer_id = r.customer_id
    JOIN bikes b     ON b.bike_id     = r.bike_id
    WHERE r.status = 'Returned'
    ORDER BY r.actual_return DESC, r.rental_id DESC
    LIMIT 10
    """
)
st.dataframe(recent, hide_index=True)
