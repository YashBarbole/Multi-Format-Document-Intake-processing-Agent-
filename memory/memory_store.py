from typing import Dict, Any, List
import json
from datetime import datetime

class MemoryStore:
    """
    Simple memory storage for processed data
    """
    
    def __init__(self):
        self.data = []
        
    def store_data(self, input_type: str, intent: str, extracted_data: Dict[str, Any], source_info: str) -> None:
        """
        Store processed data with metadata
        
        Args:
            input_type: Type of input (JSON, EMAIL, etc.)
            intent: Detected intent of the input
            extracted_data: Processed data
            source_info: Source information (filename, etc.)
        """
        record = {
            "id": len(self.data) + 1,
            "input_type": input_type,
            "intent": intent,
            "extracted_data": json.dumps(extracted_data),
            "timestamp": datetime.now().isoformat(),
            "source_info": source_info
        }
        self.data.append(record)
    
    def get_recent_data(self, limit: int = 20) -> List[tuple]:
        """
        Get recent processing history
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of tuples containing record data
        """
        return [(
            record["id"],
            record["input_type"],
            record["intent"],
            record["extracted_data"],
            record["timestamp"],
            record["source_info"]
        ) for record in reversed(self.data[-limit:])]