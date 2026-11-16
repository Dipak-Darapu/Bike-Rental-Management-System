-- =====================================================
-- Practice / analytics queries (good for interviews)
-- =====================================================
USE bike_rental;

-- 1. Most rented bikes
SELECT b.bike_name, b.registration_no, COUNT(r.rental_id) AS total_rentals
FROM bikes b
LEFT JOIN rentals r ON r.bike_id = b.bike_id
GROUP BY b.bike_id, b.bike_name, b.registration_no
ORDER BY total_rentals DESC;

-- 2. Monthly revenue with month-over-month change (window function)
SELECT month, revenue,
       revenue - LAG(revenue) OVER (ORDER BY month) AS change_vs_prev_month
FROM (
    SELECT DATE_FORMAT(payment_date, '%Y-%m') AS month, SUM(amount) AS revenue
    FROM payments
    GROUP BY DATE_FORMAT(payment_date, '%Y-%m')
) m
ORDER BY month;

-- 3. Revenue by bike type
SELECT b.bike_type, SUM(p.amount) AS revenue
FROM payments p
JOIN rentals r ON r.rental_id = p.rental_id
JOIN bikes b   ON b.bike_id   = r.bike_id
GROUP BY b.bike_type
ORDER BY revenue DESC;

-- 4. Top customers by spend, ranked
SELECT c.name, SUM(p.amount) AS total_spent,
       RANK() OVER (ORDER BY SUM(p.amount) DESC) AS spend_rank
FROM customers c
JOIN rentals r  ON r.customer_id = c.customer_id
JOIN payments p ON p.rental_id   = r.rental_id
GROUP BY c.customer_id, c.name;

-- 5. Pending payments
SELECT rental_id, customer_name, phone, total_amount, paid_amount, balance
FROM v_rental_balance
WHERE balance > 0
ORDER BY balance DESC;

-- 6. Overdue active rentals
SELECT r.rental_id, c.name, c.phone, b.bike_name, r.expected_return,
       DATEDIFF(CURDATE(), r.expected_return) AS days_overdue
FROM rentals r
JOIN customers c ON c.customer_id = r.customer_id
JOIN bikes b     ON b.bike_id     = r.bike_id
WHERE r.status = 'Active' AND r.expected_return < CURDATE();

-- 7. Total days each bike has been rented (utilisation)
SELECT b.bike_name,
       COALESCE(SUM(DATEDIFF(COALESCE(r.actual_return, r.expected_return), r.rental_date)), 0) AS days_rented
FROM bikes b
LEFT JOIN rentals r ON r.bike_id = b.bike_id
GROUP BY b.bike_id, b.bike_name
ORDER BY days_rented DESC;

-- 8. Late fee income vs normal rental income
SELECT SUM(base_amount) AS rental_income, SUM(late_fee) AS late_fee_income
FROM rentals;

-- 9. Customers who have never rented
SELECT c.customer_id, c.name
FROM customers c
LEFT JOIN rentals r ON r.customer_id = c.customer_id
WHERE r.rental_id IS NULL;
