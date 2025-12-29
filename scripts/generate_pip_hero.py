#!/usr/bin/env python3
"""Generate a hero image of Pip the Pseudodragon - creature showcase with callouts.
16:10 landscape for MacBook screen, field guide / monster manual aesthetic."""

import os
import datetime
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# Load environment
load_dotenv()

# Model configuration - same as generate_nanobananapro.py
PRO_MODEL_ID = "gemini-3-pro-image-preview"


def generate_pip_hero_image() -> str:
    """Generate a D&D creature field guide style image of Pip."""
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    # Ensure output directory exists
    output_dir = Path("/Users/robgruhl/Projects/dnd-graphic-novel/output/campaign-images")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamp filename
    now = datetime.datetime.now()
    timestamp = now.strftime("%H%M%S")
    filename = f"{timestamp}_pip_pseudodragon_field_guide.png"
    filepath = output_dir / filename

    # Detailed prompt for fantasy creature field guide aesthetic
    # CRITICAL: Pip is a TINY DRAGON, NOT a cat!
    prompt = """CREATURE FIELD GUIDE PAGE - WIDESCREEN LANDSCAPE FORMAT

A fantasy monster manual / naturalist's bestiary illustration page featuring a PSEUDODRAGON named Pip.

CRITICAL - PIP IS A TINY DRAGON, NOT A CAT:
- This is a DRAGON with fully REPTILIAN features
- Small DRAGON head with ELONGATED REPTILIAN SNOUT (like a tiny dragon or wyvern)
- NOT a cat face - this is a SCALED REPTILE with dragon snout
- Tiny curved horns sprouting from the head
- Large expressive amber eyes with VERTICAL SLIT PUPILS (reptilian)
- Scales covering the entire body - absolutely NO FUR anywhere
- Think fairy dragon, tiny wyvern, or classic D&D pseudodragon

MAIN SUBJECT - PIP THE PSEUDODRAGON:
- Cat-SIZED body (about the size of a house cat) but entirely DRAGON APPEARANCE
- Perched heroically on a weathered moss-covered rock with wings spread wide
- Covered in iridescent reddish-brown SCALES that shimmer with rainbow highlights
- Small DRAGON head: elongated reptilian snout, tiny curved horns, intelligent expression
- Bat-like membranous wings spread dramatically showing wing structure
- Long sinuous dragon body with elegant curved neck
- Long whip-like tail held proudly, ending in distinctive venomous stinger
- Small clawed dragon feet gripping the stone perch
- Pose is HEROIC but ADORABLE - brave little dragon ready for adventure

VISUAL STYLE - MONSTER MANUAL / FIELD GUIDE AESTHETIC:
- Aged parchment or cream paper background with coffee-stained weathered edges
- Hand-drawn annotation lines and arrows pointing to different features
- Handwritten scholar's notes in elegant fantasy calligraphy script
- Medieval naturalist's bestiary / scientific illustration aesthetic
- Classic D&D Monster Manual illustration style
- Small decorative flourishes and corner ornaments

ANNOTATION CALLOUTS (include as visual hand-lettered text with pointing lines/arrows):
1. "Iridescent reddish-brown scales" - arrow pointing to body scales
2. "Bat-like wings for silent flight" - arrow pointing to spread wings
3. "Magic Resistance" - notation near the creature with small arcane symbol
4. "Telepathic Bond" - pointing to head/eyes area with thought-wave illustration
5. "Keen Senses" - pointing to snout/eyes indicating alertness
6. "Venomous stinger tail" - arrow pointing to the distinctive tail tip

LIGHTING AND ATMOSPHERE:
- Warm golden candlelight making scales shimmer beautifully
- Iridescent rainbow highlights catching on the reddish-brown scales
- Soft fantasy glow suggesting magical nature
- Scholarly documentation feel - loving study of a magical creature

COMPOSITION:
- WIDE LANDSCAPE FORMAT (16:10 aspect ratio to fill widescreen display)
- Pip positioned slightly left of center, wings spreading across the frame
- Generous space on right side for scholarly annotations and callouts
- Pip takes up about 50% of horizontal space
- Annotation text distributed around the creature
- No modern elements, no watermarks, no logos

ART STYLE: Professional fantasy illustration blending realistic creature rendering with hand-drawn field guide annotations. Rich warm colors against aged parchment, detailed iridescent scales and translucent wing membranes, painterly quality like classic D&D Monster Manual artwork combined with Victorian naturalist illustration. A scholar's loving documentation of a beloved magical companion creature."""

    print(f"Generating Pip hero image (16:10 landscape field guide)...")
    print(f"Output path: {filepath}")

    # Configure for image generation - 16:9 is closest available to 16:10
    config = types.GenerateContentConfig(
        response_modalities=['Image'],
        image_config=types.ImageConfig(aspect_ratio='16:9')
    )

    # Generate image
    response = client.models.generate_content(
        model=PRO_MODEL_ID,
        contents=prompt,
        config=config
    )

    # Extract and save image
    for part in response.parts:
        if image := part.as_image():
            image.save(str(filepath))
            # Verify and report
            pil_img = Image.open(str(filepath))
            size = pil_img.size
            print(f"Success! Image saved: {filepath}")
            print(f"Dimensions: {size[0]}x{size[1]}")
            return str(filepath)

    raise Exception("No image generated in response")


if __name__ == "__main__":
    filepath = generate_pip_hero_image()
    print(f"\nGenerated Pip hero image: {filepath}")
