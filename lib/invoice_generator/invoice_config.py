#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Module
Handles loading and validation of invoice configuration
"""

import json
import os
from datetime import datetime
from .date_calculator import process_dates, DateMode


def load_config(config_file="invoice_config.json"):
    """
    Load configuration from JSON file
    
    Args:
        config_file: Path to configuration JSON file
        
    Returns:
        dict: Configuration dictionary
        
    Raises:
        FileNotFoundError: If configuration file doesn't exist
        json.JSONDecodeError: If configuration file is invalid JSON
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Process dates if mode is calculated
    dates_config = config.get('dates', {})
    mode = dates_config.get('mode', DateMode.EXPLICIT.value)
    
    if mode == DateMode.CALCULATED.value:
        # Get reference date from config or use today
        reference_date_str = dates_config.get('reference_date')
        if reference_date_str:
            from .date_calculator import parse_date_string
            reference_date = parse_date_string(reference_date_str)
        else:
            reference_date = datetime.now().date()
        
        # Get country code
        country = dates_config.get('country')
        
        # Merge date config with invoice config for processing
        date_config = {
            'mode': mode,
            'date': config.get('invoice', {}).get('date'),
            'due_date': config.get('invoice', {}).get('due_date'),
            'service_end_date': config.get('invoice', {}).get('service_end_date'),
            'due_date_config': dates_config.get('due_date_config', {}),
        }
        
        # Calculate dates
        calculated_dates = process_dates(date_config, country, reference_date)
        
        # Update invoice config with calculated dates
        if 'invoice' not in config:
            config['invoice'] = {}
        
        config['invoice'].update(calculated_dates)
    
    return config


def validate_config(config):
    """
    Validate configuration structure
    
    Args:
        config: Configuration dictionary
        
    Returns:
        bool: True if valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    required_sections = ['sender', 'invoice', 'bill_to', 'line_items']
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required section: {section}")
    
    # Validate required fields
    if not config.get('invoice', {}).get('invoice_number'):
        raise ValueError("Invoice number is required")
    
    if not config.get('line_items') or len(config['line_items']) == 0:
        raise ValueError("At least one line item is required")
    
    # Validate dates mode
    dates_config = config.get('dates', {})
    mode = dates_config.get('mode', DateMode.EXPLICIT.value)
    
    if mode not in [DateMode.EXPLICIT.value, DateMode.CALCULATED.value]:
        raise ValueError(f"Invalid date mode: {mode}. Must be 'explicit' or 'calculated'")
    
    if mode == DateMode.CALCULATED.value:
        due_date_config = dates_config.get('due_date_config', {})
        rule = due_date_config.get('rule')
        valid_rules = ['today', 'last_working_day_current_month', 'last_working_day_next_month']
        if rule and rule not in valid_rules:
            raise ValueError(f"Invalid due date rule: {rule}. Must be one of: {', '.join(valid_rules)}")
    
    return True

