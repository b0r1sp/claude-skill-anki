# Anki Card Creation Guidelines

## Core Principles

1. **Cluster by concept** — Never create one card per sentence, slide, or fact. Group content by core concepts and build cards around those clusters.

2. **Exam-relevance only** — Only create cards essential for achieving ≥95% on the exam. Consult the Assessment Skills and exam weightings to prioritize content.

3. **Nucleus principle** — Each core concept must form a nucleus of at least 3 cards using different semantic angles:
   - A Basic card for the **definition**
   - A Cloze card for the **rule or key fact**
   - A Basic card for **practical application**
   This creates a hermetic memory structure where the concept is anchored from multiple directions.

4. **Learn before memorizing** — Create a Context/Logic card for each major concept to establish the "big picture" before drilling individual facts. This card can have a longer answer with context and examples.

5. **Minimum information** — Each card must contain exactly one atomic fact. Target answer length: <5 words. Context/Logic cards are exempt from the 5-word limit.

6. **Visuals** — For concepts involving curves, shifts, or structural relationships, include an ASCII diagram, a cropped screenshot reference, or a "Visualize This" mental instruction to engage the visual cortex.

7. **Personalization & Examples** — For every application card, include a relatable real-world example in brackets to create a stronger emotional and associative anchor.

8. **Self-containment** — Replace all pronouns with specific names. Every card must be understandable without external context.

9. **Reference format** — Every card must include a source reference:
   `Filename > Chapter > Slide N`
   Example: `01_Roles and Responsibilities > 01 What is Delivery? > Slide 5`

10. **Mnemonics for lists/sets** — Build coordinated mnemonic words for list knowledge. See the Mnemonic System section below.

## Mnemonic System

For any list or set of items that must be memorized, create a fantasy mnemonic word. The word consists of two parts:

- **Name part** — identifies what the list is about (e.g. "Service" for service groups)
- **Memory part** — syllables from each list item, woven together

### Rules for mnemonic construction
- Use syllables that clearly reference each list item
- Weave syllables into an organic fantasy word that feels natural to speak
- Use HTML color spans to highlight each syllable in the Back field

### Example
Legal concept "Vertrag mit Schutzwirkung zugunsten Dritter" with 4 test points:
- Leistungsnähe → **Näh**
- Interesse des Gläubigers → **In**
- Erkennbarkeit → **Erk**
- Bedürftigkeit → **Bed**

Mnemonic: Schutzwirk**Näh****In****Erk****Bed**

HTML in Back field:
```html
Merkhilfe: Schutzwirk<b><span style="color:#e24b4a">Näh</span><span style="color:#378add">In</span><span style="color:#639922">Erk</span><span style="color:#ef9f27">Bed</span></b>
```

### Color palette for syllables
| Position | Color   | Hex       |
|----------|---------|-----------|
| 1st      | Red     | `#e24b4a` |
| 2nd      | Blue    | `#378add` |
| 3rd      | Green   | `#639922` |
| 4th      | Amber   | `#ef9f27` |
| 5th      | Purple  | `#7f77dd` |
| 6th      | Teal    | `#1d9e75` |

## Card Formats

### #BASIC
```
Front (question);Back (atomic answer + example);Tags
```
- Front: Question, optionally with MCQ options
- Back: Atomic answer. Include real-world example in brackets for application cards.
- Tags: Space-separated, derived from source reference

### #CLOZE
```
Sentence with {{c1::cloze deletion}};Tags
```
- Sentence provides context
- Cloze only the answer part
- Options can be in the text, but only cloze the answer

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
            "tags": ["source_file", "concept_name"],
            "ref": "Filename > Chapter > Slide N"
        },
        {
            "type": "cloze",
            "text": "Sentence with {{c1::cloze part}}.",
            "tags": ["source_file", "concept_name"],
            "ref": "Filename > Chapter > Slide N"
        }
    ]
}
```
