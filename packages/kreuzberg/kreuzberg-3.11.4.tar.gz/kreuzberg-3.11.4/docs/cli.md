# CLI Usage

The Kreuzberg CLI provides a convenient command-line interface for text extraction from documents.

## Installation

Install Kreuzberg with CLI support:

```bash
pip install kreuzberg[cli]
```

Or install all optional dependencies:

```bash
pip install kreuzberg[all]
```

## Basic Usage

### Extract from a file

```bash
kreuzberg extract document.pdf
```

### Extract to a file

```bash
kreuzberg extract document.pdf -o output.txt
```

### Extract from stdin

```bash
cat document.pdf | kreuzberg extract
# or
kreuzberg extract -
```

## Command-Line Options

### General Options

- `-o, --output PATH`: Output file path (default: stdout)
- `--output-format [text|json]`: Output format
- `--show-metadata`: Include metadata in output
- `-v, --verbose`: Verbose output for debugging

### Processing Options

- `--force-ocr`: Force OCR processing
- `--chunk-content`: Enable content chunking
- `--extract-tables`: Enable table extraction
- `--max-chars INTEGER`: Maximum characters per chunk (default: 2000)
- `--max-overlap INTEGER`: Maximum overlap between chunks (default: 100)

### OCR Backend Options

- `--ocr-backend [tesseract|easyocr|paddleocr|none]`: OCR backend to use

#### Tesseract Options

- `--tesseract-lang TEXT`: Language(s) (e.g., 'eng+deu')
- `--tesseract-psm INTEGER`: PSM mode (0-13)

#### EasyOCR Options

- `--easyocr-languages TEXT`: Language codes (comma-separated, e.g., 'en,de')

#### PaddleOCR Options

- `--paddleocr-languages TEXT`: Language codes (comma-separated, e.g., 'en,german')

## Configuration File

Kreuzberg can load configuration from a `pyproject.toml` file:

```toml
[tool.kreuzberg]
force_ocr = false
chunk_content = true
extract_tables = false
max_chars = 5000
ocr_backend = "tesseract"

[tool.kreuzberg.tesseract]
language = "eng+deu"
psm = 3

[tool.kreuzberg.gmft]
verbosity = 1
cell_required_confidence = 50
```

Use a specific config file:

```bash
kreuzberg extract document.pdf --config custom-config.toml
```

## Examples

### Basic text extraction

```bash
kreuzberg extract report.pdf -o report.txt
```

### OCR with specific language

```bash
kreuzberg extract scan.jpg --force-ocr --tesseract-lang deu
```

### Extract tables to JSON

```bash
kreuzberg extract spreadsheet.pdf --extract-tables --output-format json -o tables.json
```

### Extract with metadata

```bash
kreuzberg extract document.pdf --show-metadata --output-format json
```

### Using EasyOCR backend

```bash
kreuzberg extract image.png --ocr-backend easyocr --easyocr-languages en,de
```

### Extract with chunking

```bash
kreuzberg extract large-document.pdf --chunk-content --max-chars 1000
```

## Module Execution

You can also run Kreuzberg as a Python module:

```bash
python -m kreuzberg extract document.pdf
```

## Command Reference

### `kreuzberg extract`

Extract text from a document.

**Usage:**

```bash
kreuzberg extract [OPTIONS] [FILE]
```

**Arguments:**

- `FILE`: Path to document or '-' for stdin (optional, defaults to stdin)

### `kreuzberg config`

Show current configuration.

**Usage:**

```bash
kreuzberg config [OPTIONS]
```

**Options:**

- `--config PATH`: Configuration file path

### `kreuzberg --version`

Show version information.

## Error Handling

The CLI provides clear error messages:

- Exit code 0: Success
- Exit code 1: General error (parsing, validation, etc.)
- Exit code 2: Missing dependency error

Use `--verbose` for detailed error information and stack traces.
