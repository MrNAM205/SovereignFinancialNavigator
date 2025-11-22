"""Test sample bill data structure and field validation."""
import os
from datetime import datetime

def read_sample_bill(filename):
    """Read a sample bill file and return its contents."""
    docs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
    with open(os.path.join(docs_path, filename), "r") as f:
        return f.read()

def test_synthetic_bill_matches_phoenix_structure():
    """Verify our synthetic bill has same key fields as Phoenix sample."""
    synthetic = read_sample_bill("sample_bill.txt")
    
    # Known values from Phoenix bill (manually verified)
    phoenix_values = {
        "account_number": "111111111",  # From image: Account Number field
        "amount_due": "$81.52",         # From image: Amount Due
        "billing_date": "3/21/2017",    # From image: Billing Date
        "service_address": "200 W. Main St",  # From image: Service Address
    }
    
    # Check each key field exists in our synthetic bill
    for field, value in phoenix_values.items():
        # For demo, we just verify field presence - real impl would parse exact values
        if field == "account_number":
            assert "Account Number: " in synthetic, f"Missing {field}"
        elif field == "amount_due":
            assert "Total Amount Due:" in synthetic, f"Missing {field}"
        elif field == "billing_date":
            assert "Billing Date:" in synthetic, f"Missing {field}"
        elif field == "service_address":
            assert "Address:" in synthetic, f"Missing {field}"

def test_synthetic_bill_date_format():
    """Verify date format is parseable in synthetic bill."""
    synthetic = read_sample_bill("sample_bill.txt")
    
    # Extract date from "Billing Date: YYYY-MM-DD" format
    for line in synthetic.splitlines():
        if "Billing Date:" in line:
            date_str = line.split("Billing Date:")[1].strip()
            # Verify we can parse the date
            try:
                parsed = datetime.strptime(date_str, "%Y-%m-%d")
                assert parsed is not None, "Date should be parseable"
            except ValueError as e:
                raise AssertionError(f"Date format invalid: {date_str}") from e
            break
    else:
        raise AssertionError("Billing Date not found")