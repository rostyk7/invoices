#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markup Renderer Module
Renders markup templates to ReportLab PDF elements
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

# Points are the base unit in ReportLab (1 pt = 1 unit)
pt = 1

from .markup_parser import MarkupElement, MarkupStyle, Align, get_data_field, format_field_value
from .invoice_calculator import calculate_totals


class MarkupRenderer:
    """Renders markup templates to PDF"""
    
    def __init__(self, font_name: str, font_bold: str, data: dict, currency_code: str = "PLN", currency_symbol: str = "zł"):
        """
        Initialize markup renderer
        
        Args:
            font_name: Font name for regular text
            font_bold: Font name for bold text
            data: Invoice data dictionary
            currency_code: Currency code
            currency_symbol: Currency symbol
        """
        self.font_name = font_name
        self.font_bold = font_bold
        self.data = data
        self.currency_code = currency_code
        self.currency_symbol = currency_symbol
        
        # Calculate totals if not present
        if 'totals' not in self.data:
            line_items = self.data.get('line_items', [])
            tax = self.data.get('tax', {})
            vat_rate = tax.get('vat_rate', 23.0)
            apply_to_net = tax.get('apply_to_net', True)
            self.data['totals'] = calculate_totals(line_items, vat_rate, apply_to_net)
        
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup base paragraph styles"""
        self.styles = getSampleStyleSheet()
        self.base_styles = {
            'normal': ParagraphStyle(
                'Normal',
                parent=self.styles['Normal'],
                fontName=self.font_name,
                fontSize=9,
            ),
            'bold': ParagraphStyle(
                'Bold',
                parent=self.styles['Normal'],
                fontName=self.font_bold,
                fontSize=9,
            ),
        }
    
    def _create_paragraph_style(self, markup_style: MarkupStyle) -> ParagraphStyle:
        """Create ParagraphStyle from MarkupStyle"""
        font_name = self.font_bold if markup_style.font_weight == 'bold' else self.font_name
        
        align_map = {
            Align.LEFT: TA_LEFT,
            Align.RIGHT: TA_RIGHT,
            Align.CENTER: TA_CENTER,
        }
        
        return ParagraphStyle(
            'Custom',
            parent=self.styles['Normal'],
            fontName=font_name,
            fontSize=markup_style.font_size,
            textColor=colors.HexColor(markup_style.color),
            alignment=align_map.get(markup_style.align, TA_LEFT),
            spaceAfter=markup_style.spacing * cm if markup_style.spacing else 0,
        )
    
    def _render_text(self, element: MarkupElement) -> Paragraph:
        """Render text element"""
        text = element.text or ""
        
        # Handle data fields
        if 'data-field' in element.attributes:
            field_path = element.attributes['data-field']
            format_type = element.attributes.get('data-format')
            value = get_data_field(self.data, field_path, "")
            text = format_field_value(value, format_type, self.currency_code, self.currency_symbol)
        
        # Handle label + field pattern
        if 'data-label' in element.attributes and 'data-field' in element.attributes:
            label = element.attributes['data-label']
            field_path = element.attributes['data-field']
            format_type = element.attributes.get('data-format')
            value = get_data_field(self.data, field_path, "")
            formatted_value = format_field_value(value, format_type, self.currency_code, self.currency_symbol)
            text = f"{label}{formatted_value}"
        
        # Apply style
        style = self._create_paragraph_style(element.style)
        
        # Handle bold in text
        if element.style.font_weight == 'bold' and text:
            text = f"<b>{text}</b>"
        
        return Paragraph(text, style)
    
    def _render_section(self, element: MarkupElement) -> list:
        """Render section element"""
        elements = []
        
        # Render children
        for child in element.children:
            rendered = self._render_element(child)
            if rendered:
                if isinstance(rendered, list):
                    elements.extend(rendered)
                else:
                    elements.append(rendered)
        
        # Add spacing if specified
        spacing = element.style.spacing
        if spacing > 0:
            elements.append(Spacer(1, spacing * cm))
        
        return elements
    
    def _render_table(self, element: MarkupElement) -> Table:
        """Render table element"""
        table_data = []
        
        # Process header if exists
        header_element = next((child for child in element.children if child.tag == 'header'), None)
        if header_element:
            header_row = []
            for cell in header_element.children:
                if cell.tag == 'cell':
                    text = cell.text or ""
                    if 'data-field' in cell.attributes:
                        field_path = cell.attributes['data-field']
                        text = str(get_data_field(self.data, field_path, ""))
                    style = self._create_paragraph_style(cell.style)
                    header_row.append(Paragraph(text, style))
            if header_row:
                table_data.append(header_row)
        
        # Process rows
        rows_element = next((child for child in element.children if child.tag == 'rows'), None)
        if rows_element and 'data-field' in rows_element.attributes:
            # Iterate over array field
            field_path = rows_element.attributes['data-field']
            items = get_data_field(self.data, field_path, [])
            
            if isinstance(items, list):
                for item in items:
                    row = []
                    for cell_template in rows_element.children:
                        if cell_template.tag == 'cell':
                            text = cell_template.text or ""
                            if 'data-field' in cell_template.attributes:
                                # Resolve field relative to item
                                field_path_cell = cell_template.attributes['data-field']
                                format_type = cell_template.attributes.get('data-format')
                                value = item.get(field_path_cell) if isinstance(item, dict) else None
                                text = format_field_value(value, format_type, self.currency_code, self.currency_symbol)
                            style = self._create_paragraph_style(cell_template.style)
                            row.append(Paragraph(text, style))
                    if row:
                        table_data.append(row)
        
        # Regular rows (not from data array)
        for row_element in element.children:
            if row_element.tag == 'row':
                row = []
                for cell in row_element.children:
                    if cell.tag == 'cell':
                        # Handle nested text elements or direct cell content
                        if cell.children:
                            # Cell contains child elements (like text with formatting)
                            cell_texts = []
                            for child in cell.children:
                                if child.tag == 'text':
                                    text = child.text or ""
                                    if 'data-field' in child.attributes:
                                        field_path = child.attributes['data-field']
                                        format_type = child.attributes.get('data-format')
                                        value = get_data_field(self.data, field_path)
                                        text = format_field_value(value, format_type, self.currency_code, self.currency_symbol)
                                    cell_texts.append(text)
                                else:
                                    cell_texts.append(child.text or "")
                            text = " ".join(cell_texts)
                        else:
                            text = cell.text or ""
                            if 'data-field' in cell.attributes:
                                field_path = cell.attributes['data-field']
                                format_type = cell.attributes.get('data-format')
                                value = get_data_field(self.data, field_path)
                                text = format_field_value(value, format_type, self.currency_code, self.currency_symbol)
                        
                        style = self._create_paragraph_style(cell.style)
                        row.append(Paragraph(text, style))
                if row:
                    table_data.append(row)
        
        # Get column widths
        col_widths = None
        if 'col-widths' in element.attributes:
            widths_str = element.attributes['col-widths']
            col_widths = [float(w.strip()) * cm for w in widths_str.split(',')]
        
        if not table_data:
            return None
        
        # Create table
        table = Table(table_data, colWidths=col_widths)
        
        # Apply table styles
        table_style = []
        
        # Header styling
        if header_element and len(table_data) > 0:
            bg_color = element.attributes.get('background', '#E0E0E0')
            table_style.append(('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(bg_color)))
            table_style.append(('FONTNAME', (0, 0), (-1, 0), self.font_bold))
        
        # Grid
        if element.attributes.get('grid', 'true').lower() == 'true':
            table_style.append(('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')))
        
        # Padding
        padding = float(element.attributes.get('padding', '6'))
        table_style.extend([
            ('LEFTPADDING', (0, 0), (-1, -1), padding),
            ('RIGHTPADDING', (0, 0), (-1, -1), padding),
            ('TOPPADDING', (0, 0), (-1, -1), padding),
            ('BOTTOMPADDING', (0, 0), (-1, -1), padding),
        ])
        
        # Alignment (default: left for first column, right for others)
        table_style.append(('ALIGN', (0, 0), (-1, -1), 'LEFT'))
        if len(table_data[0]) > 1:
            table_style.append(('ALIGN', (1, 0), (1, -1), 'RIGHT'))
        
        table.setStyle(TableStyle(table_style))
        return table
    
    def _render_element(self, element: MarkupElement):
        """Render a markup element"""
        if element.tag == 'text':
            return self._render_text(element)
        elif element.tag == 'section':
            return self._render_section(element)
        elif element.tag == 'table':
            return self._render_table(element)
        elif element.tag == 'spacer':
            spacing = float(element.attributes.get('height', '1')) * cm
            return Spacer(1, spacing)
        elif element.tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            # Heading element
            text = element.text or ""
            if 'data-field' in element.attributes:
                field_path = element.attributes['data-field']
                text = str(get_data_field(self.data, field_path, ""))
            
            # Adjust font size based on heading level
            level = int(element.tag[1])
            font_size = 16 - (level - 1) * 2
            element.style.font_size = font_size
            element.style.font_weight = 'bold'
            
            return self._render_text(element)
        else:
            # Default: render as text with children
            if element.children:
                return self._render_section(element)
            else:
                return self._render_text(element)
    
    def render(self, root_element: MarkupElement) -> list:
        """
        Render markup template to PDF elements
        
        Args:
            root_element: Root MarkupElement
        
        Returns:
            List of ReportLab elements
        """
        elements = []
        
        # Render all children of root
        for child in root_element.children:
            rendered = self._render_element(child)
            if rendered:
                if isinstance(rendered, list):
                    elements.extend(rendered)
                else:
                    elements.append(rendered)
        
        return elements

