#!/usr/bin/env python3
"""
Campaign Image Generator - Standalone script for D&D session scene generation.
Uses Google Gemini for fantasy artwork generation.
"""

import os
import sys
import datetime
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# Load environment
load_dotenv()

# Configuration
OUTPUT_DIR = Path("output/campaign-images")
PRO_MODEL_ID = "gemini-3-pro-image-preview"


def generate_campaign_image(prompt: str, description: str) -> str:
    """Generate a D&D campaign image and save with timestamp filename."""

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate timestamp filename
    now = datetime.datetime.now()
    timestamp = now.strftime("%H%M%S")
    # Clean description for filename
    safe_description = description.lower().replace(" ", "_").replace("-", "_")
    safe_description = "".join(c for c in safe_description if c.isalnum() or c == "_")[:50]
    filename = f"{timestamp}_{safe_description}.png"
    filepath = OUTPUT_DIR / filename

    # Enhanced prompt for fantasy art
    full_prompt = f"""Professional fantasy illustration for a Dungeons & Dragons campaign.

{prompt}

Style: Rich colors, detailed linework, dramatic fantasy lighting, painterly quality, fantasy comic book art style, vibrant colors.
No modern elements, no text, no watermarks, no speech bubbles."""

    print(f"Generating image...")
    print(f"Output: {filepath}")

    # Initialize client
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment. Check your .env file.")

    client = genai.Client(api_key=api_key)

    # Generate image
    config = types.GenerateContentConfig(
        response_modalities=['Image'],
        image_config=types.ImageConfig(aspect_ratio='1:1')
    )

    response = client.models.generate_content(
        model=PRO_MODEL_ID,
        contents=full_prompt,
        config=config
    )

    # Save image
    for part in response.parts:
        if image := part.as_image():
            image.save(str(filepath))
            pil_img = Image.open(str(filepath))
            size = pil_img.size
            print(f"Generated: {size[0]}x{size[1]}")
            return str(filepath)

    raise Exception("No image generated in response")


if __name__ == "__main__":
    # The prompt from command line or hardcoded for this run
    prompt = """A young 10-year-old boy (Hendrix - messy brown hair, bright curious eyes, simple peasant tunic) stands in a temple courtyard fumbling excitedly with a spread of colorful magical cards in his hands. He's trying to choose which cards to use. The cards are spread out in front of him - some held in his hands, some floating slightly with magic, a few scattered on a stone pedestal. The cards have four distinct color schemes visible: crimson red (Warrior), forest green (Hunter), sapphire blue (Arcane), and warm gold (Divine). Each card glows faintly with its aspect's color. The boy's expression shows excited concentration - the overwhelming joy of having SO MANY options. Soft magical light from the cards illuminates his face from below. Temple pillars visible in the background, each glowing with one of the four aspect colors. Fantasy comic book art style, vibrant colors, dynamic composition."""

    description = "hendrix_choosing_magical_cards"

    try:
        filepath = generate_campaign_image(prompt, description)
        print(f"\nSuccess! Image saved to: {filepath}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
