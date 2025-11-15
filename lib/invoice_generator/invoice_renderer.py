#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Invoice Renderer Module
Handles PDF layout and rendering (UI layer)
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT

from .invoice_calculator import calculate_totals, format_currency, format_amount
from .template_config import get_template_config, TemplateConfig, TemplateStyle


class InvoiceRenderer:
    """Handles PDF rendering and layout"""
    
    def __init__(self, font_name, font_bold, template_config: TemplateConfig = None):
        """
        Initialize renderer with fonts and optional template configuration
        
        Args:
            font_name: Font name for regular text
            font_bold: Font name for bold text
            template_config: Optional template configuration for dynamic layouts
        """
        self.font_name = font_name
        self.font_bold = font_bold
        self.template_config = template_config or TemplateConfig()
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup paragraph styles based on template configuration"""
        styles = getSampleStyleSheet()
        style = self.template_config.style
        
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=style.title_font_size,
            textColor=colors.HexColor(style.primary_color),
            fontName=self.font_bold,
            spaceAfter=14,  # Increased for better separation
        )
        
        self.header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontSize=style.header_font_size,
            textColor=colors.HexColor(style.primary_color),
            fontName=self.font_bold,
            spaceAfter=6,  # Increased for better separation
        )
        
        self.normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=style.normal_font_size,
            textColor=colors.HexColor(style.primary_color),
            fontName=self.font_name,
            spaceAfter=5,  # Slightly increased for better line spacing
            leading=style.normal_font_size * 1.2,  # Better line height (1.2x font size)
        )
        
        self.invoice_info_style = ParagraphStyle(
            'InvoiceInfoStyle',
            parent=styles['Normal'],
            fontSize=style.info_font_size,
            textColor=colors.HexColor(style.primary_color),
            fontName=self.font_name,
            spaceAfter=5,  # Slightly increased
            leading=style.info_font_size * 1.2,  # Better line height
            alignment=TA_LEFT,
        )
    
    def _render_sender_section(self, sender):
        """Render sender information section"""
        sender_data = []
        if sender.get('name'):
            sender_data.append([Paragraph(sender['name'], self.title_style)])
        if sender.get('nip'):
            sender_data.append([Paragraph(f"NIP: {sender['nip']}", self.normal_style)])
        if sender.get('bank_account_number'):
            sender_data.append([Paragraph(f"Bank Account Number: {sender['bank_account_number']}", self.normal_style)])
        if sender.get('bic'):
            sender_data.append([Paragraph(f"BIC: {sender['bic']}", self.normal_style)])
        if sender.get('account_holder_name'):
            sender_data.append([Paragraph(f"Account Holder Name: {sender['account_holder_name']}", self.normal_style)])
        if sender.get('address'):
            sender_data.append([Paragraph(f"Address: {sender['address']}", self.normal_style)])
        if sender.get('phone'):
            sender_data.append([Paragraph(f"Phone Number: {sender['phone']}", self.normal_style)])
        if sender.get('email'):
            sender_data.append([Paragraph(f"Email: {sender['email']}", self.normal_style)])
        
        sender_table = Table(sender_data, colWidths=[16*cm])
        sender_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('SPACEAFTER', (0, -1), (-1, -1), 6),  # Extra space after last row
        ]))
        
        return sender_table
    
    def _render_invoice_details_section(self, invoice, totals, currency_code, currency_symbol):
        """Render invoice details section"""
        invoice_details = []
        if invoice.get('invoice_number'):
            invoice_details.append([
                Paragraph("<b>Invoice Number:</b>", self.invoice_info_style),
                Paragraph(invoice['invoice_number'], self.invoice_info_style)
            ])
        if invoice.get('date'):
            invoice_details.append([
                Paragraph("<b>Date:</b>", self.invoice_info_style),
                Paragraph(invoice['date'], self.invoice_info_style)
            ])
        if invoice.get('due_date'):
            invoice_details.append([
                Paragraph("<b>Due Date:</b>", self.invoice_info_style),
                Paragraph(invoice['due_date'], self.invoice_info_style)
            ])
        if invoice.get('service_end_date'):
            invoice_details.append([
                Paragraph("<b>Service End Date:</b>", self.invoice_info_style),
                Paragraph(invoice['service_end_date'], self.invoice_info_style)
            ])
        
        # Balance Due (Total)
        balance_due = format_currency(totals['total'], currency_code, currency_symbol)
        invoice_details.append([
            Paragraph("<b>Balance Due:</b>", self.invoice_info_style),
            Paragraph(f"<b>{balance_due}</b>", self.invoice_info_style)
        ])
        
        invoice_table = Table(invoice_details, colWidths=[4*cm, 12*cm])
        invoice_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('SPACEAFTER', (0, -1), (-1, -1), 6),  # Extra space after last row
        ]))
        
        return invoice_table
    
    def _render_bill_to_section(self, bill_to):
        """Render BILL TO section"""
        recipient_data = []
        if bill_to.get('company_name'):
            recipient_data.append([Paragraph(f"Company Name: {bill_to['company_name']}", self.normal_style)])
        if bill_to.get('full_legal_name'):
            recipient_data.append([Paragraph(f"Full Legal Name: {bill_to['full_legal_name']}", self.normal_style)])
        if bill_to.get('address'):
            recipient_data.append([Paragraph(f"Address: {bill_to['address']}", self.normal_style)])
        if bill_to.get('vat_number'):
            recipient_data.append([Paragraph(f"VAT Number: {bill_to['vat_number']}", self.normal_style)])
        
        recipient_table = Table(recipient_data, colWidths=[16*cm])
        recipient_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('SPACEAFTER', (0, -1), (-1, -1), 6),  # Extra space after last row
        ]))
        
        # Add spacing after header
        header_para = Paragraph("<b>BILL TO</b>", self.header_style)
        return header_para, recipient_table
    
    def _render_line_items_table(self, line_items, totals, vat_rate, currency_code, currency_symbol):
        """Render itemized table section"""
        # Table data - dynamic line items
        table_data = [
            [Paragraph("<b>Description</b>", self.normal_style), 
             Paragraph(f"<b>Amount ({currency_code})</b>", self.normal_style)]
        ]
        
        # Add line items
        for item in line_items:
            description = item.get('description', '')
            amount = item.get('amount', 0)
            formatted_amount = format_amount(amount, currency_code, currency_symbol)
            table_data.append([
                Paragraph(description, self.normal_style),
                Paragraph(formatted_amount, self.normal_style)
            ])
        
        # Add Net Amount row
        table_data.append([
            Paragraph("Net Amount", self.normal_style),
            Paragraph(format_amount(totals['net_amount'], currency_code, currency_symbol), self.normal_style)
        ])
        
        # Add VAT row
        table_data.append([
            Paragraph(f"VAT ({vat_rate}%)", self.normal_style),
            Paragraph(format_amount(totals['vat_amount'], currency_code, currency_symbol), self.normal_style)
        ])
        
        # Add Total row
        table_data.append([
            Paragraph("<b>Total</b>", self.normal_style),
            Paragraph(f"<b>{format_amount(totals['total'], currency_code, currency_symbol)}</b>", self.normal_style)
        ])
        
        # Create table
        itemized_table = Table(table_data, colWidths=[12*cm, 4*cm])
        
        # Table style - use template configuration
        layout = self.template_config.layout
        style = self.template_config.style
        
        table_style_rules = [
            # Header row
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(style.primary_color)),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), self.font_bold),
            ('FONTSIZE', (0, 0), (-1, 0), style.normal_font_size),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 1), (-1, -1), style.normal_font_size),
            ('TOPPADDING', (0, 1), (-1, -1), int(style.table_padding)),
            ('BOTTOMPADDING', (0, 1), (-1, -1), int(style.table_padding)),
            ('LEFTPADDING', (0, 0), (-1, -1), int(style.table_padding)),
            ('RIGHTPADDING', (0, 0), (-1, -1), int(style.table_padding)),
            # Better row spacing
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [None, colors.HexColor('#FAFAFA')]),  # Alternating row colors (subtle)
        ]
        
        # Add header background if enabled
        if layout.table_header_bg:
            table_style_rules.insert(0, ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(style.secondary_color)))
        
        # Add grid lines if enabled
        if layout.show_table_grid:
            table_style_rules.append(('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')))
        
        # Add total row styling
        if layout.table_total_bg:
            table_style_rules.append(('BACKGROUND', (0, -1), (-1, -1), colors.HexColor(style.accent_color)))
        table_style_rules.extend([
            ('FONTNAME', (0, -1), (-1, -1), self.font_bold),
            ('TOPPADDING', (0, -1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
        ])
        
        itemized_table.setStyle(TableStyle(table_style_rules))
        
        return itemized_table
    
    def render(self, config, output_filename):
        """
        Render complete invoice PDF
        
        Args:
            config: Configuration dictionary
            output_filename: Output PDF filename
        """
        # Extract configuration
        sender = config.get('sender', {})
        invoice = config.get('invoice', {})
        bill_to = config.get('bill_to', {})
        line_items = config.get('line_items', [])
        tax = config.get('tax', {})
        currency = config.get('currency', {})
        
        vat_rate = tax.get('vat_rate', 23.0)
        apply_to_net = tax.get('apply_to_net', True)
        currency_code = currency.get('code', 'PLN')
        currency_symbol = currency.get('symbol', 'zł')
        
        # Calculate totals (business logic)
        totals = calculate_totals(line_items, vat_rate, apply_to_net)
        
        # Get template config from main config if not already set
        if not self.template_config.preset:
            from .template_config import get_template_config
            self.template_config = get_template_config(config)
            self._setup_styles()  # Re-setup styles with new config
        
        layout = self.template_config.layout
        style = self.template_config.style
        
        # Create the PDF document with template margins
        doc = SimpleDocTemplate(
            output_filename,
            pagesize=A4,
            rightMargin=style.right_margin*mm,
            leftMargin=style.left_margin*mm,
            topMargin=style.top_margin*mm,
            bottomMargin=style.bottom_margin*mm
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Determine section order
        if layout.custom_order:
            section_order = layout.custom_order
        else:
            if layout.section_order.value == 'invoice_first':
                section_order = ['invoice_details', 'sender', 'bill_to', 'line_items']
            elif layout.section_order.value == 'bill_to_first':
                section_order = ['bill_to', 'invoice_details', 'sender', 'line_items']
            else:  # sender_first (default)
                section_order = ['sender', 'invoice_details', 'bill_to', 'line_items']
        
        # Render sections based on template configuration
        spacer = Spacer(1, style.section_spacing*cm)
        
        for section in section_order:
            if section == 'sender' and layout.show_sender:
                elements.append(self._render_sender_section(sender))
                elements.append(spacer)
            elif section == 'invoice_details' and layout.show_invoice_details:
                elements.append(self._render_invoice_details_section(invoice, totals, currency_code, currency_symbol))
                elements.append(spacer)
            elif section == 'bill_to' and layout.show_bill_to:
                bill_to_header, bill_to_table = self._render_bill_to_section(bill_to)
                elements.append(bill_to_header)
                elements.append(bill_to_table)
                elements.append(spacer)
            elif section == 'line_items' and layout.show_line_items:
                elements.append(self._render_line_items_table(line_items, totals, vat_rate, currency_code, currency_symbol))
        
        # Build PDF
        doc.build(elements)

