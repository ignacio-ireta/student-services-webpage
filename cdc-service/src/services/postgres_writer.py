from sqlalchemy import create_engine, text
from datetime import datetime

class PostgresWriter:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)

    def apply_changes(self, table_name, changes, checksum):
        """Apply detected changes to PostgreSQL."""
        with self.engine.begin() as connection:  # This creates a transaction
            try:
                # Handle inserts
                for row in changes['inserted']:
                    self._insert_row(connection, table_name, row, 'I', checksum)

                # Handle updates
                for row in changes['updated']:
                    self._update_row(connection, table_name, row, 'U', checksum)

                # Handle deletes
                for row in changes['deleted']:
                    self._mark_deleted(connection, table_name, row, 'D', checksum)

                # Update sync status
                self._update_sync_status(connection, table_name, len(changes['inserted']) + 
                                      len(changes['updated']) + len(changes['deleted']), checksum)
                
            except Exception as e:
                print(f"Error applying changes to {table_name}: {str(e)}")
                raise

    def _insert_row(self, connection, table_name, row, operation, checksum):
        """Insert a row into the CDC schema."""
        # Prepare the values
        values = {**row, 
                 'cdc_operation': operation,
                 'cdc_timestamp': datetime.now(),
                 'cdc_checksum': checksum}
        
        # Build the SQL dynamically based on the columns
        columns = ', '.join(values.keys())
        placeholders = ', '.join(f':{key}' for key in values.keys())
        
        sql = f"""
        INSERT INTO cdc.{table_name} ({columns})
        VALUES ({placeholders})
        ON CONFLICT (id) DO UPDATE 
        SET 
            {', '.join(f"{k} = EXCLUDED.{k}" for k in values.keys())}
        """
        
        connection.execute(text(sql), values)

    def _update_row(self, connection, table_name, row, operation, checksum):
        """Update an existing row in the CDC schema."""
        self._insert_row(connection, table_name, row, operation, checksum)

    def _mark_deleted(self, connection, table_name, row, operation, checksum):
        """Mark a row as deleted in the CDC schema."""
        self._insert_row(connection, table_name, row, operation, checksum)

    def _update_sync_status(self, connection, table_name, changes_count, checksum):
        """Update the sync status table."""
        sql = """
        INSERT INTO cdc.sync_status 
            (table_name, last_sync_time, last_success_sync_time, row_count, last_checksum, status)
        VALUES 
            (:table_name, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, :changes_count, :checksum, 'SUCCESS')
        ON CONFLICT (table_name) 
        DO UPDATE SET 
            last_sync_time = CURRENT_TIMESTAMP,
            last_success_sync_time = CURRENT_TIMESTAMP,
            row_count = :changes_count,
            last_checksum = :checksum,
            status = 'SUCCESS'
        """
        
        connection.execute(text(sql), {
            'table_name': table_name,
            'changes_count': changes_count,
            'checksum': checksum
        })