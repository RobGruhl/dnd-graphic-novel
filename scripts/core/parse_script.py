#!/usr/bin/env python3
"""
Parse the comic script into structured JSON files - one per page.
Extracts characters, NPCs, locations, and creates prompt-ready panel data.
"""

import re
import json
from pathlib import Path

SCRIPT_FILE = "script.md"  # Your script file
PAGES_DIR = Path("pages")


def extract_characters(content):
    """Extract main party character descriptions."""
    characters = {}

    # Find character section
    char_section = re.search(
        r'## CHARACTER VISUAL DESCRIPTIONS.*?^## ',
        content,
        re.MULTILINE | re.DOTALL
    )

    if not char_section:
        return characters

    char_text = char_section.group(0)

    # Extract each character
    char_pattern = r'#### \*\*(.*?)\*\*.*?(?=#### \*\*|^## )'

    for match in re.finditer(char_pattern, char_text, re.DOTALL):
        name_line = match.group(1)
        char_content = match.group(0)

        # Extract character name (before parentheses if present)
        name = re.sub(r'\s*\(.*?\)', '', name_line).strip()

        # Extract key visual details
        physical = re.search(r'\*\*Physical Description:\*\*(.*?)(?=\*\*|$)', char_content, re.DOTALL)
        clothing = re.search(r'\*\*Clothing & Equipment:\*\*(.*?)(?=\*\*|$)', char_content, re.DOTALL)
        traits = re.search(r'\*\*Distinctive Traits:\*\*(.*?)(?=\*\*|$)', char_content, re.DOTALL)

        # Build concise description
        desc_parts = []
        if physical:
            # Extract key physical traits
            phys_text = physical.group(1).strip()
            lines = [l.strip('- ').strip() for l in phys_text.split('\n') if l.strip().startswith('-')]
            desc_parts.extend(lines[:3])  # Take first 3 key details

        if clothing:
            cloth_text = clothing.group(1).strip()
            lines = [l.strip('- ').strip() for l in cloth_text.split('\n') if l.strip().startswith('-')]
            desc_parts.extend(lines[:2])  # Take 2 clothing details

        characters[name] = ' '.join(desc_parts)

    return characters


def extract_npcs(content):
    """Extract NPC descriptions."""
    npcs = {}

    # Find NPC section
    npc_section = re.search(
        r'### NPCs.*?(?=^## |^### The Party|\Z)',
        content,
        re.MULTILINE | re.DOTALL
    )

    if not npc_section:
        return npcs

    npc_text = npc_section.group(0)

    # Extract each NPC
    npc_pattern = r'#### \*\*(.*?)\*\*.*?(?=#### \*\*|^## |^### |\Z)'

    for match in re.finditer(npc_pattern, npc_text, re.DOTALL):
        name = match.group(1).strip()
        npc_content = match.group(0)

        # Extract description (usually after name)
        desc_lines = []
        for line in npc_content.split('\n')[1:]:
            line = line.strip()
            if line and not line.startswith('**') and not line.startswith('#'):
                desc_lines.append(line.strip('- ').strip())
                if len(desc_lines) >= 3:  # Take first 3 key details
                    break

        npcs[name] = ' '.join(desc_lines)

    return npcs


def extract_locations(content):
    """Extract location descriptions."""
    locations = {}

    # Common locations that appear in the script
    location_keywords = ['festival', 'marketplace', 'citadel', 'forge', 'temple', 'sanctum', 'chamber']

    # For now, return empty - can be expanded later
    # In practice, locations are often described in panel visuals
    return locations


