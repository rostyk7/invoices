# Invoice Generator Monorepo

Monorepo containing the invoice generator library and web application.

## Structure

```
invoices/
├── lib/                    # Invoice generator library
│   ├── invoice_generator/  # Main package
│   └── pyproject.toml      # Library configuration
├── web/                    # Web application
│   ├── app.py             # FastAPI application
│   ├── templates/         # HTML templates
│   └── requirements.txt   # Web app dependencies
└── invoice_config.json    # Example configuration
```

## Library (lib/)

The invoice generator library - can be used independently or installed in other projects.

See `lib/README.md` for library documentation.

## Web Application (web/)

Simple web interface for generating invoices.

### Quick Start

```bash
# Install web app dependencies
cd web
uv pip install -r requirements.txt

# Install library from local path
uv pip install -e ../lib

# Run the application
python app.py
# Or: uvicorn app:app --reload
```

Open http://localhost:8000 in your browser.

See `web/README.md` for detailed documentation.

## Usage

### Markup Templates (New!)

Create custom invoice layouts using XML-like markup (similar to HTML):

```python
from invoice_generator import generate_from_markup_file

# Generate from markup template file
generate_from_markup_file(
    markup_file='my_template.xml',
    config=invoice_config,
    output_filename='invoice.pdf'
)
```

**Features:**
- Write templates like HTML (sections, tables, text elements)
- Data binding with `data-field` attributes (e.g., `sender.name`)
- Full control over layout, styling, and structure

See [MARKUP_GUIDE.md](MARKUP_GUIDE.md) for complete documentation and examples.

### As a Library

```python
from invoice_generator import generate_invoice

generate_invoice(config_file="invoice_config.json", output_filename="invoice.pdf")
```

### As a Web Application

1. Start the web server
2. Open browser to http://localhost:8000
3. Paste JSON configuration
4. Generate and download invoice
