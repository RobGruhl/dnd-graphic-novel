#!/usr/bin/env python3
"""
Create CBZ from panels without separate assembly step.
Each 4-panel page is arranged in a 2x2 grid.
"""

import json
import zipfile
from pathlib import Path
from PIL import Image

# Configuration
PAGES_JSON_DIR = Path("pages")
PANELS_DIR = Path("output/panels")
OUTPUT_DIR = Path("output")
CBZ_FILE = OUTPUT_DIR / "comic.cbz"

# Page dimensions for assembled pages
PAGE_WIDTH = 1696  # 2 panels wide (848x2)
PAGE_HEIGHT = 2528  # 2 panels tall (1264x2)
GUTTER = 0  # No gutter for tight layout

def create_page_from_panels(page_num, panels_dir, panel_count):
    """Create a single page image from panels.

    - For panel_count=1: Use single panel resized to page dimensions
    - For panel_count=4: Arrange in 2x2 grid
    """

    if panel_count == 1:
        # Single panel splash page - use full page size
        panel_file = panels_dir / f"page-{page_num:03d}-panel-1.png"
        if not panel_file.exists():
            print(f"  ⚠️  Missing panel 1 for page {page_num}")
            return None

        panel_img = Image.open(panel_file)
        # Resize to page dimensions (maintaining aspect ratio with letterboxing if needed)
        page_img = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGHT), 'black')
        panel_img = panel_img.resize((PAGE_WIDTH, PAGE_HEIGHT), Image.Resampling.LANCZOS)
        page_img.paste(panel_img, (0, 0))
        return page_img

    elif panel_count == 4:
        # Load panel images for 2x2 grid
        panel_images = []
        for i in range(1, 5):
            panel_file = panels_dir / f"page-{page_num:03d}-panel-{i}.png"
            if panel_file.exists():
                panel_images.append(Image.open(panel_file))
            else:
                print(f"  ⚠️  Missing panel {i} for page {page_num}")
                return None

        if len(panel_images) != 4:
            return None

        # Create page canvas
        page_img = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGHT), 'white')

        # Arrange in 2x2 grid
        positions = [
            (0, 0),           # Top left
            (848, 0),         # Top right
            (0, 1264),        # Bottom left
            (848, 1264)       # Bottom right
        ]

        for img, pos in zip(panel_images, positions):
            page_img.paste(img, pos)

        return page_img

    else:
        print(f"  ⚠️  Unsupported panel count {panel_count} for page {page_num}")
        return None

def create_cbz(title="D&D Graphic Novel", series="D&D Graphic Novel"):
    """Create CBZ file from panels."""

    print("="*70)
    print("CREATING CBZ FROM PANELS")
    print("="*70)
    print()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Get list of pages with their panel counts from JSON
    pages_to_include = []

    for page_num in range(1, 100):  # Check up to 99 pages
        # Check JSON for expected panel count
        page_file = PAGES_JSON_DIR / f"page-{page_num:03d}.json"
        if not page_file.exists():
            continue

        with open(page_file, 'r') as f:
            page_data = json.load(f)
        expected_count = page_data.get('panel_count', 4)

        # Check if we have the expected panels
        panel_files = list(PANELS_DIR.glob(f"page-{page_num:03d}-panel-*.png"))
        actual_count = len(panel_files)

        if actual_count == expected_count:
            pages_to_include.append((page_num, expected_count))
        elif actual_count > 0:
            print(f"⚠️  Page {page_num}: {actual_count}/{expected_count} panels (INCOMPLETE - skipping)")
        # Silently skip pages with 0 panels

    print(f"\n✓ Found {len(pages_to_include)} complete pages")
    print()

    # Create assembled pages
    assembled_pages = {}
    for page_num, panel_count in pages_to_include:
        print(f"→ Assembling page {page_num} ({panel_count} panel{'s' if panel_count > 1 else ''})...")
        page_img = create_page_from_panels(page_num, PANELS_DIR, panel_count)

        if page_img:
            assembled_pages[page_num] = page_img
            print(f"  ✓ Page {page_num} assembled ({PAGE_WIDTH}x{PAGE_HEIGHT})")
        else:
            print(f"  ✗ Failed to assemble page {page_num}")

    print()
    print(f"✓ Assembled {len(assembled_pages)} pages")
    print()

    # Create CBZ
    print("→ Creating CBZ archive...")

    # ComicInfo.xml metadata
    comic_info = f"""<?xml version="1.0"?>
<ComicInfo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <Title>{title}</Title>
  <Series>{series}</Series>
  <Number>1</Number>
  <Summary>A D&D character backstory graphic novel.</Summary>
  <Publisher>AI-Generated</Publisher>
  <Genre>Fantasy</Genre>
  <PageCount>{len(assembled_pages)}</PageCount>
  <LanguageISO>en</LanguageISO>
</ComicInfo>"""

    with zipfile.ZipFile(CBZ_FILE, 'w', zipfile.ZIP_DEFLATED) as cbz:
        # Add metadata
        cbz.writestr('ComicInfo.xml', comic_info)

        # Add pages in order
        for page_num in sorted(assembled_pages.keys()):
            page_img = assembled_pages[page_num]

            # Save to temp file
            temp_file = OUTPUT_DIR / f"temp_page_{page_num:03d}.png"
            page_img.save(temp_file)

            # Add to CBZ with padded numbering
            cbz.write(temp_file, f"{page_num:03d}.png")

            # Clean up temp file
            temp_file.unlink()

    print(f"✓ Created {CBZ_FILE}")
    print()
    print("="*70)
    print(f"✓ CBZ COMPLETE: {len(assembled_pages)} pages")
    print(f"  File: {CBZ_FILE}")
    print(f"  Size: {CBZ_FILE.stat().st_size / (1024*1024):.1f} MB")
    print("="*70)

    return CBZ_FILE

if __name__ == "__main__":
    create_cbz()
