import argparse
import os
import sys

from parser import extract_lines_with_format
from formatter import convert_to_markdown


def parse_args():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Convert a PDF file into structured Markdown."
    )
    parser.add_argument(
        "input_pdf",
        help="Path to the input PDF file"
    )
    parser.add_argument(
        "output_md",
        help="Path to the output Markdown file"
    )
    return parser.parse_args()


def validate_input_file(input_pdf: str):
    """
    Validate input file existence and extension.
    """
    if not os.path.exists(input_pdf):
        print(f"Error: Input file not found: {input_pdf}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(input_pdf):
        print(f"Error: Input path is not a file: {input_pdf}", file=sys.stderr)
        sys.exit(1)

    if not input_pdf.lower().endswith(".pdf"):
        print("Error: Input file must have a .pdf extension.", file=sys.stderr)
        sys.exit(1)


def ensure_output_directory(output_md: str):
    """
    Create output directory if it does not already exist.
    """
    output_dir = os.path.dirname(output_md)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)


def main():
    args = parse_args()
    input_pdf = args.input_pdf
    output_md = args.output_md

    validate_input_file(input_pdf)
    ensure_output_directory(output_md)

    try:
        lines, font_sizes = extract_lines_with_format(input_pdf)

        if not lines:
            print(
                "Warning: No extractable text found in the PDF. "
                "The file may be scanned or image-based.",
                file=sys.stderr
            )

        markdown_content = convert_to_markdown(lines, font_sizes)

        with open(output_md, "w", encoding="utf-8") as file:
            file.write(markdown_content)

        print("Conversion completed successfully.")
        print(f"Input PDF : {input_pdf}")
        print(f"Output MD : {output_md}")
        print(f"Lines read: {len(lines)}")

    except Exception as error:
        print(f"Processing failed: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()