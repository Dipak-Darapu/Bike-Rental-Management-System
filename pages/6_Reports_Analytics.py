import streamlit as st

from utils.db import fetch_df
from utils.helpers import money

st.set_page_config(page_title="Reports & Analytics", page_icon="📊", layout="wide")
st.title("📊 Reports & Analytics")

tab_bikes, tab_revenue, tab_customers, tab_history = st.tabs(
    ["🏆 Most-Rented Bikes", "💰 Revenue", "👥 Top Customers", "🕘 Customer History"]
)

# ---------------- MOST RENTED ----------------
with tab_bikes:
    df = fetch_df(
        """
        SELECT CONCAT(b.bike_name, ' (', b.registration_no, ')') AS bike,
               b.bike_type, COUNT(r.rental_id) AS total_rentals,
               COALESCE(SUM(r.total_amount), 0) AS billed_amount
        FROM bikes b
        LEFT JOIN rentals r ON r.bike_id = b.bike_id
        GROUP BY b.bike_id, b.bike_name, b.registration_no, b.bike_type
        ORDER BY total_rentals DESC, bike
        """
    )
    if df.empty:
        st.info("No data yet.")
    else:
        st.bar_chart(df.head(10), x="bike", y="total_rentals")
        st.dataframe(df, hide_index=True)

# ---------------- REVENUE ----------------
with tab_revenue:
    monthly = fetch_df(
        """
        SELECT DATE_FORMAT(payment_date, '%Y-%m') AS month, SUM(amount) AS revenue
        FROM payments
        GROUP BY DATE_FORMAT(payment_date, '%Y-%m')
        ORDER BY month
        """
    )
    left, right = st.columns(2)
    with left:
        st.subheader("Monthly revenue")
        if monthly.empty:
            st.info("No payments yet.")
        else:
            st.bar_chart(monthly, x="month", y="revenue")
            monthly["change_vs_prev_month"] = monthly["revenue"].diff()
            st.dataframe(monthly, hide_index=True)
    with right:
        st.subheader("Revenue by bike type")
        by_type = fetch_df(
            """
            SELECT b.bike_type, SUM(p.amount) AS revenue
            FROM payments p
            JOIN rentals r ON r.rental_id = p.rental_id
            JOIN bikes b   ON b.bike_id   = r.bike_id
            GROUP BY b.bike_type
            ORDER BY revenue DESC
            """
        )
        if not by_type.empty:
            st.bar_chart(by_type, x="bike_type", y="revenue")
            st.dataframe(by_type, hide_index=True)

    inc = fetch_df("SELECT COALESCE(SUM(base_amount),0) AS rental_income, "
                   "COALESCE(SUM(late_fee),0) AS late_fee_income FROM rentals")
    a, b = st.columns(2)
    a.metric("Rental income (billed)", money(inc.loc[0, "rental_income"]))
    b.metric("Late fee income (billed)", money(inc.loc[0, "late_fee_income"]))

# ---------------- TOP CUSTOMERS ----------------
with tab_customers:
    top = fetch_df(
        """
        SELECT c.name AS customer, COUNT(DISTINCT r.rental_id) AS rentals,
               COALESCE(SUM(p.amount), 0) AS total_paid
        FROM customers c
        JOIN rentals r       ON r.customer_id = c.customer_id
        LEFT JOIN payments p ON p.rental_id   = r.rental_id
        GROUP BY c.customer_id, c.name
        ORDER BY total_paid DESC
        LIMIT 10
        """
    )
    if top.empty:
        st.info("No data yet.")
    else:
        st.bar_chart(top, x="customer", y="total_paid")
        st.dataframe(top, hide_index=True)

# ---------------- CUSTOMER HISTORY ----------------
with tab_history:
    customers = fetch_df("SELECT customer_id, name, phone FROM customers ORDER BY name")
    if customers.empty:
        st.info("No customers yet.")
    else:
        lookup = customers.set_index("customer_id")
        cid = st.selectbox(
            "Select customer",
            customers["customer_id"].tolist(),
            format_func=lambda i: f"{lookup.loc[i, 'name']} ({lookup.loc[i, 'phone']})",
        )
        hist = fetch_df(
            "SELECT rental_id, bike_name, rental_date, status, total_amount, paid_amount, balance "
            "FROM v_rental_balance WHERE customer_id = %s ORDER BY rental_date DESC",
            (int(cid),),
        )
        if hist.empty:
            st.info("This customer has no rentals yet.")
        else:
            m = st.columns(3)
            m[0].metric("Total rentals", len(hist))
            m[1].metric("Total billed", money(hist["total_amount"].sum()))
            m[2].metric("Pending", money(hist["balance"].clip(lower=0).sum()))
            st.dataframe(hist, hide_index=True)
