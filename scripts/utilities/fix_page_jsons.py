#!/usr/bin/env python3
"""
Fix page JSONs to include complete character, monster, and location descriptions.
Reads from characters.json, monsters.json, and locations.json databases.
"""

import json
import re
from pathlib import Path

# Paths
PAGES_DIR = Path("pages")
CHARACTERS_DB = Path("characters.json")
MONSTERS_DB = Path("monsters.json")
LOCATIONS_DB = Path("locations.json")

# Load databases
with open(CHARACTERS_DB) as f:
    characters = json.load(f)
with open(MONSTERS_DB) as f:
    monsters = json.load(f)
with open(LOCATIONS_DB) as f:
    locations = json.load(f)

# Merge for unified lookup
all_entities = {**characters, **monsters}

# Character name mappings (visual text -> database key)
CHARACTER_MAPPINGS = {
    # Main characters
    "Lightsword": "LightswordGlowing",
    "Lightsword (pre-transformation)": "LightswordGlowing",
    "Lightsword (glowing form)": "LightswordGlowing",
    "Lightsword (Lizardfolk)": "LightswordLizardfolk",
    "Lightsword (post-transformation)": "LightswordLizardfolk",

    # Companions
    "Spore": "Spore",
    "Spore (captive)": "SporeCaptive",
    "Darkstorm": "Darkstorm",
    "Dire Wolf": "DireWolfCursed",
    "Cursed Dire Wolf": "DireWolfCursed",
    "Dire Wolf (healing)": "DireWolfAlly",
    "Dire Wolf (healed)": "Darkstorm",
    "Pip": "Pip",
    "Pip (injured)": "PipInjured",
    "Starwind": "Starwind",
    "Starwind (cursed)": "StarwindCursed",
    "Starwind (chained)": "StarwindCursed",

    # NPCs
    "The Elder": "TheElder",
    "Elder": "TheElder",
    "Elder (weakened)": "ElderWeakened",
    "Garrett": "GarrettMerchant",
    "Garrett the Merchant": "GarrettMerchant",
    "Garrett (hiding)": "GarrettHiding",

    # Monsters
    "Goblins": "GoblinWarrior",
    "Goblin": "GoblinWarrior",
    "Goblin Boss": "GoblinBoss",
    "Flying Sword": "AnimatedFlyingSword",
    "Flying Swords": "AnimatedFlyingSword",
    "Animated Sword": "AnimatedFlyingSword",
    "Shadow": "Shadow",
    "Shadows": "Shadow",
    "Shadow Sorcerer": "ShadowSorcerer",
    "The Shadow Sorcerer": "ShadowSorcerer",
    "Shadow Sorcerer (fading)": "ShadowSorcererFading",
}

# Location mappings (panel context -> database key)
LOCATION_MAPPINGS = {
    "cave bedroom": "the PlayerRoom",
    "underground cave": "the PlayerRoom",
    "cave home": "the PlayerRoom",
    "temple courtyard": "TempleCourtyard",
    "temple of aspects": "TempleCourtyard",
    "four pillars": "TempleCourtyard",
    "pillar": "TempleCourtyard",
    "stone bridge": "StoneBridge",
    "bridge": "StoneBridge",
    "ruined tower": "TowerRuins",
    "tower": "TowerRuins",
    "goblin tower": "TowerRuins",
    "merchant wagon": "MerchantWagon",
    "maze entrance": "MazeEntrance",
    "maze of echoes": "MazeEntrance",
    "crystal halls": "MazeCrystalHalls",
    "maze": "MazeCrystalHalls",
    "sword chamber": "MazeSwordRoom",
    "sword room": "MazeSwordRoom",
    "pip alcove": "PseudodragonAlcove",
    "hidden alcove": "PseudodragonAlcove",
    "cursed grove": "DarkGrove",
    "dark grove": "DarkGrove",
    "grove": "DarkGrove",
    "pegasus": "DarkGrove",
    "flight": "SkyFlight",
    "flying": "SkyFlight",
    "sky": "SkyFlight",
    "corrupted temple": "CorruptedTemple",
    "temple under shadow": "CorruptedTemple",
    "shadow halls": "ShadowHalls",
    "inner sanctum": "TempleSanctum",
    "sanctum": "TempleSanctum",
}


