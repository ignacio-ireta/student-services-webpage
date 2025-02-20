import os

# MySQL Configuration
MYSQL_HOST = os.getenv('MYSQL_HOST', 'mysql')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'cdc_user')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'cdc_password')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'student_registration')

# PostgreSQL Configuration
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
POSTGRES_DATABASE = os.getenv('POSTGRES_DATABASE', 'student_registration_backup')

# CDC Configuration
POLL_INTERVAL_SECONDS = int(os.getenv('POLL_INTERVAL_SECONDS', 60))
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 1000))

# Tables to monitor
MONITORED_TABLES = ['student', 'course', 'registration']