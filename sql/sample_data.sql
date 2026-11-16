-- =====================================================
-- Sample data. Run AFTER schema.sql
-- Late fee rule used: late_days x daily_rate x 1.5
-- =====================================================
USE bike_rental;

INSERT INTO customers (name, phone, email, address, license_no, registered_on) VALUES
('Ravi Kumar',     '9876501001','ravi.kumar@example.com',    'Madhapur, Hyderabad',      'TS0920230001','2026-05-28'),
('Sneha Reddy',    '9876501002','sneha.reddy@example.com',   'Gachibowli, Hyderabad',    'TS0920230002','2026-06-01'),
('Arjun Varma',    '9876501003','arjun.varma@example.com',   'Kondapur, Hyderabad',      'TS0920230003','2026-06-10'),
('Priya Sharma',   '9876501004','priya.sharma@example.com',  'Banjara Hills, Hyderabad', 'TS0920230004','2026-06-25'),
('Karthik Naidu',  '9876501005','karthik.naidu@example.com', 'Kukatpally, Hyderabad',    'TS0920230005','2026-06-28'),
('Ananya Rao',     '9876501006','ananya.rao@example.com',    'Jubilee Hills, Hyderabad', 'TS0920230006','2026-07-10'),
('Mohammed Irfan', '9876501007','irfan.m@example.com',       'Tolichowki, Hyderabad',    'TS0920230007','2026-07-20'),
('Divya Teja',     '9876501008','divya.teja@example.com',    'Ameerpet, Hyderabad',      'TS0920230008','2026-08-05'),
('Sai Prasad',     '9876501009','sai.prasad@example.com',    'Miyapur, Hyderabad',       'TS0920230009','2026-08-10'),
('Neha Gupta',     '9876501010','neha.gupta@example.com',    'Secunderabad, Hyderabad',  'TS0920230010','2026-09-01'),
('Vikram Singh',   '9876501011','vikram.singh@example.com',  'Begumpet, Hyderabad',      'TS0920230011','2026-09-28'),
('Lakshmi Devi',   '9876501012','lakshmi.devi@example.com',  'LB Nagar, Hyderabad',      'TS0920230012','2026-10-29');

INSERT INTO bikes (bike_name, brand, bike_type, registration_no, daily_rate, status) VALUES
('Activa 6G',    'Honda',          'Scooter',  'TS09AB1001',  400.00, 'Available'),
('Jupiter',      'TVS',            'Scooter',  'TS09AB1002',  400.00, 'Available'),
('Pulsar 150',   'Bajaj',          'Geared',   'TS09CD2001',  600.00, 'Rented'),
('Classic 350',  'Royal Enfield',  'Cruiser',  'TS09CD2002', 1000.00, 'Rented'),
('Hunter 350',   'Royal Enfield',  'Cruiser',  'TS09EF3001',  900.00, 'Available'),
('FZ-S',         'Yamaha',         'Geared',   'TS09EF3002',  550.00, 'Available'),
('Ather 450X',   'Ather',          'Electric', 'TS09GH4001',  700.00, 'Rented'),
('Ola S1 Pro',   'Ola Electric',   'Electric', 'TS09GH4002',  650.00, 'Available'),
('Duke 200',     'KTM',            'Geared',   'TS09JK5001',  800.00, 'Available'),
('Access 125',   'Suzuki',         'Scooter',  'TS09JK5002',  380.00, 'Maintenance');

