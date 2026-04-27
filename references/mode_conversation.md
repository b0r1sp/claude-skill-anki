# Mode: Create Cards from Conversation

Use this mode when the user wants to create cards for a concept that came up
in the current conversation.

## Workflow

1. **Identify the concept** — derive it from the conversation context, or ask
   the user to clarify if it's not obvious.

2. **Draft cards** — follow the card creation rules in `references/card_guidelines.md`.
   Create at minimum a Basic card (definition) and one Cloze card (key fact).
   Keep answers atomic (< 5 words unless it's a context/logic card).

3. **Preview** — show the card(s) using the ASCII format from `references/shared_preview.md`.
   Strip all HTML. After the last card show:
   ```
   ── Start import? [y] yes · [n] no ──
   ```

4. **Select deck** — propose a deck name based on the topic, then present:
   ```
   [1] Create new deck       — enter a name
   [2] Add to existing deck  — Suggested: My Subject::Chapter 01
   [3] Select existing deck  — show list
   ```
   - **[1]** → prompt `Deck name: _`, user types a name
   - **[2]** → use the suggested name directly, proceed
   - **[3]** → query AnkiConnect for all deck names, show numbered list,
               user enters a number to select

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
