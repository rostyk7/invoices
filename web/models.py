from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean
from sqlalchemy.sql import func
from database import Base


class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True, nullable=False)
    config_json = Column(JSON, nullable=False)  # Store the full invoice config
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    sender_name = Column(String, nullable=True)
    bill_to_name = Column(String, nullable=True)
    
    subtotal = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    total = Column(Float, nullable=True)


