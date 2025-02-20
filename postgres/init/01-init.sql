-- Create schema to track changes
CREATE SCHEMA IF NOT EXISTS cdc;

-- Create tables that mirror the source tables
CREATE TABLE IF NOT EXISTS cdc.user (
    id INT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    -- CDC-specific columns
    cdc_operation CHAR(1) NOT NULL,
    cdc_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cdc_checksum TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cdc.student (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    -- CDC-specific columns
    cdc_operation CHAR(1) NOT NULL, -- I: Insert, U: Update, D: Delete
    cdc_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cdc_checksum TEXT NOT NULL -- To detect changes
);

CREATE TABLE IF NOT EXISTS cdc.course (
    id INT PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    -- CDC-specific columns
    cdc_operation CHAR(1) NOT NULL,
    cdc_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cdc_checksum TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cdc.registration (
    id INT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    registration_date TIMESTAMP NOT NULL,
    -- CDC-specific columns
    cdc_operation CHAR(1) NOT NULL,
    cdc_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cdc_checksum TEXT NOT NULL
);

-- Create a table to track CDC status
CREATE TABLE IF NOT EXISTS cdc.sync_status (
    table_name VARCHAR(100) PRIMARY KEY,
    last_sync_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_success_sync_time TIMESTAMP,
    row_count INT,
    last_checksum TEXT,
    status VARCHAR(50)
);