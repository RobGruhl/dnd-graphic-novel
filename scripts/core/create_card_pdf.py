#!/usr/bin/env python3
"""
Create printable PDF of aspect cards for 8.5x11 paper.
Arranges cards in a 3x3 grid with cut marks.
"""

from pathlib import Path
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# Configuration
CARDS_DIR = Path("output/cards")
OUTPUT_PDF = Path("output/aspect-cards-printable.pdf")

# Page dimensions (8.5 x 11 inches)
PAGE_WIDTH, PAGE_HEIGHT = letter  # 612 x 792 points

# Card layout: 3 columns x 3 rows
CARDS_PER_ROW = 3
ROWS_PER_PAGE = 3
CARDS_PER_PAGE = CARDS_PER_ROW * ROWS_PER_PAGE

# Card size (standard trading card is 2.5" x 3.5")
CARD_WIDTH = 2.5 * inch
CARD_HEIGHT = 3.5 * inch

# Margins and spacing
MARGIN_X = (PAGE_WIDTH - (CARDS_PER_ROW * CARD_WIDTH)) / 2
MARGIN_Y = (PAGE_HEIGHT - (ROWS_PER_PAGE * CARD_HEIGHT)) / 2

# Cut mark settings
CUT_MARK_LENGTH = 0.15 * inch
CUT_MARK_OFFSET = 0.05 * inch


def get_card_files():
    """Get all card PNG files in order."""
    cards = sorted(CARDS_DIR.glob("*.png"))

    # Sort by aspect then number
    def sort_key(p):
        name = p.stem
        aspects = {'warrior': 0, 'hunter': 1, 'arcane': 2, 'divine': 3}
        for aspect, order in aspects.items():
            if name.startswith(aspect):
                return (order, name)
        return (99, name)

    return sorted(cards, key=sort_key)


def draw_cut_marks(c, x, y, card_w, card_h):
    """Draw cut marks around a card position."""
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.setLineWidth(0.5)

    # Top-left corner
    c.line(x - CUT_MARK_OFFSET - CUT_MARK_LENGTH, y + card_h,
           x - CUT_MARK_OFFSET, y + card_h)
    c.line(x, y + card_h + CUT_MARK_OFFSET,
           x, y + card_h + CUT_MARK_OFFSET + CUT_MARK_LENGTH)

    # Top-right corner
    c.line(x + card_w + CUT_MARK_OFFSET, y + card_h,
           x + card_w + CUT_MARK_OFFSET + CUT_MARK_LENGTH, y + card_h)
    c.line(x + card_w, y + card_h + CUT_MARK_OFFSET,
           x + card_w, y + card_h + CUT_MARK_OFFSET + CUT_MARK_LENGTH)

    # Bottom-left corner
    c.line(x - CUT_MARK_OFFSET - CUT_MARK_LENGTH, y,
           x - CUT_MARK_OFFSET, y)
    c.line(x, y - CUT_MARK_OFFSET,
           x, y - CUT_MARK_OFFSET - CUT_MARK_LENGTH)

    # Bottom-right corner
    c.line(x + card_w + CUT_MARK_OFFSET, y,
           x + card_w + CUT_MARK_OFFSET + CUT_MARK_LENGTH, y)
    c.line(x + card_w, y - CUT_MARK_OFFSET,
           x + card_w, y - CUT_MARK_OFFSET - CUT_MARK_LENGTH)


def create_pdf():
    """Create the printable PDF."""
    cards = get_card_files()

    if not cards:
        print("No card images found in", CARDS_DIR)
        return

    print(f"Found {len(cards)} cards")
    print(f"Layout: {CARDS_PER_ROW}x{ROWS_PER_PAGE} = {CARDS_PER_PAGE} cards per page")
    print(f"Card size: {CARD_WIDTH/inch:.2f}\" x {CARD_HEIGHT/inch:.2f}\"")

    # Create PDF
    c = canvas.Canvas(str(OUTPUT_PDF), pagesize=letter)

    card_index = 0
    page_num = 1

    while card_index < len(cards):
        print(f"\nPage {page_num}:")

        # Draw cards for this page
        for row in range(ROWS_PER_PAGE):
            for col in range(CARDS_PER_ROW):
                if card_index >= len(cards):
                    break

                card_path = cards[card_index]

                # Calculate position (bottom-left origin in PDF)
                x = MARGIN_X + (col * CARD_WIDTH)
                y = PAGE_HEIGHT - MARGIN_Y - ((row + 1) * CARD_HEIGHT)

                # Draw cut marks
                draw_cut_marks(c, x, y, CARD_WIDTH, CARD_HEIGHT)

                # Draw card image
                c.drawImage(str(card_path), x, y, CARD_WIDTH, CARD_HEIGHT,
                           preserveAspectRatio=True)

                print(f"  [{row},{col}] {card_path.stem}")
                card_index += 1

        # Add page number
        c.setFont("Helvetica", 8)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawCentredString(PAGE_WIDTH / 2, 0.3 * inch,
                           f"Aspect Cards - Page {page_num} of {(len(cards) + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE}")

        c.showPage()
        page_num += 1

    c.save()
    print(f"\n✓ Created: {OUTPUT_PDF}")
    print(f"  {page_num - 1} pages, ready for printing on 8.5\" x 11\" paper")


if __name__ == "__main__":
    create_pdf()
