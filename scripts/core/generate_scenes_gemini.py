#!/usr/bin/env python3
"""
Gemini 3 Pro scene generator - parallel generation of adventure visual aids.
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

# Gemini model
MODEL_ID = "gemini-3-pro-image-preview"

# Concurrency settings
MAX_CONCURRENT = int(os.getenv('MAX_CONCURRENT', 12))
VARIANTS_PER_SCENE = 3

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Semaphore created at runtime
semaphore = None

# Stats
stats = {'total': 0, 'successful': 0, 'failed': 0, 'start_time': None}


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

    # Style
    if style_db and 'comic_aesthetic' in style_db:
        parts.append(style_db['comic_aesthetic'].get('base_style', 'Professional comic book illustration.'))
    parts.append("Full page establishing shot. No speech bubbles or text. No main character visible.")
    parts.append("")

    # Location
    if panel.get('location'):
        parts.append(build_location_description(panel['location'], locations_db))
        parts.append("")

    # NPCs
    for npc in panel.get('npcs', []):
        parts.append(build_entity_description(npc, characters_db))

    # Monsters
    for monster in panel.get('monsters', []):
        parts.append(build_entity_description(monster, monsters_db))

    if panel.get('npcs') or panel.get('monsters'):
        parts.append("")

    # Scene
    parts.append(f"Scene: {panel.get('visual', '')}")
    parts.append("")

    # Style details
    if style_db and 'comic_aesthetic' in style_db:
        aesthetic = style_db['comic_aesthetic']
        if aesthetic.get('art_style'):
            parts.append(f"Style: {aesthetic['art_style']}")
        if aesthetic.get('setting_tone'):
            parts.append(aesthetic['setting_tone'])

    return "\n".join(parts)


def generate_image_sync(prompt, output_path, scene_name, variant):
    """Synchronous Gemini image generation."""
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
                logger.info(f"✓ {scene_name} v{variant} ({img.size[0]}x{img.size[1]})")
                return True

        logger.error(f"✗ No image in response: {scene_name} v{variant}")
        return False

    except Exception as e:
        logger.error(f"✗ {scene_name} v{variant}: {e}")
        return False


async def generate_variant(prompt, output_path, scene_name, variant):
    """Generate a single variant with rate limiting."""
    async with semaphore:
        try:
            start = time_module.time()
            success = await asyncio.to_thread(
                generate_image_sync, prompt, output_path, scene_name, variant
            )
            if success:
                stats['successful'] += 1
            else:
                stats['failed'] += 1
            return success
        except Exception as e:
            logger.error(f"✗ {scene_name} v{variant}: {e}")
            stats['failed'] += 1
            return False


async def generate_scene(scene_data, characters_db, locations_db, monsters_db, style_db):
    """Generate all variants for a scene."""
    scene_name = scene_data.get('source_file', '').replace('.json', '')
    title = scene_data.get('title', 'Untitled')
    panel = scene_data['panels'][0]

    prompt = assemble_prompt(panel, characters_db, locations_db, monsters_db, style_db)

    tasks = []
    for v in range(1, VARIANTS_PER_SCENE + 1):
        output_path = SCENE_PANELS_DIR / f"{scene_name}-v{v}.png"
        if output_path.exists():
            logger.info(f"⏭️  {scene_name} v{v} exists, skipping")
            continue
        tasks.append(generate_variant(prompt, output_path, scene_name, v))

    if tasks:
        await asyncio.gather(*tasks)


def load_all_scenes():
    """Load all scene JSON files."""
    scenes = []
    for f in sorted(SCENES_DIR.glob("scene-*.json")):
        with open(f, 'r') as file:
            data = json.load(file)
            data['source_file'] = f.name
            scenes.append(data)
    return scenes


async def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate scene intros with Gemini')
    parser.add_argument('scenes', nargs='?', default='all', help='Scene range or "all"')
    args = parser.parse_args()

    SCENE_PANELS_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize semaphore in the current event loop
    global semaphore
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    # Load databases
    logger.info("Loading databases...")
    characters_db = load_database(CHARACTERS_DB_PATH)
    locations_db = load_database(LOCATIONS_DB_PATH)
    monsters_db = load_database(MONSTERS_DB_PATH)
    style_db = load_database(STYLE_DB_PATH)

    # Load scenes
    all_scenes = load_all_scenes()

    if args.scenes.lower() == 'all':
        scenes = all_scenes
    else:
        # Parse scene numbers
        nums = set()
        for part in args.scenes.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                nums.update(range(start, end + 1))
            else:
                nums.add(int(part))
        scenes = [s for s in all_scenes if s['page_num'] in nums]

    total_images = len(scenes) * VARIANTS_PER_SCENE

    logger.info("=" * 60)
    logger.info("GEMINI SCENE GENERATOR")
    logger.info("=" * 60)
    logger.info(f"Model: {MODEL_ID}")
    logger.info(f"Scenes: {len(scenes)} × {VARIANTS_PER_SCENE} variants = {total_images} images")
    logger.info(f"Concurrency: {MAX_CONCURRENT}")
    logger.info("=" * 60)

    stats['total'] = total_images
    stats['start_time'] = time_module.time()

    # Generate all scenes in parallel
    logger.info("\n🚀 Starting parallel generation...")

    tasks = [
        generate_scene(scene, characters_db, locations_db, monsters_db, style_db)
        for scene in scenes
    ]
    await asyncio.gather(*tasks)

    elapsed = time_module.time() - stats['start_time']

    logger.info("\n" + "=" * 60)
    logger.info("✓ COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    logger.info(f"Generated: {stats['successful']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Output: {SCENE_PANELS_DIR}/")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
