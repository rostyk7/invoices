#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Date Calculator Module
Business logic for date calculations (working days, service dates, deadlines)
"""

from datetime import datetime, timedelta, date
from calendar import monthrange
from enum import Enum
import holidays


class DateMode(Enum):
    """Date calculation modes"""
    EXPLICIT = "explicit"  # Use dates exactly as provided
    CALCULATED = "calculated"  # Calculate dates based on rules


class DueDateRule(Enum):
    """Due date calculation rules"""
    TODAY = "today"  # Current date (today)
    LAST_WORKING_DAY_CURRENT_MONTH = "last_working_day_current_month"
    LAST_WORKING_DAY_NEXT_MONTH = "last_working_day_next_month"


def get_country_holidays(country_code, year=None):
    """
    Get holidays for a country
    
    Args:
        country_code: ISO country code (e.g., 'PL', 'US', 'GB')
        year: Year to get holidays for (default: current year)
    
    Returns:
        set: Set of holiday dates (date objects)
    """
    holiday_dates = set()
    
    if year is None:
        year = datetime.now().year
    
    # Use holidays library for country-specific holidays
    if country_code:
        try:
            # Create country holiday object
            # Note: Some countries need specific province/subdivision codes
            country_map = {
                'PL': 'PL',  # Poland
                'US': 'US',  # United States
                'GB': 'GB',  # United Kingdom
                'DE': 'DE',  # Germany
                'FR': 'FR',  # France
                'IT': 'IT',  # Italy
                'ES': 'ES',  # Spain
                # Add more as needed
            }
            
            mapped_code = country_map.get(country_code.upper(), country_code.upper())
            
            # Get holidays for the year
            country_holidays = holidays.country_holidays(mapped_code, years=year)
            holiday_dates.update(country_holidays.keys())
        except (KeyError, NotImplementedError) as e:
            # Country not supported or not implemented
            print(f"Warning: Country '{country_code}' not supported by holidays library: {e}")
            print(f"  Falling back to weekday-only calculation")
        except Exception as e:
            print(f"Warning: Error loading holidays for '{country_code}': {e}")
            print(f"  Falling back to weekday-only calculation")
    
    return holiday_dates


def is_working_day(date_obj, country=None, holiday_cache=None):
    """
    Check if a date is a working day (Monday-Friday, excluding holidays)
    
    Args:
        date_obj: datetime date object
        country: Country code for country-specific holidays (ISO code, e.g., 'PL', 'US')
        holiday_cache: Dictionary to cache holidays by (country, year) to avoid repeated lookups
    
    Returns:
        bool: True if working day
    """
    # Basic: Monday = 0, Sunday = 6
    weekday = date_obj.weekday()
    # Monday-Friday (0-4) are working days
    is_weekday = weekday < 5
    
    if not is_weekday:
        return False
    
    # Check for holidays if country is provided
    if country:
        # Use cache if provided
        if holiday_cache is None:
            holiday_cache = {}
        
        cache_key = (country, date_obj.year)
        if cache_key not in holiday_cache:
            holiday_cache[cache_key] = get_country_holidays(country, date_obj.year)
        
        if date_obj in holiday_cache[cache_key]:
            return False
    
    return True


def get_last_working_day_of_month(year, month, country=None, holiday_cache=None):
    """
    Get the last working day of a given month
    
    Args:
        year: Year (e.g., 2025)
        month: Month (1-12)
        country: Country code for country-specific holidays
        holiday_cache: Dictionary to cache holidays by (country, year)
    
    Returns:
        datetime.date: Last working day of the month
    """
    # Get the last day of the month
    last_day = monthrange(year, month)[1]
    
    # Start from the last day and work backwards
    for day in range(last_day, 0, -1):
        date_obj = datetime(year, month, day).date()
        if is_working_day(date_obj, country, holiday_cache):
            return date_obj
    
    # Should not reach here, but return last day if no working day found
    return datetime(year, month, last_day).date()


def get_last_working_day_of_previous_month(reference_date=None, country=None, holiday_cache=None):
    """
    Get the last working day of the previous month relative to a reference date
    
    Args:
        reference_date: Reference date (defaults to today)
        country: Country code for country-specific holidays
        holiday_cache: Dictionary to cache holidays by (country, year)
    
    Returns:
        datetime.date: Last working day of previous month
    """
    if reference_date is None:
        reference_date = datetime.now().date()
    
    # Go to first day of current month, then back one day to get last day of previous month
    first_day_current = reference_date.replace(day=1)
    last_day_previous = first_day_current - timedelta(days=1)
    
    return get_last_working_day_of_month(
        last_day_previous.year,
        last_day_previous.month,
        country,
        holiday_cache
    )


def calculate_service_end_date(date_config, country=None, reference_date=None, holiday_cache=None):
    """
    Calculate service end date based on configuration
    
    Args:
        date_config: Date configuration dictionary
        country: Country code for country-specific holidays
        reference_date: Reference date for calculations (defaults to today)
        holiday_cache: Dictionary to cache holidays by (country, year)
    
    Returns:
        datetime.date: Calculated service end date
    """
    if reference_date is None:
        reference_date = datetime.now().date()
    
    # If explicitly provided, use it (but still calculate if mode is calculated and not provided)
    mode = date_config.get('mode', DateMode.EXPLICIT.value)
    
    if mode == DateMode.EXPLICIT.value:
        # In explicit mode, return the provided date if exists
        service_end_date_str = date_config.get('service_end_date')
        if service_end_date_str:
            # Parse the date string
            return parse_date_string(service_end_date_str)
    
    # Calculate: last working day of previous month
    return get_last_working_day_of_previous_month(reference_date, country, holiday_cache)


def calculate_due_date(date_config, country=None, reference_date=None, holiday_cache=None):
    """
    Calculate due date based on configuration
    
    Args:
        date_config: Date configuration dictionary
        country: Country code for country-specific holidays
        reference_date: Reference date for calculations (defaults to today)
        holiday_cache: Dictionary to cache holidays by (country, year)
    
    Returns:
        datetime.date: Calculated due date
    """
    if reference_date is None:
        reference_date = datetime.now().date()
    
    mode = date_config.get('mode', DateMode.EXPLICIT.value)
    due_date_config = date_config.get('due_date_config', {})
    
    if mode == DateMode.EXPLICIT.value:
        # In explicit mode, return the provided date if exists
        due_date_str = date_config.get('due_date')
        if due_date_str:
            return parse_date_string(due_date_str)
    
    # Calculate based on rule
    rule = due_date_config.get('rule', DueDateRule.LAST_WORKING_DAY_CURRENT_MONTH.value)
    month_offset = due_date_config.get('month_offset', 0)  # 0 = current month, 1 = next month
    
    if rule == DueDateRule.TODAY.value:
        return reference_date
    elif rule in [DueDateRule.LAST_WORKING_DAY_CURRENT_MONTH.value, 
                  DueDateRule.LAST_WORKING_DAY_NEXT_MONTH.value]:
        # Determine target month
        target_month = reference_date.month + month_offset
        target_year = reference_date.year
        
        # Handle year overflow
        if target_month > 12:
            target_month -= 12
            target_year += 1
        
        return get_last_working_day_of_month(target_year, target_month, country, holiday_cache)
    else:
        # Default to today
        return reference_date


def calculate_invoice_date(date_config, reference_date=None):
    """
    Calculate invoice date (typically today)
    
    Args:
        date_config: Date configuration dictionary
        reference_date: Reference date for calculations (defaults to today)
    
    Returns:
        datetime.date: Invoice date
    """
    if reference_date is None:
        reference_date = datetime.now().date()
    
    mode = date_config.get('mode', DateMode.EXPLICIT.value)
    
    if mode == DateMode.EXPLICIT.value:
        # In explicit mode, return the provided date if exists
        invoice_date_str = date_config.get('date')
        if invoice_date_str:
            return parse_date_string(invoice_date_str)
    
    # Default to today/reference date
    return reference_date


def parse_date_string(date_str):
    """
    Parse date string in various formats
    
    Args:
        date_str: Date string (e.g., "Oct 6, 2025", "2025-10-06", etc.)
    
    Returns:
        datetime.date: Parsed date object
    """
    # Common formats
    formats = [
        "%b %d, %Y",      # Oct 6, 2025
        "%B %d, %Y",      # October 6, 2025
        "%Y-%m-%d",       # 2025-10-06
        "%d/%m/%Y",       # 06/10/2025
        "%m/%d/%Y",       # 10/06/2025
        "%d-%m-%Y",       # 06-10-2025
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    # If no format matches, raise error
    raise ValueError(f"Unable to parse date string: {date_str}")


def format_date_string(date, format_str="%b %d, %Y"):
    """
    Format date object to string
    
    Args:
        date: datetime.date object
        format_str: Format string (default: "Oct 6, 2025")
    
    Returns:
        str: Formatted date string
    """
    return date.strftime(format_str)


def process_dates(date_config, country=None, reference_date=None):
    """
    Process all dates based on configuration mode
    
    Args:
        date_config: Date configuration dictionary
        country: Country code for country-specific holidays
        reference_date: Reference date for calculations (defaults to today)
    
    Returns:
        dict: Dictionary with formatted date strings for 'date', 'due_date', 'service_end_date'
    """
    if reference_date is None:
        reference_date = datetime.now().date()
    
    # Create holiday cache to avoid repeated lookups
    holiday_cache = {}
    
    # Calculate or use explicit dates
    invoice_date = calculate_invoice_date(date_config, reference_date)
    due_date = calculate_due_date(date_config, country, reference_date, holiday_cache)
    service_end_date = calculate_service_end_date(date_config, country, reference_date, holiday_cache)
    
    return {
        'date': format_date_string(invoice_date),
        'due_date': format_date_string(due_date),
        'service_end_date': format_date_string(service_end_date),
    }

