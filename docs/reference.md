# Technical Reference & Workflow

## Workflows

The skill has three modes. Steps 6–10 (deck selection, JSON export, pre-import
check, and import) are identical in all modes. The steps before that differ.

---

### Mode 1 — Import from Document(s)

```
1.  Read card guidelines
2.  Read source material(s) — one or more PDFs, PPTXs, or other files
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
```

---

### Mode 2 — Create from Conversation

```
1.  Identify the concept from the current conversation
2.  Draft cards — Basic (definition) + Cloze (key fact) at minimum
```

*No exam check. No clustering. Cards are created directly from context.*

---

### Mode 3 — Research & Create

```
1.  User names a topic
2.  Claude researches it (web search, authoritative sources)
3.  Build learning plan — concept clusters ordered foundational → advanced:

    Learning plan: <Topic>
    ─────────────────────────────────────────
    [1] <Foundational concept>    ~3 cards
    [2] <Core principle A>        ~5 cards
    [3] <Core principle B>        ~4 cards
    [4] <Application / use case>  ~3 cards
    ─────────────────────────────────────────
    Total: ~15 cards

    Proceed? [y] yes · [e] edit · [n] cancel

4.  Create cards from confirmed plan (nucleus principle, mnemonics, references)
```

*No exam check. Depth is determined by the research plan, not file content.*

---

### Shared steps (all modes)

```
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

---

## CLI Scripts

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

---

## JSON Format

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

---

## Custom Note Types

The import script creates two note types in Anki if they don't exist:

- **DL-Basic** — Fields: Front, Back, Ref
- **DL-Cloze** — Fields: Text, Ref

Both include clean styling with dark mode support.
