# Mode: Research & Create Cards

Use this mode when the user wants to learn a topic or concept from scratch.
Claude researches the topic first, builds a structured learning plan, and
creates cards based on the confirmed plan.

## Workflow

1. **Understand the topic** — ask the user:
   ```
   What topic or concept would you like to learn?
   Any specific angle, depth, or context? (optional)
   ```

2. **Deep research** — search the web and synthesise authoritative sources.
   Cover: definition, core principles, sub-concepts, common misconceptions,
   real-world applications, and connections to related topics.

3. **Build a learning plan** — structure the research into concept clusters,
   ordered from foundational to advanced. Present the plan for approval:

   ```
   Learning plan: <Topic>
   ──────────────────────────────────────────────
   [1] <Foundational concept>      ~3 cards
   [2] <Core principle A>          ~5 cards
   [3] <Core principle B>          ~4 cards
   [4] <Application / use case>    ~3 cards
   [5] <Common misconception>      ~2 cards
   ──────────────────────────────────────────────
   Total: ~17 cards

   Proceed? [y] yes · [e] edit · [n] cancel
   ```

   - **[y]** → proceed to card creation
   - **[e]** → user can add, remove, or reorder clusters; re-show plan
   - **[n]** → cancel

4. **Create cards** — follow all rules in `references/card_guidelines.md`.
   Use the confirmed plan as the structure:
   - Nucleus principle per cluster (definition, rule, application)
   - Mnemonics for ordered lists
   - Self-contained, with a research-based reference on every card
     (e.g. `Research > <Topic> > <Sub-concept>`)

5. **Preview** — show all cards using the ASCII format from
   `references/shared_preview.md`. After the last card show:
   ```
   ── Start import? [y] yes · [n] no ──
   ```

6. **Select deck** — propose a deck name based on the topic, then present:
   ```
   [1] Create new deck       — enter a name
   [2] Add to existing deck  — Suggested: <Topic>
   [3] Select existing deck  — show list
   ```
   - **[1]** → prompt `Deck name: _`, user types a name
   - **[2]** → use the suggested name directly, proceed
   - **[3]** → query AnkiConnect for all deck names, show numbered list,
               user enters a number to select

7. **Write JSON** — write to `/tmp/anki_cards.json` (or a path the user specifies).
   Use the JSON format from `references/card_guidelines.md`.

8. **Pre-import check & import** — follow `references/shared_import.md`.
