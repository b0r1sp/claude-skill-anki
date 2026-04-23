# Claude Skill: Anki Card Creator

A Claude Skill for creating high-quality Anki flashcards from study materials and importing them via the [AnkiConnect](https://foosoft.net/projects/anki-connect/) REST API.

## What it does

1. Reads study materials (PDF, PPTX, etc.)
2. Clusters content by core concepts
3. Creates cards following evidence-based spaced repetition principles
4. Exports cards as JSON
5. Imports into Anki via AnkiConnect

## Project structure

```
.
├── SKILL.md                        # Skill definition (triggers, workflow)
├── references/
│   └── card_guidelines.md          # Card creation rules & mnemonic system
└── scripts/
    ├── anki_connect.py             # Reusable AnkiConnect REST client
    └── import_cards.py             # CLI tool: JSON → Anki import
```

## Card creation principles

Cards follow a nucleus approach — each core concept gets at least three cards from different angles (definition, rule, application). Lists use colored-syllable mnemonics for recall. Every card is self-contained and references its source slide.

Full guidelines: [`references/card_guidelines.md`](references/card_guidelines.md)

## Prerequisites

- Python 3.10+
- [Anki](https://apps.ankiweb.net/) with [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on (code: `2055492159`)
- AnkiConnect listening on `127.0.0.1:8765` (default)

No external Python dependencies — uses only the standard library.

## Usage

### Import cards from JSON

```bash
python scripts/import_cards.py path/to/cards.json
```

### Dry run (validate without importing)

```bash
python scripts/import_cards.py path/to/cards.json --dry-run
```

### Test AnkiConnect connection

```bash
python scripts/anki_connect.py
```

## JSON format

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

## Custom note types

The import script creates two note types in Anki if they don't exist:

- **DL-Basic** — Fields: Front, Back, Ref
- **DL-Cloze** — Fields: Text, Ref

Both include clean styling with dark mode support.

## License

MIT
