#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Module for Invoice Generator
Command-line interface for generating invoices
"""

import sys
import argparse

# Ensure UTF-8 encoding for stdout
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from .invoice_generator import generate_invoice


def main():
    """
    Main CLI entry point
    """
    parser = argparse.ArgumentParser(
        description='Generate invoice PDF from configuration file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate invoice using default config file
  invoice-generate
  
  # Generate invoice with custom config file
  invoice-generate -c my_config.json
  
  # Generate invoice with custom output filename
  invoice-generate -o output.pdf
        """
    )
    
    parser.add_argument(
        '-c', '--config',
        default='invoice_config.json',
        help='Path to configuration JSON file (default: invoice_config.json)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output PDF filename (overrides config file)'
    )
    
    args = parser.parse_args()
    
    try:
        output_file = generate_invoice(config_file=args.config, output_filename=args.output)
        print(f"Invoice generated successfully: {output_file}")
        sys.exit(0)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error generating invoice: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

