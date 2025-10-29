from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
from enum import Enum

class DispatchStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    DELIVERED = "delivered"
    RESPONDED = "responded"

class RemedyEvent(BaseModel):
    id: str
    timestamp: datetime
    action: str
    actor: str  # 'user' or 'system'
    document_url: Optional[str] = None
    stage: str  # 'notice', 'response', 'rebuttal', 'endorsement'

class RemedyEventCreate(BaseModel):
    action: str
    actor: str
    document_url: Optional[str] = None
    stage: str

class Creditor(BaseModel):
    id: str
    name: str
    address: str
    contact_method: str # e.g., 'mail', 'email'
    tags: List[str] = []

class UserProfile(BaseModel):
    id: str
    full_name: str
    address: str
    status: Optional[str] = None # e.g., 'Sovereign Living Man/Woman'
    declarations: Optional[List[str]] = None

class MonthlyBill(BaseModel):
    id: str
    user_id: str
    creditor_id: str
    due_date: date
    amount_due: float
    status: str  # 'pending', 'endorsed', 'disputed'
    notes: Optional[str] = None
    endorsement_date: Optional[date] = None
    document_url: Optional[str] = None

class ViolationEvent(BaseModel):
    id: str
    date: date
    collector: str # Could be linked to Creditor ID later
    violation_type: str # e.g., 'Harassment', 'False Representation'
    statute_reference: str # e.g., '15 U.S.C. § 1692d'
    notes: str

class Notice(BaseModel):
    id: str
    user_id: str
    creditor_id: str
    template_name: str
    content: str
    created_at: datetime
    status: DispatchStatus = DispatchStatus.DRAFT

class DispatchEvent(BaseModel):
    id: str
    document_id: str
    document_type: str # e.g., 'notice', 'affidavit'
    dispatch_method: str # e.g., 'USPS Certified Mail', 'Email'
    tracking_number: Optional[str] = None
    sent_at: datetime
    delivered_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None

class Suggestion(BaseModel):
    id: str
    title: str
    description: str
    action_type: str  # e.g., 'send_notice', 'endorse_bill', 'follow_up'
    priority: int  # 1-5 scale, 5 is highest
    related_document_id: Optional[str] = None
