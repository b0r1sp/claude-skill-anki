---
name: anki
description: |
  Create Anki flashcards from study materials and import them via AnkiConnect.
  Use this skill whenever the user wants to create Anki cards, flashcards, or
  Lernkarten from PDFs, presentations, or other study materials. Also use when
  the user mentions Anki, spaced repetition, or exam preparation with flashcards.
  Also proactively suggest a card at the end of any response where the user
  explains a concept, asks about something worth long-term remembering, or
  encounters a notable gotcha or mental model — even without invoking /anki.
  Triggers: anki, flashcards, Lernkarten, Karteikarten, spaced repetition,
  "Karten erstellen", "cards from PDF", exam prep cards.
license: MIT
---

# Anki Card Creation Skill

## Overview

This skill creates high-quality Anki flashcards from study materials and imports
them into Anki via the AnkiConnect REST API. It follows evidence-based principles
for effective spaced repetition learning.

## Workflow

### Batch import (from documents)

1. **Read the card guidelines** in `references/card_guidelines.md` before creating any cards.
2. **Read the source material** (PDF, PPTX, or other documents).
3. **Identify core concepts** — cluster content by concept, not by slide or paragraph.
4. **Create cards** following the guidelines (nucleus principle, minimum information, mnemonics).
5. **Present cards to the user** for review and approval using the ASCII card format below.
   If more than 5 cards were created, show them in pages of 5. After each page display:
   ```
   ── Page 1/3 ── [n] for next ──
   ```
   Wait for the user to send any reply (e.g. a single space or enter) before showing the next page.
   After the last page, show the approve/edit/skip prompt.
6. **Write cards to JSON** to `/tmp/anki_cards.json` by default (unless the user specifies a different path).
7. **Import automatically if running in Claude Code** — run the import script via Bash immediately after writing the JSON and show the result. No Terminal step needed for the user.
   ```bash
   python /path/to/scripts/import_cards.py /tmp/anki_cards.json
   ```
   If running in Claude Desktop or another environment without Bash access, guide the user to run the import script from their Terminal instead.

### Proactive suggestions (during conversation)

When the user explains a concept, asks about something worth remembering long-term,
or encounters a notable gotcha or mental model — even without invoking `/anki` —
propose a card at the end of your response:

```
💡 Anki card?
Front: <concise question>
Back:  <atomic answer>
Deck:  <suggested deck>
Tags:  <structured tags per guideline rule 13>
```

Wait for the user to confirm ("ja" / "yes" / feedback) before writing the JSON.
Do not suggest a card if the topic is trivial, already well-known, or the user is
clearly not in a learning context.

## Card Preview Format

Render each card in ASCII style before asking for approval:

```
┌─ Card 01 · Basic ──────────────────────────────────────┐
│ FRONT                                               │
│ What is Atomicity in ACID?                          │
├─────────────────────────────────────────────────────┤
│ BACK                                                │
│ A transaction is all-or-nothing — completes fully   │
│ or not at all.                                      │
├─────────────────────────────────────────────────────┤
│ Tags: subject:DB::chapter01 · type:Basic            │
│ Ref:  lecture.pdf > Chapter 1 > Slide 5             │
└─────────────────────────────────────────────────────┘
```

- Strip all HTML tags and color spans — show plain text only
- Show max **5 cards per page**
- After each page (except the last): `── Page 1/3 ── [n] for next ──`
- After the last page: `── Start import? [y] yes · [n] no ──`

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

### Duplicate handling
When a duplicate is detected the user is prompted interactively:
- **[R]eplace** — delete old card, create new one (metadata lost)
- **[U]pdate** — update fields of existing card, metadata preserved by default;
  optionally reset review history when prompted
- **[S]kip** — leave existing card unchanged

Non-interactive modes (no prompt):
```bash
# Auto-replace all duplicates
python import_cards.py cards.json --on-duplicate replace

# Auto-update, keep review history
python import_cards.py cards.json --on-duplicate update --keep-metadata

# Auto-update, reset review history
python import_cards.py cards.json --on-duplicate update --reset-metadata

# Auto-skip all duplicates
python import_cards.py cards.json --on-duplicate skip
```

## Note Types

The import script creates two custom note types if they don't exist:

- **DL-Basic** — Fields: Front, Back, Ref. Clean card template with reference line.
- **DL-Cloze** — Fields: Text, Ref. Cloze deletion template with reference line.
