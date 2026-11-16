import mysql.connector
import streamlit as st

from utils.db import execute, fetch_df
from utils.helpers import flash, show_flash, valid_email, valid_phone

st.set_page_config(page_title="Customer Management", page_icon="👤", layout="wide")
st.title("👤 Customer Management")
show_flash()

tab_view, tab_add, tab_edit, tab_delete = st.tabs(["📋 View", "➕ Register", "✏️ Update", "🗑️ Delete"])


def validate(name, phone, email, license_no):
    if not (name.strip() and phone.strip() and license_no.strip()):
        return "Name, phone and licence number are required."
    if not valid_phone(phone.strip()):
        return "Enter a valid 10-digit Indian mobile number."
    if email.strip() and not valid_email(email.strip()):
        return "Enter a valid email address."
    return None


# ---------------- VIEW ----------------
with tab_view:
    search = st.text_input("Search (name / phone / licence no)")
    sql = ("SELECT customer_id, name, phone, email, address, license_no, registered_on "
           "FROM customers WHERE 1=1")
    params = []
    if search:
        sql += " AND (name LIKE %s OR phone LIKE %s OR license_no LIKE %s)"
        params += [f"%{search}%"] * 3
    df = fetch_df(sql + " ORDER BY customer_id", params)
    st.caption(f"{len(df)} customer(s) found")
    st.dataframe(df, hide_index=True)

# ---------------- REGISTER ----------------
with tab_add:
    with st.form("add_customer", clear_on_submit=True):
        name = st.text_input("Full name *")
        c1, c2 = st.columns(2)
        phone = c1.text_input("Phone * (10 digits)")
        email = c2.text_input("Email")
        license_no = st.text_input("Driving licence number *")
        address = st.text_area("Address")
        submitted = st.form_submit_button("Register customer")

    if submitted:
        error = validate(name, phone, email, license_no)
        if error:
            st.error(error)
        else:
            try:
                execute(
                    "INSERT INTO customers (name, phone, email, address, license_no) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (name.strip(), phone.strip(), email.strip() or None,
                     address.strip() or None, license_no.strip().upper()),
                )
                flash(f"Customer '{name.strip()}' registered successfully.")
                st.rerun()
            except mysql.connector.IntegrityError:
                st.error("A customer with this phone number or licence number already exists.")

# ---------------- UPDATE ----------------
with tab_edit:
    customers = fetch_df("SELECT * FROM customers ORDER BY customer_id")
    if customers.empty:
        st.info("No customers to edit.")
    else:
        lookup = customers.set_index("customer_id")
        cid = st.selectbox(
            "Select customer",
            customers["customer_id"].tolist(),
            format_func=lambda i: f"#{i} · {lookup.loc[i, 'name']} ({lookup.loc[i, 'phone']})",
        )
        row = lookup.loc[cid]
        with st.form(f"edit_customer_{cid}"):
            name = st.text_input("Full name", value=row["name"])
            c1, c2 = st.columns(2)
            phone = c1.text_input("Phone", value=row["phone"])
            email = c2.text_input("Email", value=row["email"] or "")
            license_no = st.text_input("Driving licence number", value=row["license_no"])
            address = st.text_area("Address", value=row["address"] or "")
            saved = st.form_submit_button("Save changes")

        if saved:
            error = validate(name, phone, email, license_no)
            if error:
                st.error(error)
            else:
                try:
                    execute(
                        "UPDATE customers SET name=%s, phone=%s, email=%s, address=%s, license_no=%s "
                        "WHERE customer_id=%s",
                        (name.strip(), phone.strip(), email.strip() or None,
                         address.strip() or None, license_no.strip().upper(), int(cid)),
                    )
                    flash("Customer updated successfully.")
                    st.rerun()
                except mysql.connector.IntegrityError:
                    st.error("Another customer already uses this phone or licence number.")

# ---------------- DELETE ----------------
with tab_delete:
    customers = fetch_df("SELECT customer_id, name, phone FROM customers ORDER BY customer_id")
    if customers.empty:
        st.info("No customers to delete.")
    else:
        lookup = customers.set_index("customer_id")
        cid = st.selectbox(
            "Select customer to delete",
            customers["customer_id"].tolist(),
            format_func=lambda i: f"#{i} · {lookup.loc[i, 'name']} ({lookup.loc[i, 'phone']})",
            key="del_customer",
        )
        confirm = st.checkbox("I understand this cannot be undone")
        if st.button("Delete customer", type="primary", disabled=not confirm):
            try:
                execute("DELETE FROM customers WHERE customer_id = %s", (int(cid),))
                flash("Customer deleted.")
                st.rerun()
            except mysql.connector.IntegrityError:
                st.error("This customer has rental history, so they cannot be deleted.")
