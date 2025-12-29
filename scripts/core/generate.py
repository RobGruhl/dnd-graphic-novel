#!/usr/bin/env python3
"""
Async parallel comic generator for D&D Graphic Novel.
Generates multiple variants per panel with intelligent rate limiting.
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
PAGES_JSON_DIR = Path("pages")
OUTPUT_DIR = Path("output")
PANELS_DIR = OUTPUT_DIR / "panels"
PAGES_DIR = OUTPUT_DIR / "pages"
CHARACTERS_DB_PATH = Path("characters.json")
LOCATIONS_DB_PATH = Path("locations.json")
STYLE_DB_PATH = Path("style.json")

# Rate limiting settings (can be overridden via env vars or CLI)
MAX_CONCURRENT = int(os.getenv('MAX_CONCURRENT', 20))  # Maximum concurrent API requests (default: 20)
MAX_RPM = int(os.getenv('MAX_RPM', 50))                # Maximum requests per minute
VARIANTS_PER_PANEL = 3  # Number of variants to generate per panel

# Image generation settings
PANEL_WIDTH = 1024
PANEL_HEIGHT = 1024

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

            # Refill capacity based on time elapsed
            self.capacity = min(
                self.capacity + (self.max_per_minute * elapsed / 60.0),
                self.max_per_minute
            )
            self.last_update = now

            # Wait if no capacity
            while self.capacity < 1.0:
                await asyncio.sleep(0.1)
                now = time_module.time()
                elapsed = now - self.last_update
                self.capacity = min(
                    self.capacity + (self.max_per_minute * elapsed / 60.0),
                    self.max_per_minute
                )
                self.last_update = now

            # Consume one token
            self.capacity -= 1.0


# Global rate limiters
semaphore = asyncio.Semaphore(MAX_CONCURRENT)
rpm_limiter = RPMLimiter(MAX_RPM)


def setup_directories():
    """Create output directory structure."""
    PANELS_DIR.mkdir(parents=True, exist_ok=True)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("✓ Created output directories")


def load_character_database():
    """Load canonical character descriptions from characters.json."""
    if not CHARACTERS_DB_PATH.exists():
        logger.warning(f"⚠ Character database not found at {CHARACTERS_DB_PATH}")
        return {}

    with open(CHARACTERS_DB_PATH, 'r') as f:
        return json.load(f)


def load_location_database():
    """Load canonical location descriptions from locations.json."""
    if not LOCATIONS_DB_PATH.exists():
        logger.warning(f"⚠ Location database not found at {LOCATIONS_DB_PATH}")
        return {}

    with open(LOCATIONS_DB_PATH, 'r') as f:
        return json.load(f)


def load_style_database():
    """Load comic style and aesthetic guidelines from style.json."""
    if not STYLE_DB_PATH.exists():
        logger.warning(f"⚠ Style database not found at {STYLE_DB_PATH}")
        return {}

    with open(STYLE_DB_PATH, 'r') as f:
        return json.load(f)


def build_location_prompt_section(location_name, locations_db):
    """
    Build detailed location description for prompt.

    Args:
        location_name: Name of location
        locations_db: Location database loaded from locations.json

    Returns:
        Formatted location description string
    """
    loc = locations_db.get(location_name)
    if not loc:
        logger.warning(f"⚠ Location '{location_name}' not found in database")
        return f"Location: {location_name} [LOCATION NOT IN DATABASE]"

    # Use structured description_components if available
    desc_components = loc.get('description_components', {})

    if desc_components and len(desc_components) > 1:
        # Build detailed structured description
        parts = [f"Location: {loc['name']}"]

        # Add each component if present
        if desc_components.get('location_context'):
            parts.append(desc_components['location_context'])

        if desc_components.get('architecture'):
            parts.append(desc_components['architecture'])

        if desc_components.get('key_features'):
            parts.append(desc_components['key_features'])

        if desc_components.get('atmosphere'):
            parts.append(desc_components['atmosphere'])

        if desc_components.get('lighting') or desc_components.get('lighting_magic'):
            lighting = desc_components.get('lighting_magic') or desc_components.get('lighting')
            parts.append(lighting)

        # Additional components
        for key in ['surroundings', 'people', 'setting', 'views', 'terrain', 'furniture', 'action', 'magic', 'purpose', 'restrictions', 'style']:
            if desc_components.get(key):
                parts.append(desc_components[key])

        return " ".join(parts)
    else:
        # Fallback to full_description
        desc = loc.get('full_description', loc.get('description', ''))
        return f"Location: {loc['name']}\n{desc}"


def build_character_prompt_section(char_name, characters_db, scene_context="default"):
    """
    Build detailed character description for prompt.

    Args:
        char_name: Name of character
        characters_db: Character database loaded from characters.json
        scene_context: Context for character (e.g., "action", "dialogue", "resting")

    Returns:
        Formatted character description string
    """
    char = characters_db.get(char_name)
    if not char:
        logger.warning(f"⚠ Character '{char_name}' not found in database")
        return f"- {char_name}: [CHARACTER NOT IN DATABASE]"

    # Use structured description_components if available, otherwise fallback to full_description
    desc_components = char.get('description_components', {})

    if desc_components and len(desc_components) > 1:
        # Build detailed structured description
        parts = [f"- {char_name}:"]

        # Add each component if present
        if desc_components.get('head_face'):
            parts.append(f"  HEAD/FACE: {desc_components['head_face']}")

        if desc_components.get('body_build'):
            parts.append(f"  BUILD: {desc_components['body_build']}")

        if desc_components.get('scales_skin'):
            parts.append(f"  APPEARANCE: {desc_components['scales_skin']}")

        if desc_components.get('armor_clothing'):
            parts.append(f"  ARMOR/CLOTHING: {desc_components['armor_clothing']}")

        if desc_components.get('accessories'):
            parts.append(f"  ACCESSORIES: {desc_components['accessories']}")

        if desc_components.get('personality_bearing'):
            parts.append(f"  BEARING: {desc_components['personality_bearing']}")

        # Fallback to visual if other components not present
        if len(parts) == 1 and desc_components.get('visual'):
            parts.append(f"  {desc_components['visual']}")

        return "\n".join(parts)
    else:
        # Fallback to full_description
        desc = char.get('full_description', '')
        return f"- {char_name}: {desc}"


def assemble_prompt(panel_data, characters_db, locations_db, style_db=None):
    """
    Dynamically assemble prompt from panel data and reference databases.

    Args:
        panel_data: Panel dict from page JSON
        characters_db: Loaded character descriptions
        locations_db: Loaded location descriptions
        style_db: Loaded style/aesthetic guidelines (optional)

    Returns:
        Complete prompt string ready for image generation
    """
    parts = []

    # Base style (from style.json or default)
    if style_db and 'comic_aesthetic' in style_db:
        aesthetic = style_db['comic_aesthetic']
        parts.append(aesthetic.get('base_style', 'Professional comic book panel illustration.'))
    else:
        parts.append("Professional comic book panel illustration.")

    parts.append("")  # Blank line

    # Location
    location_name = panel_data.get('location')
    if location_name and location_name in locations_db:
        location_desc = build_location_prompt_section(location_name, locations_db)
        parts.append(location_desc)
        parts.append("")  # Blank line after location

    # Characters
    characters = panel_data.get('characters', [])
    if characters:
        parts.append("Characters:")
        for char_name in characters:
            char_desc = build_character_prompt_section(char_name, characters_db)
            parts.append(char_desc)
        parts.append("")

    # NPCs
    npcs = panel_data.get('npcs', [])
    if npcs:
        parts.append("NPCs:")
        for npc_name in npcs:
            npc_desc = build_character_prompt_section(npc_name, characters_db)
            parts.append(npc_desc)
        parts.append("")

    # Scene description
    visual = panel_data.get('visual', '')
    parts.append(f"Scene: {visual}\n")

    # Dialogue
    dialogue = panel_data.get('dialogue', '')
    if dialogue:
        parts.append(f"Dialogue: {dialogue}\n")

        # Dialogue rendering instruction (from style.json or default)
        if style_db and 'dialogue_rendering' in style_db:
            dialogue_instr = style_db['dialogue_rendering'].get('instruction', '')
            if dialogue_instr:
                parts.append(f"{dialogue_instr}\n")
        else:
            parts.append("Include speech bubbles with dialogue text clearly readable.\n")

    # Style/Aesthetic (from style.json or default)
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

        # Important restrictions
        restrictions = aesthetic.get('important_restrictions', [])
        if restrictions:
            parts.append(f"IMPORTANT: {' '.join(restrictions)}")
    else:
        # Default style
        parts.append("Style: Bold ink line art, vibrant colors, dynamic composition, sequential art style, graphic novel quality, medieval fantasy setting, high fantasy atmosphere.")

    return "\n".join(parts)


def load_page_data(page_num):
    """Load page data from JSON file."""
    # Handle cover page (page 0)
    if page_num == 0:
        page_file = PAGES_JSON_DIR / "cover.json"
    else:
        page_file = PAGES_JSON_DIR / f"page-{page_num:03d}.json"

    if not page_file.exists():
        raise FileNotFoundError(f"Page file not found: {page_file}")

    with open(page_file, 'r', encoding='utf-8') as f:
        return json.load(f)


@retry(
    retry=retry_if_exception_type((RateLimitError, APIError)),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    stop=stop_after_attempt(3)
)
async def generate_panel_variant_async(panel, page_num, variant_num, client, characters_db, locations_db, style_db, is_cover=False):
    """Generate a single variant of a panel with retry logic."""

    # All pages use page-XXX format (page 0 = page-000)
    variant_filename = PANELS_DIR / f"page-{page_num:03d}-panel-{panel['panel_num']}-v{variant_num}.png"

    # Assemble prompt dynamically from panel data and databases
    prompt = assemble_prompt(panel, characters_db, locations_db, style_db)
    if not prompt:
        logger.error(f"  ✗ Could not assemble prompt for panel {panel['panel_num']}")
        return None

    # Get size from panel data or use default
    size = panel.get('size', '1024x1024')

    # Acquire rate limiting tokens
    async with semaphore:
        await rpm_limiter.acquire()

        try:
            start_time = time_module.time()

            # Generate image with OpenAI
            response = await client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size=size,
                quality="high",
                n=1
            )

            duration = time_module.time() - start_time

            # Decode and save image
            image_bytes = base64.b64decode(response.data[0].b64_json)

            async with aiofiles.open(variant_filename, 'wb') as f:
                await f.write(image_bytes)

            logger.info(f"  ✓ Panel {panel['panel_num']} variant {variant_num} generated in {duration:.1f}s")
            return variant_filename

        except Exception as e:
            logger.error(f"  ✗ Error generating panel {panel['panel_num']} variant {variant_num}: {e}")

            # Create placeholder on failure
            img = Image.new('RGB', (PANEL_WIDTH, PANEL_HEIGHT), 'lightgray')
            draw = ImageDraw.Draw(img)
            draw.text((50, 50), f"Error: {str(e)[:100]}", fill='black')
            img.save(variant_filename)

            return variant_filename


async def generate_panel_variants(panel, page_num, client, characters_db, locations_db, style_db, is_cover=False):
    """Generate all variants for a single panel concurrently."""

    # All pages use page-XXX format (page 0 = page-000)
    final_filename = PANELS_DIR / f"page-{page_num:03d}-panel-{panel['panel_num']}.png"

    # Check if final selection already exists
    if final_filename.exists():
        logger.info(f"  ↪ Panel {panel['panel_num']} already selected, skipping")
        return

    # Check if all variants already exist
    all_exist = all(
        (PANELS_DIR / f"page-{page_num:03d}-panel-{panel['panel_num']}-v{i}.png").exists()
        for i in range(1, VARIANTS_PER_PANEL + 1)
    )

    if all_exist:
        logger.info(f"  ↪ Panel {panel['panel_num']} variants already generated, skipping")
        return

    logger.info(f"  → Generating {VARIANTS_PER_PANEL} variants for panel {panel['panel_num']}...")

    # Generate all variants concurrently
    tasks = [
        generate_panel_variant_async(panel, page_num, variant_num, client, characters_db, locations_db, style_db, is_cover)
        for variant_num in range(1, VARIANTS_PER_PANEL + 1)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Count successes
    successes = sum(1 for r in results if r is not None and not isinstance(r, Exception))
    logger.info(f"  ✓ Panel {panel['panel_num']}: {successes}/{VARIANTS_PER_PANEL} variants generated")


async def generate_page_panels(page_data, client, characters_db, locations_db, style_db):
    """Generate all panels for a page."""

    page_num = page_data['page_num']
    panels = page_data['panels']
    is_spread = page_data.get('is_spread', False)
    is_cover = page_data.get('is_cover', False)
    page_end = page_data.get('page_end')

    # Display page info
    page_label = "Cover" if is_cover else f"Page {page_num}"
    if is_spread and page_end:
        page_label += f"-{page_end} (SPREAD)"

    logger.info(f"\n📄 {page_label} ({len(panels)} panels, {len(panels) * VARIANTS_PER_PANEL} total images)")

    # Process all panels in parallel (each panel generates 3 variants concurrently)
    # The semaphore limits total concurrent API requests across all panels
    tasks = [
        generate_panel_variants(panel, page_num, client, characters_db, locations_db, style_db, is_cover)
        for panel in panels
    ]
    await asyncio.gather(*tasks)


async def generate_pages_async(page_nums, force=False, concurrent=None, rpm=None):
    """Generate panels for specified pages."""

    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("✗ Error: OPENAI_API_KEY environment variable not set")
        logger.error("  Set it in .env file or: export OPENAI_API_KEY='your-key-here'")
        return

    client = AsyncOpenAI(api_key=api_key)

    # Load character, location, and style databases
    logger.info("Loading databases...")
    characters_db = load_character_database()
    locations_db = load_location_database()
    style_db = load_style_database()
    logger.info(f"✓ Loaded {len(characters_db)} characters, {len(locations_db)} locations, and style guidelines")

    # Use provided values or defaults
    concurrent = concurrent or MAX_CONCURRENT
    rpm = rpm or MAX_RPM

    logger.info("=" * 60)
    logger.info("D&D GRAPHIC NOVEL GENERATOR")
    logger.info(f"Concurrent requests: {concurrent} | RPM limit: {rpm}")
    logger.info(f"Variants per panel: {VARIANTS_PER_PANEL}")
    logger.info("=" * 60)

    setup_directories()

    # Load page data
    pages_data = []
    for page_num in page_nums:
        try:
            page_data = load_page_data(page_num)
            pages_data.append(page_data)
            logger.info(f"✓ Loaded page {page_num}: '{page_data.get('title', 'Untitled')}' ({page_data['panel_count']} panels)")
        except FileNotFoundError as e:
            logger.error(f"✗ Error loading page {page_num}: {e}")
            logger.error("  Run parse_script.py first to generate page JSON files")
            return

    if not pages_data:
        logger.error("✗ No valid pages to generate")
        return

    # Generate panels
    logger.info("\n" + "=" * 60)
    logger.info("GENERATING PANEL VARIANTS")
    logger.info("=" * 60)

    start_time = time_module.time()

    for page_data in pages_data:
        await generate_page_panels(page_data, client, characters_db, locations_db, style_db)

    duration = time_module.time() - start_time
    total_variants = sum(p['panel_count'] * VARIANTS_PER_PANEL for p in pages_data)

    logger.info("\n" + "=" * 60)
    logger.info(f"✓ Generation complete in {duration:.1f}s ({total_variants} images)")
    logger.info(f"  Next step: python scripts/core/review.py {page_nums[0]}")
    logger.info("=" * 60)

    await client.close()


def parse_page_range(page_arg):
    """Parse page argument (e.g., '1', '1-5', '1,3,5')."""
    pages = []

    for part in page_arg.split(','):
        if '-' in part:
            start, end = part.split('-')
            pages.extend(range(int(start), int(end) + 1))
        else:
            pages.append(int(part))

    return sorted(set(pages))


def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(
        description='Generate comic panel variants with OpenAI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate.py 1          # Generate page 1
  python generate.py 1-5        # Generate pages 1-5
  python generate.py 1,3,5      # Generate pages 1, 3, and 5
  python generate.py 1 --force  # Regenerate page 1 even if exists
        """
    )

    parser.add_argument(
        'pages',
        type=str,
        help='Page number(s) to generate (e.g., 1, 1-5, 1,3,5)'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Regenerate panels even if they already exist'
    )

    parser.add_argument(
        '--concurrent',
        type=int,
        default=MAX_CONCURRENT,
        help=f'Maximum concurrent requests (default: {MAX_CONCURRENT})'
    )

    parser.add_argument(
        '--rpm',
        type=int,
        default=MAX_RPM,
        help=f'Maximum requests per minute (default: {MAX_RPM})'
    )

    args = parser.parse_args()

    # Update global rate limiters
    global semaphore, rpm_limiter
    semaphore = asyncio.Semaphore(args.concurrent)
    rpm_limiter = RPMLimiter(args.rpm)

    # Parse page numbers
    try:
        page_nums = parse_page_range(args.pages)
    except ValueError as e:
        logger.error(f"✗ Invalid page argument: {args.pages}")
        logger.error(f"  Use format like: 1, 1-5, or 1,3,5")
        sys.exit(1)

    # Run async generation
    asyncio.run(generate_pages_async(page_nums, args.force, args.concurrent, args.rpm))


if __name__ == "__main__":
    main()
