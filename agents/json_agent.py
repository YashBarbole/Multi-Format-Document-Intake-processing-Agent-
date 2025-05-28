from typing import Dict, Any
import json
from datetime import datetime

class JSONAgent:
    """
    Agent responsible for processing JSON data
    """
    
    def extract_json_data(self, content: str) -> Dict[str, Any]:
        """
        Process JSON content with enhanced formatting
        
        Args:
            content: JSON content to process
            
        Returns:
            Dict containing processed results with nice formatting
        """
        try:
            data = json.loads(content)
            
            # Determine document type based on content
            doc_type = self._determine_document_type(data)
            
            # Extract key metrics
            metrics = self._extract_key_metrics(data)
            
            return {
                "summary": {
                    "status": "✅ PROCESSED SUCCESSFULLY",
                    "document_type": f"JSON ({doc_type})",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "size": f"{len(content):,} bytes"
                },
                "structure": {
                    "total_fields": len(data) if isinstance(data, dict) else len(data) if isinstance(data, list) else 1,
                    "data_type": type(data).__name__,
                    "key_fields": list(data.keys()) if isinstance(data, dict) else []
                },
                "metrics": metrics,
                "suggested_action": self._suggest_action(doc_type)
            }
        except json.JSONDecodeError as e:
            return {
                "status": "❌ PROCESSING FAILED",
                "error": f"Invalid JSON: {str(e)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def _determine_document_type(self, data: Any) -> str:
        """Determine the type of JSON document based on its content"""
        if isinstance(data, dict):
            keys = [k.lower() for k in data.keys()]
            
            if any(k in keys for k in ["invoice", "bill", "payment"]):
                return "INVOICE"
            elif any(k in keys for k in ["order", "purchase"]):
                return "PURCHASE ORDER"
            elif any(k in keys for k in ["product", "item", "sku"]):
                return "PRODUCT DATA"
            elif any(k in keys for k in ["user", "customer", "client"]):
                return "CUSTOMER DATA"
        
        return "GENERAL DATA"
    
    def _extract_key_metrics(self, data: Any) -> Dict[str, Any]:
        """Extract key metrics from the JSON data"""
        metrics = {}
        
        if isinstance(data, dict):
            # Look for monetary values
            for key, value in data.items():
                if isinstance(value, (int, float)) and any(term in key.lower() for term in ["total", "amount", "price", "cost"]):
                    metrics[key] = f"${value:,.2f}"
            
            # Look for status fields
            status_keys = [k for k in data.keys() if "status" in k.lower()]
            if status_keys:
                metrics["Status"] = data[status_keys[0]]
            
            # Look for dates
            date_keys = [k for k in data.keys() if any(term in k.lower() for term in ["date", "time", "created", "updated"])]
            if date_keys:
                metrics["Date"] = data[date_keys[0]]
        
        return metrics
    
    def _suggest_action(self, doc_type: str) -> str:
        """Suggest an action based on the document type"""
        if doc_type == "INVOICE":
            return "💰 Process Payment"
        elif doc_type == "PURCHASE ORDER":
            return "📦 Fulfill Order"
        elif doc_type == "PRODUCT DATA":
            return "📝 Update Inventory"
        elif doc_type == "CUSTOMER DATA":
            return "👤 Update CRM"
        else:
            return "📋 Review Data"