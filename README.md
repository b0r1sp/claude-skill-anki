# Claude Skill: Anki Card Creator

A (Claude) Skill for creating high-quality Anki flashcards from study materials or any provided concept and importing them via the [AnkiConnect](https://ankiweb.net/shared/info/2055492159) REST API.

> [!NOTE]
> This skill covers specific use cases I needed — use it as-is or as inspiration for your own learning skill.
> It is built on the [Agent Skills](https://agentskills.io/home) standard and can be used in any compatible environment, though the documentation here focuses on Claude Code.
> Read more about Agent Skills [here](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) and [here](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills). 

## Installation

### Prerequisites

- Python 3.10+
- [Anki](https://apps.ankiweb.net/) with [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on (code: `2055492159`)

No external Python dependencies — uses only the standard library.

### Claude Code

The recommended way to use this skill — either via the CLI or the Claude Code Desktop app. 

```bash
git clone https://github.com/b0r1sp/claude-skill-anki.git
mkdir -p ~/.claude/skills
```

Then either **copy** (simple, self-contained):
```bash
cp -r claude-skill-anki ~/.claude/skills/anki
```

Or **symlink** (stays in sync with `git pull`):
```bash
ln -s "$PWD/claude-skill-anki" ~/.claude/skills/anki
```

If `~/.claude/skills/` didn't exist before, restart Claude Code once so it picks up the new directory: type `exit` or press `Ctrl+D`, then run `claude` again. After that, the skill auto-loads in every session.

### Claude Chat / Cowork

1. Download `anki.zip` from the [latest release](../../releases/latest)
2. Open **Preferences → Skills → Upload Skill** and select `anki.zip`

The skill works the same way like in Claude Code and will help you create cards. When it's time to import, run the provided command in the Terminal — the skill prepares it for you as a ready-to-paste snippet.

---

## What it does

**Three modes:**
- **Import from document(s)** — reads one or more PDFs/PPTXs, clusters by concept, and creates a full card set
- **Create from conversation** — turns a concept from the current chat into cards instantly
- **Research & create** — researches a topic from scratch, builds a structured learning plan, and creates cards

**In all modes:**
1. Assessment criteria support *(Import mode)* — accepts exam/certification weightings (text, file, or screenshot) to scale card depth by topic importance
2. Evidence-based card creation — nucleus principle, mnemonics for lists, atomic answers
3. Pre-import check — shows deck stats, duplicates, and review history before touching anything
4. Import via AnkiConnect — interactive duplicate handling (replace, update, or skip)
5. CLI tools for querying and listing existing notes
6. Proactively suggests cards during conversation when a concept worth remembering comes up

## Card creation principles

Cards follow a nucleus approach — each core concept gets at least three cards from different angles (definition, rule, application). For ordered lists, a mnemonic is built from syllables of each item to form a fantasy word (e.g. *OppMobExeClo*), paired with a sentence where each word is a creative blend of the original term (e.g. *"Opportunities Mobst Exentually Close"*) — syllables color-coded for instant recall. Every card is self-contained and references its source slide.

Full guidelines: [`references/card_guidelines.md`](references/card_guidelines.md)

## Usage

1. **Make sure Anki is open** with the AnkiConnect add-on installed.
2. **Start Claude Code** by running `claude` in your Terminal.
3. **Invoke the skill** — type `/anki` and choose a mode:
   - `[1]` **Import from document(s)** — attach one or more PDFs, PPTXs, or other files
   - `[2]` **Create from conversation** — turn a concept from the current chat into cards
   - `[3]` **Research & create** — give Claude a topic; it researches it, builds a learning plan, and creates cards
4. **Exam or certification?** *(Mode 1 only)* — Claude asks whether the deck is for an exam. If yes, provide the assessment criteria (paste text, attach a file, or share a screenshot). Claude OCRs screenshots, parses the weightings, and uses them throughout: high-weight topics get deeper clustering and more cards, low-weight topics get minimal coverage.
5. **Review the proposed cards** — Claude shows each card in an ASCII preview. Confirm, adjust, or reject before anything is written.
6. **Select a deck** — Claude suggests a deck name based on the content:
   - `[1]` Create a new deck — enter a name
   - `[2]` Add to the suggested existing deck
   - `[3]` Select from a list of all decks in Anki
7. **Pre-import check** — Claude shows a summary before touching anything:
   ```
   Pre-import check
   Deck: My Subject::Chapter 01  (247 cards)
   ─────────────────────────────────────────
   Deck total:                  247
   To import:                    10
     ├─ New cards:                7
     └─ Duplicates:               3
          ├─ Learned:             2
          └─ Never reviewed:      1
   ```
   Duplicate details (reviews, interval, ease, lapses) are shown for each match.
8. **Confirm** — Claude asks two separate questions: proceed with import, and (if learned duplicates exist) whether to reset their learning stats.
9. **Claude imports** — writes `/tmp/anki_cards.json` and runs the import script. Results appear directly in the conversation.

---

## Technical Reference

### Pre-import analysis

```bash
python scripts/import_cards.py path/to/cards.json --check
```

### Import cards from JSON

```bash
python scripts/import_cards.py path/to/cards.json
```

### Dry run (validate without importing)

```bash
python scripts/import_cards.py path/to/cards.json --dry-run
```

### Duplicate handling

When a duplicate is found, the import script prompts interactively:

- **[R]eplace** — delete the old card and create the new one (metadata lost)
- **[U]pdate** — update fields of the existing card, review history preserved by default; optionally reset when prompted
- **[S]kip** — leave the existing card unchanged

Non-interactive modes:

```bash
python scripts/import_cards.py cards.json --on-duplicate replace
python scripts/import_cards.py cards.json --on-duplicate update --keep-metadata
python scripts/import_cards.py cards.json --on-duplicate update --reset-metadata
python scripts/import_cards.py cards.json --on-duplicate skip
```

### Query and list notes

```bash
# Search by deck
python scripts/list_cards.py --deck "My Deck"

# Search by tag, added in last 7 days
python scripts/list_cards.py --tag python --added 7

# Raw Anki query
python scripts/list_cards.py --query "tag:python is:due"

# Show all results (no limit)
python scripts/list_cards.py --deck "My Deck" --limit 0
```

### Test AnkiConnect connection

```bash
python scripts/anki_connect.py
```

### JSON format

```json
{
    "deck": "My Deck::Sub Deck",
    "cards": [
        {
            "type": "basic",
            "front": "What is X?",
            "back": "Definition of X",
            "tags": ["topic", "concept"],
            "ref": "Source > Chapter > Slide 5"
        },
        {
            "type": "cloze",
            "text": "X is defined as {{c1::the answer}}.",
            "tags": ["topic", "concept"],
            "ref": "Source > Chapter > Slide 6"
        }
    ]
}
```

### Custom note types

The import script creates two note types in Anki if they don't exist:

- **DL-Basic** — Fields: Front, Back, Ref
- **DL-Cloze** — Fields: Text, Ref

Both include clean styling with dark mode support.

---

## Workflow

```
1.  Read card guidelines
2.  Read source material(s)
3.  Exam / certification check
    Is this deck for an exam or certification? [y] yes · [n] no
    → yes: provide assessment criteria (text, file, or screenshot)
           Claude OCRs screenshots and parses topic weights

4.  Cluster by concept, weighted by assessment criteria
    High-weight (≥20%): deep clustering, ≥5 cards per concept
    Medium-weight (10–19%): standard nucleus, 3–4 cards
    Low-weight (<10%): minimal, 1–2 cards
    Not listed: skip unless foundational

5.  Create cards (nucleus principle, mnemonics, references)
    Number of cards per concept scales to its weight

6.  Preview cards — ASCII format
    ── Start import? [y] yes · [n] no ──

7.  Select deck
    [1] Create new deck       — enter a name
    [2] Add to existing deck  — Suggested: My Subject::Chapter 01
    [3] Select existing deck  — show list

8.  Write JSON to /tmp/anki_cards.json

9.  Pre-import check
    ──────────────────────────────────────────────
    Pre-import check
    Deck: My Subject::Chapter 01  (247 cards)
    ──────────────────────────────────────────────
    Deck total:                  247
    To import:                    10
      ├─ New cards:                7
      └─ Duplicates:               3
           ├─ Learned:             2
           └─ Never reviewed:      1
    ──────────────────────────────────────────────
    Duplicate details:
      [2] What is Atomicity?
          reviews=5  interval=10d  ease=2.5  lapses=1
      [8] What is Durability?
          (never reviewed)
    ──────────────────────────────────────────────

10. Proceed with import? [y] yes · [n] no
11. Reset learning stats for duplicates? [y] yes · [n] no
    (only shown if learned duplicates exist)
12. Import
```

## License

MIT
