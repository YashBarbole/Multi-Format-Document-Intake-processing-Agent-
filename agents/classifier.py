from typing import Dict, Any
import json
import os

class ClassifierAgent:
    """
    Agent responsible for classifying input data into different formats
    """
    
    def classify_input(self, content: str, filename: str = None) -> Dict[str, str]:
        """
        Classify the input content and determine its format and intent
        
        Args:
            content: Content to classify
            filename: Optional filename to help with classification
            
        Returns:
            Dict with format and intent classification
        """
        # Check filename for PDF
        if filename and filename.lower().endswith('.pdf'):
            intent = "document"
            if any(word in filename.lower() for word in ["invoice", "bill", "payment"]):
                intent = "billing"
            elif any(word in filename.lower() for word in ["contract", "agreement"]):
                intent = "legal"
            
            return {
                "format": "PDF",
                "intent": intent,
                "confidence": "high"
            }
            
        # Try to determine if it's JSON
        try:
            json.loads(content)
            return {
                "format": "JSON",
                "intent": "data_processing",
                "confidence": "high"
            }
        except json.JSONDecodeError:
            pass
        
        # Check for email characteristics
        email_markers = ["from:", "to:", "subject:", "dear", "sincerely", "regards"]
        if any(marker in content.lower() for marker in email_markers):
            intent = "communication"
            if any(word in content.lower() for word in ["order", "purchase", "buy", "quote"]):
                intent = "procurement"
            elif any(word in content.lower() for word in ["invoice", "payment", "amount", "due"]):
                intent = "billing"
                
            return {
                "format": "EMAIL",
                "intent": intent,
                "confidence": "medium"
            }
        
        # Default classification
        return {
            "format": "TEXT",
            "intent": "unknown",
            "confidence": "low"
        }