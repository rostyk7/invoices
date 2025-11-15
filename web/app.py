#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import uvicorn
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import json
import os
import tempfile
import sys

# Add lib to path to import invoice_generator
lib_path = os.path.join(os.path.dirname(__file__), '..', 'lib')
sys.path.insert(0, lib_path)

# Import invoice_generator from local lib
from invoice_generator import generate_invoice

app = FastAPI(title="Invoice Generator Web App")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main page with JSON input form"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/generate")
async def generate_invoice_api(
    config_json: str = Form(...)
):
    """
    Generate invoice from JSON config
    
    Args:
        config_json: JSON string with invoice configuration
    
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
        if not config.get('invoice', {}).get('invoice_number'):
            raise HTTPException(status_code=400, detail="Invoice number is required")
        
        # Create temporary directory for output
        temp_dir = tempfile.mkdtemp()
        invoice_number = config.get('invoice', {}).get('invoice_number', 'invoice')
        output_file = os.path.join(temp_dir, f"{invoice_number}.pdf")
        
        # Generate invoice
        try:
            generate_invoice(config=config, output_filename=output_file)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating invoice: {str(e)}")
        
        # Return PDF file for download
        return FileResponse(
            output_file,
            media_type="application/pdf",
            filename=f"{invoice_number}.pdf",
            background=None  # File will be deleted after response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/api/preview")
async def preview_config(config_json: str = Form(...)):
    """
    Validate and preview configuration without generating PDF
    
    Args:
        config_json: JSON string with invoice configuration
    
    Returns:
        JSON with validation result and calculated totals
    """
    try:
        # Parse JSON config
        try:
            config = json.loads(config_json)
        except json.JSONDecodeError as e:
            return JSONResponse(
                status_code=400,
                content={"valid": False, "error": f"Invalid JSON: {str(e)}"}
            )
        
        # Validate required fields
        required_sections = ['sender', 'invoice', 'bill_to', 'line_items']
        missing = [section for section in required_sections if section not in config]
        
        if missing:
            return JSONResponse(
                status_code=400,
                content={"valid": False, "error": f"Missing required sections: {', '.join(missing)}"}
            )
        
        # Calculate totals
        from invoice_generator.invoice_calculator import calculate_totals
        
        line_items = config.get('line_items', [])
        tax = config.get('tax', {})
        vat_rate = tax.get('vat_rate', 23.0)
        apply_to_net = tax.get('apply_to_net', True)
        
        totals = calculate_totals(line_items, vat_rate, apply_to_net)
        
        return JSONResponse(
            status_code=200,
            content={
                "valid": True,
                "totals": totals,
                "invoice_number": config.get('invoice', {}).get('invoice_number'),
            }
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

