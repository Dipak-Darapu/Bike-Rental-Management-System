# 🏍️ Bike Rental Management System

A web application to manage a bike rental business: fleet, customers, bookings, returns, payments and analytics.

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python 3.10+ |
| Database | MySQL 8 |
| DB tool | MySQL Workbench |
| IDE | VS Code |

## Features

1. **Admin Dashboard**: total bikes, customers, bookings, revenue, pending amount, fleet status, overdue returns
2. **Bike Management**: add, view (search and filter), update, delete bikes
3. **Customer Management**: register, search, update, delete customers (phone and email validation)
4. **Rental Management**: book bikes, track rental dates, automatic charge calculation, optional advance payment
5. **Return Management**: record returns, automatic late fee, bike becomes available again (or goes to maintenance)
6. **Payment Management**: record payments (UPI, Card, Cash), payment history, pending dues
7. **Reports & Analytics**: most-rented bikes, monthly revenue, revenue by bike type, top customers, customer rental history

## Folder structure

```
bike_rental/
├── app.py                      # Admin Dashboard (home page)
├── pages/
│   ├── 1_Bike_Management.py
│   ├── 2_Customer_Management.py
│   ├── 3_Rental_Management.py
│   ├── 4_Return_Management.py
│   ├── 5_Payment_Management.py
│   └── 6_Reports_Analytics.py
├── utils/
│   ├── db.py                   # MySQL connection, queries, transactions
│   └── helpers.py              # Charge / late-fee rules, validation, flash messages
├── sql/
│   ├── schema.sql              # Tables + view   (run first)
│   ├── sample_data.sql         # Demo data       (run second)
│   └── queries.sql             # Analytics queries for practice
├── .streamlit/config.toml
├── .env.example
├── requirements.txt
└── README.md
```

## Setup (step by step)

### 1. Install the tools
- Python 3.10 or newer: https://www.python.org/downloads/ (tick "Add Python to PATH")
- MySQL Server 8 and MySQL Workbench: https://dev.mysql.com/downloads/
- VS Code: https://code.visualstudio.com/

### 2. Create the database (MySQL Workbench)
1. Open MySQL Workbench and connect to your local MySQL server.
2. **File → Open SQL Script** → choose `sql/schema.sql` → click the ⚡ **Execute** button.
3. Open `sql/sample_data.sql` → click ⚡ **Execute**.
4. In the left panel click the refresh icon. You should see the `bike_rental` database with 4 tables and 1 view.

### 3. Open the project in VS Code
**File → Open Folder** → select `bike_rental`. Open the terminal with **Ctrl + `**.

### 4. Create a virtual environment and install packages
```bash
python -m venv venv

# Windows (PowerShell)
venv\Scripts\activate
# Mac / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 5. Add your MySQL password
Copy `.env.example` to a new file named `.env` and put your MySQL password in it:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=bike_rental
```

### 6. Run the app
```bash
streamlit run app.py
```
The app opens at http://localhost:8501. Use the sidebar to move between pages.

## Business rules

- **Charge** = daily rate × number of days (minimum 1 day)
- **Late fee** = late days × daily rate × 1.5
- **Early return**: no refund
- **Pending amount** = total amount − payments received
- Booking a bike sets it to *Rented*. Returning it sets it back to *Available*.
- A rented bike cannot be deleted or have its status edited.
- A bike or customer with rental history cannot be deleted (data integrity).

Booking and return each run as a single **database transaction**, so a failure in any step rolls back everything.

## Database design

```
customers (1) ──< rentals >── (1) bikes
                     │
                     └──< payments
v_rental_balance : view that joins rentals + payments to give paid amount and balance
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `Access denied for user 'root'` | Wrong password in `.env` |
| `Can't connect to MySQL server` | MySQL service is not running. Start it from Services (Windows) or MySQL Workbench |
| `Unknown database 'bike_rental'` | Run `sql/schema.sql` first |
| `streamlit: command not found` | Activate the virtual environment, or use `python -m streamlit run app.py` |
| Port already in use | `streamlit run app.py --server.port 8502` |

## Ideas to extend

- Admin login (hashed passwords)
- Download reports as CSV or PDF
- Bike images and a customer-facing booking page
- Stored procedures and triggers for booking and return
- Deploy the app online (Streamlit Community Cloud plus a cloud MySQL such as Aiven or Railway)

## Resume bullets

> **Bike Rental Management System** | Python, Streamlit, MySQL
> • Built a full-stack web app with 7 modules (dashboard, bikes, customers, rentals, returns, payments, analytics) using Streamlit, Python and MySQL.
> • Designed a normalized 4-table schema with foreign keys, indexes and a reporting view; implemented booking and return workflows as atomic transactions.
> • Automated rental charge and late-fee calculation, pending-payment tracking and revenue analytics (monthly revenue, most-rented bikes, customer history).
