# Shared: Pre-Import Check & Import

## 0. After deck selection

Once the user has confirmed a deck, show:

```
Deck confirmed: My Subject::Chapter 01
Writing cards to /tmp/anki_cards.json…
Running pre-import check — this may take a moment.
```

Then immediately write the JSON and run the check.

## 1. Pre-Import Check (mandatory — never skip)

**Always** run the check before importing. Never proceed to import without
showing the stats report first.

```bash
python /path/to/scripts/import_cards.py /tmp/anki_cards.json --check
```

**Always** present the full report to the user — deck total, cards to import,
new vs. duplicate breakdown, and duplicate details with review stats.
Do not summarise or omit any section of the report.

Then ask the following as **separate sequential steps** — do not combine them:

1. *"Proceed with import?"* — **wait** for explicit answer before continuing
2. *"Reset learning stats for duplicates?"* — ask as a separate follow-up
   **only if** learned duplicates exist; skip this step otherwise

## 2. Import

Once the user confirms, run the import:

```bash
python /path/to/scripts/import_cards.py /tmp/anki_cards.json \
  --on-duplicate [replace|update|skip] \
  [--reset-metadata|--keep-metadata]
```

### Duplicate handling options

| Mode | What happens |
|------|-------------|
| `replace` | Delete old card, create new one (metadata lost) |
| `update` | Update fields of existing card, review history preserved by default |
| `skip` | Leave existing card unchanged |

Use `--reset-metadata` with `update` only if the user confirmed they want to reset learning stats.

## 3. Prerequisites

- Anki must be running
- AnkiConnect add-on installed (code: `2055492159`)
- AnkiConnect listening on `127.0.0.1:8765`
