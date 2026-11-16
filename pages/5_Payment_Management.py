import streamlit as st

from utils.db import execute, fetch_df, fetch_value
from utils.helpers import flash, money, show_flash

st.set_page_config(page_title="Payment Management", page_icon="💳", layout="wide")
st.title("💳 Payment Management")
show_flash()

tab_pay, tab_history, tab_pending = st.tabs(["➕ Record Payment", "🧾 Payment History", "⏳ Pending Dues"])

# ---------------- RECORD ----------------
with tab_pay:
    dues = fetch_df(
        "SELECT rental_id, customer_name, bike_name, total_amount, paid_amount, balance "
        "FROM v_rental_balance WHERE balance > 0 ORDER BY rental_id"
    )
    if dues.empty:
        st.success("All rentals are fully paid. 🎉")
    else:
        lookup = dues.set_index("rental_id")
        rid = st.selectbox(
            "Select rental",
            dues["rental_id"].tolist(),
            format_func=lambda i: (f"#{i} · {lookup.loc[i, 'customer_name']} · "
                                   f"{lookup.loc[i, 'bike_name']} · due {money(lookup.loc[i, 'balance'])}"),
        )
        row = lookup.loc[rid]
        balance = float(row["balance"])

        m = st.columns(3)
        m[0].metric("Total amount", money(row["total_amount"]))
        m[1].metric("Paid so far", money(row["paid_amount"]))
        m[2].metric("Balance", money(balance))

        a1, a2 = st.columns(2)
        amount = a1.number_input("Amount (₹)", min_value=min(1.0, balance), max_value=balance,
                                 value=balance, step=100.0)
        mode = a2.selectbox("Payment mode", ["UPI", "Cash", "Card"])
        note = st.text_input("Note (optional)")

        if st.button("Save payment", type="primary"):
            execute(
                "INSERT INTO payments (rental_id, amount, payment_mode, note) VALUES (%s, %s, %s, %s)",
                (int(rid), amount, mode, note.strip() or None),
            )
            flash(f"Payment of {money(amount)} recorded for rental #{rid}.")
            st.rerun()

# ---------------- HISTORY ----------------
with tab_history:
    mode_filter = st.selectbox("Payment mode", ["All", "UPI", "Cash", "Card"], key="hist_mode")
    sql = """
        SELECT p.payment_id AS id, p.rental_id, c.name AS customer, b.bike_name AS bike,
               p.amount, p.payment_mode, p.payment_date, p.note
        FROM payments p
        JOIN rentals r   ON r.rental_id   = p.rental_id
        JOIN customers c ON c.customer_id = r.customer_id
        JOIN bikes b     ON b.bike_id     = r.bike_id
    """
    params = []
    if mode_filter != "All":
        sql += " WHERE p.payment_mode = %s"
        params.append(mode_filter)
    df = fetch_df(sql + " ORDER BY p.payment_date DESC", params)
    st.metric("Total collected", money(df["amount"].sum() if not df.empty else 0))
    st.dataframe(df, hide_index=True)

# ---------------- PENDING ----------------
with tab_pending:
    pending = fetch_df(
        "SELECT rental_id, customer_name, phone, bike_name, status, total_amount, paid_amount, balance "
        "FROM v_rental_balance WHERE balance > 0 ORDER BY balance DESC"
    )
    total_pending = fetch_value("SELECT COALESCE(SUM(balance), 0) FROM v_rental_balance WHERE balance > 0")
    st.metric("Total pending amount", money(total_pending))
    if pending.empty:
        st.success("No pending dues.")
    else:
        st.dataframe(pending, hide_index=True)
