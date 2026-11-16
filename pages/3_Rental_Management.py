from datetime import date, timedelta

import streamlit as st

from utils.db import fetch_df, transaction
from utils.helpers import calc_base_amount, flash, money, rental_days, show_flash

st.set_page_config(page_title="Rental Management", page_icon="🔑", layout="wide")
st.title("🔑 Rental Management")
show_flash()

tab_new, tab_active, tab_all = st.tabs(["➕ New Booking", "🟢 Active Rentals", "📋 All Rentals"])

# ---------------- NEW BOOKING ----------------
with tab_new:
    customers = fetch_df("SELECT customer_id, name, phone FROM customers ORDER BY name")
    bikes = fetch_df(
        "SELECT bike_id, bike_name, registration_no, daily_rate FROM bikes "
        "WHERE status = 'Available' ORDER BY bike_name"
    )

    if customers.empty:
        st.warning("Register a customer first.")
    elif bikes.empty:
        st.warning("No bikes are available right now.")
    else:
        cust_lookup = customers.set_index("customer_id")
        bike_lookup = bikes.set_index("bike_id")

        c1, c2 = st.columns(2)
        cust_id = c1.selectbox(
            "Customer", customers["customer_id"].tolist(),
            format_func=lambda i: f"{cust_lookup.loc[i, 'name']} ({cust_lookup.loc[i, 'phone']})",
        )
        bike_id = c2.selectbox(
            "Available bike", bikes["bike_id"].tolist(),
            format_func=lambda i: (f"{bike_lookup.loc[i, 'bike_name']} · "
                                   f"{bike_lookup.loc[i, 'registration_no']} · "
                                   f"₹{bike_lookup.loc[i, 'daily_rate']:,.0f}/day"),
        )

        d1, d2 = st.columns(2)
        start = d1.date_input("Rental date", value=date.today())
        end = d2.date_input("Expected return date", value=start + timedelta(days=1), min_value=start)

        daily_rate = float(bike_lookup.loc[bike_id, "daily_rate"])
        days = rental_days(start, end)
        base = calc_base_amount(daily_rate, start, end)

        m1, m2, m3 = st.columns(3)
        m1.metric("Daily rate", money(daily_rate))
        m2.metric("Rental days", days)
        m3.metric("Estimated charge", money(base))

        p1, p2 = st.columns(2)
        advance = p1.number_input("Advance payment (₹)", min_value=0.0, max_value=base,
                                  value=0.0, step=100.0)
        mode = p2.selectbox("Payment mode", ["UPI", "Cash", "Card"])

        if st.button("Confirm booking", type="primary"):
            try:
                with transaction() as cur:
                    cur.execute(
                        "INSERT INTO rentals (customer_id, bike_id, rental_date, expected_return, "
                        "rental_days, base_amount, total_amount, status) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, 'Active')",
                        (int(cust_id), int(bike_id), start, end, days, base, base),
                    )
                    rental_id = cur.lastrowid
                    cur.execute(
                        "UPDATE bikes SET status = 'Rented' WHERE bike_id = %s AND status = 'Available'",
                        (int(bike_id),),
                    )
                    if cur.rowcount == 0:
                        raise ValueError("This bike was just booked by someone else.")
                    if advance > 0:
                        cur.execute(
                            "INSERT INTO payments (rental_id, amount, payment_mode, note) "
                            "VALUES (%s, %s, %s, 'Advance at booking')",
                            (rental_id, advance, mode),
                        )
                flash(f"Booking #{rental_id} confirmed. Estimated charge {money(base)}.")
                st.rerun()
            except Exception as e:
                st.error(f"Could not complete booking: {e}")

# ---------------- ACTIVE ----------------
with tab_active:
    active = fetch_df(
        """
        SELECT r.rental_id AS id, c.name AS customer, c.phone, b.bike_name AS bike,
               r.rental_date, r.expected_return, r.total_amount AS estimated_charge,
               DATEDIFF(CURDATE(), r.expected_return) AS days_overdue
        FROM rentals r
        JOIN customers c ON c.customer_id = r.customer_id
        JOIN bikes b     ON b.bike_id     = r.bike_id
        WHERE r.status = 'Active'
        ORDER BY r.expected_return
        """
    )
    if active.empty:
        st.info("No active rentals.")
    else:
        active["days_overdue"] = active["days_overdue"].clip(lower=0)
        st.dataframe(active, hide_index=True)

# ---------------- ALL ----------------
with tab_all:
    status_filter = st.selectbox("Status", ["All", "Active", "Returned"])
    sql = """
        SELECT r.rental_id AS id, c.name AS customer, b.bike_name AS bike,
               r.rental_date, r.expected_return, r.actual_return, r.rental_days,
               r.base_amount, r.late_fee, r.total_amount, r.status
        FROM rentals r
        JOIN customers c ON c.customer_id = r.customer_id
        JOIN bikes b     ON b.bike_id     = r.bike_id
    """
    params = []
    if status_filter != "All":
        sql += " WHERE r.status = %s"
        params.append(status_filter)
    df = fetch_df(sql + " ORDER BY r.rental_id DESC", params)
    st.caption(f"{len(df)} rental(s)")
    st.dataframe(df, hide_index=True)
