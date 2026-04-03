import re
import fitz  # PyMuPDF


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing unwanted spacing artifacts.
    """
    if not text:
        return ""

    text = text.replace("\u00a0", " ")   # non-breaking space
    text = text.replace("\xad", "")      # soft hyphen
    text = text.replace("\uf0b7", "•")   # common bullet artifact
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def detect_bold(font_name: str) -> bool:
    """
    Heuristic bold detection from font name.
    """
    font_name = (font_name or "").lower()
    bold_keywords = ["bold", "black", "heavy", "demi", "semibold"]
    return any(keyword in font_name for keyword in bold_keywords)


def detect_italic(font_name: str) -> bool:
    """
    Heuristic italic detection from font name.
    """
    font_name = (font_name or "").lower()
    italic_keywords = ["italic", "oblique"]
    return any(keyword in font_name for keyword in italic_keywords)


def extract_lines_with_format(pdf_path: str):
    """
    Extract text line-by-line from a PDF along with formatting and layout metadata.

    Returns:
        extracted_lines: list of dictionaries
        font_sizes: list of font sizes for heading inference
    """
    doc = fitz.open(pdf_path)
    extracted_lines = []
    font_sizes = []

    try:
        for page_number, page in enumerate(doc, start=1):
            page_dict = page.get_text("dict")
            blocks = page_dict.get("blocks", [])

            for block_idx, block in enumerate(blocks):
                if "lines" not in block:
                    continue

                for line_idx, line in enumerate(block.get("lines", [])):
                    spans = line.get("spans", [])
                    if not spans:
                        continue

                    span_items = []
                    combined_text_parts = []
                    span_sizes = []

                    for span in spans:
                        raw_text = span.get("text", "")
                        cleaned_span_text = clean_text(raw_text)

                        # Skip empty spans after cleaning
                        if not cleaned_span_text:
                            continue

                        font_name = span.get("font", "")
                        size = float(span.get("size", 0))

                        span_data = {
                            "text": cleaned_span_text,
                            "font": font_name,
                            "size": size,
                            "bbox": span.get("bbox"),
                            "is_bold": detect_bold(font_name),
                            "is_italic": detect_italic(font_name),
                        }

                        span_items.append(span_data)
                        combined_text_parts.append(cleaned_span_text)
                        span_sizes.append(size)

                    if not span_items:
                        continue

                    line_text = " ".join(combined_text_parts)
                    line_text = re.sub(r"\s+", " ", line_text).strip()

                    if not line_text:
                        continue

                    avg_size = sum(span_sizes) / len(span_sizes)
                    is_bold = any(span["is_bold"] for span in span_items)
                    is_italic = any(span["is_italic"] for span in span_items)

                    extracted_lines.append({
                        "page": page_number,
                        "block_idx": block_idx,
                        "line_idx": line_idx,
                        "text": line_text,
                        "font_size": avg_size,
                        "is_bold": is_bold,
                        "is_italic": is_italic,
                        "bbox": line.get("bbox"),
                        "spans": span_items,
                    })

                    font_sizes.append(avg_size)

    finally:
        doc.close()

    return extracted_lines, font_sizes