# Claude Skill: Anki Card Creator

A Claude Skill for creating high-quality Anki flashcards from study materials and importing them via the [AnkiConnect](https://ankiweb.net/shared/info/2055492159) REST API.

## Installation

### Prerequisites

- Python 3.10+
- [Anki](https://apps.ankiweb.net/) with [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on (code: `2055492159`)
- AnkiConnect listening on `127.0.0.1:8765` (default)

No external Python dependencies — uses only the standard library.

### Claude Desktop

1. Download `anki.zip` from the [latest release](../../releases/latest)
2. Open Claude Desktop → **Preferences → Skills → Upload Skill**
3. Select `anki.zip` — done

### Claude Code (CLI)

```bash
git clone https://github.com/b0r1sp/claude-skill-anki.git
mkdir -p ~/.claude/skills
```

Then either **copy** (simple, self-contained):
```bash
cp -r claude-skill-anki ~/.claude/skills/anki
```

Or **symlink**:
```bash
ln -s "$PWD/claude-skill-anki" ~/.claude/skills/anki
```

If `~/.claude/skills/` didn't exist before, restart Claude Code once so it picks up the new directory: type `exit` or press `Ctrl+D`, then run `claude` again. After that, the skill auto-loads in every session.

---

## What it does

1. Reads study materials (PDF, PPTX, etc.)
2. Clusters content by core concepts
3. Creates cards following evidence-based spaced repetition principles
4. Exports cards as JSON
5. Imports into Anki via AnkiConnect — with interactive duplicate handling (replace, update, or skip)
6. Queries and lists existing notes via CLI
7. Proactively suggests cards during conversation when a concept worth remembering comes up


## Card creation principles

Cards follow a nucleus approach — each core concept gets at least three cards from different angles (definition, rule, application). Lists use colored-syllable mnemonics for recall. Every card is self-contained and references its source slide.

Full guidelines: [`references/card_guidelines.md`](references/card_guidelines.md)

## Usage

### Claude Desktop

1. **Make sure Anki is open** on your computer with the AnkiConnect add-on installed.
2. **Open Claude Desktop** — the Anki skill is available automatically.
3. **Share your study material** — attach a PDF or presentation and say something like *"Create Anki cards from this."* Or just start a conversation: if you explain a concept, Claude will suggest a card on its own.
4. **Review the proposed cards** — Claude shows you each card before doing anything. Approve, edit, or skip as you like.
5. **Save the card file** — Claude writes the cards to `/tmp/anki_cards.json` (or a path you specify).
6. **Import into Anki** — open your Terminal and run:
   ```bash
   python scripts/import_cards.py /tmp/anki_cards.json
   ```
   If a card already exists in your deck, you'll be asked whether to replace it, update it, or skip it.

### Claude Code (CLI)

1. **Make sure Anki is open** on your computer with the AnkiConnect add-on installed.
2. **Start Claude Code** by running `claude` in your Terminal.
3. **Invoke the skill** — type `/anki` and attach your study file, or just start explaining a topic. Claude will suggest cards as you learn.
4. **Review the proposed cards** — confirm, adjust, or reject each card before anything is written.
5. **Claude writes the cards** to `/tmp/anki_cards.json` (or a path you specify).
6. **Import into Anki** — run the import script in your Terminal:
   ```bash
   python ~/.claude/skills/anki/scripts/import_cards.py /tmp/anki_cards.json
   ```

---

## Technical Reference

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

## License

MIT
