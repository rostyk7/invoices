#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Invoice Generator Library
A library for generating invoice PDFs with configurable dates and full Unicode support
"""

from .invoice_generator import generate_invoice, InvoiceGenerator
from .invoice_config import load_config, validate_config
from .invoice_calculator import calculate_totals, format_currency, format_amount
from .date_calculator import process_dates, DateMode, DueDateRule
from .invoice_renderer import InvoiceRenderer
from .fonts import register_unicode_fonts
from .template_config import TemplateConfig, TemplateStyle, TemplateLayout, SectionOrder, get_template_config
from .markup_template import generate_from_markup, generate_from_markup_file
from .markup_parser import parse_markup

__version__ = "0.1.0"
__all__ = [
    'generate_invoice',
    'InvoiceGenerator',
    'load_config',
    'validate_config',
    'calculate_totals',
    'format_currency',
    'format_amount',
    'process_dates',
    'DateMode',
    'DueDateRule',
    'InvoiceRenderer',
    'register_unicode_fonts',
    'TemplateConfig',
    'TemplateStyle',
    'TemplateLayout',
    'SectionOrder',
    'get_template_config',
    'generate_from_markup',
    'generate_from_markup_file',
    'parse_markup',
]

