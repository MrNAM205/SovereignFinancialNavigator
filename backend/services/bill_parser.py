"""Bill parsing service for extracting structured data from utility bills."""
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

@dataclass
class PaymentCoupon:
    account_number: str
    amount_due: Optional[float]
    due_date: Optional[datetime]
    mail_to: Optional[str] = None

@dataclass
class BillUsage:
    electricity_kwh: Optional[float] = None
    water_gallons: Optional[float] = None
    gas_therms: Optional[float] = None

@dataclass
class BillData:
    provider: str
    billing_period: Tuple[datetime, datetime]
    usage: BillUsage
    charges: Dict[str, float]
    payment_coupon: PaymentCoupon

class BillParser:
    """Parses utility bills into structured data."""
    
    # Common patterns for bill fields
    PATTERNS = {
        "account_number": [
            r"Account\\s+Number[:.]?\\s*([A-Z0-9-]+)",
            r"Account(?:\s+)?(?:Number|#)?[:.]?\\s*([A-Z0-9-]+)",
            r"Acct(?:\s+)?(?:Number|#)?[:.]?\\s*([A-Z0-9-]+)",
            r"Account\\s*:\\s*([A-Z0-9-]+)"
        ],
        "amount_due": [
            r"Amount\\s+Due[:.]?\\s*\\$?([0-9.,]+)",
            r"Total\\s+Due[:.]?\\s*\\$?([0-9.,]+)",
            r"Balance\\s+Due[:.]?\\s*\\$?([0-9.,]+)"
        ],
        "due_date": [
            r"Due\\s+Date[:.]?\\s*([A-Za-z]+\\s+\\d{1,2},\\s+\\d{4})",
            r"Payment\\s+Due[:.]?\\s*([A-Za-z]+\\s+\\d{1,2},\\s+\\d{4})"
        ]
    }
    
    def __init__(self, text: str):
        self.text = text
        self.sections = self._segment_document()
    
    def _segment_document(self) -> Dict[str, str]:
        """Split bill into logical sections based on layout cues."""
        sections = {
            "header": "",
            "summary": "",
            "details": "",
            "payment": ""
        }
        
        lines = self.text.split("\n")
        current_section = "header"
        
        for line in lines:
            # Simple heuristic: payment section often starts with these phrases
            if any(phrase in line.lower() for phrase in [
                "detach and return", "payment coupon", "please include"
            ]):
                current_section = "payment"
            elif "account summary" in line.lower():
                current_section = "summary"
            elif "detail" in line.lower():
                current_section = "details"
            
            sections[current_section] += line + "\n"
        
        return sections
    
    def _extract_pattern(self, patterns: List[str], text: str, label: str) -> Optional[str]:
        """Extract first matching pattern from text."""
        for pattern in patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                print(f"[MATCH] {label}: {match.group(1)} using pattern: {pattern}")
                return match.group(1).strip()
            else:
                print(f"[MISS] {label} with pattern: {pattern}")
        return "NOT FOUND"
    
    def extract_payment_coupon(self) -> Optional[PaymentCoupon]:
        """Extract payment coupon data from bill text."""
        # First try payment section, then fall back to whole document
        search_text = self.sections["payment"] or self.text
        
        account_number = self._extract_pattern(self.PATTERNS["account_number"], search_text, "account_number")
        amount_str = self._extract_pattern(self.PATTERNS["amount_due"], search_text, "amount_due")
        date_str = self._extract_pattern(self.PATTERNS["due_date"], search_text, "due_date")
        
    def extract_payment_coupon(self) -> Optional[PaymentCoupon]:
        """Extract payment coupon data from bill text."""
        # First try payment section, then fall back to whole document
        search_text = self.sections["payment"] or self.text

        account_number = self._extract_pattern(self.PATTERNS["account_number"], search_text, "account_number")
        amount_str = self._extract_pattern(self.PATTERNS["amount_due"], search_text, "amount_due")
        date_str = self._extract_pattern(self.PATTERNS["due_date"], search_text, "due_date")

        amount = None
        if amount_str != "NOT FOUND":
            try:
                # Parse amount (remove commas, convert to float)
                amount = float(str(amount_str).replace(",", ""))
            except (ValueError, TypeError):
                amount = None

        due_date = None
        if date_str != "NOT FOUND":
            for fmt in ["%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d", "%B %d, %Y"]:
                try:
                    due_date = datetime.strptime(str(date_str), fmt)
                    break
                except ValueError:
                    continue

        if account_number == "NOT FOUND" and amount is None and due_date is None:
            return None

        return PaymentCoupon(
            account_number=account_number if account_number != "NOT FOUND" else "UNKNOWN",
            amount_due=amount,
            due_date=due_date
        )
    
    def parse(self) -> Optional[BillData]:
        """Parse full bill data including payment coupon."""
        coupon = self.extract_payment_coupon()
        if not coupon:
            return None
            
        # Extract provider name from header (simple heuristic)
        provider = ""
        header_lines = self.sections["header"].strip().split("\n")
        if header_lines:
            provider = header_lines[0].strip()
        
        # For now, return minimal structure - expand based on needs
        return BillData(
            provider=provider,
            billing_period=(datetime.now(), datetime.now()),  # TODO: Extract actual period
            usage=BillUsage(),  # TODO: Extract usage data
            charges={"total_due": coupon.amount_due},
            payment_coupon=coupon
        )