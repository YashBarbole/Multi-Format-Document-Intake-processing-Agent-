from typing import Dict, Any
import re
from datetime import datetime

class EmailAgent:
    """
    Agent responsible for processing email data
    """
    
    def extract_email_data(self, content: str) -> Dict[str, Any]:
        """
        Process email content with enhanced formatting
        
        Args:
            content: Email content to process
            
        Returns:
            Dict containing processed results with nice formatting
        """
        # Extract email headers and body
        headers = {}
        body_lines = []
        in_headers = True
        
        for line in content.split('\n'):
            line = line.strip()
            if in_headers and line:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.lower()] = value.strip()
                else:
                    in_headers = False
            if not in_headers and line:
                body_lines.append(line)
        
        # Determine urgency based on content
        urgency = "NORMAL"
        urgent_words = ["urgent", "asap", "emergency", "immediate", "priority"]
        if any(word in content.lower() for word in urgent_words):
            urgency = "HIGH"
        
        # Extract contact information
        contact_info = []
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        phones = re.findall(phone_pattern, content)
        emails = re.findall(email_pattern, content)
        
        if phones:
            contact_info.extend(phones)
        if emails:
            contact_info.extend(emails)
        
        # Identify key items/requests
        items = []
        for line in body_lines:
            if line.strip().startswith('-') or line.strip().startswith('•'):
                items.append(line.strip()[1:].strip())
        
        # Format the output
        return {
            "summary": {
                "status": "✅ PROCESSED SUCCESSFULLY",
                "document_type": "EMAIL",
                "intent": self._determine_intent(content),
                "sender": headers.get('from', 'Unknown'),
                "urgency": urgency,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "details": {
                "subject": headers.get('subject', 'No Subject'),
                "key_requests": items if items else ["No specific items listed"],
                "contact_info": contact_info if contact_info else ["No contact information found"],
                "body_preview": " ".join(body_lines)[:200] + "..."
            },
            "suggested_action": self._suggest_action(content)
        }
    
    def _determine_intent(self, content: str) -> str:
        """Determine the intent of the email"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["quote", "price", "cost", "rfq"]):
            return "REQUEST FOR QUOTE"
        elif any(word in content_lower for word in ["order", "purchase", "buy"]):
            return "PURCHASE ORDER"
        elif any(word in content_lower for word in ["invoice", "payment", "bill"]):
            return "BILLING INQUIRY"
        elif any(word in content_lower for word in ["support", "help", "issue"]):
            return "SUPPORT REQUEST"
        else:
            return "GENERAL INQUIRY"
    
    def _suggest_action(self, content: str) -> str:
        """Suggest an action based on the email content"""
        content_lower = content.lower()
        
        if "quote" in content_lower or "price" in content_lower:
            return "📋 Forward to Sales Team"
        elif "order" in content_lower or "purchase" in content_lower:
            return "🛒 Process Purchase Order"
        elif "support" in content_lower or "help" in content_lower:
            return "🔧 Create Support Ticket"
        elif "invoice" in content_lower or "payment" in content_lower:
            return "💰 Forward to Accounting"
        else:
            return "📥 Review and Assign"