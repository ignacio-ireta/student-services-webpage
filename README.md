# Student Services Webpage

A comprehensive student course registration system with real-time data replication powered by Change Data Capture (CDC).

## 📋 Overview

This project demonstrates a robust pattern for implementing Change Data Capture between different database systems with minimal permissions. It features a student services web application that allows students to register for courses, view their enrollments, and drop courses as needed, with all changes automatically synchronized to a backup database system.

## ✨ Features

- **Student Authentication**: Secure login system for student access
- **Course Registration**: Students can browse and register for multiple courses
- **Enrollment Management**: View current enrollments and drop unwanted courses
- **Real-time Data Replication**: Changes in the primary database automatically sync to the backup system
- **Resilient Architecture**: Designed to handle network issues and service restarts

## 🔧 Technical Implementation

### Architecture

The project consists of four main services:

- **Web Application**: Flask-based student portal
- **Primary Database**: MySQL database for storing student and course data
- **CDC Service**: Polls for data changes and applies them to the backup database
- **Backup Database**: PostgreSQL database that mirrors the primary database

### Technologies Used

- **Backend**: Python, Flask, SQLAlchemy
- **Databases**: MySQL 8.0, PostgreSQL 14
- **Data Synchronization**: Custom CDC implementation
- **Containerization**: Docker, Docker Compose
- **Networking**: Docker container networking

### Change Data Capture Implementation

This project implements a custom polling-based CDC solution that:

- Works with read-only access to the source database
- Requires no schema modifications or triggers
- Uses checksum-based change detection
- Supports inserts, updates, and deletes
- Handles transaction boundaries correctly
- Features automatic recovery from connection issues
- Maintains a comprehensive sync history

## 🚀 Getting Started

### Prerequisites

- Docker
- Docker Compose

### Installation

1. Clone this repository:
```bash
git clone https://github.com/ignacio-ireta/student-services-webpage.git
cd student-services-webpage
```

2. Start the application:
```bash
docker-compose up --build
```

3. Access the web interface:
```
http://localhost:5000
```

## 📦 Project Structure

```
project-root/
├── docker-compose.yml
├── .env
│
├── webapp/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── app.py
│       └── templates/
│
├── mysql/
│   ├── Dockerfile
│   ├── conf.d/
│   └── init/
│
├── cdc-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── main.py
│       ├── config.py
│       ├── models.py
│       └── services/
│
└── postgres/
    ├── Dockerfile
    └── init/
```

## 🔍 Technical Details

### CDC Process Flow

1. The CDC service initializes by taking a snapshot of the source database
2. It periodically polls for changes by comparing current data with the previous snapshot
3. Changes are detected by calculating checksums for each row
4. Detected changes are categorized as inserts, updates, or deletes
5. Changes are applied atomically to the backup database
6. Sync status and history are maintained for monitoring and recovery

### Fault Tolerance

- Automatic retry mechanism for database connections
- Health checks to ensure dependent services are running
- Service restarts on failure
- Comprehensive error logging
- Transaction-based change application

## 📈 Potential Enhancements

- [ ] Add CDC monitoring dashboard
- [ ] Implement incremental snapshots for large tables
- [ ] Add support for schema changes
- [ ] Implement conflict resolution strategies
- [ ] Add performance metrics tracking

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