def parse_pages(content, characters, npcs):
    """Parse pages and panels with full context."""

    # Character nickname mapping - customize for your characters
    nickname_map = {
        # Add your character nicknames here
        # 'nickname': 'Full Name',
    }

    # Find narrative section
    narrative = re.search(r'## COMIC BOOK NARRATIVE.*', content, re.DOTALL)
    if not narrative:
        return []

    narrative_text = narrative.group(0)

    # Parse pages
    pages = []
    # Updated pattern to capture end page number for spreads (e.g., "Page 2-3")
    page_pattern = r'### Page (\d+)(?:-(\d+))?:(.*?)(?=### Page \d+(?:-\d+)?:|### Chapter|\Z)'

    for page_match in re.finditer(page_pattern, narrative_text, re.DOTALL):
        page_num = int(page_match.group(1))
        page_end = int(page_match.group(2)) if page_match.group(2) else None
        is_spread = page_end is not None
        page_header = page_match.group(3).split('\n')[0].strip()
        page_content = page_match.group(3)

        # Parse panels
        panels = []
        panel_pattern = r'\*\*Panel (\d+)(?:\s*\(([^)]+)\))?:\*\*(.*?)(?=\*\*Panel \d+(?:\s*\([^)]+\))?:|\*\*Page notes:|\Z)'

        for panel_match in re.finditer(panel_pattern, page_content, re.DOTALL):
            panel_num = int(panel_match.group(1))
            panel_annotation = panel_match.group(2)  # e.g., "Wide", "Large", etc.
            panel_content = panel_match.group(3).strip()

            # Extract visual and dialogue
            lines = panel_content.split('\n')
            visual = []
            dialogue = []

            in_dialogue = False
            for line in lines:
                line = line.strip()
                if line.startswith('- **Dialogue:**') or in_dialogue:
                    in_dialogue = True
                    if line and not line.startswith('- **'):
                        dialogue.append(line.lstrip('- '))
                elif line.startswith('-') and not in_dialogue:
                    visual.append(line.lstrip('- ').strip())

            visual_text = ' '.join(visual)
            dialogue_text = ' '.join(dialogue)

            # Detect characters in this panel (using nicknames)
            panel_characters = {}
            combined_text = (visual_text + ' ' + dialogue_text).lower()

            # Check each word against nickname map
            words = re.findall(r'\b\w+\b', combined_text)
            matched_chars = set()

            for word in words:
                if word in nickname_map:
                    full_name = nickname_map[word]
                    matched_chars.add(full_name)

            # Also check full character names directly
            for char_name in characters.keys():
                if char_name.lower() in combined_text:
                    matched_chars.add(char_name)

            # Add matched characters with descriptions
            for char_name in matched_chars:
                if char_name in characters:
                    panel_characters[char_name] = characters[char_name]

            # Detect NPCs in this panel
            panel_npcs = {}
            for npc_name, npc_desc in npcs.items():
                if npc_name.lower() in combined_text:
                    panel_npcs[npc_name] = npc_desc

            # Determine size/aspect ratio
            # gpt-image-1 supports: 1024x1024, 1536x1024, 1024x1536
            aspect_ratio = "square"
            size = "1024x1024"
            if panel_annotation:
                annotation_lower = panel_annotation.lower()
                if 'wide' in annotation_lower or 'horizontal' in annotation_lower:
                    aspect_ratio = "wide"
                    size = "1536x1024"
                elif 'tall' in annotation_lower or 'vertical' in annotation_lower:
                    aspect_ratio = "tall"
                    size = "1024x1536"
                elif 'splash' in annotation_lower or 'full' in annotation_lower:
                    aspect_ratio = "splash"
                    size = "1024x1536"  # Fixed: was 1536x2048 (not supported)

            panel_data = {
                "panel_num": panel_num,
                "annotation": panel_annotation,
                "visual": visual_text,
                "dialogue": dialogue_text,
                "characters": panel_characters,
                "npcs": panel_npcs,
                "aspect_ratio": aspect_ratio,
                "size": size
            }

            panels.append(panel_data)

        if panels:
            page_data = {
                "page_num": page_num,
                "title": page_header,
                "panel_count": len(panels),
                "is_spread": is_spread,
                "panels": panels
            }
            if is_spread:
                page_data["page_end"] = page_end
            pages.append(page_data)

    return pages


def create_prompt(panel_data):
    """Create a complete prompt from panel data."""

    prompt_parts = []

    # Base description
    prompt_parts.append("Professional comic book panel illustration.")

    # Characters in this panel
    if panel_data["characters"]:
        prompt_parts.append("\nCharacters:")
        for name, desc in panel_data["characters"].items():
            prompt_parts.append(f"- {name}: {desc}")

    # NPCs in this panel
    if panel_data["npcs"]:
        prompt_parts.append("\nNPCs:")
        for name, desc in panel_data["npcs"].items():
            prompt_parts.append(f"- {name}: {desc}")

    # Scene description
    prompt_parts.append(f"\nScene: {panel_data['visual']}")

    # Dialogue
    if panel_data["dialogue"]:
        prompt_parts.append(f"\nDialogue: {panel_data['dialogue']}")
        prompt_parts.append("\nInclude speech bubbles with the dialogue text clearly readable.")

    # Style
    prompt_parts.append("\nStyle: Bold ink line art, vibrant colors, dynamic composition, sequential art style, graphic novel quality.")

    return '\n'.join(prompt_parts)


def main():
    """Parse script and create page JSON files."""

    print("=" * 60)
    print("PARSING COMIC SCRIPT")
    print("=" * 60)

    # Check if script exists
    if not Path(SCRIPT_FILE).exists():
        print(f"\n✗ Script file not found: {SCRIPT_FILE}")
        print(f"  Create your script file or update SCRIPT_FILE variable")
        return

    # Read script
    with open(SCRIPT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract character and NPC data
    print("\n→ Extracting character descriptions...")
    characters = extract_characters(content)
    print(f"  ✓ Found {len(characters)} main characters")

    print("\n→ Extracting NPC descriptions...")
    npcs = extract_npcs(content)
    print(f"  ✓ Found {len(npcs)} NPCs")

    # Parse pages
    print("\n→ Parsing pages and panels...")
    pages = parse_pages(content, characters, npcs)
    print(f"  ✓ Parsed {len(pages)} pages with {sum(p['panel_count'] for p in pages)} total panels")

    # Create pages directory
    PAGES_DIR.mkdir(exist_ok=True)

    # Save each page
    print("\n→ Creating page JSON files...")
    for page in pages:
        # Add prompts to each panel
        for panel in page["panels"]:
            panel["prompt"] = create_prompt(panel)

        # Save page file
        filename = PAGES_DIR / f"page-{page['page_num']:03d}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(page, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Saved {filename.name} ({page['panel_count']} panels)")

    print(f"\n✓ Complete! Created {len(pages)} page files in {PAGES_DIR}/")
    print(f"\nTo generate page 1:")
    print(f"  python scripts/core/generate.py 1")


if __name__ == "__main__":
    main()
