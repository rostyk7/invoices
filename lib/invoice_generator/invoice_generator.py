#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Invoice Generator Module
Main API for generating invoices
"""

import sys

# Ensure UTF-8 encoding for stdout
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from .fonts import register_unicode_fonts
from .invoice_config import load_config, validate_config
from .invoice_renderer import InvoiceRenderer


def generate_invoice(config=None, output_filename=None, config_file=None):
    """
    Generate an invoice PDF from configuration
    
    Args:
        config: Configuration dictionary. If None, loads from config_file.
        output_filename: Output PDF filename. If None, uses config value.
        config_file: Path to configuration JSON file (used if config is None)
    
    Returns:
        str: Output filename of generated PDF
    """
    # Load config if not provided
    if config is None:
        if config_file is None:
            config_file = "invoice_config.json"
        config = load_config(config_file)
    
    # Validate configuration
    validate_config(config)
    
    # Use output filename from config if not provided
    if output_filename is None:
        output_filename = config.get('output', {}).get('filename', 'invoice_output.pdf')
    
    # Register fonts
    font_name, font_bold = register_unicode_fonts()
    
    # Get template configuration if provided
    from .template_config import get_template_config
    template_config = get_template_config(config)
    
    # Create renderer and generate PDF
    renderer = InvoiceRenderer(font_name, font_bold, template_config)
    renderer.render(config, output_filename)
    
    return output_filename


class InvoiceGenerator:
    """
    Invoice Generator class for programmatic use
    """
    
    def __init__(self, config=None, config_file=None):
        """
        Initialize invoice generator
        
        Args:
            config: Configuration dictionary
            config_file: Path to configuration JSON file
        """
        if config is None:
            if config_file is None:
                config_file = "invoice_config.json"
            config = load_config(config_file)
        
        validate_config(config)
        self.config = config
        
        # Register fonts
        self.font_name, self.font_bold = register_unicode_fonts()
        
        # Get template configuration
        from .template_config import get_template_config
        template_config = get_template_config(config)
        
        self.renderer = InvoiceRenderer(self.font_name, self.font_bold, template_config)
    
    def generate(self, output_filename=None):
        """
        Generate invoice PDF
        
        Args:
            output_filename: Output PDF filename. If None, uses config value.
        
        Returns:
            str: Output filename of generated PDF
        """
        if output_filename is None:
            output_filename = self.config.get('output', {}).get('filename', 'invoice_output.pdf')
        
        self.renderer.render(self.config, output_filename)
        return output_filename
    
    def update_config(self, config_updates):
        """
        Update configuration
        
        Args:
            config_updates: Dictionary with configuration updates
        """
        # Deep merge updates
        def deep_update(base_dict, update_dict):
            for key, value in update_dict.items():
                if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_update(self.config, config_updates)
        validate_config(self.config)

