#excel conversion working good 3 version with detection of horizontal line wokring PERFECT TO SUBMIT

import fitz
import re
import pandas as pd
from openpyxl.styles import Font, Alignment
import os
import logging

class PDFProcessor:
    def __init__(self):
        self.excel_data = []
        self.current_page = 2
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)


    def find_horizontal_lines(self, page):
        """Find horizontal lines in the page that might indicate footnote sections"""
        # Get page dimensions
        page_width = page.rect.width
        page_height = page.rect.height

        # Get all drawings from the page
        paths = page.get_drawings()
        horizontal_lines = []

        for path in paths:
            # Check if it's a line
            if 'rect' in path:
                rect = path['rect']
                y0, y1 = rect[1], rect[3]
                x0, x1 = rect[0], rect[2]

                # Check if it's horizontal (y coordinates are close)
                if abs(y1 - y0) < 2:  # Allow small deviation
                    # Check if line is in bottom third of page
                    if y0 > (page_height * 0.6):
                        # Check if line length is appropriate (25-35% of page width)
                        line_length = x1 - x0
                        length_ratio = line_length / page_width

                        if 0.25 <= length_ratio <= 0.35:
                            horizontal_lines.append({
                                'bbox': (x0, y0, x1, y1),
                                'is_separator': True
                            })

        self.logger.debug(f"Page {self.current_page}: Found {len(horizontal_lines)} horizontal lines")
        return horizontal_lines

    def validate_footnote_format(self, text):
        """Validate if text follows footnote format"""
        # Pattern for footnote: number followed by text
        footnote_pattern = r'^\d+\s+[A-Z]'  # Number followed by space and capital letter
        return bool(re.match(footnote_pattern, text.strip()))

    def find_footnote_section(self, page):
        """Find and validate footnote section"""
        lines = self.find_horizontal_lines(page)
        if not lines:
            self.logger.debug(f"Page {self.current_page}: No horizontal lines found")
            return None

        # Sort lines by y-position (bottom to top)
        lines.sort(key=lambda x: x['bbox'][1], reverse=True)

        for line in lines:
            # Check text below the line
            below_line_rect = fitz.Rect(
                0, line['bbox'][1],
                page.rect.width, line['bbox'][1] + 50
            )
            text_below = page.get_text("text", clip=below_line_rect).strip()

            if text_below and self.validate_footnote_format(text_below):
                return {
                    'separator_line': line['bbox'],
                    'section_start': line['bbox'][1],
                    'text_below': text_below
                }

        return None



    def extract_footnotes_and_refs(self, page):
        """Enhanced footnote extraction with improved detection"""
        footnotes = {}
        main_footnote_refs = []
        footnote_markers = []

        # Get page dimensions for position analysis
        page_height = page.rect.height
        page_width = page.rect.width

        # Get all blocks of text
        blocks = page.get_text("dict")["blocks"]

        # First pass: Identify all potential references in the main text
        potential_refs = []
        for block in blocks:
            block_y = block["bbox"][1]  # Y-position of block

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    # Check if span could be a reference (number and smaller font)
                    if (span["text"].strip().isdigit() and
                        self.is_smaller_font(span, line.get("spans", []))):

                        # Store reference with its position
                        potential_refs.append({
                            "text": span["text"],
                            "y_pos": span["bbox"][1],
                            "is_main_text": block_y < (page_height * 0.7)  # Consider position on page
                        })

        # Second pass: Find footnotes by looking for numbered text at bottom of page
        footnote_section_started = False
        current_footnote = ""
        current_footnote_num = None
        last_y_position = 0

        # Sort blocks by vertical position
        sorted_blocks = sorted(blocks, key=lambda x: x["bbox"][1])

        for block in sorted_blocks:
            block_y = block["bbox"][1]
            block_text = ""

            # Combine all text in block
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    span_text = span["text"].strip()

                    # Check if this might be a footnote number
                    if (span_text.isdigit() and
                        block_y > (page_height * 0.6) and  # In bottom portion of page
                        not current_footnote_num):

                        # Verify this number exists in our references
                        if any(ref["text"] == span_text for ref in potential_refs):
                            current_footnote_num = span_text
                            footnote_section_started = True
                            continue

                    if footnote_section_started:
                        current_footnote += span_text + " "

                    # Check for next footnote number
                    if (current_footnote and span_text.isdigit() and
                        any(ref["text"] == span_text for ref in potential_refs)):
                        if current_footnote_num:
                            footnotes[current_footnote_num] = current_footnote.strip()
                        current_footnote_num = span_text
                        current_footnote = ""

            # Add spacing between blocks in footnote
            if footnote_section_started and current_footnote:
                current_footnote += " "

        # Save last footnote
        if current_footnote_num and current_footnote:
            footnotes[current_footnote_num] = current_footnote.strip()

        # Separate references into main text refs and footnote markers
        for ref in potential_refs:
            if ref["is_main_text"]:
                # Find the span in original blocks
                for block in blocks:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            if span["text"] == ref["text"] and ref["is_main_text"]:
                                main_footnote_refs.append(span)
            else:
                footnote_markers.append(ref)

        # Validation: Check if we found footnotes for all references
        missing_footnotes = []
        for ref in main_footnote_refs:
            if ref["text"] not in footnotes:
                missing_footnotes.append(ref["text"])

        if missing_footnotes:
            self.logger.warning(f"Missing footnotes for references: {missing_footnotes}")

            # Second attempt to find missing footnotes
            for ref_num in missing_footnotes:
                # Look for text pattern: number followed by text
                pattern = f"{ref_num}\\s+([^0-9]+?)(?=\\d|$)"
                page_text = page.get_text()
                matches = re.finditer(pattern, page_text, re.DOTALL)

                for match in matches:
                    if match.group(1).strip():
                        footnotes[ref_num] = match.group(1).strip()
                        break

        self.logger.info(f"Found {len(main_footnote_refs)} references and {len(footnotes)} footnotes")
        return footnotes, main_footnote_refs, footnote_markers

    def is_smaller_font(self, span, line_spans):
        """Improved font size comparison"""
        if not line_spans:
            return False

        # Get average size of normal text
        sizes = [s["size"] for s in line_spans if not s["text"].strip().isdigit()]
        if not sizes:
            return False

        avg_font_size = sum(sizes) / len(sizes)
        return span["size"] < avg_font_size * 0.85  # Slightly more lenient threshold

    def organize_content(self, page, footnotes, main_footnote_refs):
        """Enhanced content organization"""
        blocks = page.get_text("dict")["blocks"]
        current_text = []
        current_paragraph = []

        for block in blocks:
            for line in block.get("lines", []):
                line_text = []
                ref_found = False

                for span in line.get("spans", []):
                    # Check if this span is a footnote reference
                    is_ref = any(ref["text"] == span["text"] for ref in main_footnote_refs)

                    if is_ref:
                        # Add text before reference
                        if line_text:
                            current_text.extend(line_text)
                            line_text = []

                        # Get the actual footnote text
                        footnote_num = span["text"]
                        if footnote_num in footnotes:
                            # Add the complete paragraph with reference
                            if current_text:
                                full_text = " ".join(current_text) + " " + footnote_num
                                self.excel_data.append([full_text, ""])
                                current_text = []

                            # Add the footnote in next row
                            self.excel_data.append(["", f"{footnote_num}. {footnotes[footnote_num]}"])
                            ref_found = True
                        else:
                            # If footnote not found, still include the reference number
                            line_text.append(span["text"])
                            self.logger.warning(f"Missing footnote for reference {footnote_num}")
                    else:
                        line_text.append(span["text"])

                if line_text:
                    current_text.extend(line_text)

                # Add line break between lines if needed
                if len(line.get("spans", [])) > 0:  # If line had content
                    current_text.append(" ")

            # End of block - add accumulated text if no reference was found
            if current_text and not ref_found:
                text = " ".join(current_text).strip()
                if text:
                    self.excel_data.append([text, ""])
                current_text = []


    def process_page(self, page):
        """Process single page content with improved footnote handling"""
        # First extract footnotes and references
        footnotes, main_footnote_refs, footnote_markers = self.extract_footnotes_and_refs(page)

        # Debug print
        print("\nExtracted Footnotes:")
        for num, text in footnotes.items():
            print(f"Footnote {num}: {text}")

        print("\nMain References:")
        for ref in main_footnote_refs:
            print(f"Reference: {ref['text']}")

        # Process and organize content
        self.organize_content(page, footnotes, main_footnote_refs)

    # Add this helper method for debugging
    def print_text_block(self, text_block):
        """Debug helper to print text block structure"""
        print("\nText Block Structure:")
        for i, (text, props) in enumerate(text_block):
            print(f"{i}: {text} (Font size: {props.get('size', 'N/A')})")


    def create_excel_file(self, input_pdf_path):
            """Create formatted Excel file"""
            output_path = input_pdf_path.replace('.pdf', '_Final.xlsx')

            # Create DataFrame
            df = pd.DataFrame(self.excel_data, columns=['Content', 'Footnotes'])

            # Write to Excel with formatting
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Processed Content')

                # Get worksheet
                worksheet = writer.sheets['Processed Content']

                # Format columns
                worksheet.column_dimensions['A'].width = 60
                worksheet.column_dimensions['B'].width = 40

                # Format cells
                for row in range(2, len(self.excel_data) + 2):
                    cell_a = worksheet.cell(row=row, column=1)
                    cell_b = worksheet.cell(row=row, column=2)

                    # Basic formatting
                    for cell in [cell_a, cell_b]:
                        cell.alignment = Alignment(wrap_text=True,
                                                vertical='top',
                                                horizontal='left')

                    # Special formatting for page markers
                    if cell_a.value and isinstance(cell_a.value, str) and cell_a.value.startswith('****'):
                        cell_a.font = Font(bold=True)
                        cell_a.alignment = Alignment(horizontal='center')

                    # Format footnotes
                    if cell_b.value:
                        cell_b.font = Font(italic=True)

            print(f"\nExcel file created: {output_path}")
            return output_path


    def validate_footnote_matching(self, footnotes, main_footnote_refs):
        """Validate footnote matching and print diagnostic information"""
        print("\nValidating Footnote Matching:")

        for ref in main_footnote_refs:
            ref_num = ref["text"]
            if ref_num in footnotes:
                print(f"\nReference {ref_num}:")
                print(f"Position in text: {ref.get('bbox', 'Unknown position')}")
                print(f"Matched footnote: {footnotes[ref_num]}")
            else:
                print(f"\nWarning: No footnote found for reference {ref_num}")

        # Check for unmatched footnotes
        ref_numbers = {ref["text"] for ref in main_footnote_refs}
        for footnote_num in footnotes:
            if footnote_num not in ref_numbers:
                print(f"\nWarning: Footnote {footnote_num} has no matching reference")

    def process_pdf(self, file_path):
        """Main processing function"""
        try:
            print(f"Processing PDF: {file_path}")
            doc = fitz.open(file_path)

            for page_num in range(len(doc)):
                page = doc[page_num]
                print(f"\nProcessing page {page_num + 1}")

                # Use your extraction method
                footnotes, main_footnote_refs, footnote_markers = self.extract_footnotes_and_refs(page)
                print(f"Found {len(footnotes)} footnotes and {len(main_footnote_refs)} references")

                # Process and organize content for Excel
                self.organize_content(page, footnotes, main_footnote_refs)

                # Add page marker
                self.excel_data.append([f"**** Page {self.current_page} ****", ""])
                self.current_page += 1

            # Create Excel file
            self.create_excel_file(file_path)
            doc.close()

        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            raise

    # Example usage:
    def process_page(self, page):
        """Enhanced page processing with validation"""
        footnotes, main_footnote_refs, footnote_markers = self.extract_footnotes_and_refs(page)

        # Validate footnote matching
        self.validate_footnote_matching(footnotes, main_footnote_refs)

        # Process content with validated footnotes
        self.organize_content(page, footnotes, main_footnote_refs)

def process_pdf_file(file_path):
    """Process a PDF file and create Excel output"""
    processor = PDFProcessor()
    processor.process_pdf(file_path)

if __name__ == "__main__":
    pdf_path = "/content/MC371.pdf"  # Replace with actual path
    process_pdf_file(pdf_path)
