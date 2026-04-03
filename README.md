# PDF to Markdown Converter

## Overview

This project is a CPU-based PDF to Markdown converter built using Python. It takes a PDF file as input, extracts its textual and formatting information, and converts it into structured Markdown format.

The goal of this project is to demonstrate clean software design, file processing, and structured text conversion without relying on GPU or paid APIs.

---

## Features

* Extracts text from digital PDF files
* Detects headings based on font size hierarchy
* Converts paragraphs into readable Markdown
* Detects bullet points and numbered lists
* Supports basic inline formatting (bold, italic)
* CLI-based interface for easy usage
* Lightweight and CPU-only

### Bonus (Partially Supported / Planned)

* Table detection (heuristic, limited)
* OCR fallback for scanned PDFs (optional extension)
* Improved layout handling for multi-column PDFs

---

## Tech Stack

* Python 3
* PyMuPDF (fitz) – PDF parsing and text extraction

---

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-link>
cd pdf-to-markdown
```

### 2. Create virtual environment (recommended)

```bash
python -m venv venv
```

Activate it:

* Windows:

```bash
venv\Scripts\activate
```

* Mac/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

Run the CLI tool:

```bash
python app.py input.pdf output.md
```

### Example

```bash
python app.py samples/sample.pdf samples/output.md
```

After execution, the Markdown file will be generated at the specified location.

---

## Project Structure

```
.
├── app.py              # CLI entry point
├── parser.py           # PDF parsing and text extraction
├── formatter.py        # Markdown conversion logic
├── README.md
├── requirements.txt
└── samples/
    ├── sample.pdf
    └── output.md
```

---

## Approach

The conversion pipeline consists of three main stages:

### 1. Parsing (parser.py)

* Uses PyMuPDF to read the PDF
* Extracts text line-by-line
* Captures metadata such as:

  * font size
  * bold/italic style
  * page number

### 2. Structuring (formatter.py)

* Determines heading levels using relative font size
* Identifies lists using regex patterns
* Groups lines into paragraphs
* Applies inline formatting

### 3. Output Generation

* Converts structured content into Markdown
* Writes output to `.md` file

---

## Design Decisions

* **CPU-only approach**: avoids heavy dependencies and keeps execution lightweight
* **Font-size-based heading detection**: simple yet effective for most PDFs
* **Modular design**:

  * parser handles extraction
  * formatter handles transformation
* **Heuristic-based processing** instead of ML models to keep it transparent and explainable

---

## Limitations

This tool is designed as a lightweight solution and has some limitations:

* Works best on **digitally generated PDFs**, not scanned documents
* Multi-column layouts may produce incorrect reading order
* Table extraction is limited and may not preserve structure perfectly
* Inline formatting is approximate (based on font metadata)
* Complex elements like equations, figures, and code blocks are not fully supported

---

## Sample Output

Sample input and output files are provided in the `samples/` directory.

Example conversion includes:

* Research paper PDF → structured Markdown
* Headings and sections preserved
* Paragraphs cleaned and merged

---

## Future Improvements

* Better table extraction and Markdown table formatting
* OCR integration for scanned PDFs
* Improved multi-column layout detection
* Code block detection using font/style heuristics
* Smart post-processing (LLM-based cleanup)

---

## Conclusion

This project focuses on clarity, simplicity, and modular design. While not perfect, it demonstrates a practical approach to PDF parsing and structured content transformation, with clear opportunities for future improvements.

---
