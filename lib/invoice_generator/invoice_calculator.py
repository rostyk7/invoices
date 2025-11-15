#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Invoice Calculator Module
Business logic for invoice calculations (totals, VAT, etc.)
"""


def calculate_totals(line_items, vat_rate, apply_to_net=True):
    """
    Calculate net amount, VAT, and total from line items
    
    Args:
        line_items: List of line items with 'amount' key
        vat_rate: VAT rate as percentage (e.g., 23.0 for 23%)
        apply_to_net: If True, VAT is calculated on net amount.
                     If False, VAT is extracted from line items total.
    
    Returns:
        dict: Dictionary with 'net_amount', 'vat_amount', and 'total'
    """
    net_amount = sum(item.get('amount', 0) for item in line_items)
    vat_amount = 0
    
    if apply_to_net and net_amount > 0:
        vat_amount = net_amount * (vat_rate / 100)
    elif not apply_to_net:
        # If VAT is already included in line items
        net_amount_excl_vat = net_amount / (1 + vat_rate / 100)
        vat_amount = net_amount - net_amount_excl_vat
        net_amount = net_amount_excl_vat
    
    total = net_amount + vat_amount
    
    return {
        'net_amount': round(net_amount, 2),
        'vat_amount': round(vat_amount, 2),
        'total': round(total, 2)
    }


def format_currency(amount, currency_code="PLN", currency_symbol="zł"):
    """
    Format currency amount with symbol for display
    
    Args:
        amount: Numeric amount
        currency_code: Currency code (default: PLN)
        currency_symbol: Currency symbol (default: zł)
    
    Returns:
        str: Formatted currency string
    """
    return f"{currency_code} {currency_symbol} {amount:,.2f}".replace(',', ' ').replace('.', ',')


def format_amount(amount, currency_code="PLN", currency_symbol="zł"):
    """
    Format amount for display in table (without currency symbol)
    
    Args:
        amount: Numeric amount
        currency_code: Currency code (for future use)
        currency_symbol: Currency symbol (for future use)
    
    Returns:
        str: Formatted amount string
    """
    return f"{amount:,.2f}".replace(',', ' ')

