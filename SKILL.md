---
name: anki
description: |
  Anki flashcard skill — create cards from documents or conversation and import
  via AnkiConnect. Proactively suggest a card whenever a concept worth remembering
  comes up, even without /anki.
  Triggers: anki, flashcards, Lernkarten, Karteikarten, spaced repetition,
  "Karten erstellen", "cards from PDF", exam prep.
license: MIT
---

# Anki Skill — Dispatcher

When this skill is invoked (via `/anki` or a matching trigger), ask the user
to choose a mode — unless it is already obvious from context (e.g. a file was
attached → Mode 2; a concept was just explained → Mode 1).

```
What would you like to do?
[1] Create a single card  — for a concept from our conversation
[2] Import from document  — batch cards from a PDF, PPTX, or other file
```

Then load and follow the instructions for the chosen mode:

| Choice | Instructions |
|--------|-------------|
| 1 — Single card | `references/mode_single_card.md` |
| 2 — Import from document | `references/mode_import_docs.md` |

Both modes share:
- **Card preview format & paging** → `references/shared_preview.md`
- **Pre-import check & import** → `references/shared_import.md`
- **Card creation rules** → `references/card_guidelines.md`

## Proactive suggestions (no invocation needed)

Even without `/anki`, follow the proactive suggestion rules in
`references/mode_single_card.md` whenever the user explains a concept or
encounters a gotcha worth remembering long-term.
