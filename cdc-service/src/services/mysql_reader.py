from sqlalchemy import create_engine, text
import hashlib
import json
import time

class MySQLReader:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string, pool_recycle=3600, pool_pre_ping=True)

    def get_table_data(self, table_name, max_retries=3):
        """Fetch all data from a table with retries."""
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                with self.engine.connect() as connection:
                    result = connection.execute(text(f"SELECT * FROM {table_name}"))
                    return [dict(row) for row in result]
            except Exception as e:
                last_error = e
                retry_count += 1
                print(f"Error reading table {table_name}: {str(e)}. Retry {retry_count}/{max_retries}")
                if retry_count < max_retries:
                    time.sleep(2)  # Wait before retrying
        
        # If we get here, all retries failed
        raise Exception(f"Failed to read table {table_name} after {max_retries} attempts: {str(last_error)}")

    def calculate_checksum(self, row):
        """Calculate a checksum for a row."""
        # Sort keys to ensure consistent ordering
        ordered_data = {k: str(row[k]) for k in sorted(row.keys())}
        json_str = json.dumps(ordered_data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def get_table_metadata(self, table_name):
        """Get table metadata including row count and overall checksum."""
        data = self.get_table_data(table_name)
        row_count = len(data)
        checksums = sorted(self.calculate_checksum(row) for row in data)
        overall_checksum = hashlib.sha256(''.join(checksums).encode()).hexdigest()
        
        return {
            'row_count': row_count,
            'checksum': overall_checksum,
            'data': data
        }

    def compare_data(self, table_name, previous_data, current_data):
        """Compare two datasets and return changes."""
        previous_dict = {self.get_key(row): row for row in previous_data}
        current_dict = {self.get_key(row): row for row in current_data}
        
        # Find changes
        changes = {
            'inserted': [],
            'updated': [],
            'deleted': []
        }
        
        # Check for inserts and updates
        for key, current_row in current_dict.items():
            if key not in previous_dict:
                changes['inserted'].append(current_row)
            elif self.calculate_checksum(current_row) != self.calculate_checksum(previous_dict[key]):
                changes['updated'].append(current_row)
        
        # Check for deletes
        for key in previous_dict:
            if key not in current_dict:
                changes['deleted'].append(previous_dict[key])
        
        return changes

    def get_key(self, row):
        """Get the primary key value(s) for a row."""
        return row['id']  # Adjust if primary key is different