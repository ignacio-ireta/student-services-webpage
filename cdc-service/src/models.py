from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime

@dataclass
class TableMetadata:
    row_count: int
    checksum: str
    data: List[Dict[str, Any]]

@dataclass
class Changes:
    inserted: List[Dict[str, Any]]
    updated: List[Dict[str, Any]]
    deleted: List[Dict[str, Any]]

@dataclass
class SyncStatus:
    table_name: str
    last_sync_time: datetime
    last_success_sync_time: Optional[datetime]
    row_count: int
    last_checksum: str
    status: str