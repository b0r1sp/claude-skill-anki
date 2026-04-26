# Shared: Pre-Import Check & Import

## 1. Pre-Import Check (always run before importing)

Run the check to show duplicate and review stats before touching anything:

```bash
python /path/to/scripts/import_cards.py /tmp/anki_cards.json --check
```

Present the report to the user:
- How many new cards
- How many duplicates — with review count, interval, ease, and lapses for each

Then ask:
- *"Proceed with import?"*
- *"Reset learning stats for duplicates?"* (only if learned duplicates exist)

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
