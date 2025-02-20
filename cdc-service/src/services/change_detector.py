import time
from datetime import datetime

class ChangeDetector:
    def __init__(self, mysql_reader, postgres_writer, monitored_tables, batch_size=1000):
        self.mysql_reader = mysql_reader
        self.postgres_writer = postgres_writer
        self.monitored_tables = monitored_tables
        self.batch_size = batch_size
        self.previous_states = {}

    def initialize(self):
        """Initialize previous states for all monitored tables."""
        for table in self.monitored_tables:
            metadata = self.mysql_reader.get_table_metadata(table)
            self.previous_states[table] = metadata['data']

    def detect_and_sync(self):
        """Detect changes in all monitored tables and sync them."""
        try:
            for table in self.monitored_tables:
                print(f"{datetime.now()} - Checking table: {table}")
                
                # Get current state
                current_metadata = self.mysql_reader.get_table_metadata(table)
                current_data = current_metadata['data']
                
                # Get previous state
                previous_data = self.previous_states.get(table, [])
                
                # Detect changes
                changes = self.mysql_reader.compare_data(table, previous_data, current_data)
                
                # If there are any changes
                total_changes = len(changes['inserted']) + len(changes['updated']) + len(changes['deleted'])
                if total_changes > 0:
                    print(f"{datetime.now()} - Found {total_changes} changes in {table}")
                    print(f"Inserts: {len(changes['inserted'])}")
                    print(f"Updates: {len(changes['updated'])}")
                    print(f"Deletes: {len(changes['deleted'])}")
                    
                    # Apply changes in batches
                    self.postgres_writer.apply_changes(table, changes, current_metadata['checksum'])
                
                # Update previous state
                self.previous_states[table] = current_data
                
        except Exception as e:
            print(f"Error in detect_and_sync: {str(e)}")
            raise

    def run(self, interval_seconds):
        """Run the change detection continuously."""
        self.initialize()
        
        while True:
            try:
                self.detect_and_sync()
                time.sleep(interval_seconds)
            except Exception as e:
                print(f"Error in CDC loop: {str(e)}")
                time.sleep(interval_seconds)  # Still sleep on error to prevent rapid retries