INSERT INTO rentals (rental_id, customer_id, bike_id, rental_date, expected_return, actual_return, rental_days, base_amount, late_fee, total_amount, status) VALUES
( 1,  1, 1, '2026-06-03','2026-06-05','2026-06-05', 2,  800.00,    0.00,  800.00,'Returned'),
( 2,  2, 4, '2026-06-10','2026-06-13','2026-06-13', 3, 3000.00,    0.00, 3000.00,'Returned'),
( 3,  3, 3, '2026-06-18','2026-06-20','2026-06-21', 2, 1200.00,  900.00, 2100.00,'Returned'),
( 4,  4, 7, '2026-07-02','2026-07-04','2026-07-04', 2, 1400.00,    0.00, 1400.00,'Returned'),
( 5,  5, 5, '2026-07-09','2026-07-12','2026-07-12', 3, 2700.00,    0.00, 2700.00,'Returned'),
( 6,  1, 2, '2026-07-15','2026-07-16','2026-07-16', 1,  400.00,    0.00,  400.00,'Returned'),
( 7,  6, 9, '2026-07-22','2026-07-25','2026-07-26', 3, 2400.00, 1200.00, 3600.00,'Returned'),
( 8,  7, 6, '2026-08-01','2026-08-03','2026-08-03', 2, 1100.00,    0.00, 1100.00,'Returned'),
( 9,  2, 8, '2026-08-08','2026-08-10','2026-08-10', 2, 1300.00,    0.00, 1300.00,'Returned'),
(10,  8, 4, '2026-08-14','2026-08-17','2026-08-17', 3, 3000.00,    0.00, 3000.00,'Returned'),
(11,  9, 1, '2026-08-20','2026-08-22','2026-08-22', 2,  800.00,    0.00,  800.00,'Returned'),
(12,  3, 5, '2026-09-05','2026-09-08','2026-09-08', 3, 2700.00,    0.00, 2700.00,'Returned'),
(13, 10, 3, '2026-09-12','2026-09-14','2026-09-14', 2, 1200.00,    0.00, 1200.00,'Returned'),
(14,  4, 7, '2026-09-19','2026-09-21','2026-09-22', 2, 1400.00, 1050.00, 2450.00,'Returned'),
(15, 11, 9, '2026-10-03','2026-10-05','2026-10-05', 2, 1600.00,    0.00, 1600.00,'Returned'),
(16, 12, 4, '2026-10-30','2026-11-03', NULL,        4, 4000.00,    0.00, 4000.00,'Active'),
(17,  5, 7, '2026-10-31','2026-11-02', NULL,        2, 1400.00,    0.00, 1400.00,'Active'),
(18,  1, 3, '2026-11-01','2026-11-04', NULL,        3, 1800.00,    0.00, 1800.00,'Active');

INSERT INTO payments (rental_id, amount, payment_mode, payment_date, note) VALUES
( 1,  800.00,'UPI', '2026-06-03 10:15:00','Full payment'),
( 2, 1500.00,'Card','2026-06-10 09:30:00','Advance'),
( 2, 1500.00,'UPI', '2026-06-13 18:05:00','Balance'),
( 3, 2100.00,'Cash','2026-06-21 17:40:00','Full payment incl. late fee'),
( 4, 1400.00,'UPI', '2026-07-02 11:00:00','Full payment'),
( 5, 2700.00,'Card','2026-07-09 10:45:00','Full payment'),
( 6,  400.00,'Cash','2026-07-15 12:10:00','Full payment'),
( 7, 2000.00,'UPI', '2026-07-22 09:50:00','Advance'),
( 7, 1000.00,'Cash','2026-07-26 19:20:00','Part payment'),
( 8, 1100.00,'UPI', '2026-08-01 10:30:00','Full payment'),
( 9, 1300.00,'UPI', '2026-08-08 15:25:00','Full payment'),
(10, 3000.00,'Card','2026-08-14 11:15:00','Full payment'),
(11,  800.00,'Cash','2026-08-20 13:00:00','Full payment'),
(12, 2700.00,'UPI', '2026-09-05 10:05:00','Full payment'),
(13, 1200.00,'UPI', '2026-09-12 16:45:00','Full payment'),
(14, 1400.00,'UPI', '2026-09-19 09:40:00','Advance'),
(15, 1600.00,'Card','2026-10-03 10:20:00','Full payment'),
(16, 2000.00,'UPI', '2026-10-30 09:10:00','Advance'),
(17, 1400.00,'Cash','2026-10-31 14:30:00','Full payment'),
(18, 1000.00,'UPI', '2026-11-01 10:00:00','Advance');
