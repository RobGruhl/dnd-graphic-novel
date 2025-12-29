#!/usr/bin/env python3
"""
Aspect Card generator - creates 2:3 ratio card images for D&D adventure.
Uses Gemini 3 Pro Image with parallel generation.
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
CARDS_DIR = Path("cards")
OUTPUT_DIR = Path("output")
CARDS_OUTPUT_DIR = OUTPUT_DIR / "cards"

MODEL_ID = "gemini-3-pro-image-preview"
MAX_CONCURRENT = int(os.getenv('MAX_CONCURRENT', 8))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

semaphore = None
stats = {'total': 0, 'successful': 0, 'failed': 0, 'skipped': 0}


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def build_card_prompt(card, aesthetics):
    """Build a detailed prompt for generating a card image."""
    aspect = card['aspect']
    style = aesthetics[aspect]

    prompt_parts = [
        "Trading card game illustration. Single vertical card design with 2:3 aspect ratio.",
        "Professional fantasy card game art quality. Bold graphic novel style.",
        "",
        f"CARD NAME: {card['name']}",
        f"CARD TYPE: {style['aspect_name']} Aspect",
        "",
        "CARD LAYOUT:",
        f"- Border/Frame: {style['border_style']}",
        f"- Background: {style['background']}",
        f"- Card surface texture: {style['card_texture']}",
        f"- Decorative accents: {style['accent_elements']}",
        "",
        "COLOR SCHEME:",
        f"{style['color_palette']}",
        "",
        "CENTRAL ILLUSTRATION:",
        f"{card['illustration']}",
        "",
        "TEXT ELEMENTS (rendered as part of the card design):",
        f"- Card title at top: \"{card['name']}\" in {style['typography']}",
        f"- Card text area at bottom with: \"{card['description']}\"",
        f"- Game mechanics text: \"{card['mechanics']}\"",
        "",
        "STYLE REQUIREMENTS:",
        "- Clean readable card layout",
        "- Dynamic central artwork taking up 60% of card",
        "- Text legible but integrated into the fantasy aesthetic",
        "- No modern elements, pure medieval fantasy",
        f"- Icon style: {style['icon_style']}"
    ]

    return "\n".join(prompt_parts)


def generate_card_sync(prompt, output_path, card_id):
    """Synchronous Gemini image generation for a card."""
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
                logger.info(f"✓ {card_id} ({img.size[0]}x{img.size[1]})")
                return True

        logger.error(f"✗ No image in response: {card_id}")
        return False

    except Exception as e:
        logger.error(f"✗ {card_id}: {e}")
        return False


async def generate_card(card, aesthetics):
    """Generate a single card with rate limiting."""
    card_id = card['id']
    output_path = CARDS_OUTPUT_DIR / f"{card_id}.png"

    if output_path.exists():
        logger.info(f"⏭️  {card_id} exists, skipping")
        stats['skipped'] += 1
        return True

    prompt = build_card_prompt(card, aesthetics)

    async with semaphore:
        try:
            success = await asyncio.to_thread(
                generate_card_sync, prompt, output_path, card_id
            )
            if success:
                stats['successful'] += 1
            else:
                stats['failed'] += 1
            return success
        except Exception as e:
            logger.error(f"✗ {card_id}: {e}")
            stats['failed'] += 1
            return False


async def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate aspect card images')
    parser.add_argument('--aspect', type=str, help='Generate only cards of this aspect (warrior/hunter/arcane/divine)')
    parser.add_argument('--card', type=str, help='Generate only a specific card by ID')
    args = parser.parse_args()

    CARDS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    global semaphore
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    # Load data
    cards_data = load_json(CARDS_DIR / "cards-data.json")
    aesthetics = load_json(CARDS_DIR / "card-aesthetics.json")

    cards = cards_data['cards']

    # Filter if requested
    if args.aspect:
        cards = [c for c in cards if c['aspect'] == args.aspect.lower()]
    if args.card:
        cards = [c for c in cards if c['id'] == args.card]

    if not cards:
        logger.error("No cards match the filter criteria")
        return

    stats['total'] = len(cards)

    logger.info("=" * 60)
    logger.info("ASPECT CARD GENERATOR")
    logger.info("=" * 60)
    logger.info(f"Model: {MODEL_ID}")
    logger.info(f"Cards to generate: {len(cards)}")
    logger.info(f"Concurrency: {MAX_CONCURRENT}")
    logger.info("=" * 60)

    start_time = time_module.time()

    # Generate all cards in parallel
    logger.info("\n🃏 Starting card generation...")

    tasks = [generate_card(card, aesthetics) for card in cards]
    await asyncio.gather(*tasks)

    elapsed = time_module.time() - start_time

    logger.info("\n" + "=" * 60)
    logger.info("✓ COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    logger.info(f"Generated: {stats['successful']}")
    logger.info(f"Skipped: {stats['skipped']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Output: {CARDS_OUTPUT_DIR}/")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
