#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Template Configuration Module
Handles dynamic template/layout configuration for invoices
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum


class SectionOrder(Enum):
    """Order of sections in invoice"""
    SENDER_FIRST = "sender_first"  # Sender, Invoice Details, Bill To, Items
    INVOICE_FIRST = "invoice_first"  # Invoice Details, Sender, Bill To, Items
    BILL_TO_FIRST = "bill_to_first"  # Bill To, Invoice Details, Sender, Items


@dataclass
class TemplateStyle:
    """Style configuration for template"""
    # Colors
    primary_color: str = "#000000"
    secondary_color: str = "#E0E0E0"
    accent_color: str = "#F0F0F0"
    
    # Fonts
    title_font_size: float = 16
    header_font_size: float = 10
    normal_font_size: float = 9
    info_font_size: float = 10
    
    # Spacing
    section_spacing: float = 1.2  # in cm (increased for better visual separation)
    table_padding: float = 8  # in points (increased for better readability)
    
    # Margins
    top_margin: float = 20  # in mm
    bottom_margin: float = 20
    left_margin: float = 20
    right_margin: float = 20


@dataclass
class TemplateLayout:
    """Layout configuration for template"""
    # Section visibility
    show_sender: bool = True
    show_invoice_details: bool = True
    show_bill_to: bool = True
    show_line_items: bool = True
    
    # Section order
    section_order: SectionOrder = SectionOrder.SENDER_FIRST
    
    # Custom section order (if provided, overrides section_order)
    custom_order: Optional[list[str]] = None
    
    # Table styling
    show_table_grid: bool = True
    table_header_bg: bool = True
    table_total_bg: bool = True
    
    # Additional options
    show_logo: bool = False
    logo_path: Optional[str] = None
    logo_position: str = "top_right"  # top_left, top_right, top_center


@dataclass
class TemplateConfig:
    """Complete template configuration"""
    style: TemplateStyle = field(default_factory=TemplateStyle)
    layout: TemplateLayout = field(default_factory=TemplateLayout)
    
    # Template preset name (if using a preset)
    preset: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'TemplateConfig':
        """Create TemplateConfig from dictionary"""
        style_data = data.get('style', {})
        layout_data = data.get('layout', {})
        
        style = TemplateStyle(
            primary_color=style_data.get('primary_color', '#000000'),
            secondary_color=style_data.get('secondary_color', '#E0E0E0'),
            accent_color=style_data.get('accent_color', '#F0F0F0'),
            title_font_size=style_data.get('title_font_size', 16),
            header_font_size=style_data.get('header_font_size', 10),
            normal_font_size=style_data.get('normal_font_size', 9),
            info_font_size=style_data.get('info_font_size', 10),
            section_spacing=style_data.get('section_spacing', 1.0),
            table_padding=style_data.get('table_padding', 6),
            top_margin=style_data.get('top_margin', 20),
            bottom_margin=style_data.get('bottom_margin', 20),
            left_margin=style_data.get('left_margin', 20),
            right_margin=style_data.get('right_margin', 20),
        )
        
        layout = TemplateLayout(
            show_sender=layout_data.get('show_sender', True),
            show_invoice_details=layout_data.get('show_invoice_details', True),
            show_bill_to=layout_data.get('show_bill_to', True),
            show_line_items=layout_data.get('show_line_items', True),
            section_order=SectionOrder(layout_data.get('section_order', 'sender_first')),
            custom_order=layout_data.get('custom_order'),
            show_table_grid=layout_data.get('show_table_grid', True),
            table_header_bg=layout_data.get('table_header_bg', True),
            table_total_bg=layout_data.get('table_total_bg', True),
            show_logo=layout_data.get('show_logo', False),
            logo_path=layout_data.get('logo_path'),
            logo_position=layout_data.get('logo_position', 'top_right'),
        )
        
        return cls(
            style=style,
            layout=layout,
            preset=data.get('preset')
        )
    
    @classmethod
    def get_preset(cls, preset_name: str) -> 'TemplateConfig':
        """Get a preset template configuration"""
        presets = {
            'default': cls(),
            'minimal': cls(
                layout=TemplateLayout(
                    show_sender=False,
                    show_bill_to=False,
                )
            ),
            'compact': cls(
                style=TemplateStyle(
                    section_spacing=0.5,
                    normal_font_size=8,
                )
            ),
            'detailed': cls(
                style=TemplateStyle(
                    section_spacing=1.5,
                    normal_font_size=10,
                )
            ),
        }
        return presets.get(preset_name, cls())


def get_template_config(config: dict[str, Any]) -> TemplateConfig:
    """
    Get template configuration from main config
    
    Args:
        config: Main configuration dictionary
    
    Returns:
        TemplateConfig object
    """
    template_data = config.get('template', {})
    
    if template_data.get('preset'):
        # Use preset
        return TemplateConfig.get_preset(template_data['preset'])
    else:
        # Use custom template config
        return TemplateConfig.from_dict(template_data)

