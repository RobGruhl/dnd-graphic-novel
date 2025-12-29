# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**D&D Graphic Novel Generator** is an AI-generated graphic novel/comic book system for D&D character backstories. The project uses:
- **OpenAI gpt-image-1** for panel artwork generation
- **Google Gemini 3 Pro Image** for optional alternative generation
- **Structured JSON workflow** for consistent, accurate prompts
- **Python + Pillow** for page assembly and CBZ packaging

**Key Files:**
- `scripts/core/parse_script.py` - Parses script into structured JSON files (one per page)
- `scripts/core/generate.py` - Main generation pipeline with OpenAI
- `scripts/core/generate_nanobananapro.py` - Alternative Gemini-based generation
- `scripts/core/review.py` - Web-based panel variant review interface
- `scripts/core/assemble.py` - Page assembly and CBZ packaging
- `pages/page-NNN.json` - Structured page data with complete prompts
- `characters.json` - Canonical character descriptions database
- `locations.json` - Canonical location descriptions database
- `style.json` - Comic style and aesthetic guidelines
- `requirements.txt` - Python dependencies
- `.env` - API keys (not committed)

## Development Commands

### Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure API keys
# Create .env file with:
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here  # Optional, for Gemini generation
```

### Running

```bash
# Step 1: Parse script into structured JSON (run after script changes)
python scripts/core/parse_script.py

# Step 2: Generate comic panels (with OpenAI)
python scripts/core/generate.py 1        # Generate page 1
python scripts/core/generate.py 1-5      # Generate pages 1-5
python scripts/core/generate.py 1,3,5    # Generate specific pages

# Step 2 Alternative: Generate with Gemini
python scripts/core/generate_nanobananapro.py 1-45

# Step 3: Review and select panel variants
python scripts/core/review.py 1

# Step 4: Assemble pages and create CBZ
python scripts/core/assemble.py 1        # Assemble page 1
python scripts/core/assemble.py          # Assemble all pages
```

## Architecture

### Workflow Pipeline

**Phase 0: Script Parsing (`parse_script.py`)**
- Reads your script markdown file
- Extracts character descriptions
- Extracts NPC descriptions
- Identifies locations
- Creates one JSON file per page in `pages/` directory

**Phase 1: Image Generation (`generate.py`)**
- Loads page data from JSON
- Assembles prompts dynamically from databases
- Generates multiple variants per panel
- Saves to `output/panels/`

**Phase 2: Review & Selection (`review.py`)**
- Web interface for reviewing variants
- Select best variant for each panel
- Generate more variants if needed

**Phase 3: Page Assembly (`assemble.py`)**
- Loads selected panel images
- Applies layout (splash or 2x2 grid)
- Creates assembled pages

**Phase 4: CBZ Packaging**
- Creates ZIP archive with .cbz extension
- Adds ComicInfo.xml metadata

### Database Files

**characters.json** - Canonical character descriptions:
```json
{
  "CharacterName": {
    "name": "CharacterName",
    "full_description": "Complete visual description...",
    "description_components": {
      "head_face": "...",
      "body_build": "...",
      "armor_clothing": "...",
      "accessories": "..."
    }
  }
}
```

**locations.json** - Canonical location descriptions:
```json
{
  "LocationName": {
    "name": "LocationName",
    "full_description": "Complete location description...",
    "description_components": {
      "architecture": "...",
      "atmosphere": "...",
      "lighting": "..."
    }
  }
}
```

**style.json** - Comic aesthetic guidelines:
```json
{
  "comic_aesthetic": {
    "base_style": "Professional comic book panel illustration.",
    "art_style": "Bold ink line art, vibrant colors...",
    "setting_tone": "Medieval fantasy...",
    "important_restrictions": ["No modern elements..."]
  },
  "dialogue_rendering": {
    "instruction": "Include speech bubbles..."
  }
}
```

### Page JSON Structure

```json
{
  "page_num": 1,
  "title": "Chapter Title",
  "panel_count": 4,
  "panels": [
    {
      "panel_num": 1,
      "visual": "Scene description...",
      "dialogue": "Character: \"Line...\"",
      "characters": ["CharacterName"],
      "npcs": ["NPCName"],
      "location": "LocationName",
      "aspect_ratio": "portrait",
      "size": "1024x1536"
    }
  ]
}
```

## Output Structure

```
output/
├── panels/
│   ├── page-001-panel-1-v1.png  (variant 1)
│   ├── page-001-panel-1-v2.png  (variant 2)
│   ├── page-001-panel-1-v3.png  (variant 3)
│   ├── page-001-panel-1.png     (selected final)
│   └── ...
├── pages/
│   ├── page-001.png
│   ├── page-002.png
│   └── ...
└── comic.cbz
```

## Cost Considerations

- **OpenAI gpt-image-1**: ~$0.02-0.04 per image
- **Google Gemini 3 Pro Image**: ~$0.134 per image
- Full comic estimate: panels × cost per image × variants

## Making Changes

### Creating a New Project
1. Create your script markdown file with character descriptions and narrative
2. Update `parse_script.py` to read your script format
3. Run `parse_script.py` to generate page JSONs
4. Create/update `characters.json` with canonical descriptions
5. Create/update `locations.json` with location descriptions
6. Update `style.json` for your desired aesthetic

### Modifying Layouts
Edit `scripts/utilities/layout_engine.py`:
- Adjust `PAGE_WIDTH`, `PAGE_HEIGHT` for different page sizes
- Modify layout functions for different panel arrangements

### Changing Image Quality
Edit generation parameters in `generate.py`:
- `size`: Panel dimensions
- `quality`: "high" for best quality
- Variants per panel for more selection options
