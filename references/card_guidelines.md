# Anki Card Creation Guidelines

## Core Principles

1. **Cluster by concept** — Never create one card per sentence, slide, or fact. Group content by core concepts and build cards around those clusters.

2. **Exam-relevance and weighting** — Only create cards essential for the exam or certification. When assessment criteria are provided, scale both the depth of clustering and the number of cards to the topic weight:
   - **High-weight** (≥ 20%) → full nucleus, ≥ 5 cards per concept
   - **Medium-weight** (10–19%) → standard nucleus, 3–4 cards
   - **Low-weight** (< 10%) → minimal, 1–2 cards
   - **Not listed** → skip unless foundational for a listed topic

3. **Nucleus principle** — Each core concept must form a nucleus of at least 3 cards using different semantic angles:
   - A Basic card for the **definition**
   - A Cloze card for the **rule or key fact**
   - A Basic card for **practical application**
   This creates a hermetic memory structure where the concept is anchored from multiple directions. Scale up for high-weight topics (see rule 2).

4. **Learn before memorizing** — Create a Context/Logic card for each major concept to establish the "big picture" before drilling individual facts. This card can have a longer answer with context and examples.

5. **Minimum information** — Each card must contain exactly one atomic fact. Target answer length: <5 words. Context/Logic cards are exempt from the 5-word limit.

6. **Visuals** — For concepts involving curves, shifts, or structural relationships, include an ASCII diagram, a cropped screenshot reference, or a "Visualize This" mental instruction to engage the visual cortex.

7. **Personalization & Examples** — For every application card, include a relatable real-world example in brackets to create a stronger emotional and associative anchor.

8. **Self-containment** — Replace all pronouns with specific names. Every card must be understandable without external context.

9. **Reference format** — Every card must include a source reference:
   `Filename > Chapter > Slide N`
   Example: `01_Roles and Responsibilities > 01 What is Delivery? > Slide 5`

10. **Mnemonics for lists/sets** — For any ordered list, build a fantasy word from syllables of each item and a sentence where each word is a creative blend of the original term. See the Mnemonic System section below.

11. **No comma-separated sentences** — Never write answers as comma-separated lists. Decompose them into individual atomic items using `<br>` or bullet points in the Back field.

12. **Spell out abbreviations** — Always expand abbreviations inline in brackets the first time they appear on a card, e.g. `TCP (Transmission Control Protocol)`. Look up the meaning in the provided source documents. If not found, ask the user before creating the card.

13. **Tags** — Every card must carry the following structured tags:
    - `subject:X::chapterXX` — subject area and chapter
    - `type:[Basic|Cloze|ImageOcclusion]` — card type
    - `source:[Filename.ext]` — source file name including extension
    - `origin:[Filename > Chapter > Slide N]` — exact slide reference

## Mnemonic System

For any list or set of items that must be memorized, build a mnemonic by taking a syllable from each item (in order) to form a fantasy word, then compose a sentence where each word is a creative blend or fantasy derivation of the original term.

### Rules for mnemonic construction
- Take a **syllable** from each item — in order, never reorder
- Weave the syllables into a **fantasy word** (e.g. OppMobExeClo)
- Write a **sentence** where each word is a creative/fantasy derivation of the original term (e.g. Mobilization → "Mobst", Execution → "Exentually")
- The sentence should **hint at the meaning** of the list while using the blended words
- **Color the syllable** in both the fantasy word and the corresponding sentence word using the color palette below
- **Keep the source language** — syllables and sentence must come from the original language of the material

### Example
Project lifecycle phases: Opportunity → Mobilization → Execution → Closure

Fantasy word: **OppMobExeClo**
Sentence: *"Opportunities Mobst Exentually Close"*

HTML in Back field:
```html
Mnemonic: <b><span style="color:#e24b4a">Opp</span><span style="color:#378add">Mob</span><span style="color:#639922">Exe</span><span style="color:#ef9f27">Clo</span></b>
— <i>"<span style="color:#e24b4a">Opp</span>ortunities <span style="color:#378add">Mob</span>st <span style="color:#639922">Exe</span>ntually <span style="color:#ef9f27">Clo</span>se"</i>
```

### Color palette
| Position | Color  | Hex       |
|----------|--------|-----------|
| 1st      | Red    | `#e24b4a` |
| 2nd      | Blue   | `#378add` |
| 3rd      | Green  | `#639922` |
| 4th      | Amber  | `#ef9f27` |
| 5th      | Purple | `#7f77dd` |
| 6th      | Teal   | `#1d9e75` |


## Card Formats

### #BASIC
```
Front (question);Back (atomic answer + example);Tags
```
- Front: Question, optionally with MCQ options
- Back: Atomic answer. Include real-world example in brackets for application cards, using the same inline HTML formatting as the mnemonic line (colored `<span>`, `<b>` — no size changes).
- Tags: See rule 13 for the required structured tag schema

### #CLOZE
```
Sentence with {{c1::cloze deletion}};Tags
```
- Sentence provides context
- Cloze only the answer part
- Options can be in the text, but only cloze the answer
- Tags: See rule 13 for the required structured tag schema

### #IMAGE_OCCLUSION_LABELS
```
Description of diagram;Labels to occlude;Tags
```
- Reference to a diagram/image in the source material
- List which labels should be hidden for recall practice

## Output Format

When presenting cards for user review, use a single code block with three sections:
- `#BASIC` — all Basic cards
- `#CLOZE` — all Cloze cards
- `#IMAGE_OCCLUSION_LABELS` — all Image Occlusion cards

One card per line. No blank lines. Semicolon (;) as field separator.

## JSON Export Format

For import via `scripts/import_cards.py`, write cards to a JSON file:

```json
{
    "deck": "Parent Deck::Sub Deck",
    "cards": [
        {
            "type": "basic",
            "front": "Question text",
            "back": "Answer with <br>HTML<br> if needed",
            "tags": ["subject:X::chapterXX", "type:Basic", "source:Filename.ext", "origin:Filename > Chapter > Slide N"],
            "ref": "Filename > Chapter > Slide N"
        },
        {
            "type": "cloze",
            "text": "Sentence with {{c1::cloze part}}.",
            "tags": ["subject:X::chapterXX", "type:Cloze", "source:Filename.ext", "origin:Filename > Chapter > Slide N"],
            "ref": "Filename > Chapter > Slide N"
        }
    ]
}
```
