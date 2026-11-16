import mysql.connector
import streamlit as st

from utils.db import execute, fetch_df
from utils.helpers import flash, show_flash

st.set_page_config(page_title="Bike Management", page_icon="🏍️", layout="wide")
st.title("🏍️ Bike Management")
show_flash()

BIKE_TYPES = ["Scooter", "Geared", "Electric", "Cruiser"]
STATUSES = ["Available", "Rented", "Maintenance"]

tab_view, tab_add, tab_edit, tab_delete = st.tabs(["📋 View", "➕ Add", "✏️ Update", "🗑️ Delete"])

# ---------------- VIEW ----------------
with tab_view:
    c1, c2, c3 = st.columns(3)
    search = c1.text_input("Search (name / brand / reg. no)")
    type_filter = c2.selectbox("Type", ["All"] + BIKE_TYPES)
    status_filter = c3.selectbox("Status", ["All"] + STATUSES)

    sql = ("SELECT bike_id, bike_name, brand, bike_type, registration_no, daily_rate, status "
           "FROM bikes WHERE 1=1")
    params = []
    if search:
        sql += " AND (bike_name LIKE %s OR brand LIKE %s OR registration_no LIKE %s)"
        params += [f"%{search}%"] * 3
    if type_filter != "All":
        sql += " AND bike_type = %s"
        params.append(type_filter)
    if status_filter != "All":
        sql += " AND status = %s"
        params.append(status_filter)

    df = fetch_df(sql + " ORDER BY bike_id", params)
    st.caption(f"{len(df)} bike(s) found")
    st.dataframe(df, hide_index=True)

# ---------------- ADD ----------------
with tab_add:
    with st.form("add_bike", clear_on_submit=True):
        name = st.text_input("Bike name *")
        brand = st.text_input("Brand *")
        bike_type = st.selectbox("Type", BIKE_TYPES)
        reg_no = st.text_input("Registration number * (e.g. TS09AB1234)")
        rate = st.number_input("Daily rate (₹) *", min_value=1.0, value=500.0, step=50.0)
        submitted = st.form_submit_button("Add bike")

    if submitted:
        if not (name.strip() and brand.strip() and reg_no.strip()):
            st.error("Please fill all required fields.")
        else:
            try:
                execute(
                    "INSERT INTO bikes (bike_name, brand, bike_type, registration_no, daily_rate) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (name.strip(), brand.strip(), bike_type, reg_no.strip().upper(), rate),
                )
                flash(f"Bike '{name.strip()}' added successfully.")
                st.rerun()
            except mysql.connector.IntegrityError:
                st.error("A bike with this registration number already exists.")

# ---------------- UPDATE ----------------
with tab_edit:
    bikes = fetch_df("SELECT * FROM bikes ORDER BY bike_id")
    if bikes.empty:
        st.info("No bikes available to edit.")
    else:
        lookup = bikes.set_index("bike_id")
        bid = st.selectbox(
            "Select bike",
            bikes["bike_id"].tolist(),
            format_func=lambda i: f"#{i} · {lookup.loc[i, 'bike_name']} ({lookup.loc[i, 'registration_no']})",
        )
        row = lookup.loc[bid]
        is_rented = row["status"] == "Rented"
        status_options = STATUSES if is_rented else ["Available", "Maintenance"]

        with st.form(f"edit_bike_{bid}"):
            name = st.text_input("Bike name", value=row["bike_name"])
            brand = st.text_input("Brand", value=row["brand"])
            bike_type = st.selectbox("Type", BIKE_TYPES, index=BIKE_TYPES.index(row["bike_type"]))
            reg_no = st.text_input("Registration number", value=row["registration_no"])
            rate = st.number_input("Daily rate (₹)", min_value=1.0, value=float(row["daily_rate"]), step=50.0)
            status = st.selectbox("Status", status_options,
                                  index=status_options.index(row["status"]), disabled=is_rented)
            saved = st.form_submit_button("Save changes")
        if is_rented:
            st.caption("Status is locked while the bike is rented. Record its return first.")

        if saved:
            if not (name.strip() and brand.strip() and reg_no.strip()):
                st.error("Name, brand and registration number cannot be empty.")
            else:
                try:
                    execute(
                        "UPDATE bikes SET bike_name=%s, brand=%s, bike_type=%s, registration_no=%s, "
                        "daily_rate=%s, status=%s WHERE bike_id=%s",
                        (name.strip(), brand.strip(), bike_type, reg_no.strip().upper(),
                         rate, status, int(bid)),
                    )
                    flash("Bike updated successfully.")
                    st.rerun()
                except mysql.connector.IntegrityError:
                    st.error("Another bike already uses this registration number.")

# ---------------- DELETE ----------------
with tab_delete:
    bikes = fetch_df("SELECT bike_id, bike_name, registration_no, status FROM bikes ORDER BY bike_id")
    if bikes.empty:
        st.info("No bikes to delete.")
    else:
        lookup = bikes.set_index("bike_id")
        bid = st.selectbox(
            "Select bike to delete",
            bikes["bike_id"].tolist(),
            format_func=lambda i: f"#{i} · {lookup.loc[i, 'bike_name']} ({lookup.loc[i, 'registration_no']})",
            key="del_bike",
        )
        confirm = st.checkbox("I understand this cannot be undone")
        if st.button("Delete bike", type="primary", disabled=not confirm):
            if lookup.loc[bid, "status"] == "Rented":
                st.error("This bike is currently rented and cannot be deleted.")
            else:
                try:
                    execute("DELETE FROM bikes WHERE bike_id = %s", (int(bid),))
                    flash("Bike deleted.")
                    st.rerun()
                except mysql.connector.IntegrityError:
                    st.error("This bike has rental history, so it cannot be deleted. "
                             "Set its status to 'Maintenance' instead.")
