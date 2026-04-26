#!/usr/bin/env python3
"""
Create a single Anki card via AnkiConnect.

Usage:
    python create_card.py --deck "My Deck" --front "What is X?" --back "The answer"
    python create_card.py --deck "My Deck" --cloze "X is {{c1::the answer}}."
    python create_card.py --deck "My Deck" --front "Q" --back "A" --tags tag1 tag2
    python create_card.py --deck "My Deck" --front "Q" --back "A" --ref "File > Ch > Slide 5"
    python create_card.py --deck "My Deck" --front "Q" --back "A" --dry-run

Card types:
    basic  — requires --front and --back
    cloze  — requires --cloze (text with {{c1::...}} deletions)
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anki_connect import AnkiConnect, AnkiConnectError

# ── Note type definitions (reused from import_cards.py) ──────────────────

CARD_CSS = """\
.card {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 18px;
    text-align: center;
    color: #1a1a1a;
    background-color: #ffffff;
    padding: 20px;
    max-width: 600px;
    margin: 0 auto;
}
@media (prefers-color-scheme: dark) {
    .card { color: #e8e8e8; background-color: #1a1a1a; }
}
.ref { font-size: 12px; color: #999; margin-top: 16px; }
"""

BASIC_TEMPLATES = [
    {
        "Name": "Card 1",
        "Front": "{{Front}}",
        "Back": "{{FrontSide}}<hr id='answer'>{{Back}}<div class='ref'>{{Ref}}</div>",
    }
]

CLOZE_TEMPLATES = [
    {
        "Name": "Cloze",
        "Front": "{{cloze:Text}}<div class='ref'>{{Ref}}</div>",
        "Back": "{{cloze:Text}}<div class='ref'>{{Ref}}</div>",
    }
]


def ensure_note_types(anki: AnkiConnect) -> None:
    anki.ensure_model("DL-Basic", ["Front", "Back", "Ref"], BASIC_TEMPLATES, CARD_CSS)
    anki.ensure_model("DL-Cloze", ["Text", "Ref"], CLOZE_TEMPLATES, CARD_CSS)


def create_basic_card(
    anki: AnkiConnect,
    deck: str,
    front: str,
    back: str,
    tags: list[str],
    ref: str,
    dry_run: bool,
) -> None:
    fields = {"Front": front, "Back": back, "Ref": ref}
    if dry_run:
        print(f"[dry-run] Would add Basic card to '{deck}':")
        print(f"  Front: {front}")
        print(f"  Back:  {back}")
        print(f"  Tags:  {tags}")
        print(f"  Ref:   {ref}")
        return
    note_id = anki.add_note(deck, "DL-Basic", fields, tags=tags)
    if note_id:
        print(f"✓ Card added (ID {note_id})")
    else:
        print("⚠ Card was not added — possible duplicate.")


def create_cloze_card(
    anki: AnkiConnect,
    deck: str,
    text: str,
    tags: list[str],
    ref: str,
    dry_run: bool,
) -> None:
    fields = {"Text": text, "Ref": ref}
    if dry_run:
        print(f"[dry-run] Would add Cloze card to '{deck}':")
        print(f"  Text: {text}")
        print(f"  Tags: {tags}")
        print(f"  Ref:  {ref}")
        return
    note_id = anki.add_note(deck, "DL-Cloze", fields, tags=tags)
    if note_id:
        print(f"✓ Card added (ID {note_id})")
    else:
        print("⚠ Card was not added — possible duplicate.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a single Anki card via AnkiConnect.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--deck", required=True, help="Target deck name (supports :: for sub-decks)")
    parser.add_argument("--front", help="Front field (Basic card)")
    parser.add_argument("--back", help="Back field (Basic card)")
    parser.add_argument("--cloze", help="Cloze text with {{c1::...}} deletions")
    parser.add_argument("--tags", nargs="*", default=[], help="Space-separated list of tags")
    parser.add_argument("--ref", default="", help="Source reference (e.g. 'File > Chapter > Slide 5')")
    parser.add_argument("--dry-run", action="store_true", help="Validate without importing")
    parser.add_argument("--host", default="127.0.0.1", help="AnkiConnect host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="AnkiConnect port (default: 8765)")
    args = parser.parse_args()

    # Validate card type
    if args.cloze:
        card_type = "cloze"
        if "{{c" not in args.cloze:
            parser.error("--cloze text must contain at least one {{c1::...}} deletion")
    elif args.front and args.back:
        card_type = "basic"
    else:
        parser.error("Provide --front and --back for a Basic card, or --cloze for a Cloze card")

    anki = AnkiConnect(host=args.host, port=args.port)

    if not args.dry_run:
        try:
            anki.test_connection()
        except AnkiConnectError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        try:
            ensure_note_types(anki)
            anki.create_deck(args.deck)
        except AnkiConnectError as e:
            print(f"Error setting up deck/models: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        if card_type == "basic":
            create_basic_card(anki, args.deck, args.front, args.back, args.tags, args.ref, args.dry_run)
        else:
            create_cloze_card(anki, args.deck, args.cloze, args.tags, args.ref, args.dry_run)
    except AnkiConnectError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
