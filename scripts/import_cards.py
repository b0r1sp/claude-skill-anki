#!/usr/bin/env python3
"""
Import Anki cards from a JSON file via AnkiConnect.

Usage:
    python import_cards.py cards.json
    python import_cards.py cards.json --dry-run
    python import_cards.py cards.json --host 127.0.0.1 --port 8765

JSON format:
{
    "deck": "DL Certification::01 Roles and Responsibilities",
    "cards": [
        {
            "type": "basic",
            "front": "What is Delivery?",
            "back": "Fulfilment of commitments",
            "tags": ["01_Roles", "Slide5"],
            "ref": "01_Roles > 01 What is Delivery > Slide 5"
        },
        {
            "type": "cloze",
            "text": "Delivery is the fulfilment of {{c1::commercial}} commitments.",
            "tags": ["01_Roles", "Slide5"],
            "ref": "01_Roles > 01 What is Delivery > Slide 5"
        }
    ]
}
"""

import argparse
import json
import sys
import os

# Allow importing anki_connect from the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anki_connect import AnkiConnect, AnkiConnectError


# ── Default card styling ──────────────────────────────────────────────

CARD_CSS = """\
.card {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 18px;
    text-align: center;
    color: #1a1a1a;
    background-color: #ffffff;
    padding: 20px;
    line-height: 1.6;
}
.card.nightMode {
    color: #e0e0e0;
    background-color: #1e1e1e;
}
.ref {
    font-size: 11px;
    color: #999;
    margin-top: 16px;
    font-style: italic;
}
.merkhilfe {
    margin-top: 12px;
    padding: 8px 12px;
    background: #f5f5f5;
    border-radius: 6px;
    font-size: 15px;
}
.card.nightMode .merkhilfe {
    background: #2a2a2a;
}
"""

BASIC_FRONT = """\
<div class="front">{{Front}}</div>
"""

BASIC_BACK = """\
<div class="front">{{Front}}</div>
<hr id="answer">
<div class="back">{{Back}}</div>
<div class="ref">{{Ref}}</div>
"""

CLOZE_FRONT = """\
<div class="cloze">{{cloze:Text}}</div>
"""

CLOZE_BACK = """\
<div class="cloze">{{cloze:Text}}</div>
<div class="ref">{{Ref}}</div>
"""

# ── Model names ───────────────────────────────────────────────────────

BASIC_MODEL = "DL-Basic"
CLOZE_MODEL = "DL-Cloze"


def ensure_models(anki: AnkiConnect) -> None:
    """Create the Basic and Cloze note types if they don't exist."""
    anki.ensure_model(
        name=BASIC_MODEL,
        fields=["Front", "Back", "Ref"],
        card_templates=[{
            "Name": "Card 1",
            "Front": BASIC_FRONT,
            "Back": BASIC_BACK,
        }],
        css=CARD_CSS,
    )

    anki.ensure_model(
        name=CLOZE_MODEL,
        fields=["Text", "Ref"],
        card_templates=[{
            "Name": "Cloze",
            "Front": CLOZE_FRONT,
            "Back": CLOZE_BACK,
        }],
        css=CARD_CSS,
    )


def import_cards(anki: AnkiConnect, data: dict, dry_run: bool = False) -> dict:
    """Import cards from a parsed JSON structure.

    Args:
        anki: AnkiConnect client instance.
        data: Parsed JSON with 'deck' and 'cards' keys.
        dry_run: If True, validate but don't actually import.

    Returns:
        dict with 'success', 'skipped', 'failed' counts and 'errors' list.
    """
    deck = data["deck"]
    cards = data["cards"]

    result = {"success": 0, "skipped": 0, "failed": 0, "errors": [], "total": len(cards)}

    if dry_run:
        print(f"[DRY RUN] Would create deck: {deck}")
        print(f"[DRY RUN] Would import {len(cards)} cards")
        for i, card in enumerate(cards):
            card_type = card.get("type", "basic")
            if card_type == "basic":
                print(f"  [{i+1}] BASIC: {card['front'][:60]}...")
            elif card_type == "cloze":
                print(f"  [{i+1}] CLOZE: {card['text'][:60]}...")
        result["success"] = len(cards)
        return result

    # Create deck and ensure models exist
    anki.get_or_create_deck(deck)
    ensure_models(anki)

    # Import each card
    for i, card in enumerate(cards):
        card_type = card.get("type", "basic")
        ref = card.get("ref", "")
        tags = card.get("tags", [])

        try:
            if card_type == "basic":
                note_id = anki.add_note(
                    deck=deck,
                    model=BASIC_MODEL,
                    fields={
                        "Front": card["front"],
                        "Back": card["back"],
                        "Ref": ref,
                    },
                    tags=tags,
                )
            elif card_type == "cloze":
                note_id = anki.add_note(
                    deck=deck,
                    model=CLOZE_MODEL,
                    fields={
                        "Text": card["text"],
                        "Ref": ref,
                    },
                    tags=tags,
                )
            else:
                result["failed"] += 1
                result["errors"].append(f"[{i+1}] Unknown card type: {card_type}")
                continue

            if note_id is None:
                result["skipped"] += 1
                print(f"  [{i+1}] SKIPPED (duplicate)")
            else:
                result["success"] += 1
                print(f"  [{i+1}] OK ({card_type})")

        except AnkiConnectError as e:
            result["failed"] += 1
            error_msg = str(e)
            result["errors"].append(f"[{i+1}] {error_msg}")
            print(f"  [{i+1}] FAILED: {error_msg}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Import Anki cards from a JSON file via AnkiConnect.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: python import_cards.py my_cards.json",
    )
    parser.add_argument("file", help="Path to the JSON file with card data")
    parser.add_argument("--host", default="127.0.0.1", help="AnkiConnect host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="AnkiConnect port (default: 8765)")
    parser.add_argument("--dry-run", action="store_true", help="Validate without importing")
    args = parser.parse_args()

    # Load JSON
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate structure
    if "deck" not in data or "cards" not in data:
        print("Error: JSON must contain 'deck' and 'cards' keys.", file=sys.stderr)
        sys.exit(1)

    print(f"Deck: {data['deck']}")
    print(f"Cards: {len(data['cards'])}")
    print()

    # Connect
    anki = AnkiConnect(host=args.host, port=args.port)

    if not args.dry_run:
        try:
            info = anki.test_connection()
            print(f"Connected to AnkiConnect v{info['version']}")
        except AnkiConnectError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    print()

    # Import
    result = import_cards(anki, data, dry_run=args.dry_run)

    # Summary
    print()
    print("─" * 40)
    print(f"Total:   {result['total']}")
    print(f"Success: {result['success']}")
    print(f"Skipped: {result['skipped']}")
    print(f"Failed:  {result['failed']}")

    if result["errors"]:
        print()
        print("Errors:")
        for err in result["errors"]:
            print(f"  {err}")

    sys.exit(0 if result["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
