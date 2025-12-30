# How to Use Claude Code for Creative Projects
## A Tutorial for Colleagues (Based on Rob's D&D Graphic Novel Project)

---

## What is Claude Code?

Claude Code is a command-line AI assistant that can read your files, write code, run commands, search the web, and help you build things. Think of it like having a very capable collaborator who lives in your terminal.

Key differences from ChatGPT or Claude.ai web:
- **It can see and edit your actual files** (not just text you paste)
- **It can run shell commands** (git, python, npm, etc.)
- **It remembers context** across a session
- **It has specialized agents** for different tasks (image generation, code exploration, etc.)

---

## Rob's Project: D&D Graphic Novel Generator

This project started as an AI-generated comic book system and evolved into a live D&D session tool. It uses:
- Python scripts for image generation
- JSON databases for characters, locations, monsters
- Markdown files for adventure scripts
- AI image generators (OpenAI's gpt-image-1, Google Gemini)

The magic is that Claude Code helps with ALL of it - writing code, generating images, running D&D sessions live, creating documentation.

---

## Example Prompts from Rob's Sessions

### Pattern 1: "Set Context, Then Do"

Rob often starts by telling Claude to read relevant files, then asks for something specific:

```
"Read through the transcripts and the session plan and the summary
and the character sheets and start brainstorming a D&D session for
Lightsword and Spore, the 3rd level characters."
```

**Why this works:** Claude Code can read multiple files at once. By naming what to read, Rob ensures Claude has all the context it needs before doing creative work.

---

### Pattern 2: "Kick the Tires"

Testing new functionality with a small scope:

```
"Let's kick the tires on the image generator. Read the /adventure
we'll be running and then create a full page intro for each major
scene that I can show to the Player as a visual aide. Make about a
dozen but let's start with one."
```

**Why this works:** "Start with one" lets you verify the approach before committing to a big batch. If something's wrong, you catch it early.

---

### Pattern 3: "Copy and Adapt"

Rob bootstrapped this project from another one:

```
"Please copy ~/Projects/everpeak-comic here in its entirety minus
the git or any images or JSON - I want to turn that single purpose
everpeak citadel campaign comic book into a single character graphic
novel backstory kind of system."
```

**Why this works:** Instead of starting from scratch, Rob asks Claude to copy an existing working project and then adapt it. This saves a ton of time.

---

### Pattern 4: "Make Me an Image of..."

During live D&D sessions, Rob generates images on-the-fly:

```
"make an image of this past scene please"

"Create images of the four pillars with the new view of the Player
and the underground theme."
```

**Why this works:** Claude Code has a specialized agent (`dnd-image-generator`) that knows how to use the project's image generation pipeline. Rob just describes what he wants in natural language.

---

### Pattern 5: "Update the Journal"

Keeping persistent memory across sessions:

```
"update the journal please"

"update the journal as well. with much more details from the session."
```

**Why this works:** Claude Code uses a `campaign-journal-keeper` agent that reads the current journal, understands the session context, and adds new entries. This means Rob doesn't lose progress between sessions.

---

### Pattern 6: "Next Readaloud Please"

During live DM sessions, Rob asks for the next script section:

```
"OK next readaloud please"

"Yes please next read aloud"

"readaloud next please"
```

**Why this works:** Claude Code understands it's acting as a Co-DM and provides formatted "read aloud" text that Rob speaks to the Player.

---

### Pattern 7: "Perplexity First, Then Claude Code"

Rob uses a two-tool research workflow:

**Step 1 - Perplexity.ai for scouring:**
```
"Please research a variety of best practices and questionnaires and
origin story adventures for creating a backstory for a 5e D&D character.
Be comprehensive."
```

**Step 2 - Paste the entire answer into Claude Code:**
```
"Draw inspiration from these to create a fun origin story interview.
the Player is a young player."

[Paste Perplexity's ~1000 word answer with citations]
```

**Why this works:**
- **Perplexity** is excellent at scouring the internet, finding diverse sources, and providing citation URLs
- **Claude Code** is excellent at synthesizing that research, adapting it to your specific needs, and executing on it
- Claude Code *can* fetch and read from URLs, but it's less good at the initial "search and discover" phase
- This combo gets you the best of both: broad research + deep execution

Rob used this pattern to find D&D backstory best practices, origin story adventure templates, and questionnaire formats - then had Claude Code synthesize all of it into a kid-friendly adventure for a young player.

---

### Pattern 8: Incorporate Player Feedback in Real-Time

Rob pastes what the Player says into the chat:

```
"Before you turn into a lizard, you're actually kind of a globe
kind of thing. And then you're like... Oh, you're like indeterminate
looking. Yeah, like you don't have a species and after the thing
you turn into a species. Got it. So if you're indeterminate, are
you like a little bit blurry or... Like, you're like, you're
actually like, you're basically like a glowy figure but you don't
actually look like anything and you have like a robe around you..."
```

**Why this works:** Claude Code processes the transcript, understands the player's creative input (the Player wants his character to be "indeterminate" before the trials), and adapts the story and images accordingly.

---

## The Live D&D Session Workflow

Here's how Rob runs a live session with his player the Player:

### Setup
1. Rob opens Claude Code in terminal
2. Tells Claude to read the adventure files
3. Has printed aspect cards and dice ready
4. Has laptop open to show images to the Player

### During Play
1. **Claude provides read-aloud text** - Rob speaks it to the Player
2. **the Player responds** - Rob types or pastes what the Player says
3. **Claude suggests dice rolls** - "Roll d20+4 to see if your illusions work"
4. **Rob reports the roll** - "17 total"
5. **Claude narrates the outcome** - Provides success/failure description
6. **Image generation** - "make an image of the dire wolf on the bridge"
7. **Journal updates** - "update the journal" to save progress

### Example Flow:

```
[Rob types]
"The goblins haven't noticed you yet. You're about 60 feet away,
hidden in the shadows with Darkstorm. Um, for this one can I use
multiple? Like three? Three if you can give a really good
explanation. Um, use protection... Which I'm going to use around
the person. The merchant..."

[Claude responds with]
- Mechanics: What rolls are needed
- Read-aloud text for success/failure
- Dice instructions (d20+4, d6 for damage, etc.)
```

---

## The CLAUDE.md File

Every project has a `.claude/CLAUDE.md` file that gives Claude context about the project. Here's what Rob's includes:

```markdown
## Live Session DM Mode

**Claude is CO-DUNGEON MASTER** alongside Rob (the human DM).
Rob runs the laptop, rolls dice, and speaks to the Player.
Claude provides real-time support via transcript processing.

### Co-DM Responsibilities

**ALWAYS provide READ-ALOUD TEXT** for Rob to speak to the Player:

📖 READ ALOUD:
"The massive wolf blocks your path, hackles raised, teeth bared..."

When responding to transcripts, Claude should provide:
1. **Read-aloud text** - Boxed narration Rob can speak verbatim
2. **Mechanics** - DC, rolls needed, card suggestions
3. **Outcome options** - Success/failure narration ready to go
4. **DM notes** - Whispered tips for Rob (not read aloud)
```

**Why this matters:** The CLAUDE.md file is like giving Claude its job description. It tells Claude how to behave for THIS specific project.

---

## Specialized Agents

Claude Code can spawn specialized agents for different tasks:

| Agent | What It Does |
|-------|-------------|
| `dnd-image-generator` | Creates images using Gemini, pulls from character/location JSON |
| `campaign-journal-keeper` | Updates the persistent campaign journal |
| `Explore` | Searches the codebase to answer questions |
| `Plan` | Designs implementation strategies |

Rob triggers these naturally:
- "make an image of..." → dnd-image-generator
- "update the journal" → campaign-journal-keeper
- "where are errors handled?" → Explore agent

---

## Code Writing Examples

When Rob needed to adapt the comic book system for D&D sessions, Claude Code:

1. **Copied the existing project structure**
2. **Created new Python scripts** for image generation with Gemini
3. **Built JSON databases** for characters, locations, monsters
4. **Wrote markdown adventure scripts** with read-aloud text
5. **Created character sheets** with D&D 5e mechanics

Claude Code handles the technical work while Rob focuses on creative direction.

---

## Tips for Using Claude Code

### 1. Give Context First
Tell Claude what files to read before asking it to do something creative or complex.

### 2. Start Small
"Make about a dozen but let's start with one" - verify your approach before scaling up.

### 3. Use Natural Language
You don't need special commands. Just describe what you want like you're talking to a collaborator.

### 4. Create a CLAUDE.md
Put project-specific instructions in `.claude/CLAUDE.md` so Claude always knows how to behave.

### 5. Use the Journal Pattern
For ongoing projects, keep a journal/log file that Claude can read and update. This gives continuity across sessions.

### 6. Paste Real Conversations
If you're working with someone else (like Rob with the Player), paste their actual words into Claude. It can parse natural conversation and extract what matters.

### 7. Ask for Parallel Work
Claude can run multiple tasks at once: "generate these 4 images in parallel"

---

## Project Structure

Here's how Rob's project is organized:

```
dnd-graphic-novel/
├── .claude/
│   └── CLAUDE.md           # Project instructions for Claude
├── adventure/
│   ├── session-2-dragon-egg.md      # Adventure script
│   ├── campaign-journal.md          # Persistent memory
│   └── dragon-egg-dm-reference.md   # Quick stat blocks
├── characters.json          # Character database
├── locations.json           # Location database
├── monsters.json            # Monster database
├── scripts/
│   └── core/
│       └── generate_nanobananapro.py  # Image generation
└── output/
    └── campaign-images/     # Generated scene images
```

---

## Summary

Claude Code is powerful because:
1. **It can see your actual project** - not just snippets you paste
2. **It can run commands** - generate images, run scripts, git operations
3. **It has memory** - through journals and session context
4. **It adapts to your project** - via CLAUDE.md instructions
5. **It understands natural language** - no special syntax needed

Rob uses it as a creative collaborator for D&D - writing adventures, generating art, running live sessions, and keeping track of story progress. The same patterns work for any creative or technical project.

---

## DEEP DIVE: Genesis of the Adventures

This section walks through exactly how Rob created two complete D&D adventures using Claude Code, showing the actual prompts and workflow in detail.

---

### Session 1: "The Trials of the Choosing" - From Zero to Playable

**Goal:** Create a solo adventure for the Player (young) that discovers his character's class through gameplay instead of choosing upfront.

#### Phase 1: Project Bootstrap (5 minutes)

Rob had previously built a comic book generator for a different D&D campaign. Instead of starting from scratch:

```
"please copy ~/Projects/everpeak-comic here in its entirety minus the git
or any images or JSON - I want to turn that single purpose everpeak citadel
campaign comic book into a single character graphic novel backstory kind
of system. So I want all the comic creation functionality and then I'll
use it for my other player the Player's D&D character with a full backstory
and novellette."
```

**What Claude Code did:**
- Copied the entire project structure (Python scripts, templates, configs)
- Excluded git history, images, and JSON data (keeping structure but not content)
- Preserved the working image generation and comic assembly code

```
"Please git commit an initial repo and use gh to create a
github.com/robgruhl/dnd-graphic-novel repo and push to that."
```

**What Claude Code did:**
- Initialized new git repo
- Created GitHub repository via `gh` CLI
- Pushed initial commit with the adapted codebase

#### Phase 2: Research + Constraints (10 minutes)

Rob started with a Perplexity.ai search to gather best practices:

**Perplexity query:**
```
"Please research a variety of best practices and questionnaires and
origin story adventures for creating a backstory for a 5e D&D character.
Be comprehensive."
```

Perplexity returned ~1000 words of synthesized advice from multiple D&D blogs, Reddit threads, and RPG resources - including citation URLs.

**Then Rob pasted the entire Perplexity answer into Claude Code:**
```
"Draw inspiration from these to create a fun origin story interview.
the Player is a young player."

[Perplexity's full response with advice about hooks, NPCs, class origins,
motivations, structured questionnaires, "botched job" adventure patterns, etc.]
```

**What Claude Code did:**
- Read the research document
- Synthesized the adult-oriented advice into kid-friendly questions
- Created `hendrix-character-interview.md` with age-appropriate prompts

**Why two tools?** Perplexity is great at scouring the internet and finding diverse sources. Claude Code is great at taking that raw research and turning it into something tailored and actionable. Together: broad discovery + deep execution.

#### Phase 3: Adventure Design (15 minutes)

Rob described what he wanted:

```
"Okay, I want to construct a brief one shot origin story adventure...
appropriate for a 10 year old... opportunities for him to use melee,
to use range weapons, to use spells, to use prayers... we're going to
be kind of sussing out his character behaviorally, and at the end of
the adventure, we will have his feats and skills and character class
selected... no more than a two hour game session with a solo DM and
a solo player."
```

**What Claude Code did:**
- Entered "Plan Mode" to design the adventure
- Created a detailed plan file with:
  - 24 "Aspect Cards" (6 Warrior, 6 Hunter, 6 Arcane, 6 Divine)
  - 4-act structure (Setup → Trials → Climax → Choosing)
  - Class determination rubric (track which cards used most)
  - Timer breakdown for 90-minute session

Claude then asked clarifying questions:

```
[Claude asks about mechanics, tone, player choice]

[Rob answers]: "Cards + dice mechanics, between heroic and balanced tone,
no strong preferences, the Player creates beloved NPC, PDF cards to cut out"
```

#### Phase 4: Asset Creation (30 minutes)

After plan approval, Claude Code created:

1. **Session Script** (`adventure/session-script.md`)
   - ~400 lines of read-aloud text, DM notes, mechanics
   - Four tutorial pillars, four trial encounters
   - Success/failure narration for each choice

2. **Printable Aspect Cards** (`output/aspect-cards-printable.pdf`)
   - 24 cards with art, organized by aspect color
   - Print-and-cut format

3. **DM Quick Reference**
   - Monster stats, DC tables, class determination rubric

4. **Scene Images** (12+ images via image generator)
   - Trial scenes, temple, valley, boss encounter

#### Phase 5: Live Session - Co-DM Mode

During the actual game, Rob ran Claude Code on his laptop while playing:

```
"Let's begin! Read up on the adventure and let's get started!"
```

Rob would paste transcripts of what the Player said:

```
"The morning sun streams through your window... Okay, this is where
you help tell the story. What does your room look like?

[the Player]: It's in a cave. Like deep underground? Mm-hmm. In my room
there's a river running through it with fish..."
```

Claude adapted on the fly:

```
"Update the image location definitions to reflect this underground theme."
```

When the Player had a creative idea mid-session:

```
"Before you turn into a lizard, you're actually kind of a globe kind
of thing... you're basically like a glowy figure but you don't actually
look like anything and you have like a robe around you..."
```

Claude incorporated it:
- Updated all descriptions to show "indeterminate glowing figure"
- Changed the narrative to reveal species AFTER the trials
- Generated new images with the updated character concept

#### Result: Complete Adventure in One Session

**Files created:**
- `adventure/session-script.md` - Full session script
- `adventure/campaign-journal.md` - Persistent memory
- `output/aspect-cards-printable.pdf` - Physical cards
- 12+ scene images
- Character sheets for the resulting character (Lightsword, Lizardfolk Sorcerer)

**What the Player actually experienced:**
- Discovered he prefers Arcane (15 cards) + Divine (12 cards) = Sorcerer
- Named his character "Lightsword"
- Acquired three animal companions through compassionate choices
- Defeated the Shadow Sorcerer in a climactic battle

---

### Session 2: "The Dragon's Egg" - Building on What Came Before

**Goal:** Create a follow-up adventure for the now-established characters, with full D&D 5e mechanics.

#### Phase 1: Context Gathering

Rob starts by having Claude read everything:

```
"Read through the transcripts and the session plan and the summary
and the character sheets and start brainstorming a D&D session for
Lightsword and Spore, the 3rd level characters."
```

**What Claude Code did:**
- Read the campaign journal (what happened in Session 1)
- Read both character sheets (Lightsword the Sorcerer, Spore the Rogue)
- Read the Session 1 script and transcript
- Understood the established world (underground caves, companions, tone)

#### Phase 2: Brainstorming + Planning

Claude entered Plan Mode and designed the adventure:

**Key design decisions:**
- **Pip (pseudodragon) gets the spotlight** - the Player loved this companion
- **Connects to Lightsword's draconic heritage** - Gold dragon ancestor meets copper dragon
- **Spore's stealth abilities shine** - Rogue needs moments to be useful
- **Moral complexity** - Not all cultists are evil (some are tricked)
- **Two-character management** - Full 5e but streamlined for solo player

The plan file included:
- 5-act structure with read-aloud text
- Full monster stat blocks
- Two complete character sheets with spell lists
- Adaptive difficulty rules

#### Phase 3: Creating the DM Guide

Rob realized the Player's dad (also named Rob, but not "the DM") might want to run this adventure:

```
"the Player's dad Rob is new to D&D. Please create a standalone markdown
version of this whole new campaign for Rob with DM notes and tips for
running the Player, playing both PCs, or maybe with a friend playing Spore?
Include readaloud text, DC rolls, monster stat blocks, whatever would
help make this work."
```

**What Claude Code did:**
- Created a comprehensive 1,500-line DM guide
- Included complete character sheets with spell descriptions
- Wrote "New DM Quick Start" sections
- Added combat cheat sheets and troubleshooting guides
- Organized everything so a complete beginner could run it

#### Phase 4: Image Generation

```
"Generate 4 scene images using dnd-image-generator"
```

Claude spawned 4 parallel image generation agents:
1. Emberheart the copper dragon
2. The cult shrine with the corrupted egg
3. Pip leading the heroes through crystal tunnels
4. The egg rescue scene

Each image:
- Used the established visual style
- Referenced `characters.json`, `locations.json`, `monsters.json`
- Generated in 16:10 aspect ratio (fills laptop screen)
- Auto-opened in Chrome for display to the Player

---

### What Makes This Workflow Powerful

#### 1. Continuity Through Files

The `campaign-journal.md` file tracks everything:
- Where the story left off
- Card usage tallies (for class determination)
- Companion acquisition
- Player decisions and memorable quotes

When a new session starts or context is lost, Claude reads this file first.

#### 2. Layered Asset Creation

Each session builds on previous work:
- Session 1 created: aspect cards, character interview, session script
- Session 1 output: character sheet, campaign journal, scene images
- Session 2 used Session 1 output as input
- Session 2 created: new adventure, stat blocks, DM guide

#### 3. Real-Time Adaptation

The system handles live improvisation:
- the Player's "indeterminate glowing figure" idea → immediate image regeneration
- Underground cave theme → location database updates
- Unexpected player choices → narrative adaptation

#### 4. Multiple Delivery Formats

The same content becomes:
- PDF cards (for physical play)
- Markdown scripts (for DM reference)
- Scene images (for player visualization)
- JSON databases (for consistency)
- Campaign journals (for continuity)

---

### Timeline Summary

| Day | Phase | Key Prompts | Output |
|-----|-------|-------------|--------|
| Dec 28 AM | Project setup | "copy everpeak-comic...", "create github repo" | Project structure |
| Dec 28 PM | Adventure design | "create origin story adventure for 10 year old" | Plan file, session script |
| Dec 28 PM | Asset creation | "generate scene images", "create printable cards" | PDFs, images |
| Dec 29 AM | Live session | "Let's begin!", [paste the Player's words] | Completed adventure, character created |
| Dec 29 PM | Session 2 design | "brainstorm session for Lightsword and Spore" | Dragon's Egg adventure |
| Dec 29 PM | DM guide | "create standalone guide for Rob who's new to D&D" | 1,500-line DM guide |

**Total time:** ~6 hours of active work across 2 days
**Output:** Two complete adventures, character sheets, 20+ images, printable cards, DM guides

---

*Tutorial generated from Rob's actual session data in `~/.claude/projects/`*
