#!/usr/bin/env python3
"""
Generate a hero image of Starwind the Pegasus in creature showcase/field guide style.
16:10 landscape format optimized for MacBook display.
"""

import os
import datetime
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import io

def generate_starwind_hero_image():
    """Generate a majestic hero image of Starwind with field guide annotations."""
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment. Check your .env file.")

    client = genai.Client(api_key=api_key)

    # Ensure output directory exists
    output_dir = Path("/Users/robgruhl/Projects/dnd-graphic-novel/output/campaign-images")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamp filename
    now = datetime.datetime.now()
    timestamp = now.strftime("%H%M%S")
    filename = f"{timestamp}_starwind_pegasus_field_guide.png"
    filepath = output_dir / filename

    # Detailed prompt for Starwind creature showcase - 16:10 LANDSCAPE
    prompt = """WIDE LANDSCAPE FORMAT (16:10 aspect ratio) fantasy creature field guide illustration.

BACKGROUND: Aged parchment paper with subtle coffee stains and wear at edges. Cream/sepia tones. Scholar's study aesthetic.

CENTRAL SUBJECT - STARWIND THE PEGASUS:
A magnificent celestial pegasus in a dramatic majestic pose - REARING UP on hind legs with MASSIVE WHITE-FEATHERED WINGS SPREAD WIDE to show their full 20-foot wingspan.

Physical details:
- Pure white coat that GLOWS with faint inner celestial light
- Noble equine head with intelligent, expressive eyes showing wisdom and understanding
- Flowing SILVER-WHITE MANE cascading like liquid moonlight
- Powerful athletic horse body with muscular haunches built for flight
- SILVER HOOVES that gleam like polished metal
- Long flowing tail like spun moonlight trailing dramatically

LIGHTING: Dawn/golden hour ethereal lighting. Warm rays backlighting the wings creating a holy celestial glow. Soft, divine atmosphere.

CALLOUT ANNOTATIONS with lines pointing to features (handwritten scholar's notes style):
- Arrow to wings: "20-foot wingspan"
- Arrow to coat: "Pure white coat glowing with inner light"
- Arrow to mane: "Flowing silver-white mane"
- Arrow to eyes: "Intelligent eyes - understands Common"
- Arrow to hooves: "Silver hooves"
- In margin notation: "90 ft flying speed"
- Corner note: "Loyal mount for worthy heroes"

COMPOSITION:
- Starwind positioned left-of-center, facing right
- Ample margin space on right side and corners for annotations
- Wings spread to show full magnificent span
- Background suggests open sky/clouds behind the parchment frame

STYLE: D&D Monster Manual / Victorian naturalist field guide. Elegant calligraphy annotations. Professional fantasy illustration with painterly quality. Medieval fantasy aesthetic.

NO modern elements, NO watermarks, NO dark/gloomy atmosphere. This is a HEROIC, LEGENDARY creature showcase."""

    print(f"Generating Starwind hero image (16:10 landscape)...")
    print(f"Prompt length: {len(prompt)} characters")

    # Generate image using Gemini with 16:9 (closest available to 16:10)
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            temperature=1.0,
        )
    )

    # Extract and save image
    image_saved = False
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image_data = part.inline_data.data
            image = Image.open(io.BytesIO(image_data))
            image.save(filepath)
            image_saved = True
            print(f"\n[OK] Image saved: {filepath}")
            print(f"Dimensions: {image.size[0]}x{image.size[1]}")
            break

    if not image_saved:
        # Try alternate response structure
        if hasattr(response, 'generated_images') and response.generated_images:
            image_data = response.generated_images[0].image.image_bytes
            image = Image.open(io.BytesIO(image_data))
            image.save(filepath)
            print(f"\n[OK] Image saved: {filepath}")
            print(f"Dimensions: {image.size[0]}x{image.size[1]}")
        else:
            raise Exception("No image found in response")

    return str(filepath)

if __name__ == "__main__":
    filepath = generate_starwind_hero_image()
    print(f"\nGeneration complete!")
    print(f"Full path: {filepath}")
    print(f"\nOpening in Chrome...")
    os.system(f"open -a 'Google Chrome' '{filepath}'")
