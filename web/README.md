# Invoice Generator Web Application

Simple web interface for generating invoices using the invoice-generator library.

## Features

- Modern, clean HTML interface
- JSON configuration input
- Real-time validation
- Generate and download PDF invoices
- Example configuration loader

## Setup

### Install Dependencies

```bash
cd web
uv pip install -r requirements.txt
```

### Install Library from Local Path

The web app uses the library from the monorepo:

```bash
# From web directory
cd ..
uv pip install -e lib/
```

Or if already in venv:
```bash
uv pip install -e ./lib
```

## Run the Application

### Option 1: Using the run script (Recommended)

```bash
cd web
./run.sh
```

### Option 2: Manual setup

```bash
# From root of monorepo
cd web

# Install web dependencies
uv pip install -r requirements.txt

# Install library from local path
uv pip install -e ../lib/

# Run the application
python app.py
```

### Option 3: With uvicorn directly

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Then open in browser: **http://localhost:8000**

## Usage

1. Open the web interface in your browser
2. Paste your invoice configuration JSON (or click "Load Example Configuration")
3. Click "Validate & Preview" to check your config
4. Click "Generate Invoice PDF" to create and download the invoice

## API Endpoints

- `GET /` - Main HTML page
- `POST /api/generate` - Generate invoice PDF (returns file for download)
- `POST /api/preview` - Validate configuration and preview totals (returns JSON)

## Example Configuration

See the "Load Example Configuration" button in the web interface for a complete example.

