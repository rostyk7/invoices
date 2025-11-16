import uvicorn
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import json
import os
import tempfile
import sys


lib_path = os.path.join(os.path.dirname(__file__), '..', 'lib')
sys.path.insert(0, lib_path)

from invoice_generator import generate_invoice

from invoice_generator.invoice_calculator import calculate_totals
from database import get_db, init_db, engine
from models import Invoice, InvoiceTemplate
from schemas import InvoiceResponse, InvoiceTemplateResponse
from config import get_database_url

app = FastAPI(title="Invoice Generator Web App")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    # Initialize database tables
    init_db()
    print(f"Database initialized: {get_database_url()}")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main page with JSON input form"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/invoices", response_class=HTMLResponse)
async def invoices_page(request: Request, db: Session = Depends(get_db)):
    invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).all()
    return templates.TemplateResponse("invoices.html", {
        "request": request,
        "invoices": invoices,
        "total": len(invoices)
    })


@app.post("/api/generate")
async def generate_invoice_api(
    config_json: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Generate invoice from JSON config and save to database
    
    Args:
        config_json: JSON string with invoice configuration
        db: Database session
    
    Returns:
        PDF file for download
    """
    try:
        # Parse JSON config
        try:
            config = json.loads(config_json)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
        
        # Validate required fields
        invoice_data = config.get('invoice', {})
        if not invoice_data.get('invoice_number'):
            raise HTTPException(status_code=400, detail="Invoice number is required")
        
        invoice_number = invoice_data.get('invoice_number')
        
        # Calculate totals
        from invoice_generator.invoice_calculator import calculate_totals
        line_items = config.get('line_items', [])
        tax = config.get('tax', {})
        vat_rate = tax.get('vat_rate', 23.0)
        apply_to_net = tax.get('apply_to_net', True)
        totals = calculate_totals(line_items, vat_rate, apply_to_net)
        
        # Extract metadata
        sender = config.get('sender', {})
        bill_to = config.get('bill_to', {})
        sender_name = sender.get('name') or sender.get('company_name')
        bill_to_name = bill_to.get('name') or bill_to.get('company_name')
        
        # Check if invoice already exists
        existing_invoice = db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()
        
        if existing_invoice:
            # Update existing invoice
            existing_invoice.config_json = config
            existing_invoice.sender_name = sender_name
            existing_invoice.bill_to_name = bill_to_name
            existing_invoice.subtotal = totals.get('net_amount')  # calculate_totals returns 'net_amount'
            existing_invoice.tax_amount = totals.get('vat_amount')  # calculate_totals returns 'vat_amount'
            existing_invoice.total = totals.get('total')
            db.commit()
            db.refresh(existing_invoice)
            invoice_id = existing_invoice.id
        else:
            # Create new invoice
            db_invoice = Invoice(
                invoice_number=invoice_number,
                config_json=config,
                sender_name=sender_name,
                bill_to_name=bill_to_name,
                subtotal=totals.get('net_amount'),
                tax_amount=totals.get('vat_amount'),
                total=totals.get('total')
            )
            db.add(db_invoice)
            db.commit()
            db.refresh(db_invoice)
            invoice_id = db_invoice.id
        
        temp_dir = tempfile.mkdtemp()
        output_file = os.path.join(temp_dir, f"{invoice_number}.pdf")
        
        try:
            generate_invoice(config=config, output_filename=output_file)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating invoice: {str(e)}")
        
        return FileResponse(
            output_file,
            media_type="application/pdf",
            filename=f"{invoice_number}.pdf",
            background=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/api/invoices")
async def list_invoices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):

    invoices = db.query(Invoice).offset(skip).limit(limit).all()
    return {
        "invoices": [
            {
                "id": inv.id,
                "invoice_number": inv.invoice_number,
                "sender_name": inv.sender_name,
                "bill_to_name": inv.bill_to_name,
                "subtotal": inv.subtotal,
                "tax_amount": inv.tax_amount,
                "total": inv.total,
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
                "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
            }
            for inv in invoices
        ],
        "total": db.query(Invoice).count()
    }


@app.get("/api/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "config_json": invoice.config_json,
        "sender_name": invoice.sender_name,
        "bill_to_name": invoice.bill_to_name,
        "subtotal": invoice.subtotal,
        "tax_amount": invoice.tax_amount,
        "total": invoice.total,
        "created_at": invoice.created_at.isoformat() if invoice.created_at else None,
        "updated_at": invoice.updated_at.isoformat() if invoice.updated_at else None,
    }


@app.post("/api/preview")
async def preview_config(
    config_json: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        try:
            config = json.loads(config_json)
        except json.JSONDecodeError as e:
            return JSONResponse(
                status_code=400,
                content={"valid": False, "error": f"Invalid JSON: {str(e)}"}
            )
        
        required_sections = ['sender', 'invoice', 'bill_to', 'line_items']
        missing = [section for section in required_sections if section not in config]
        
        if missing:
            return JSONResponse(
                status_code=400,
                content={"valid": False, "error": f"Missing required sections: {', '.join(missing)}"}
            )
        
        line_items = config.get('line_items', [])
        tax = config.get('tax', {})
        vat_rate = tax.get('vat_rate', 23.0)
        apply_to_net = tax.get('apply_to_net', True)
        
        totals = calculate_totals(line_items, vat_rate, apply_to_net)
        
        invoice_number = config.get('invoice', {}).get('invoice_number')
        
        existing_invoice = None
        if invoice_number:
            existing_invoice = db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()
        
        response_data = {
            "valid": True,
            "totals": totals,
            "invoice_number": invoice_number,
        }
        
        if existing_invoice:
            response_data["exists"] = True
            response_data["invoice_id"] = existing_invoice.id
            response_data["created_at"] = existing_invoice.created_at.isoformat() if existing_invoice.created_at else None
        else:
            response_data["exists"] = False
        
        return JSONResponse(
            status_code=200,
            content=response_data
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"valid": False, "error": f"Unexpected error: {str(e)}"}
        )


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

