#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markup Parser Module
Parses XML-like markup templates for invoice layouts
"""

from xml.etree import ElementTree as ET
from typing import Any, Optional
from dataclasses import dataclass
from enum import Enum


class Align(Enum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


@dataclass
class MarkupStyle:
    """Style attributes for markup elements"""
    font_size: float = 9
    font_weight: str = "normal"  # normal, bold
    color: str = "#000000"
    align: Align = Align.LEFT
    padding: float = 0
    margin: float = 0
    spacing: float = 0


@dataclass
class MarkupElement:
    """Base class for markup elements"""
    tag: str
    attributes: dict[str, str]
    children: list['MarkupElement']
    style: MarkupStyle
    text: Optional[str] = None
    
    def __init__(self, tag: str, attributes: Optional[dict[str, str]] = None, text: Optional[str] = None):
        self.tag = tag
        self.attributes = attributes or {}
        self.children = []
        self.text = text
        
        # Parse style from attributes
        self.style = MarkupStyle()
        if 'font-size' in self.attributes:
            self.style.font_size = float(self.attributes['font-size'])
        if 'font-weight' in self.attributes:
            self.style.font_weight = self.attributes['font-weight']
        if 'color' in self.attributes:
            self.style.color = self.attributes['color']
        if 'align' in self.attributes:
            try:
                self.style.align = Align(self.attributes['align'])
            except ValueError:
                self.style.align = Align.LEFT
        if 'padding' in self.attributes:
            self.style.padding = float(self.attributes['padding'].replace('cm', '').replace('mm', '').replace('pt', ''))
        if 'spacing' in self.attributes:
            self.style.spacing = float(self.attributes['spacing'].replace('cm', '').replace('mm', '').replace('pt', ''))


def parse_markup(markup_content: str) -> MarkupElement:
    """
    Parse markup XML content into MarkupElement tree
    
    Args:
        markup_content: XML markup string
    
    Returns:
        Root MarkupElement
    """
    try:
        root = ET.fromstring(markup_content)
        return _parse_element(root)
    except ET.ParseError as e:
        raise ValueError(f"Invalid markup XML: {e}")


def _parse_element(xml_element: ET.Element) -> MarkupElement:
    """Recursively parse XML element to MarkupElement"""
    attributes = dict(xml_element.attrib)
    text = xml_element.text.strip() if xml_element.text and xml_element.text.strip() else None
    
    element = MarkupElement(
        tag=xml_element.tag,
        attributes=attributes,
        text=text
    )
    
    # Parse children
    for child in xml_element:
        element.children.append(_parse_element(child))
    
    # Handle tail text (text after element)
    if xml_element.tail and xml_element.tail.strip():
        tail_element = MarkupElement(
            tag='text',
            text=xml_element.tail.strip()
        )
        element.children.append(tail_element)
    
    return element


def get_data_field(data: dict[str, Any], field_path: str, default: Any = None) -> Any:
    """
    Get nested data field using dot notation (e.g., 'sender.name')
    
    Args:
        data: Data dictionary
        field_path: Dot-separated field path
        default: Default value if field not found
    
    Returns:
        Field value
    """
    parts = field_path.split('.')
    value = data
    
    for part in parts:
        if isinstance(value, dict):
            value = value.get(part)
        elif isinstance(value, list) and part.isdigit():
            value = value[int(part)] if int(part) < len(value) else None
        else:
            return default
        
        if value is None:
            return default
    
    return value


def format_field_value(value: Any, format_type: str = None, currency_code: str = "PLN", currency_symbol: str = "zł") -> str:
    """
    Format field value based on format type
    
    Args:
        value: Value to format
        format_type: Format type (currency, number, date, etc.)
        currency_code: Currency code for currency formatting
        currency_symbol: Currency symbol for currency formatting
    
    Returns:
        Formatted string
    """
    if value is None:
        return ""
    
    if format_type == "currency":
        if isinstance(value, (int, float)):
            from .invoice_calculator import format_amount
            return format_amount(value, currency_code, currency_symbol)
    
    if format_type == "number":
        if isinstance(value, (int, float)):
            return f"{value:,.2f}"
    
    return str(value)

