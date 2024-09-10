-- Create the database
CREATE DATABASE IF NOT EXISTS electricity_db;

-- Switch to the new database
USE electricity_db;

-- Create the bills table
CREATE TABLE IF NOT EXISTS bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    units_consumed INT NOT NULL,
    bill_amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);