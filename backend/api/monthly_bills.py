from fastapi import APIRouter, HTTPException
from typing import List
from datetime import date, datetime
import uuid

from models import MonthlyBill, RemedyEvent
# This creates a dependency between API modules. For a larger app,
# a shared service layer would be a better architecture.
from api.remedy_log import remedy_log_db

router = APIRouter()

monthly_bills_db: List[MonthlyBill] = []

@router.get("/monthly-bills", response_model=List[MonthlyBill], tags=["Monthly Bills"])
def get_monthly_bills():
    return monthly_bills_db

@router.post("/monthly-bills", response_model=MonthlyBill, tags=["Monthly Bills"])
def add_monthly_bill(bill: MonthlyBill):
    # In a real app, ID would be handled by the database
    bill.id = str(uuid.uuid4())
    monthly_bills_db.append(bill)
    return bill

@router.post("/monthly-bills/{bill_id}/endorse", response_model=MonthlyBill, tags=["Monthly Bills"])
def endorse_bill(bill_id: str):
    bill_to_endorse = None
    for bill in monthly_bills_db:
        if bill.id == bill_id:
            bill_to_endorse = bill
            break

    if not bill_to_endorse:
        raise HTTPException(status_code=404, detail="Bill not found")

    bill_to_endorse.status = "endorsed"
    bill_to_endorse.endorsement_date = date.today()

    # --- Sovereign Integration: Log the endorsement event ---
    endorsement_event = RemedyEvent(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        action=f"Monthly bill (ID: {bill_to_endorse.id}) endorsed for amount {bill_to_endorse.amount_due}",
        actor='user',
        stage='endorsement'
    )
    remedy_log_db.append(endorsement_event)
    # -----------------------------------------------------

    return bill_to_endorse
