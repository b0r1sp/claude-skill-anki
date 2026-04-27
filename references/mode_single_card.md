# Mode: Single Card

Use this mode when the user wants to create one card for a specific concept —
either from the current conversation or by providing content directly.

## Workflow

1. **Understand the concept** — ask the user what the concept is (or derive it from
   the current conversation context if it's clear).

2. **Select deck** — propose a deck name based on the topic, then present:
   ```
   [1] Create new deck       — enter a name
   [2] Add to existing deck  — Suggested: My Subject::Chapter 01
   [3] Select existing deck  — show list
   ```
   - **[1]** → prompt `Deck name: _`, user types a name
   - **[2]** → use the suggested name directly, proceed
   - **[3]** → query AnkiConnect for all deck names, show numbered list,
               user enters a number to select

3. **Draft the card** — follow the card creation rules in `references/card_guidelines.md`.
   For a single concept, create a Basic card (definition) plus one Cloze card (key fact).
   Keep answers atomic (< 5 words unless it's a context/logic card).

4. **Preview** — show the card(s) using the ASCII format from `references/shared_preview.md`.
   Strip all HTML. Wait for the user to confirm, edit, or reject.

5. **Write JSON** — write to `/tmp/anki_cards.json` (or a path the user specifies).

   Use the JSON format from `references/card_guidelines.md`.

6. **Pre-import check & import** — follow `references/shared_import.md`.

## Proactive suggestions

When the user explains a concept, asks about something worth remembering long-term,
or encounters a notable gotcha or mental model — even without invoking `/anki` —
propose a card at the end of your response:

```
💡 Anki card?
Front: <concise question>
Back:  <atomic answer>
Deck:  <suggested deck>
Tags:  <structured tags per card_guidelines.md rule 13>
```

Wait for the user to confirm ("ja" / "yes" / feedback) before writing the JSON.
Do **not** suggest a card if the topic is trivial, already well-known, or the user
is clearly not in a learning context.
