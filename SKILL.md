---
name: anki
description: |
  Create Anki flashcards from study materials and import them via AnkiConnect.
  Use this skill whenever the user wants to create Anki cards, flashcards, or
  Lernkarten from PDFs, presentations, or other study materials. Also use when
  the user mentions Anki, spaced repetition, or exam preparation with flashcards.
  Triggers: anki, flashcards, Lernkarten, Karteikarten, spaced repetition,
  "Karten erstellen", "cards from PDF", exam prep cards.
license: MIT — see [LICENSE](LICENSE).
---

# Anki Card Creation Skill

## Overview

This skill creates high-quality Anki flashcards from study materials and imports
them into Anki via the AnkiConnect REST API. It follows evidence-based principles
for effective spaced repetition learning.

## Workflow

1. **Read the card guidelines** in `references/card_guidelines.md` before creating any cards.
2. **Read the source material** (PDF, PPTX, or other documents).
3. **Identify core concepts** — cluster content by concept, not by slide or paragraph.
4. **Create cards** following the guidelines (nucleus principle, minimum information, mnemonics).
5. **Present cards to the user** for review and approval.
6. **Write cards to JSON** in the import format (see below).
7. **Guide the user** to run the import script from their Terminal.

## Card Creation Rules

Read `references/card_guidelines.md` for the complete set of rules. Key principles:

- **Cluster by concept** — not one card per slide.
- **Nucleus principle** — each concept gets ≥3 cards (definition, rule, application).
- **Minimum information** — one atomic fact per card, answers <5 words.
- **Learn before memorizing** — context card before detail cards.
- **Mnemonics for lists** — colored syllable mnemonics in the Back field.
- **Self-contained** — no pronouns, full names, understandable without context.
- **References** — every card gets a source reference: `Filename > Chapter > Slide N`.

## JSON Format

Write cards to a JSON file that `scripts/import_cards.py` can import:

```json
{
    "deck": "DL Certification::01 Roles and Responsibilities",
    "cards": [
        {
            "type": "basic",
            "front": "What is Delivery at Accenture?",
            "back": "Fulfilment of commercial and emotional commitments",
            "tags": ["01_Roles", "concept_delivery"],
            "ref": "01_Roles and Responsibilities > 01 What is Delivery > Slide 5"
        },
        {
            "type": "cloze",
            "text": "Every Accenture contract is assigned exactly {{c1::one}} RDE.",
            "tags": ["01_Roles", "concept_rde"],
            "ref": "01_Roles and Responsibilities > 01 What is Delivery > Slide 10"
        }
    ]
}
```

### Card types

- `basic` — requires `front` and `back` fields. Use for definitions, Q&A, lists.
- `cloze` — requires `text` field with `{{c1::...}}` cloze deletions.

### Tags

Use tags to categorize cards by source file and concept cluster.

### HTML in fields

Anki renders HTML in fields. Use for:
- Line breaks: `<br>`
- Mnemonic formatting: `<span style="color:#e24b4a">Silbe</span>`
- Bold: `<b>...</b>`

## Import via AnkiConnect

The user must run the import script from their own Terminal because AnkiConnect
runs on localhost and is not reachable from the Claude sandbox.

### Prerequisites
- Anki must be running
- AnkiConnect add-on installed (code: 2055492159)
- AnkiConnect listening on 127.0.0.1:8765

### Import command
```bash
python /path/to/scripts/import_cards.py /path/to/cards.json
```

### Dry run (validate without importing)
```bash
python /path/to/scripts/import_cards.py /path/to/cards.json --dry-run
```

## Note Types

The import script creates two custom note types if they don't exist:

- **DL-Basic** — Fields: Front, Back, Ref. Clean card template with reference line.
- **DL-Cloze** — Fields: Text, Ref. Cloze deletion template with reference line.
