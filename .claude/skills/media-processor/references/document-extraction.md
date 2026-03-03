# Document Extraction Reference

> Model IDs change frequently — check the [official models page](https://ai.google.dev/gemini-api/docs/models) for latest.

Convert documents to Markdown using Gemini's vision API via the `document_converter.py` script.

## Default Model

**`gemini-2.5-flash`** — cheapest option, sufficient for document extraction tasks.

For complex layouts (dense tables, multi-column, mixed media), consider `gemini-3-flash-preview`.

## What It Does

The `document_converter.py` script sends documents to Gemini's vision API and receives clean Markdown output. It preserves:
- Heading hierarchy
- Table structure (converted to Markdown tables)
- Lists, code blocks, and quotes
- Text extracted from embedded images (OCR)
- Overall document formatting and structure

## Supported Formats

| Format | Extensions | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Native vision processing, up to 1,000 pages |
| Images | `.jpeg`, `.jpg`, `.png`, `.webp`, `.heic` | OCR text extraction |
| Word | `.docx` | Uploaded as binary to Gemini |
| Excel | `.xlsx` | Tables converted to Markdown |
| PowerPoint | `.pptx` | Slides converted sequentially |
| Text | `.txt`, `.html`, `.md`, `.csv` | Direct text processing |

## CLI Usage

### Basic Conversion

```bash
# Convert single PDF (output: docs/assets/document-extraction.md)
python scripts/document_converter.py --input document.pdf

# Convert with auto-generated filename
python scripts/document_converter.py --input report.pdf --auto-name
# Output: docs/assets/report-extraction.md

# Specify custom output path
python scripts/document_converter.py --input document.pdf --output ./result.md
```

### Batch Processing

```bash
# Convert multiple files into one output
python scripts/document_converter.py --input doc1.pdf doc2.docx image.png

# Convert all PDFs in a directory
python scripts/document_converter.py --input ./documents/*.pdf --verbose
```

### Custom Prompts

```bash
# Extract only tables
python scripts/document_converter.py \
  --input spreadsheet.pdf \
  --prompt "Extract only the tables as markdown tables"

# Extract specific content
python scripts/document_converter.py \
  --input contract.pdf \
  --prompt "Extract all dates, dollar amounts, and party names"
```

### All Options

| Flag | Short | Description |
|------|-------|-------------|
| `--input` | `-i` | Input file(s) to convert (required, accepts multiple) |
| `--output` | `-o` | Output markdown file path |
| `--auto-name` | `-a` | Auto-generate output filename from input (e.g., `report.pdf` -> `report-extraction.md`) |
| `--model` | | Gemini model to use (default: `gemini-2.5-flash`) |
| `--prompt` | `-p` | Custom prompt for conversion |
| `--verbose` | `-v` | Show detailed progress output |

## Output

By default, output goes to `<project-root>/docs/assets/document-extraction.md`.

The output file contains:
- A header with conversion metadata (file count)
- Each input file as a separate section (`## filename.ext`)
- The extracted Markdown content
- Error details for any files that failed

### `--auto-name` Behavior

When processing a single file with `--auto-name`, the output filename is derived from the input:
- `report.pdf` -> `docs/assets/report-extraction.md`
- `quarterly-review.docx` -> `docs/assets/quarterly-review-extraction.md`

When processing multiple files, `--auto-name` is ignored and the default `document-extraction.md` is used.

## File Size Handling

- Files under 20MB are sent inline (faster)
- Files over 20MB are uploaded via the Gemini File API (2GB max per file)
- Uploaded files auto-delete after 48 hours
- Processing timeout: 5 minutes per file

## Error Handling

The script uses exponential backoff retry (3 attempts by default). Failed files are recorded in the output with error details rather than stopping the entire batch.

## Cost Estimation

PDF documents consume 258 tokens per page:
- 10-page document: ~2,580 tokens (~$0.003 with Flash)
- 100-page document: ~25,800 tokens (~$0.026 with Flash)
- 1,000-page document: ~258,000 tokens (~$0.258 with Flash)

Images vary by resolution (258-6,192 tokens depending on size).
