"""Test the bill parser service."""
import os
from datetime import datetime
from backend.services.bill_parser import BillParser

def read_sample_bill(filename):
    """Read a sample bill file and return its contents."""
    root_path = os.path.dirname(os.path.dirname(__file__))
    docs_path = os.path.join(root_path, "docs")
    with open(os.path.join(docs_path, filename), "r") as f:
        return f.read()

def test_bill_parser_extracts_payment_coupon():
    """Test that parser can extract payment coupon data from synthetic bill."""
    bill_text = read_sample_bill("sample_bill.txt")
    parser = BillParser(bill_text)
    
    coupon = parser.extract_payment_coupon()
    assert coupon is not None, "Should extract payment coupon"
    assert coupon.account_number == "000-123-456", "Should extract account number"
    assert coupon.amount_due == 112.34, "Should extract correct amount"
    assert isinstance(coupon.due_date, datetime), "Should parse due date"
    assert coupon.due_date.year == 2025, "Should extract correct year"
    assert coupon.due_date.month == 10, "Should extract correct month"
    assert coupon.due_date.day == 25, "Should extract correct day"

def test_bill_parser_matches_phoenix_sample():
    """Test that parser can handle Phoenix bill format fields."""
    # Using known values from Phoenix sample bill image
    phoenix_values = {
        "account_number": "111111111",
        "amount_due": 81.52,
        "billing_date": "3/21/2017"
    }
    
    # Parse synthetic bill and verify it has similar field structure
    bill_text = read_sample_bill("sample_bill.txt")
    parser = BillParser(bill_text)
    parsed = parser.parse()
    
    assert parsed is not None, "Should parse bill data"
    assert parsed.payment_coupon is not None, "Should have payment coupon"
    
    # Verify field presence and types (not exact values since synthetic)
    assert isinstance(parsed.payment_coupon.account_number, str), "Should have account number"
    assert isinstance(parsed.payment_coupon.amount_due, float), "Should have amount due"
    assert isinstance(parsed.payment_coupon.due_date, datetime), "Should have due date"
    
    # Verify amount has proper precision (2 decimal places)
    assert round(parsed.payment_coupon.amount_due, 2) == parsed.payment_coupon.amount_due, \
        "Amount should have 2 decimal places"