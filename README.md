# Claude Skill: Anki Card Creator

A (Claude) Skill for creating high-quality Anki flashcards from study materials or any provided concept and importing them via the [AnkiConnect](https://ankiweb.net/shared/info/2055492159) REST API.

> [!NOTE]
> This skill covers specific use cases I needed — use it as-is or as inspiration for your own learning skill.
> It is built on the [Agent Skills](https://agentskills.io/home) standard and can be used in any compatible environment, though the documentation here focuses on Claude Code.
> Read more about Agent Skills [here](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) and [here](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills). 

## Installation

### Prerequisites

- Python 3.10+
- [Anki](https://apps.ankiweb.net/) with [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on (code: `2055492159`)

No external Python dependencies — uses only the standard library.

### Claude Code

The recommended way to use this skill — either via the CLI or the Claude Code Desktop app. 

```bash
git clone https://github.com/b0r1sp/claude-skill-anki.git
mkdir -p ~/.claude/skills
```

Then either **copy** (simple, self-contained):
```bash
cp -r claude-skill-anki ~/.claude/skills/anki
```

Or **symlink** (stays in sync with `git pull`):
```bash
ln -s "$PWD/claude-skill-anki" ~/.claude/skills/anki
```

If `~/.claude/skills/` didn't exist before, restart Claude Code once so it picks up the new directory: type `exit` or press `Ctrl+D`, then run `claude` again. After that, the skill auto-loads in every session.

### Claude Chat / Cowork

1. Download `anki.zip` from the [latest release](../../releases/latest)
2. Open **Preferences → Skills → Upload Skill** and select `anki.zip`

The skill works the same way like in Claude Code and will help you create cards. When it's time to import, run the provided command in the Terminal — the skill prepares it for you as a ready-to-paste snippet.

---

## What it does

**Three modes:**
- **Import from document(s)** — reads one or more PDFs/PPTXs, clusters by concept, and creates a full card set
- **Create from conversation** — turns a concept from the current chat into cards instantly
- **Research & create** — researches a topic from scratch, builds a structured learning plan, and creates cards

**In all modes:**
1. Assessment criteria support *(Import mode)* — accepts exam/certification weightings (text, file, or screenshot) to scale card depth by topic importance
2. Evidence-based card creation — nucleus principle, mnemonics for lists, atomic answers
3. Pre-import check — shows deck stats, duplicates, and review history before touching anything
4. Import via AnkiConnect — interactive duplicate handling (replace, update, or skip)
5. CLI tools for querying and listing existing notes
6. Proactively suggests cards during conversation when a concept worth remembering comes up

## Card creation principles

Cards follow a nucleus approach — each core concept gets at least three cards from different angles (definition, rule, application). For ordered lists, a mnemonic is built from syllables of each item to form a fantasy word (e.g. *OppMobExeClo*), paired with a sentence where each word is a creative blend of the original term (e.g. *"Opportunities Mobst Exentually Close"*) — syllables color-coded for instant recall. Every card is self-contained and references its source slide.

Full guidelines: [`references/card_guidelines.md`](references/card_guidelines.md)

## Usage

1. **Make sure Anki is open** with the AnkiConnect add-on installed.
2. **Start Claude Code** by running `claude` in your Terminal.
3. **Invoke the skill** — type `/anki` and choose a mode:
   - `[1]` **Import from document(s)** — attach one or more PDFs, PPTXs, or other files
   - `[2]` **Create from conversation** — turn a concept from the current chat into cards
   - `[3]` **Research & create** — give Claude a topic; it researches it, builds a learning plan, and creates cards
4. **Exam or certification?** *(Mode 1 only)* — Claude asks whether the deck is for an exam. If yes, provide the assessment criteria (paste text, attach a file, or share a screenshot). Claude OCRs screenshots, parses the weightings, and uses them throughout: high-weight topics get deeper clustering and more cards, low-weight topics get minimal coverage.
5. **Review the proposed cards** — Claude shows each card in an ASCII preview. Confirm, adjust, or reject before anything is written.
6. **Select a deck** — Claude suggests a deck name based on the content:
   - `[1]` Create a new deck — enter a name
   - `[2]` Add to the suggested existing deck
   - `[3]` Select from a list of all decks in Anki
7. **Pre-import check** — Claude shows a summary before touching anything:
   ```
   Pre-import check
   Deck: My Subject::Chapter 01  (247 cards)
   ─────────────────────────────────────────
   Deck total:                  247
   To import:                    10
     ├─ New cards:                7
     └─ Duplicates:               3
          ├─ Learned:             2
          └─ Never reviewed:      1
   ```
   Duplicate details (reviews, interval, ease, lapses) are shown for each match.
8. **Confirm** — Claude asks two separate questions: proceed with import, and (if learned duplicates exist) whether to reset their learning stats.
9. **Claude imports** — writes `/tmp/anki_cards.json` and runs the import script. Results appear directly in the conversation.

---

→ **[Workflow & Technical Reference](docs/reference.md)**
