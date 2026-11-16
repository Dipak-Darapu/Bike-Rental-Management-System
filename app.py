"""Admin Dashboard (home page). Run with:  streamlit run app.py"""
import streamlit as st

from utils.db import check_connection, fetch_df, fetch_value
from utils.helpers import money

st.set_page_config(page_title="Bike Rental Admin Dashboard", page_icon="🏍️", layout="wide")

st.title("🏍️ Bike Rental Management System")
st.caption("Admin Dashboard")

ok, err = check_connection()
if not ok:
    st.error("Could not connect to MySQL. Check your `.env` file and make sure MySQL is running.")
    st.code(err)
    st.stop()

# ---------- KPI cards ----------
total_bikes = int(fetch_value("SELECT COUNT(*) FROM bikes"))
available = int(fetch_value("SELECT COUNT(*) FROM bikes WHERE status = 'Available'"))
customers = int(fetch_value("SELECT COUNT(*) FROM customers"))
bookings = int(fetch_value("SELECT COUNT(*) FROM rentals"))
active = int(fetch_value("SELECT COUNT(*) FROM rentals WHERE status = 'Active'"))
revenue = fetch_value("SELECT COALESCE(SUM(amount), 0) FROM payments")
pending = fetch_value("SELECT COALESCE(SUM(balance), 0) FROM v_rental_balance WHERE balance > 0")

row1 = st.columns(4)
row1[0].metric("Total Bikes", total_bikes)
row1[1].metric("Available Now", available)
row1[2].metric("Total Customers", customers)
row1[3].metric("Total Bookings", bookings)

row2 = st.columns(3)
row2[0].metric("Active Rentals", active)
row2[1].metric("Revenue Collected", money(revenue))
row2[2].metric("Pending Amount", money(pending))

st.divider()

# ---------- charts / tables ----------
left, right = st.columns([1, 2])

with left:
    st.subheader("Fleet Status")
    fleet = fetch_df("SELECT status, COUNT(*) AS bikes FROM bikes GROUP BY status")
    if not fleet.empty:
        st.bar_chart(fleet, x="status", y="bikes")

with right:
    st.subheader("Recent Bookings")
    recent = fetch_df(
        """
        SELECT r.rental_id AS id, c.name AS customer, b.bike_name AS bike,
               r.rental_date, r.expected_return, r.total_amount, r.status
        FROM rentals r
        JOIN customers c ON c.customer_id = r.customer_id
        JOIN bikes b     ON b.bike_id     = r.bike_id
        ORDER BY r.rental_id DESC
        LIMIT 8
        """
    )
    st.dataframe(recent, hide_index=True)

# ---------- overdue alert ----------
overdue = fetch_df(
    """
    SELECT r.rental_id AS id, c.name AS customer, c.phone, b.bike_name AS bike,
           r.expected_return, DATEDIFF(CURDATE(), r.expected_return) AS days_overdue
    FROM rentals r
    JOIN customers c ON c.customer_id = r.customer_id
    JOIN bikes b     ON b.bike_id     = r.bike_id
    WHERE r.status = 'Active' AND r.expected_return < CURDATE()
    ORDER BY days_overdue DESC
    """
)
if not overdue.empty:
    st.subheader("⚠️ Overdue Returns")
    st.dataframe(overdue, hide_index=True)
else:
    st.success("No overdue rentals right now.")

st.sidebar.info("Use the pages above to manage bikes, customers, rentals, returns and payments.")
