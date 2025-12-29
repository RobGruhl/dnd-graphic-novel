#!/usr/bin/env python3
"""
Extract character and location descriptions from existing page JSONs
and build canonical characters.json and locations.json databases.
"""

import json
from pathlib import Path
from collections import defaultdict

PAGES_DIR = Path("pages")

def extract_databases():
    """Extract all unique characters, NPCs, and locations from page JSONs."""

    # Collect all unique descriptions
    characters_db = {}
    locations_db = {}

    # Track which descriptions appear most frequently for each character
    character_variants = defaultdict(list)
    location_variants = defaultdict(list)

    # Read all page JSONs
    page_files = sorted(PAGES_DIR.glob("page-*.json"))

    print(f"Scanning {len(page_files)} page files...")

    for page_file in page_files:
        with open(page_file, 'r') as f:
            page_data = json.load(f)

        for panel in page_data.get('panels', []):
            # Extract character descriptions
            for char_name, char_desc in panel.get('characters', {}).items():
                if char_desc:  # Skip empty descriptions
                    character_variants[char_name].append(char_desc)

            # Extract NPC descriptions
            for npc_name, npc_desc in panel.get('npcs', {}).items():
                if npc_desc:
                    character_variants[npc_name].append(npc_desc)

            # Extract location from prompt (if exists)
            prompt = panel.get('prompt', '')
            if prompt and 'Location:' in prompt:
                # Extract location section from prompt
                location_section = prompt.split('Location:')[1].split('\n\n')[0]
                location_lines = location_section.strip().split('\n')
                if location_lines:
                    location_name = location_lines[0].strip()
                    location_desc = '\n'.join(location_lines[1:]).strip() if len(location_lines) > 1 else ""
                    if location_name and location_desc:
                        location_variants[location_name].append(location_desc)

    # For each character, pick the most detailed description
    print(f"\nProcessing {len(character_variants)} unique characters/NPCs...")
    for char_name, descriptions in character_variants.items():
        # Pick longest description as canonical (usually most detailed)
        canonical_desc = max(descriptions, key=len) if descriptions else ""

        # Parse description into structured format
        characters_db[char_name] = parse_character_description(char_name, canonical_desc)
        print(f"  ✓ {char_name}: {len(descriptions)} variant(s) found")

    # For each location, pick most detailed description
    print(f"\nProcessing {len(location_variants)} unique locations...")
    for loc_name, descriptions in location_variants.items():
        canonical_desc = max(descriptions, key=len) if descriptions else ""
        locations_db[loc_name] = {
            "name": loc_name,
            "description": canonical_desc
        }
        print(f"  ✓ {loc_name}: {len(descriptions)} variant(s) found")

    return characters_db, locations_db


def parse_character_description(name, description):
    """
    Parse a character description into structured components.
    This is a simple version - could be enhanced with NLP.
    """

    # Try to extract components (this is basic - real implementation could be smarter)
    lines = description.split('.')

    return {
        "name": name,
        "full_description": description,
        "description_components": {
            "visual": description  # For now, store full description
        }
    }


def save_databases(characters_db, locations_db):
    """Save databases to JSON files."""

    # Save characters.json
    with open('characters.json', 'w') as f:
        json.dump(characters_db, f, indent=2)
    print(f"\n✓ Saved {len(characters_db)} characters to characters.json")

    # Save locations.json
    with open('locations.json', 'w') as f:
        json.dump(locations_db, f, indent=2)
    print(f"✓ Saved {len(locations_db)} locations to locations.json")


def main():
    print("=" * 60)
    print("BUILDING CHARACTER AND LOCATION DATABASES")
    print("=" * 60)

    characters_db, locations_db = extract_databases()
    save_databases(characters_db, locations_db)

    print("\n" + "=" * 60)
    print("DATABASE BUILD COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review and enhance characters.json with canonical descriptions")
    print("2. Review and enhance locations.json with canonical descriptions")
    print("3. Update generate.py to use dynamic prompt assembly")
    print("4. Convert page JSONs to reference-based format")


if __name__ == "__main__":
    main()
