# Mode: Import from Document(s)

Use this mode when the user provides a study file (PDF, PPTX, etc.) and wants
a full batch of cards created and imported into Anki.

## Workflow

1. **Read the card guidelines** — load `references/card_guidelines.md` before
   creating any cards.

2. **Read the source material** — read the attached PDF, PPTX, or other document(s).

3. **Identify core concepts** — cluster content by concept, not by slide or paragraph.
   Consult exam weightings if provided to prioritize content.

4. **Create cards** — follow all rules in `references/card_guidelines.md`:
   - Nucleus principle: ≥ 3 cards per core concept (definition, rule, application)
   - Minimum information: one atomic fact per card, answers < 5 words
   - Mnemonics for ordered lists
   - Self-contained, with source reference on every card

5. **Preview cards** — show cards using the ASCII format from
   `references/shared_preview.md`. Pages of 5. Wait for `n` between pages.
   After the last page show:
   ```
   ── Start import? [y] yes · [n] no ──
   ```

6. **Write JSON** — if the user confirms, write to `/tmp/anki_cards.json`
   (or a path the user specifies). Use the JSON format from `references/card_guidelines.md`.

7. **Pre-import check & import** — follow `references/shared_import.md`.
