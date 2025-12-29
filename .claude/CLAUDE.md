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

---

## Live Session DM Mode: The Trials of the Choosing

**Claude is CO-DUNGEON MASTER** alongside Rob (the human DM). Rob runs the laptop, rolls dice, and speaks to Hendrix. Claude provides real-time support via transcript processing.

### Co-DM Responsibilities

**ALWAYS provide READ-ALOUD TEXT** for Rob to speak to Hendrix. Format it clearly:

```
📖 READ ALOUD:
"The massive wolf blocks your path, hackles raised, teeth bared in a
vicious snarl. Its eyes glow with an unnatural orange light. One front
leg hovers slightly off the ground. What do you do?"
```

When responding to transcripts, Claude should provide:
1. **Read-aloud text** - Boxed narration Rob can speak verbatim
2. **Mechanics** - DC, rolls needed, card suggestions
3. **Outcome options** - Success/failure narration ready to go
4. **DM notes** - Whispered tips for Rob (not read aloud)

### Image Generation Agent

The **dnd-image-generator** agent creates images on-demand during play:
- Trigger: "make an image of...", "illustrate...", "show me..."
- Uses Gemini 3 Pro Image (nanobanana pro)
- Pulls descriptions from `characters.json`, `locations.json`, `monsters.json`
- Saves to `output/campaign-images/` with timestamp filenames
- 2:3 portrait aspect ratio
- **Automatically opens the image in Chrome** after generation

Example: "Make an image of Hendrix facing down the dire wolf on the bridge"

### Displaying Scene Images

As the adventure progresses, **open scene images in Chrome** for Hendrix to see:

```bash
open -a "Google Chrome" output/scene_panels/IMAGE_NAME.png
```

Proactively display relevant images when:
- Entering a new location (show establishing shot)
- Starting a trial (show trial image)
- Beginning tutorial pillars (show pillar image)
- Dramatic moments warrant visualization

### Equipment Checklist
- [ ] Blue Yeti microphone (set to **interview mode**)
- [ ] USB-A to USB-C adapter
- [ ] Headphones
- [ ] Analog pomodoro timer (ticking adds urgency!)
- [ ] Printed Aspect Cards (`output/aspect-cards-printable-compressed.pdf`)
- [ ] Scene images on laptop for showing Hendrix

### Hendrix-Specific Notes
- **Age:** 10 years old
- **NO zombies or undead humans** (mom confirmed)
- **OK:** Skeletons, evil wizards, shadows, monsters
- **Final boss:** "Shadow Sorcerer" (hooded wizard with purple eyes) - uses Specter stats
- **Tone:** Heroic and fun, not scary. Celebrate creativity!

### 90-Minute Timer Breakdown

| Timer | Scenes | Content | If Running Long |
|-------|--------|---------|-----------------|
| **15 min** | 1-2 | Temple ceremony, get cards, tutorial | Skip pillar tests, jump to "You're chosen!" |
| **15 min** | 3 | Bridge + Dire Wolf | One attempt, then wolf lets them pass |
| **15 min** | 4 | Tower + Goblins | 2 combat rounds max, merchant saved |
| **20 min** | 5-8 | Maze + Pip | Skip color puzzle, find Pip quickly |
| **15 min** | 9-10 | Grove + Pegasus + Flight | One combat round, then rescue |
| **10 min** | 11-12 | Shadow Sorcerer finale | Roleplay OR 2-round combat |

**Timer rules:** When it dings, say "The magic pulls you forward! What do you do RIGHT NOW?"

### Scene Images (Show on Laptop)