def get_db_key(name):
    """Get database key for a character/monster name."""
    # Check direct mapping
    if name in CHARACTER_MAPPINGS:
        return CHARACTER_MAPPINGS[name]

    # Check if it's already a valid key
    if name in all_entities:
        return name

    # Try case-insensitive match
    for key in all_entities:
        if key.lower() == name.lower():
            return key

    return None


def get_location_key(visual_text):
    """Infer location key from visual text."""
    visual_lower = visual_text.lower()

    for pattern, loc_key in LOCATION_MAPPINGS.items():
        if pattern in visual_lower:
            return loc_key

    return None


def get_full_description(db_key):
    """Get full description for a character/monster."""
    if db_key not in all_entities:
        return None

    entity = all_entities[db_key]
    return entity.get('full_description', '')


def fix_panel(panel, page_num):
    """Fix a single panel's character and location entries."""
    visual = panel.get('visual', '')
    changes = []

    # Fix location if missing
    if not panel.get('location'):
        loc_key = get_location_key(visual)
        if loc_key:
            panel['location'] = loc_key
            changes.append(f"Added location: {loc_key}")

    # Get current characters dict
    chars = panel.get('characters', {})
    if not isinstance(chars, dict):
        chars = {}

    # Look for characters/monsters mentioned in visual
    # Common patterns to look for
    entities_to_check = [
        "Lightsword", "Spore", "Darkstorm", "Pip", "Starwind",
        "Dire Wolf", "Elder", "Garrett", "Goblin", "Shadow Sorcerer",
        "Flying Sword", "Shadow", "shadows"
    ]

    for entity_name in entities_to_check:
        # Check if entity is mentioned in visual but not in characters dict
        if entity_name.lower() in visual.lower():
            # Determine the right database key
            db_key = get_db_key(entity_name)

            # Check variant forms
            if "captive" in visual.lower() and entity_name == "Spore":
                db_key = "SporeCaptive"
            elif "injured" in visual.lower() and entity_name == "Pip":
                db_key = "PipInjured"
            elif "cursed" in visual.lower() and entity_name == "Starwind":
                db_key = "StarwindCursed"
            elif "chained" in visual.lower() and entity_name == "Starwind":
                db_key = "StarwindCursed"
            elif "fading" in visual.lower() and entity_name == "Shadow Sorcerer":
                db_key = "ShadowSorcererFading"
            elif "healing" in visual.lower() and entity_name == "Dire Wolf":
                db_key = "DireWolfAlly"
            elif "healed" in visual.lower() and entity_name == "Dire Wolf":
                db_key = "Darkstorm"

            if db_key and db_key not in chars:
                desc = get_full_description(db_key)
                if desc:
                    chars[db_key] = desc
                    changes.append(f"Added {db_key}")

    panel['characters'] = chars
    return changes


def fix_page(page_num):
    """Fix all panels in a page."""
    page_file = PAGES_DIR / f"page-{page_num:03d}.json"

    if not page_file.exists():
        print(f"Page {page_num} not found")
        return

    with open(page_file) as f:
        page_data = json.load(f)

    all_changes = []
    for panel in page_data.get('panels', []):
        panel_num = panel.get('panel_num', '?')
        changes = fix_panel(panel, page_num)
        if changes:
            all_changes.append(f"  Panel {panel_num}: {', '.join(changes)}")

    if all_changes:
        print(f"\nPage {page_num} ({page_data.get('title', 'Untitled')}):")
        for change in all_changes:
            print(change)

        # Save updated page
        with open(page_file, 'w') as f:
            json.dump(page_data, f, indent=2)
        print(f"  Saved!")
    else:
        print(f"Page {page_num}: No changes needed")


def main():
    print("=" * 60)
    print("PAGE JSON FIXER")
    print("=" * 60)
    print(f"Loaded {len(characters)} characters, {len(monsters)} monsters, {len(locations)} locations")
    print()

    # Fix all pages 1-24
    for page_num in range(1, 25):
        fix_page(page_num)

    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
