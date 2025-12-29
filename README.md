# D&D Graphic Novel Generator

AI-generated graphic novel system for D&D character backstories. Generate beautiful comic panels using OpenAI's gpt-image-1 or Google's Gemini 3 Pro Image, then assemble them into professional-looking comic book pages.

## Features

- **Script Parsing**: Parse structured markdown scripts into page JSON files
- **Dynamic Prompt Assembly**: Character and location descriptions pulled from canonical databases
- **Multi-Variant Generation**: Generate multiple variants per panel for selection
- **Web-Based Review**: Interactive interface to select your favorite variants
- **Page Assembly**: Automatic layout with splash pages and 2x2 grids
- **CBZ Packaging**: Create comic book archives readable by any CBZ reader
- **Web Viewer**: Host your comic online with keyboard navigation

## Quick Start

### 1. Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and add your API keys
cp .env.example .env
# Edit .env with your actual API keys
```

### 2. Create Your Content

1. Write your script in `script.md` (see format below)
2. Create `characters.json` with character descriptions
3. Create `locations.json` with location descriptions
4. Create `style.json` with your aesthetic preferences

### 3. Generate Your Comic

```bash
# Step 1: Parse your script into page JSONs
python scripts/core/parse_script.py

# Step 2: Generate panel images
python scripts/core/generate.py 1        # Single page
python scripts/core/generate.py 1-10     # Range of pages

# Step 3: Review and select variants
python scripts/core/review.py 1

# Step 4: Assemble pages and create CBZ
python scripts/core/assemble.py
```

## Project Structure

```
dnd-graphic-novel/
├── script.md                 # Your comic script
├── characters.json           # Character descriptions database
├── locations.json            # Location descriptions database
├── style.json               # Comic style guidelines
├── pages/                   # Generated page JSONs
│   ├── page-001.json
│   └── ...
├── output/
│   ├── panels/              # Generated panel images
│   ├── pages/               # Assembled pages
│   └── comic.cbz            # Final comic archive
├── scripts/
│   ├── core/                # Main generation scripts
│   └── utilities/           # Helper utilities
└── docs/                    # Web viewer (for hosting online)
```

## Script Format

Write your script in markdown with this structure:

```markdown
# Your Comic Title

## CHARACTER VISUAL DESCRIPTIONS

#### **Character Name** (Role)
**Physical Description:**
- Key physical trait 1
- Key physical trait 2

**Clothing & Equipment:**
- Main outfit details
- Important equipment

## COMIC BOOK NARRATIVE

### Page 1: Scene Title

**Panel 1 (Wide):**
- Visual description of the scene
- What characters are doing
- **Dialogue:**
  - Character: "What they say"

**Panel 2:**
- Next scene description
```

## Database Files

### characters.json

```json
{
  "CharacterName": {
    "name": "CharacterName",
    "full_description": "Complete visual description...",
    "description_components": {
      "head_face": "Face and head details",
      "body_build": "Body type and build",
      "armor_clothing": "What they wear",
      "accessories": "Items they carry"
    }
  }
}
```

### locations.json

```json
{
  "LocationName": {
    "name": "LocationName",
    "full_description": "Complete location description...",
    "description_components": {
      "architecture": "Building style",
      "atmosphere": "Mood and feeling",
      "lighting": "Light sources and quality"
    }
  }
}
```

### style.json

```json
{
  "comic_aesthetic": {
    "base_style": "Professional comic book panel illustration.",
    "art_style": "Bold ink line art, vibrant colors, dynamic composition.",
    "setting_tone": "High fantasy medieval setting.",
    "visual_quality": "High detail, professional quality.",
    "important_restrictions": ["No modern elements", "No text unless dialogue"]
  },
  "dialogue_rendering": {
    "instruction": "Include speech bubbles with dialogue text clearly readable."
  }
}
```

## Web Viewer

Host your comic online by copying the `docs/` folder to any web server. The viewer includes:

- Single page view with navigation
- Grid thumbnail view
- Keyboard shortcuts (arrow keys, A/D, G for grid)
- Touch gestures for mobile
- Character and location galleries

Create `docs/data/pages.json` to configure your pages:

```json
[
  {
    "page": 0,
    "title": "Cover",
    "image": "images/pages/page-000.webp",
    "thumbnail": "images/thumbnails/page-000.webp"
  },
  {
    "page": 1,
    "title": "Chapter 1",
    "image": "images/pages/page-001.webp",
    "thumbnail": "images/thumbnails/page-001.webp",
    "characters": ["Hero", "Sidekick"],
    "locations": ["Tavern"]
  }
]
```

## Cost Estimates

- **OpenAI gpt-image-1**: ~$0.02-0.04 per image (1024x1024)
- **Google Gemini 3 Pro**: ~$0.13 per image

With 3 variants per panel and 4 panels per page:
- Per page: ~$0.24-0.48 (OpenAI) or ~$1.56 (Gemini)
- 20 page comic: ~$5-10 (OpenAI) or ~$31 (Gemini)

## Tips

1. **Write detailed character descriptions** - The more specific, the more consistent your characters will look
2. **Use consistent terminology** - Same clothing, same features, every time
3. **Start with a few pages** - Test your prompts before generating everything
4. **Review carefully** - The variant selection step is crucial for quality
5. **Iterate on style.json** - Fine-tune your aesthetic preferences

## License

MIT License - Feel free to use for your own D&D campaigns!
