#!/usr/bin/env python3
"""
Generate trial images with Gemini - 1 image per trial to conserve quota.
"""

import os
import sys
import json
import asyncio
import logging
import time as time_module
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

# Configuration
SCENES_DIR = Path("scenes")
OUTPUT_DIR = Path("output")
SCENE_PANELS_DIR = OUTPUT_DIR / "scene_panels"
CHARACTERS_DB_PATH = Path("characters.json")
LOCATIONS_DB_PATH = Path("locations.json")
MONSTERS_DB_PATH = Path("monsters.json")
STYLE_DB_PATH = Path("style.json")

MODEL_ID = "gemini-3-pro-image-preview"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def load_database(path):
    if not path.exists():
        return {}
    with open(path, 'r') as f:
        return json.load(f)


def build_entity_description(name, database):
    entity = database.get(name)
    if not entity:
        return f"- {name}"

    desc = entity.get('description_components', {})
    if desc:
        parts = [f"- {entity.get('name', name)}:"]
        for key, value in desc.items():
            if value and key != 'name':
                parts.append(f"  {value}")
        return "\n".join(parts)
    return f"- {entity.get('name', name)}: {entity.get('full_description', '')}"


def build_location_description(name, locations_db):
    loc = locations_db.get(name)
    if not loc:
        return f"Location: {name}"

    desc = loc.get('description_components', {})
    if desc:
        parts = [f"Location: {loc.get('name', name)}"]
        for value in desc.values():
            if value:
                parts.append(value)
        return " ".join(parts)
    return f"Location: {loc.get('name', name)}\n{loc.get('full_description', '')}"


def assemble_prompt(panel, characters_db, locations_db, monsters_db, style_db):
    parts = []

    if style_db and 'comic_aesthetic' in style_db:
        parts.append(style_db['comic_aesthetic'].get('base_style', 'Professional comic book illustration.'))
    parts.append("Full page establishing shot. No speech bubbles or text. No main character visible.")
    parts.append("")

    if panel.get('location'):
        parts.append(build_location_description(panel['location'], locations_db))
        parts.append("")

    for npc in panel.get('npcs', []):
        parts.append(build_entity_description(npc, characters_db))

    for monster in panel.get('monsters', []):
        parts.append(build_entity_description(monster, monsters_db))

    if panel.get('npcs') or panel.get('monsters'):
        parts.append("")

    parts.append(f"Scene: {panel.get('visual', '')}")
    parts.append("")

    if style_db and 'comic_aesthetic' in style_db:
        aesthetic = style_db['comic_aesthetic']
        if aesthetic.get('art_style'):
            parts.append(f"Style: {aesthetic['art_style']}")
        if aesthetic.get('setting_tone'):
            parts.append(aesthetic['setting_tone'])

    return "\n".join(parts)


def generate_image(prompt, output_path, trial_name):
    """Generate a single image."""
    try:
        client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

        config = types.GenerateContentConfig(
            response_modalities=['Image'],
            image_config=types.ImageConfig(aspect_ratio='2:3')
        )

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=config
        )

        for part in response.parts:
            if image := part.as_image():
                image.save(str(output_path))
                img = Image.open(str(output_path))
                logger.info(f"✓ {trial_name} ({img.size[0]}x{img.size[1]})")
                return True

        logger.error(f"✗ No image in response: {trial_name}")
        return False

    except Exception as e:
        logger.error(f"✗ {trial_name}: {e}")
        return False


def main():
    import sys

    SCENE_PANELS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Loading databases...")
    characters_db = load_database(CHARACTERS_DB_PATH)
    locations_db = load_database(LOCATIONS_DB_PATH)
    monsters_db = load_database(MONSTERS_DB_PATH)
    style_db = load_database(STYLE_DB_PATH)

    # Load trial or tutorial JSON files based on argument
    pattern = sys.argv[1] if len(sys.argv) > 1 else "trial"
    trial_files = sorted(SCENES_DIR.glob(f"{pattern}-*.json"))

    logger.info("=" * 60)
    logger.info("TRIAL IMAGE GENERATOR (1 per trial)")
    logger.info("=" * 60)
    logger.info(f"Found {len(trial_files)} trial files")
    logger.info("=" * 60)

    start_time = time_module.time()
    successful = 0
    failed = 0

    for trial_file in trial_files:
        with open(trial_file, 'r') as f:
            trial_data = json.load(f)

        trial_name = trial_file.stem  # e.g., "trial-01-dire-wolf"
        title = trial_data.get('title', 'Untitled')
        panel = trial_data['panels'][0]

        output_path = SCENE_PANELS_DIR / f"{trial_name}.png"

        if output_path.exists():
            logger.info(f"⏭️  {trial_name} exists, skipping")
            continue

        logger.info(f"\n🎨 Generating: {title}")
        prompt = assemble_prompt(panel, characters_db, locations_db, monsters_db, style_db)

        if generate_image(prompt, output_path, trial_name):
            successful += 1
        else:
            failed += 1

    elapsed = time_module.time() - start_time

    logger.info("\n" + "=" * 60)
    logger.info("✓ COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Time: {elapsed:.1f}s")
    logger.info(f"Generated: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Output: {SCENE_PANELS_DIR}/")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
