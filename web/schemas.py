from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class InvoiceCreate(BaseModel):
    invoice_number: str = Field(..., description="Unique invoice number")
    config_json: Dict[str, Any] = Field(..., description="Invoice configuration JSON")
    sender_name: Optional[str] = None
    bill_to_name: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    sender_name: Optional[str] = None
    bill_to_name: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    total: Optional[float] = None
    is_generated: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

