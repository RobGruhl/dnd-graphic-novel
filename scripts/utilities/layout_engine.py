#!/usr/bin/env python3
"""
Simplified comic book layout engine.
Two layouts only: Splash (1 panel) and 2x2 Grid (4 panels).
All panels are 1024x1536 (portrait, 2:3 aspect ratio).
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
from typing import List, Dict
import random


# Layout Configuration
PAGE_WIDTH = 1600
PAGE_HEIGHT = 2400
GUTTER = 20
PANEL_BORDER = 3
SHADOW_OFFSET = 4
SHADOW_BLUR = 6

# Background Configuration
BACKGROUND_COLOR = (245, 240, 235)  # Warm off-white/cream
TEXTURE_INTENSITY = 0.15  # Subtle texture overlay


def create_textured_background(width: int, height: int) -> Image.Image:
    """Create subtle textured background for professional comic appearance."""
    bg = Image.new('RGB', (width, height), BACKGROUND_COLOR)

    # Generate subtle noise texture
    pixels = bg.load()
    for y in range(height):
        for x in range(width):
            variation = int((random.random() - 0.5) * TEXTURE_INTENSITY * 255)
            r, g, b = BACKGROUND_COLOR
            pixels[x, y] = (
                max(0, min(255, r + variation)),
                max(0, min(255, g + variation)),
                max(0, min(255, b + variation))
            )

    # Slight blur to smooth texture
    bg = bg.filter(ImageFilter.GaussianBlur(0.5))
    return bg


def draw_panel_with_shadow(page_img: Image.Image, panel_img: Image.Image,
                           x: int, y: int, width: int, height: int):
    """Draw a panel with drop shadow onto the page."""
    # Create shadow layer
    shadow = Image.new('RGBA', (width + SHADOW_OFFSET * 2, height + SHADOW_OFFSET * 2), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rectangle(
        [SHADOW_OFFSET, SHADOW_OFFSET, width + SHADOW_OFFSET, height + SHADOW_OFFSET],
        fill=(0, 0, 0, 100)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(SHADOW_BLUR))

    # Paste shadow
    page_img.paste(shadow, (x - SHADOW_OFFSET, y - SHADOW_OFFSET), shadow)

    # Resize panel to fit box (maintain portrait aspect ratio)
    panel_resized = panel_img.resize((width, height), Image.Resampling.LANCZOS)

    # Draw border
    bordered_panel = Image.new('RGB', (width, height), 'black')
    inner_width = width - 2 * PANEL_BORDER
    inner_height = height - 2 * PANEL_BORDER
    panel_resized = panel_resized.resize((inner_width, inner_height), Image.Resampling.LANCZOS)
    bordered_panel.paste(panel_resized, (PANEL_BORDER, PANEL_BORDER))

    # Paste panel
    page_img.paste(bordered_panel, (x, y))


def layout_splash(page_img: Image.Image, panel_images: List[Image.Image]):
    """
    Splash layout: Single panel fills entire page.

    Panel is centered and scaled to fit page while maintaining aspect ratio.
    """
    if not panel_images:
        return

    panel = panel_images[0]

    # Calculate dimensions to fit panel in page (centered, maintain aspect ratio)
    available_width = PAGE_WIDTH - 2 * GUTTER
    available_height = PAGE_HEIGHT - 2 * GUTTER

    # Panel is 2:3 ratio (1024x1536), scale to fit
    panel_ratio = 2 / 3
    page_ratio = available_width / available_height

    if panel_ratio < page_ratio:
        # Panel is narrower than page, fit to height
        panel_height = available_height
        panel_width = int(panel_height * panel_ratio)
    else:
        # Panel is wider than page, fit to width
        panel_width = available_width
        panel_height = int(panel_width / panel_ratio)

    # Center the panel
    x = (PAGE_WIDTH - panel_width) // 2
    y = (PAGE_HEIGHT - panel_height) // 2

    draw_panel_with_shadow(page_img, panel, x, y, panel_width, panel_height)


def layout_2x2_grid(page_img: Image.Image, panel_images: List[Image.Image]):
    """
    2x2 Grid layout: 4 panels in a grid.

    Each panel maintains portrait 2:3 aspect ratio.
    Panels are evenly spaced with gutters.
    """
    # Calculate panel dimensions (2 columns, 2 rows)
    available_width = PAGE_WIDTH - 3 * GUTTER  # Left, middle, right gutters
    available_height = PAGE_HEIGHT - 3 * GUTTER  # Top, middle, bottom gutters

    panel_width = available_width // 2
    panel_height = available_height // 2

    # Ensure panels maintain 2:3 aspect ratio
    # If calculated dimensions don't match, adjust to fit the more constraining dimension
    ideal_height_from_width = int(panel_width * 1.5)  # 2:3 ratio
    ideal_width_from_height = int(panel_height / 1.5)

    if ideal_height_from_width <= panel_height:
        # Width is constraining, use it
        panel_height = ideal_height_from_width
    else:
        # Height is constraining, use it
        panel_width = ideal_width_from_height

    # Draw panels in 2x2 grid
    positions = [
        (0, 0),  # Top-left
        (1, 0),  # Top-right
        (0, 1),  # Bottom-left
        (1, 1),  # Bottom-right
    ]

    for i, panel in enumerate(panel_images[:4]):  # Max 4 panels
        col, row = positions[i]
        x = GUTTER + col * (panel_width + GUTTER)
        y = GUTTER + row * (panel_height + GUTTER)
        draw_panel_with_shadow(page_img, panel, x, y, panel_width, panel_height)


def assemble_page_simple(panel_images: List[Image.Image], num_panels: int) -> Image.Image:
    """
    Assemble a comic page using simplified layout system.

    Args:
        panel_images: List of loaded panel images (all 1024x1536 portrait)
        num_panels: Number of panels (1 or 4)

    Returns:
        Assembled page image (1600x2400)
    """
    # Create textured background
    page_img = create_textured_background(PAGE_WIDTH, PAGE_HEIGHT)

    # Apply appropriate layout
    if num_panels == 1:
        layout_splash(page_img, panel_images)
    else:  # 4 panels or fewer (pad with empty if needed)
        layout_2x2_grid(page_img, panel_images)

    return page_img


# Legacy compatibility function (called by assemble.py)
def assemble_page_with_layout(panels_data: List[Dict], panel_images: List[Image.Image],
                                page_width: int = PAGE_WIDTH, page_height: int = PAGE_HEIGHT,
                                custom_layout: str = None) -> Image.Image:
    """
    Legacy wrapper for compatibility with existing code.
    Simplified to use only splash or 2x2 grid.
    """
    num_panels = len(panels_data)
    return assemble_page_simple(panel_images, num_panels)
