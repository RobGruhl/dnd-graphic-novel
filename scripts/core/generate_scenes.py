#!/usr/bin/env python3
"""
Scene intro generator for D&D Graphic Novel.
Generates full-page establishing shots for adventure visual aids.
"""

import os
import sys
import json
import base64
import asyncio
import argparse
import logging
from pathlib import Path
from openai import AsyncOpenAI
from PIL import Image, ImageDraw
from dotenv import load_dotenv
import aiofiles
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type
)
from openai import RateLimitError, APIError
import time as time_module

# Load environment variables
load_dotenv()

# Configuration
SCENES_DIR = Path("scenes")
OUTPUT_DIR = Path("output")
SCENE_PANELS_DIR = OUTPUT_DIR / "scene_panels"
CHARACTERS_DB_PATH = Path("characters.json")
LOCATIONS_DB_PATH = Path("locations.json")
MONSTERS_DB_PATH = Path("monsters.json")
STYLE_DB_PATH = Path("style.json")

# Rate limiting settings
MAX_CONCURRENT = int(os.getenv('MAX_CONCURRENT', 10))
MAX_RPM = int(os.getenv('MAX_RPM', 30))
VARIANTS_PER_SCENE = 3

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class RPMLimiter:
    """Token bucket rate limiter for requests per minute."""

    def __init__(self, max_per_minute):
        self.max_per_minute = max_per_minute
        self.capacity = float(max_per_minute)
        self.last_update = time_module.time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Acquire permission to make a request."""
        async with self.lock:
            now = time_module.time()
            elapsed = now - self.last_update
            self.capacity = min(
                self.capacity + (self.max_per_minute * elapsed / 60.0),
                self.max_per_minute
            )
            self.last_update = now

            while self.capacity < 1.0:
                await asyncio.sleep(0.1)
                now = time_module.time()
                elapsed = now - self.last_update
                self.capacity = min(
                    self.capacity + (self.max_per_minute * elapsed / 60.0),
                    self.max_per_minute
                )
                self.last_update = now

            self.capacity -= 1.0


# Global rate limiters
semaphore = asyncio.Semaphore(MAX_CONCURRENT)
rpm_limiter = RPMLimiter(MAX_RPM)


def setup_directories():
    """Create output directory structure."""
    SCENE_PANELS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("✓ Created output directories")


def load_database(path):
    """Load a JSON database file."""
    if not path.exists():
        logger.warning(f"⚠ Database not found at {path}")
        return {}
    with open(path, 'r') as f:
        return json.load(f)


def build_entity_description(name, database, entity_type="character"):
    """Build description for a character, NPC, or monster."""
    entity = database.get(name)
    if not entity:
        logger.warning(f"⚠ {entity_type} '{name}' not found in database")
        return f"- {name}: [{entity_type.upper()} NOT IN DATABASE]"

    desc_components = entity.get('description_components', {})

    if desc_components and len(desc_components) > 1:
        parts = [f"- {entity.get('name', name)}:"]

        for key, value in desc_components.items():
            if value and key != 'name':
                parts.append(f"  {key.upper()}: {value}")

        return "\n".join(parts)
    else:
        desc = entity.get('full_description', '')
        return f"- {entity.get('name', name)}: {desc}"


def build_location_description(location_name, locations_db):
    """Build detailed location description."""
    loc = locations_db.get(location_name)
    if not loc:
        return f"Location: {location_name}"

    desc_components = loc.get('description_components', {})

    if desc_components:
        parts = [f"Location: {loc.get('name', location_name)}"]
        for key, value in desc_components.items():
            if value:
                parts.append(value)
        return " ".join(parts)
    else:
        return f"Location: {loc.get('name', location_name)}\n{loc.get('full_description', '')}"


def assemble_scene_prompt(panel_data, characters_db, locations_db, monsters_db, style_db):
    """Assemble a complete prompt for scene generation."""
    parts = []

    # Base style
    if style_db and 'comic_aesthetic' in style_db:
        aesthetic = style_db['comic_aesthetic']
        parts.append(aesthetic.get('base_style', 'Professional comic book panel illustration.'))
        parts.append("Full page establishing shot. No speech bubbles or text.")
    else:
        parts.append("Professional comic book panel illustration. Full page establishing shot.")

    parts.append("")

    # Location
    location_name = panel_data.get('location')
    if location_name:
        location_desc = build_location_description(location_name, locations_db)
        parts.append(location_desc)
        parts.append("")

    # NPCs
    npcs = panel_data.get('npcs', [])
    if npcs:
        parts.append("Characters present:")
        for npc_name in npcs:
            npc_desc = build_entity_description(npc_name, characters_db, "NPC")
            parts.append(npc_desc)
        parts.append("")

    # Monsters
    monsters = panel_data.get('monsters', [])
    if monsters:
        parts.append("Creatures present:")
        for monster_name in monsters:
            monster_desc = build_entity_description(monster_name, monsters_db, "monster")
            parts.append(monster_desc)
        parts.append("")

    # Scene visual description
    visual = panel_data.get('visual', '')
    parts.append(f"Scene: {visual}")
    parts.append("")

    # Style
    if style_db and 'comic_aesthetic' in style_db:
        aesthetic = style_db['comic_aesthetic']
        style_parts = []
        if aesthetic.get('art_style'):
            style_parts.append(aesthetic['art_style'])
        if aesthetic.get('setting_tone'):
            style_parts.append(aesthetic['setting_tone'])
        if aesthetic.get('visual_quality'):
            style_parts.append(aesthetic['visual_quality'])
        if style_parts:
            parts.append(f"Style: {' '.join(style_parts)}")

        restrictions = aesthetic.get('important_restrictions', [])
        if restrictions:
            parts.append(f"IMPORTANT: {' '.join(restrictions)}")

    return "\n".join(parts)


def load_scene_data(scene_num):
    """Load scene data from JSON file."""
    # Find matching scene file
    pattern = f"scene-{scene_num:03d}-*.json"
    matching = list(SCENES_DIR.glob(pattern))

    if not matching:
        raise FileNotFoundError(f"Scene file not found matching: {pattern}")

    scene_file = matching[0]
    with open(scene_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        data['source_file'] = scene_file.name
        return data


def get_all_scene_numbers():
    """Get all available scene numbers."""
    scenes = []
    for f in SCENES_DIR.glob("scene-*.json"):
        try:
            num = int(f.name.split('-')[1])
            scenes.append(num)
        except (IndexError, ValueError):
            continue
    return sorted(scenes)


@retry(
    retry=retry_if_exception_type((RateLimitError, APIError)),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    stop=stop_after_attempt(3)
)
async def generate_scene_variant(panel, scene_num, variant_num, client, characters_db, locations_db, monsters_db, style_db, scene_name):
    """Generate a single variant of a scene."""

    variant_filename = SCENE_PANELS_DIR / f"{scene_name}-v{variant_num}.png"

    prompt = assemble_scene_prompt(panel, characters_db, locations_db, monsters_db, style_db)

    size = panel.get('size', '1024x1536')

    async with semaphore:
        await rpm_limiter.acquire()

        try:
            start_time = time_module.time()

            response = await client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size=size,
                quality="high",
                n=1
            )

            duration = time_module.time() - start_time

            image_bytes = base64.b64decode(response.data[0].b64_json)

            async with aiofiles.open(variant_filename, 'wb') as f:
                await f.write(image_bytes)

            logger.info(f"  ✓ Variant {variant_num} generated in {duration:.1f}s → {variant_filename.name}")
            return variant_filename

        except Exception as e:
            logger.error(f"  ✗ Error generating variant {variant_num}: {e}")
            return None


async def generate_scene(scene_data, client, characters_db, locations_db, monsters_db, style_db):
    """Generate all variants for a scene."""

    scene_num = scene_data['page_num']
    title = scene_data.get('title', 'Untitled')
    source_file = scene_data.get('source_file', '')

    # Extract scene name from source file
    scene_name = source_file.replace('.json', '') if source_file else f"scene-{scene_num:03d}"

    logger.info(f"\n🎬 Scene {scene_num}: {title}")
    logger.info(f"   Source: {source_file}")

    panel = scene_data['panels'][0]  # Scene intros have 1 panel

    # Check if variants already exist
    existing = list(SCENE_PANELS_DIR.glob(f"{scene_name}-v*.png"))
    if len(existing) >= VARIANTS_PER_SCENE:
        logger.info(f"  ↪ All variants already exist, skipping")
        return

    logger.info(f"  → Generating {VARIANTS_PER_SCENE} variants...")

    tasks = [
        generate_scene_variant(panel, scene_num, v, client, characters_db, locations_db, monsters_db, style_db, scene_name)
        for v in range(1, VARIANTS_PER_SCENE + 1)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    successes = sum(1 for r in results if r is not None and not isinstance(r, Exception))
    logger.info(f"  ✓ {successes}/{VARIANTS_PER_SCENE} variants generated")


async def generate_scenes_async(scene_nums):
    """Generate specified scenes."""

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("✗ OPENAI_API_KEY not set")
        return

    client = AsyncOpenAI(api_key=api_key)

    # Load databases
    logger.info("Loading databases...")
    characters_db = load_database(CHARACTERS_DB_PATH)
    locations_db = load_database(LOCATIONS_DB_PATH)
    monsters_db = load_database(MONSTERS_DB_PATH)
    style_db = load_database(STYLE_DB_PATH)
    logger.info(f"✓ Loaded {len(characters_db)} characters, {len(locations_db)} locations, {len(monsters_db)} monsters")

    logger.info("=" * 60)
    logger.info("SCENE INTRO GENERATOR")
    logger.info(f"Generating {len(scene_nums)} scenes × {VARIANTS_PER_SCENE} variants each")
    logger.info("=" * 60)

    setup_directories()

    # Load and generate scenes
    start_time = time_module.time()

    for scene_num in scene_nums:
        try:
            scene_data = load_scene_data(scene_num)
            await generate_scene(scene_data, client, characters_db, locations_db, monsters_db, style_db)
        except FileNotFoundError as e:
            logger.error(f"✗ {e}")

    duration = time_module.time() - start_time
    logger.info("\n" + "=" * 60)
    logger.info(f"✓ Generation complete in {duration:.1f}s")
    logger.info(f"  Output: {SCENE_PANELS_DIR}/")
    logger.info("=" * 60)

    await client.close()


def parse_scene_range(arg):
    """Parse scene argument (e.g., '1', '1-5', '1,3,5', 'all')."""
    if arg.lower() == 'all':
        return get_all_scene_numbers()

    scenes = []
    for part in arg.split(','):
        if '-' in part:
            start, end = part.split('-')
            scenes.extend(range(int(start), int(end) + 1))
        else:
            scenes.append(int(part))
    return sorted(set(scenes))


def main():
    parser = argparse.ArgumentParser(
        description='Generate scene intro images for adventure visual aids',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_scenes.py 1        # Generate scene 1
  python generate_scenes.py 1-3      # Generate scenes 1-3
  python generate_scenes.py all      # Generate all scenes
        """
    )

    parser.add_argument(
        'scenes',
        type=str,
        help='Scene number(s) to generate (e.g., 1, 1-5, all)'
    )

    args = parser.parse_args()

    try:
        scene_nums = parse_scene_range(args.scenes)
    except ValueError:
        logger.error(f"✗ Invalid scene argument: {args.scenes}")
        sys.exit(1)

    if not scene_nums:
        logger.error("✗ No scenes found")
        sys.exit(1)

    asyncio.run(generate_scenes_async(scene_nums))


if __name__ == "__main__":
    main()
