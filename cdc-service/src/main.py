import time
import sys
from sqlalchemy.exc import OperationalError
from services.mysql_reader import MySQLReader
from services.postgres_writer import PostgresWriter
from services.change_detector import ChangeDetector
import config

def main():
    # Create MySQL connection string
    mysql_conn_string = f"mysql://{config.MYSQL_USER}:{config.MYSQL_PASSWORD}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{config.MYSQL_DATABASE}"
    
    # Create PostgreSQL connection string
    postgres_conn_string = f"postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DATABASE}"

    # Retry counters
    mysql_retries = 5
    postgres_retries = 5
    retry_delay = 10  # seconds
    
    print("Starting CDC service...")
    print(f"Monitoring tables: {config.MONITORED_TABLES}")
    print(f"Poll interval: {config.POLL_INTERVAL_SECONDS} seconds")
    
    # Initialize MySQL connection with retries
    mysql_reader = None
    while mysql_retries > 0:
        try:
            print(f"Attempting to connect to MySQL ({mysql_retries} retries left)...")
            mysql_reader = MySQLReader(mysql_conn_string)
            # Test connection
            for table in config.MONITORED_TABLES:
                mysql_reader.get_table_data(table)
                print(f"Successfully connected to MySQL and read table: {table}")
            break
        except OperationalError as e:
            mysql_retries -= 1
            if mysql_retries <= 0:
                print(f"Failed to connect to MySQL after multiple attempts: {str(e)}")
                sys.exit(1)
            print(f"MySQL connection failed: {str(e)}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    # Initialize PostgreSQL connection with retries
    postgres_writer = None
    while postgres_retries > 0:
        try:
            print(f"Attempting to connect to PostgreSQL ({postgres_retries} retries left)...")
            postgres_writer = PostgresWriter(postgres_conn_string)
            # Test the connection
            with postgres_writer.engine.connect() as conn:
                conn.execute("SELECT 1")
            print("Successfully connected to PostgreSQL")
            break
        except Exception as e:
            postgres_retries -= 1
            if postgres_retries <= 0:
                print(f"Failed to connect to PostgreSQL after multiple attempts: {str(e)}")
                sys.exit(1)
            print(f"PostgreSQL connection failed: {str(e)}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    try:
        # Initialize change detector
        detector = ChangeDetector(
            mysql_reader=mysql_reader,
            postgres_writer=postgres_writer,
            monitored_tables=config.MONITORED_TABLES,
            batch_size=config.BATCH_SIZE
        )
        
        # Start the monitoring loop
        detector.run(config.POLL_INTERVAL_SECONDS)
        
    except Exception as e:
        print(f"Fatal error in CDC service: {str(e)}")
        raise

if __name__ == "__main__":
    main()