```
output/scene_panels/
# Establishing shots (3 variants each)
├── scene-001-temple-courtyard-v[1-3].png   # Ceremony
├── scene-002-whispering-valley-v[1-3].png  # Valley path
├── scene-003-stone-bridge-v[1-3].png       # Dire wolf
├── scene-004-ruined-tower-v[1-3].png       # Goblin fight
├── scene-005-maze-entrance-v[1-3].png      # Maze start
├── scene-006-crystal-halls-v[1-3].png      # Inside maze
├── scene-007-sword-chamber-v[1-3].png      # Flying swords
├── scene-008-pip-alcove-v[1-3].png         # Pseudodragon
├── scene-009-cursed-grove-v[1-3].png       # Shadows + Pegasus
├── scene-010-pegasus-flight-v[1-3].png     # Flying scene
├── scene-011-corrupted-temple-v[1-3].png   # Temple under attack
├── scene-012-inner-sanctum-v[1-3].png      # Shadow Sorcerer boss

# Tutorial pillar images (cinematic shots)
├── tutorial-01-red-pillar.png    # Warrior test - armored dummy
├── tutorial-02-green-pillar.png  # Hunter test - illusory bushes
├── tutorial-03-blue-pillar.png   # Arcane test - spinning crystal
├── tutorial-04-gold-pillar.png   # Divine test - shadow on flower

# Trial images (action-focused)
├── trial-01-dire-wolf.png        # Threatening wolf on bridge
├── trial-02-goblin-ambush.png    # Merchant under attack
├── trial-03-maze.png             # Maze of Echoes entrance
├── trial-04-pegasus-grove.png    # Three paths visible
```

### Monster Quick Stats

| Monster | AC | HP | Attack | Notes |
|---------|----|----|--------|-------|
| Dire Wolf | 14 | 22 | +5, 1d10+3 | Cursed leg. Heal = ally! |
| Goblin | 15 | 10 | +4, 1d6+2 | Nimble Escape |
| Goblin Boss | 17 | 21 | +4 x2 | Redirect Attack |
| Flying Sword | 17 | 14 | +4, 1d8+2 | Immune poison/psychic |
| Shadow | 12 | 27 | +4, 1d6+2 necrotic | **Vulnerable to radiant!** |
| Shadow Sorcerer | 12 | 22 | +4, 2d6 necrotic | Resistant to non-radiant. Can be redeemed! |

### Class Determination (End of Session)

Track which Aspect cards Hendrix uses most:

| Primary | Secondary | Class |
|---------|-----------|-------|
| Warrior | Divine | **Paladin** |
| Warrior | Hunter | **Fighter** |
| Warrior | Warrior | **Barbarian** |
| Hunter | Warrior | **Ranger** |
| Hunter | Arcane | **Rogue** |
| Arcane | Hunter | **Wizard** |
| Arcane | Arcane | **Sorcerer** |
| Divine | Warrior | **Paladin/War Cleric** |
| Divine | Hunter | **Druid** |
| Divine | Divine | **Life Cleric** |
| Balanced | (all close) | **Bard** |

### On-Demand Commands

**Generate new image:**
```bash
./venv/bin/python -c "
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
load_dotenv()
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
response = client.models.generate_content(
    model='gemini-3-pro-image-preview',
    contents='YOUR PROMPT HERE',
    config=types.GenerateContentConfig(
        response_modalities=['Image'],
        image_config=types.ImageConfig(aspect_ratio='2:3')
    )
)
for part in response.parts:
    if img := part.as_image():
        img.save('output/custom-image.png')
        print('Saved!')
"
```

**Quick dice roll:** Just ask Claude to roll and narrate!

### Transcript Processing

When Rob pastes session transcripts, Claude will:
1. Identify what Hendrix is trying to do
2. Suggest which Aspect cards apply
3. Provide DC targets and roll interpretations
4. **Provide READ-ALOUD text for both outcomes**
5. Track card usage for class determination
6. Flag if pacing needs adjustment

**Example transcript input:**
> "Hendrix says he wants to sneak past the wolf and look for another way across"

**Claude response format:**

**Action:** Sneak past dire wolf
**Card:** Hunter - Sneak (DC 14, wolf has Perception +5)
**Roll needed:** d20+4 (Sneak bonus)

📖 **IF SUCCESS - READ ALOUD:**
> "You press yourself against the bridge's cold stone railing, moving like
> a shadow. The wolf's ears twitch, but its burning eyes stay fixed on the
> far end of the bridge. Step by careful step, you slip past... and the
> beast never turns. You're across!"

📖 **IF FAIL - READ ALOUD:**
> "You're almost past when your boot catches a loose stone. It clatters
> across the bridge like a warning bell. The wolf's head snaps toward you,
> lips curling back from massive fangs. It knows you're here now."

🎲 **DM NOTE:** If he fails, the wolf doesn't attack immediately - it blocks
the path and growls. Give him a chance to try something else.
