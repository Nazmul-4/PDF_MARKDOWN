import re
from collections import Counter


def is_list_item(text: str) -> bool:
    """
    Detect common bullet and numbered list formats.
    """
    patterns = [
        r"^[-*•]\s+",
        r"^\d+\.\s+",
        r"^\d+\)\s+",
        r"^\(\d+\)\s+",
        r"^[a-zA-Z]\)\s+",
        r"^[ivxlcdmIVXLCDM]+\.\s+",
    ]
    return any(re.match(pattern, text) for pattern in patterns)


def normalize_font_size(size: float) -> float:
    """
    Round font size so near-identical sizes group together.
    """
    return round(size, 1)


def build_heading_map(font_sizes):
    """
    Build a mapping from larger font sizes to Markdown heading levels.
    Only the top few distinct font sizes are considered headings.
    """
    if not font_sizes:
        return {}

    normalized = [normalize_font_size(size) for size in font_sizes]
    counts = Counter(normalized)
    unique_sizes = sorted(counts.keys(), reverse=True)

    heading_map = {}

    # Assign only the largest 3 distinct sizes as headings
    levels = ["#", "##", "###"]
    for i, size in enumerate(unique_sizes[:3]):
        heading_map[size] = levels[i]

    return heading_map


def looks_like_heading(text: str, font_size: float, heading_map: dict) -> str | None:
    """
    Return heading marker (#, ##, ###) if the line looks like a heading.
    Otherwise return None.
    """
    if not text:
        return None

    normalized_size = normalize_font_size(font_size)
    heading_marker = heading_map.get(normalized_size)

    if not heading_marker:
        return None

    # Strong filters to avoid false headings
    if len(text) > 120:
        return None

    if text.endswith((".", "?", "!", ";", ":")):
        return None

    if len(text.split()) > 16:
        return None

    # Avoid converting likely metadata lines into headings
    metadata_indicators = ["@", "http://", "https://", "www.", "arxiv", "doi"]
    if any(indicator in text.lower() for indicator in metadata_indicators):
        return None

    return heading_marker


def apply_inline_formatting(text: str, is_bold: bool = False, is_italic: bool = False) -> str:
    """
    Apply markdown formatting to a text chunk.
    """
    clean = text.strip()
    if not clean:
        return ""

    if is_bold and is_italic:
        return f"***{clean}***"
    if is_bold:
        return f"**{clean}**"
    if is_italic:
        return f"*{clean}*"
    return clean


def format_spans(spans) -> str:
    """
    Format text at span level if parser provides spans.
    """
    parts = []

    for span in spans:
        text = span.get("text", "")
        if not text.strip():
            continue

        font_name = span.get("font", "").lower()
        is_bold = span.get("is_bold", "bold" in font_name)
        is_italic = span.get("is_italic", ("italic" in font_name or "oblique" in font_name))

        formatted = apply_inline_formatting(text, is_bold=is_bold, is_italic=is_italic)
        parts.append(formatted)

    result = "".join(parts)
    result = re.sub(r"\s+", " ", result).strip()
    return result


def should_merge_with_paragraph(prev_item, current_item) -> bool:
    """
    Decide whether the current line should continue the previous paragraph.
    """
    if prev_item is None:
        return False

    # Prefer merging only inside same page and same block when metadata exists
    same_page = prev_item.get("page") == current_item.get("page")
    same_block = prev_item.get("block_idx") == current_item.get("block_idx")

    prev_text = prev_item.get("text", "").strip()
    curr_text = current_item.get("text", "").strip()

    if not same_page:
        return False

    if prev_item.get("is_heading") or current_item.get("is_heading"):
        return False

    if prev_item.get("is_list") or current_item.get("is_list"):
        return False

    if not same_block and prev_item.get("block_idx") is not None and current_item.get("block_idx") is not None:
        return False

    # If previous line ends strongly like a paragraph ending, do not merge
    if prev_text.endswith((".", "?", "!", ":", ";")):
        return False

    # Short current line might still be heading-like or caption-like
    if len(curr_text.split()) <= 2:
        return False

    return True


def merge_paragraph_text(paragraph_parts):
    """
    Merge paragraph lines and repair simple hyphenated line breaks.
    """
    if not paragraph_parts:
        return ""

    merged = []
    for part in paragraph_parts:
        if not merged:
            merged.append(part)
            continue

        if merged[-1].endswith("-"):
            merged[-1] = merged[-1][:-1] + part.lstrip()
        else:
            merged.append(part)

    text = " ".join(merged)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def convert_to_markdown(lines, font_sizes):
    """
    Convert extracted PDF lines into structured Markdown.
    """
    if not lines:
        return ""

    heading_map = build_heading_map(font_sizes)

    enriched_lines = []
    for item in lines:
        raw_text = item.get("text", "").strip()
        if not raw_text:
            continue

        if item.get("spans"):
            formatted_text = format_spans(item["spans"])
        else:
            formatted_text = apply_inline_formatting(
                raw_text,
                is_bold=item.get("is_bold", False),
                is_italic=item.get("is_italic", False),
            )

        heading_marker = looks_like_heading(raw_text, item.get("font_size", 0), heading_map)
        is_heading = heading_marker is not None
        is_list = is_list_item(raw_text)

        enriched_lines.append({
            **item,
            "text": formatted_text,
            "is_heading": is_heading,
            "heading_marker": heading_marker,
            "is_list": is_list,
        })

    markdown_lines = []
    paragraph_buffer = []
    previous_item = None
    current_page = None

    def flush_paragraph():
        nonlocal paragraph_buffer
        if paragraph_buffer:
            paragraph_text = merge_paragraph_text(paragraph_buffer)
            if paragraph_text:
                markdown_lines.append(paragraph_text)
                markdown_lines.append("")
            paragraph_buffer = []

    for item in enriched_lines:
        text = item["text"].strip()
        if not text:
            continue

        # Optional page break marker for readability/debugging
        item_page = item.get("page")
        if current_page is None:
            current_page = item_page
        elif item_page is not None and item_page != current_page:
            flush_paragraph()
            markdown_lines.append(f"<!-- Page {item_page} -->")
            markdown_lines.append("")
            current_page = item_page

        if item["is_heading"]:
            flush_paragraph()
            markdown_lines.append(f"{item['heading_marker']} {text}")
            markdown_lines.append("")
        elif item["is_list"]:
            flush_paragraph()
            markdown_lines.append(text)
        else:
            if should_merge_with_paragraph(previous_item, item):
                paragraph_buffer.append(text)
            else:
                flush_paragraph()
                paragraph_buffer.append(text)

        previous_item = item

    flush_paragraph()

    # Clean extra blank lines
    output = "\n".join(markdown_lines)
    output = re.sub(r"\n{3,}", "\n\n", output).strip()

    return output