#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markup Template Module
High-level API for using markup templates
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate

from .markup_parser import parse_markup
from .markup_renderer import MarkupRenderer
from .fonts import register_unicode_fonts


def generate_from_markup(markup_content: str, config: dict, output_filename: str, margins: dict = None):
    """
    Generate invoice PDF from markup template
    
    Args:
        markup_content: XML markup template content
        config: Invoice configuration dictionary
        output_filename: Output PDF filename
        margins: Optional margin dictionary (top, bottom, left, right in mm)
    """
    # Register fonts
    font_name, font_bold = register_unicode_fonts()
    
    # Parse markup
    root_element = parse_markup(markup_content)
    
    # Get currency info
    currency = config.get('currency', {})
    currency_code = currency.get('code', 'PLN')
    currency_symbol = currency.get('symbol', 'zł')
    
    # Create renderer
    renderer = MarkupRenderer(font_name, font_bold, config, currency_code, currency_symbol)
    
    # Render to elements
    elements = renderer.render(root_element)
    
    # Set margins
    if margins is None:
        margins = {'top': 20, 'bottom': 20, 'left': 20, 'right': 20}
    
    # Create PDF
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=margins.get('right', 20) * mm,
        leftMargin=margins.get('left', 20) * mm,
        topMargin=margins.get('top', 20) * mm,
        bottomMargin=margins.get('bottom', 20) * mm
    )
    
    # Build PDF
    doc.build(elements)
    
    return output_filename


def generate_from_markup_file(markup_file: str, config: dict, output_filename: str, margins: dict = None):
    """
    Generate invoice PDF from markup template file
    
    Args:
        markup_file: Path to XML markup template file
        config: Invoice configuration dictionary
        output_filename: Output PDF filename
        margins: Optional margin dictionary
    """
    with open(markup_file, 'r', encoding='utf-8') as f:
        markup_content = f.read()
    
    return generate_from_markup(markup_content, config, output_filename, margins)

