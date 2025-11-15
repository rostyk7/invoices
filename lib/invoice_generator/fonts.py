#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Font Registration Module
Handles Unicode font registration for cross-platform support
"""

import os
import platform
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily


def register_unicode_fonts():
    """
    Register Unicode fonts for full Polish character support.
    Cross-platform: Works on macOS, Linux, and Windows.
    
    Returns:
        tuple: (FONT_NAME, FONT_BOLD) - Registered font names
    """
    system = platform.system()
    unicode_font_found = False
    unicode_font_bold_found = False
    FONT_NAME = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'
    
    try:
        # Define font search paths based on platform
        if system == 'Darwin':  # macOS
            font_paths = [
                ('/System/Library/Fonts/Supplemental/Arial Unicode.ttf', 'ArialUnicode'),
                ('/Library/Fonts/DejaVuSans.ttf', 'DejaVuSans'),
                ('/Library/Fonts/DejaVuSans-Bold.ttf', 'DejaVuSans-Bold'),
            ]
            # Try Arial Unicode first on macOS
            arial_unicode = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
            if os.path.exists(arial_unicode):
                pdfmetrics.registerFont(TTFont('ArialUnicode', arial_unicode))
                unicode_font_found = True
                FONT_NAME = 'ArialUnicode'
        elif system == 'Linux':
            # Linux: DejaVu fonts are commonly installed in these locations
            font_paths = [
                ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'DejaVuSans'),
                ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'DejaVuSans-Bold'),
                ('/usr/share/fonts/TTF/DejaVuSans.ttf', 'DejaVuSans'),
                ('/usr/share/fonts/TTF/DejaVuSans-Bold.ttf', 'DejaVuSans-Bold'),
                ('/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf', 'DejaVuSans'),
                ('/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf', 'DejaVuSans-Bold'),
                ('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', 'LiberationSans'),
                ('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 'LiberationSans-Bold'),
            ]
        elif system == 'Windows':
            font_paths = [
                ('C:\\Windows\\Fonts\\arialuni.ttf', 'ArialUnicode'),
                ('C:\\Windows\\Fonts\\DejaVuSans.ttf', 'DejaVuSans'),
                ('C:\\Windows\\Fonts\\DejaVuSans-Bold.ttf', 'DejaVuSans-Bold'),
            ]
            # Try Arial Unicode first on Windows
            arial_unicode = 'C:\\Windows\\Fonts\\arialuni.ttf'
            if os.path.exists(arial_unicode):
                pdfmetrics.registerFont(TTFont('ArialUnicode', arial_unicode))
                unicode_font_found = True
                FONT_NAME = 'ArialUnicode'
        else:
            # Unknown platform - try common paths
            font_paths = [
                ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'DejaVuSans'),
                ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'DejaVuSans-Bold'),
            ]
        
        # Try to find and register fonts
        if not unicode_font_found:
            for font_path, font_name in font_paths:
                try:
                    if os.path.exists(font_path):
                        if font_name in ['DejaVuSans', 'LiberationSans']:
                            pdfmetrics.registerFont(TTFont(font_name, font_path))
                            FONT_NAME = font_name
                            unicode_font_found = True
                        elif font_name in ['DejaVuSans-Bold', 'LiberationSans-Bold']:
                            pdfmetrics.registerFont(TTFont(font_name, font_path))
                            FONT_BOLD = font_name
                            unicode_font_bold_found = True
                        if unicode_font_found and unicode_font_bold_found:
                            break
                except Exception:
                    continue
        
        # Try to find bold version if we found regular but not bold
        if unicode_font_found and not unicode_font_bold_found:
            for font_path, font_name in font_paths:
                if font_name.endswith('-Bold') and FONT_NAME.replace('-Bold', '') in font_name:
                    try:
                        if os.path.exists(font_path):
                            pdfmetrics.registerFont(TTFont(font_name, font_path))
                            FONT_BOLD = font_name
                            unicode_font_bold_found = True
                            break
                    except Exception:
                        continue
        
        # If no Unicode font found, use Helvetica (limited Polish support)
        if not unicode_font_found:
            print("Warning: Unicode font not found. Polish characters may not render correctly.")
            print(f"  To fix this on Linux, install fonts-dejavu: sudo apt-get install fonts-dejavu")
            print(f"  Or on RHEL/CentOS: sudo yum install dejavu-sans-fonts")
        else:
            # For Arial Unicode, use it for both regular and bold to ensure all Unicode characters render
            if FONT_NAME == 'ArialUnicode':
                FONT_BOLD = 'ArialUnicode'
            elif not unicode_font_bold_found:
                # If bold not found, use regular for bold too
                FONT_BOLD = FONT_NAME
            registerFontFamily(FONT_NAME, normal=FONT_NAME, bold=FONT_BOLD)
            print(f"Using Unicode font: {FONT_NAME} / {FONT_BOLD}")
            
    except Exception as e:
        # Fallback to Helvetica if font registration fails
        print(f"Note: Using default fonts. Unicode support may be limited: {e}")
    
    return FONT_NAME, FONT_BOLD

