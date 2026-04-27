# Mode: Import from Document(s)

Use this mode when the user provides one or more study files (PDF, PPTX, etc.)
and wants a full batch of cards created and imported into Anki.

## Workflow

1. **Read the card guidelines** — load `references/card_guidelines.md` before
   creating any cards.

2. **Read the source material** — read all attached PDFs, PPTXs, or other documents.
   If multiple files are provided, read them all before creating any cards.

3. **Exam or certification check** — ask the user:
   ```
   Is this deck for an exam or certification? [y] yes · [n] no
   ```
   If **yes**, ask for the assessment criteria:
   ```
   Please provide the assessment criteria or skill weightings.
   You can paste text, attach a file, or share a screenshot — I'll read it.
   ```
   - Accept text, PDF, or screenshot (OCR the screenshot to extract the criteria)
   - Parse each topic/skill and its weight (percentage, points, or priority level)
   - Keep the criteria in mind for every step that follows

4. **Identify core concepts** — cluster content by concept, not by slide or paragraph.
   If assessment criteria are available, apply them here:
   - **High-weight topics** (e.g. ≥ 20%) → always form a nucleus; cluster deeply
   - **Medium-weight topics** (e.g. 10–19%) → include all key concepts
   - **Low-weight topics** (e.g. < 10%) → cover briefly; one cluster at most
   - **Not in criteria** → skip unless foundational for understanding a listed topic

5. **Create cards** — follow all rules in `references/card_guidelines.md`.
   Scale the number of cards per concept to its weight in the assessment criteria:
   - **High-weight** → full nucleus (≥ 5 cards: definition, rule, application,
     context/logic, cloze variants, mnemonic if list)
   - **Medium-weight** → standard nucleus (3–4 cards)
   - **Low-weight** → minimal (1–2 cards, definition only)
   - Always: minimum information, self-contained, source reference on every card

6. **Preview cards** — show all cards using the ASCII format from
   `references/shared_preview.md`. After the last card show:
   ```
   ── Start import? [y] yes · [n] no ──
   ```

7. **Select deck** — propose a deck name based on the source file and content,
   then present the following options:
   ```
   [1] Create new deck       — enter a name
   [2] Add to existing deck  — Suggested: My Subject::Chapter 01
   [3] Select existing deck  — show list
   ```
   - **[1]** → prompt `Deck name: _`, user types a name
   - **[2]** → use the suggested name directly, proceed
   - **[3]** → query AnkiConnect for all deck names, show numbered list,
               user enters a number to select

   Update the deck in the JSON with the confirmed name before continuing.

8. **Write JSON** — write to `/tmp/anki_cards.json` (or a path the user specifies).
   Use the JSON format from `references/card_guidelines.md`.

9. **Pre-import check & import** — follow `references/shared_import.md`.
