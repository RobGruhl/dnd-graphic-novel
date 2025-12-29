#!/usr/bin/env python3
"""
Generate a hero creature showcase image of Starwind the Pegasus
with field guide/monster manual aesthetic and scholarly callout annotations.
"""

import os
import sys
import datetime
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageFont
import io

# Load environment
load_dotenv()

# Directories
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output" / "campaign-images"

def generate_starwind_showcase():
    """Generate the Starwind creature showcase image."""

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Build the detailed prompt for a legendary creature showcase
    prompt = """Professional fantasy creature illustration for a Dungeons & Dragons monster manual / field guide.

SUBJECT: Starwind the Pegasus - a MAGNIFICENT legendary winged horse in a heroic rearing pose, wings spread dramatically wide.

CREATURE DETAILS - MUST INCLUDE ALL:
- Pure pristine WHITE coat that glows faintly with inner celestial light
- MASSIVE feathered wings spanning 20 feet, fully extended in majestic display, pure white feathers
- Flowing silver-white mane like spun moonlight, ethereal and luminous
- Intelligent, expressive eyes that convey wisdom and understanding
- Gleaming SILVER hooves catching the light
- Powerful athletic horse body, muscular haunches built for flight
- Long flowing tail like spun moonlight

POSE: Rearing up dramatically on hind legs OR wings fully spread in magnificent display. Heroic, legendary, awe-inspiring.

BACKGROUND: Aged parchment texture, like a scholar's field guide or bestiary page. Warm sepia/cream tones. Dawn light or ethereal golden glow illuminating the pegasus from behind, making the white coat GLOW.

COMPOSITION: Center the pegasus prominently. Leave clear space around the creature for text annotations to be added later. Full body visible.

LIGHTING: Dramatic dawn/golden hour lighting. Ethereal glow emanating from the creature. Celestial radiance. The white coat should LUMINOUS.

STYLE: High fantasy creature illustration. Painterly quality with rich detail. Monster Manual / Bestiary aesthetic. This is THE legendary mount for a hero. Make it feel EPIC and LEGENDARY.

NO modern elements, NO text, NO watermarks, NO saddle or tack - wild celestial freedom."""

    print("Generating Starwind creature showcase...")
    print("-" * 60)

    # Initialize Gemini client
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in environment")
        print("Please check your .env file")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # Configure for 2:3 portrait aspect ratio
    config = types.GenerateContentConfig(
        response_modalities=['Image'],
        image_config=types.ImageConfig(aspect_ratio='2:3')
    )

    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=prompt,
            config=config
        )

        # Extract and save the base image
        for part in response.parts:
            if image := part.as_image():
                # Generate timestamp filename
                now = datetime.datetime.now()
                timestamp = now.strftime("%H%M%S")
                base_filename = f"{timestamp}_starwind_pegasus_showcase.png"
                base_filepath = OUTPUT_DIR / base_filename

                # Save base image
                image.save(str(base_filepath))
                print(f"Base image saved: {base_filepath}")

                # Now add callout annotations
                annotated_filepath = add_callout_annotations(base_filepath)

                return annotated_filepath

        print("ERROR: No image in response")
        return None

    except Exception as e:
        print(f"ERROR: {e}")
        return None


