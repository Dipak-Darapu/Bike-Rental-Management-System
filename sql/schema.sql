-- =====================================================
-- Bike Rental Management System : Database Schema
-- Run this file FIRST in MySQL Workbench
-- =====================================================
CREATE DATABASE IF NOT EXISTS bike_rental;
USE bike_rental;

-- ---------- CUSTOMERS ----------
CREATE TABLE customers (
    customer_id   INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    phone         VARCHAR(15)  NOT NULL UNIQUE,
    email         VARCHAR(100),
    address       VARCHAR(255),
    license_no    VARCHAR(30)  NOT NULL UNIQUE,
    registered_on DATE NOT NULL DEFAULT (CURRENT_DATE)
);

-- ---------- BIKES ----------
CREATE TABLE bikes (
    bike_id         INT AUTO_INCREMENT PRIMARY KEY,
    bike_name       VARCHAR(100) NOT NULL,
    brand           VARCHAR(50)  NOT NULL,
    bike_type       ENUM('Scooter','Geared','Electric','Cruiser') NOT NULL,
    registration_no VARCHAR(20)  NOT NULL UNIQUE,
    daily_rate      DECIMAL(8,2) NOT NULL CHECK (daily_rate > 0),
    status          ENUM('Available','Rented','Maintenance') NOT NULL DEFAULT 'Available'
);

-- ---------- RENTALS ----------
CREATE TABLE rentals (
    rental_id       INT AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT NOT NULL,
    bike_id         INT NOT NULL,
    rental_date     DATE NOT NULL,
    expected_return DATE NOT NULL,
    actual_return   DATE NULL,
    rental_days     INT NOT NULL,
    base_amount     DECIMAL(10,2) NOT NULL,
    late_fee        DECIMAL(10,2) NOT NULL DEFAULT 0,
    total_amount    DECIMAL(10,2) NOT NULL,
    status          ENUM('Active','Returned') NOT NULL DEFAULT 'Active',
    CONSTRAINT fk_rent_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_rent_bike     FOREIGN KEY (bike_id)     REFERENCES bikes(bike_id),
    INDEX idx_rental_date (rental_date),
    INDEX idx_rental_status (status)
);

-- ---------- PAYMENTS ----------
CREATE TABLE payments (
    payment_id   INT AUTO_INCREMENT PRIMARY KEY,
    rental_id    INT NOT NULL,
    amount       DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    payment_mode ENUM('UPI','Card','Cash') NOT NULL,
    payment_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    note         VARCHAR(150),
    CONSTRAINT fk_pay_rental FOREIGN KEY (rental_id) REFERENCES rentals(rental_id),
    INDEX idx_payment_date (payment_date)
);

-- ---------- VIEW : amount paid & pending per rental ----------
CREATE VIEW v_rental_balance AS
SELECT  r.rental_id,
        r.customer_id,
        c.name       AS customer_name,
        c.phone      AS phone,
        r.bike_id,
        b.bike_name  AS bike_name,
        r.rental_date,
        r.status,
        r.total_amount,
        COALESCE(SUM(p.amount), 0)                  AS paid_amount,
        r.total_amount - COALESCE(SUM(p.amount), 0) AS balance
FROM rentals r
JOIN customers c ON c.customer_id = r.customer_id
JOIN bikes b     ON b.bike_id     = r.bike_id
LEFT JOIN payments p ON p.rental_id = r.rental_id
GROUP BY r.rental_id, r.customer_id, c.name, c.phone, r.bike_id, b.bike_name,
         r.rental_date, r.status, r.total_amount;
