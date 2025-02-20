-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS student_registration;
USE student_registration;

-- Create users table for authentication
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Create tables without timestamp columns
CREATE TABLE student (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    student_id VARCHAR(20) UNIQUE NOT NULL
) ENGINE=InnoDB;

CREATE TABLE course (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE registration (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(id),
    FOREIGN KEY (course_id) REFERENCES course(id)
) ENGINE=InnoDB;

-- Create read-only user with minimal permissions
CREATE USER 'cdc_user'@'%' IDENTIFIED BY 'cdc_password';
GRANT SELECT ON student_registration.* TO 'cdc_user'@'%';
FLUSH PRIVILEGES;

-- Insert sample courses
INSERT INTO course (code, name) VALUES 
    ('CS101', 'Introduction to Programming'),
    ('CS201', 'Data Structures'),
    ('CS301', 'Algorithms'),
    ('CS401', 'Database Systems'),
    ('CS501', 'Machine Learning');