def add_callout_annotations(base_image_path):
    """Add scholarly field guide callout annotations to the image."""

    # Load the base image
    img = Image.open(base_image_path)
    width, height = img.size

    # Create drawing context
    draw = ImageDraw.Draw(img)

    # Try to load a handwritten-style font, fall back to default
    try:
        # Try common macOS fonts that look handwritten/scholarly
        font_paths = [
            "/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf",
            "/System/Library/Fonts/Supplemental/Noteworthy.ttc",
            "/System/Library/Fonts/Supplemental/Papyrus.ttc",
            "/Library/Fonts/Georgia.ttf",
            "/System/Library/Fonts/Times.ttc",
        ]
        font = None
        for fp in font_paths:
            if Path(fp).exists():
                font = ImageFont.truetype(fp, size=28)
                break
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    # Try smaller font for longer annotations
    try:
        small_font = ImageFont.truetype(font_paths[0] if font_paths else "", size=22)
    except:
        small_font = font

    # Define callout annotations with positions (as percentages of image size)
    # Format: (text, x%, y%, alignment, line_to_x%, line_to_y%)
    callouts = [
        # Top left - mane
        ("Flowing silver-white mane\nlike spun moonlight", 0.05, 0.12, "left", 0.35, 0.18),

        # Top right - eyes
        ("Intelligent expressive eyes\nunderstands Common", 0.95, 0.15, "right", 0.65, 0.22),

        # Left side - wings
        ("20-foot wingspan with\npowerful feathered wings", 0.05, 0.35, "left", 0.25, 0.38),

        # Right side - coat
        ("Pure white coat that glows\nfaintly with inner light", 0.95, 0.45, "right", 0.75, 0.48),

        # Bottom left - hooves
        ("Silver hooves\nthat gleam", 0.08, 0.82, "left", 0.35, 0.85),

        # Bottom right - stats
        ("Loyal mount for\nworthy heroes\n\n90 ft flying speed", 0.92, 0.78, "right", 0.65, 0.75),
    ]

    # Colors for scholarly look
    ink_color = (45, 30, 15)  # Dark sepia/brown ink
    line_color = (80, 60, 40, 180)  # Semi-transparent brown for lines

    for text, x_pct, y_pct, align, line_x_pct, line_y_pct in callouts:
        x = int(width * x_pct)
        y = int(height * y_pct)
        line_x = int(width * line_x_pct)
        line_y = int(height * line_y_pct)

        # Draw connecting line
        draw.line([(x, y), (line_x, line_y)], fill=ink_color, width=2)

        # Draw small circle at the end pointing to creature
        draw.ellipse([line_x-4, line_y-4, line_x+4, line_y+4], fill=ink_color)

        # Calculate text position based on alignment
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=small_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        if align == "right":
            text_x = x - text_width - 10
        else:
            text_x = x + 10

        text_y = y - text_height // 2

        # Draw text with slight shadow for readability
        shadow_offset = 1
        draw.text((text_x + shadow_offset, text_y + shadow_offset), text,
                  fill=(200, 180, 150), font=small_font)
        draw.text((text_x, text_y), text, fill=ink_color, font=small_font)

    # Add title at top
    try:
        title_font = ImageFont.truetype(font_paths[0] if font_paths else "", size=42)
    except:
        title_font = font

    title = "STARWIND"
    subtitle = "Pegasus - Celestial Mount"

    # Title positioning
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    title_y = 20

    # Draw title
    draw.text((title_x + 2, title_y + 2), title, fill=(180, 160, 130), font=title_font)
    draw.text((title_x, title_y), title, fill=ink_color, font=title_font)

    # Subtitle
    sub_bbox = draw.textbbox((0, 0), subtitle, font=small_font)
    sub_width = sub_bbox[2] - sub_bbox[0]
    sub_x = (width - sub_width) // 2
    sub_y = title_y + 50
    draw.text((sub_x, sub_y), subtitle, fill=ink_color, font=small_font)

    # Save annotated image
    now = datetime.datetime.now()
    timestamp = now.strftime("%H%M%S")
    annotated_filename = f"{timestamp}_starwind_showcase_annotated.png"
    annotated_filepath = OUTPUT_DIR / annotated_filename

    img.save(str(annotated_filepath))
    print(f"Annotated image saved: {annotated_filepath}")

    return annotated_filepath


if __name__ == "__main__":
    filepath = generate_starwind_showcase()
    if filepath:
        print("-" * 60)
        print(f"SUCCESS: Image saved to {filepath}")
        print("-" * 60)
    else:
        print("FAILED: No image generated")
        sys.exit(1)
