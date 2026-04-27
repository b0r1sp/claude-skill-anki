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
import re
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


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def _strip_cloze(text: str) -> str:
    return re.sub(r"\{\{c\d+::(.*?)\}\}", r"\1", text)


def find_duplicate_notes(anki: AnkiConnect, deck: str, card: dict) -> list[dict]:
    """Search for existing notes in the deck that match the given card's first field.

    Returns a list of matching note info dicts (empty list = no duplicates).
    """
    card_type = card.get("type", "basic")

    if card_type == "basic":
        raw = card.get("front", "")
        field_name = "Front"
    elif card_type == "cloze":
        raw = _strip_cloze(card.get("text", ""))
        field_name = "Text"
    else:
        return []

    search_value = _strip_html(raw)[:60].replace('"', "")
    query = f'deck:"{deck}" {field_name}:"{search_value}"'

    try:
        note_ids = anki.find_notes(query)
        return anki.notes_info(note_ids) if note_ids else []
    except AnkiConnectError:
        return []


def _prompt_action(card: dict, existing: list[dict]) -> str:
    """Ask the user what to do with a duplicate. Returns 'replace', 'update', or 'skip'."""
    first_field = _strip_html(list(existing[0]["fields"].values())[0]["value"])[:60]
    card_preview = _strip_html(card.get("front", card.get("text", "")))[:60]

    print(f"\n  ⚠  Duplicate detected:")
    print(f"     Existing : {first_field}")
    print(f"     New card : {card_preview}")

    while True:
        choice = input("  [R]eplace / [U]pdate / [S]kip: ").strip().lower()
        if choice in ("r", "replace"):
            return "replace"
        if choice in ("u", "update"):
            return "update"
        if choice in ("s", "skip", ""):
            return "skip"
        print("  Please enter R, U, or S.")


def _build_fields(card: dict) -> dict[str, str]:
    """Build the fields dict for a card."""
    card_type = card.get("type", "basic")
    ref = card.get("ref", "")
    if card_type == "basic":
        return {"Front": card["front"], "Back": card["back"], "Ref": ref}
    return {"Text": card["text"], "Ref": ref}


def _do_replace(
    anki: AnkiConnect,
    deck: str,
    card: dict,
    existing: list[dict],
) -> int | None:
    """Delete all matching notes, then add the new card."""
    anki.delete_notes([n["noteId"] for n in existing])
    model = BASIC_MODEL if card.get("type", "basic") == "basic" else CLOZE_MODEL
    return anki.add_note(
        deck=deck,
        model=model,
        fields=_build_fields(card),
        tags=card.get("tags", []),
        allow_duplicate=True,
    )


def _do_update(
    anki: AnkiConnect,
    card: dict,
    existing: list[dict],
    reset_metadata: bool | None,
) -> None:
    """Update fields (and optionally tags + review history) of the first matching note."""
    note = existing[0]
    note_id = note["noteId"]

    anki.update_note_fields(note_id, _build_fields(card))

    tags = card.get("tags")
    if tags:
        anki.update_note_tags(note_id, tags)

    # Resolve metadata reset
    if reset_metadata is None:
        answer = input("  Reset review history? [y/N]: ").strip().lower()
        reset_metadata = answer in ("y", "yes")

    if reset_metadata:
        card_ids = note.get("cards", [])
        if card_ids:
            anki.forget_cards(card_ids)


def check_cards(anki: AnkiConnect, data: dict) -> dict:
    """Analyse a card set against the existing Anki collection without importing.

    For each card:
    - Checks if a duplicate exists in the target deck
    - For duplicates, fetches review stats (reviews, interval, ease, lapses)

    Returns a report dict:
    {
        "deck": str,
        "deck_total": int,         # current note count in the target deck
        "total": int,
        "new": int,
        "duplicates": [
            {
                "index": int,          # 1-based card index
                "card": dict,          # original card data
                "note": dict,          # existing note info
                "reviews": int,
                "interval": int,       # days
                "ease": float,
                "lapses": int,
                "learned": bool,       # True if reviews > 0
            },
            ...
        ]
    }
    """
    deck = data["deck"]
    cards = data["cards"]
    duplicates = []

    # Fetch current deck size
    try:
        deck_note_ids = anki.find_notes(f'deck:"{deck}"')
        deck_total = len(deck_note_ids)
    except AnkiConnectError:
        deck_total = 0

    for i, card in enumerate(cards):
        existing = find_duplicate_notes(anki, deck, card)
        if not existing:
            continue

        note = existing[0]
        card_ids = note.get("cards", [])

        reviews = interval = lapses = 0
        ease = 0.0

        if card_ids:
            try:
                stats = anki.cards_info(card_ids)
                if stats:
                    # Aggregate across all cards of the note
                    reviews = sum(c.get("reviews", 0) for c in stats)
                    lapses = sum(c.get("lapses", 0) for c in stats)
                    interval = max(c.get("interval", 0) for c in stats)
                    ease = round(stats[0].get("factor", 2500) / 1000, 2)
            except AnkiConnectError:
                pass

        duplicates.append({
            "index": i + 1,
            "card": card,
            "note": note,
            "reviews": reviews,
            "interval": interval,
            "ease": ease,
            "lapses": lapses,
            "learned": reviews > 0,
        })

    return {
        "deck": deck,
        "deck_total": deck_total,
        "total": len(cards),
        "new": len(cards) - len(duplicates),
        "duplicates": duplicates,
    }


def print_check_report(report: dict) -> None:
    """Print a human-readable pre-import analysis report."""
    dupes = report["duplicates"]
    learned = [d for d in dupes if d["learned"]]
    unlearned = [d for d in dupes if not d["learned"]]
    W = 58

    print("─" * W)
    print("Pre-import check")
    print(f"Deck: {report['deck']}  ({report['deck_total']} cards)")
    print("─" * W)
    print(f"  Deck total:              {report['deck_total']:>6}")
    print(f"  To import:               {report['total']:>6}")
    print(f"  ├─ New cards:            {report['new']:>6}")
    print(f"  └─ Duplicates:           {len(dupes):>6}")

    if dupes:
        learned_marker  = "├─" if unlearned else "└─"
        print(f"       {learned_marker} Learned:         {len(learned):>6}")
        if unlearned:
            print(f"       └─ Never reviewed:  {len(unlearned):>6}")

    print("─" * W)

    if dupes:
        print("Duplicate details:")
        for d in dupes:
            front = _strip_html(d["card"].get("front", d["card"].get("text", "")))[:50]
            print(f"  [{d['index']}] {front}")
            if d["learned"]:
                print(f"      reviews={d['reviews']}  interval={d['interval']}d"
                      f"  ease={d['ease']}  lapses={d['lapses']}")
            else:
                print(f"      (never reviewed)")
        print("─" * W)


def import_cards(
    anki: AnkiConnect,
    data: dict,
    dry_run: bool = False,
    on_duplicate: str = "ask",
    reset_metadata: bool | None = None,
) -> dict:
    """Import cards from a parsed JSON structure.

    Args:
        anki: AnkiConnect client instance.
        data: Parsed JSON with 'deck' and 'cards' keys.
        dry_run: If True, validate but don't actually import.
        on_duplicate: How to handle duplicates — 'ask', 'replace', 'update', or 'skip'.
        reset_metadata: For 'update' mode — True/False to auto-decide; None = ask interactively.

    Returns:
        dict with 'success', 'skipped', 'replaced', 'updated', 'failed' counts and 'errors'.
    """
    deck = data["deck"]
    cards = data["cards"]

    result = {
        "total": len(cards),
        "success": 0,
        "replaced": 0,
        "updated": 0,
        "skipped": 0,
        "failed": 0,
        "errors": [],
    }

    if dry_run:
        print(f"[DRY RUN] Would create deck: {deck}")
        print(f"[DRY RUN] Would import {len(cards)} cards")
        for i, card in enumerate(cards):
            card_type = card.get("type", "basic")
            preview = card.get("front", card.get("text", ""))[:60]
            print(f"  [{i+1}] {card_type.upper()}: {preview}")
        result["success"] = len(cards)
        return result

    # Create deck and ensure models exist
    anki.get_or_create_deck(deck)
    ensure_models(anki)

    # Import each card
    for i, card in enumerate(cards):
        card_type = card.get("type", "basic")
        label = f"[{i+1}]"

        try:
            if card_type not in ("basic", "cloze"):
                result["failed"] += 1
                result["errors"].append(f"{label} Unknown card type: {card_type}")
                print(f"  {label} FAILED: unknown type '{card_type}'")
                continue

            model = BASIC_MODEL if card_type == "basic" else CLOZE_MODEL
            note_id = anki.add_note(
                deck=deck,
                model=model,
                fields=_build_fields(card),
                tags=card.get("tags", []),
            )

            if note_id is not None:
                result["success"] += 1
                print(f"  {label} OK ({card_type})")
                continue

            # ── Duplicate detected ────────────────────────────────────
            existing = find_duplicate_notes(anki, deck, card)

            action = on_duplicate
            if action == "ask":
                action = _prompt_action(card, existing) if existing else "skip"

            if action == "skip":
                result["skipped"] += 1
                print(f"  {label} SKIPPED (duplicate)")

            elif action == "replace":
                _do_replace(anki, deck, card, existing)
                result["replaced"] += 1
                print(f"  {label} REPLACED ({card_type})")

            elif action == "update":
                _do_update(anki, card, existing, reset_metadata)
                result["updated"] += 1
                print(f"  {label} UPDATED ({card_type})")

            else:
                result["skipped"] += 1
                print(f"  {label} SKIPPED (unknown action '{action}')")

        except AnkiConnectError as e:
            result["failed"] += 1
            result["errors"].append(f"{label} {e}")
            print(f"  {label} FAILED: {e}")

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
    parser.add_argument("--check", action="store_true",
                        help="Analyse duplicates and review stats without importing")
    parser.add_argument("--dry-run", action="store_true", help="Validate without importing")
    parser.add_argument(
        "--on-duplicate",
        choices=["ask", "replace", "update", "skip"],
        default="ask",
        help="How to handle duplicates (default: ask)",
    )
    parser.add_argument(
        "--reset-metadata",
        action="store_true",
        default=None,
        help="With --on-duplicate=update: always reset review history",
    )
    parser.add_argument(
        "--keep-metadata",
        action="store_true",
        help="With --on-duplicate=update: never reset review history",
    )
    args = parser.parse_args()

    # Resolve metadata reset flag
    reset_metadata: bool | None = None
    if args.reset_metadata:
        reset_metadata = True
    elif args.keep_metadata:
        reset_metadata = False

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

    # Check mode — analyse duplicates and stats, then exit
    if args.check:
        report = check_cards(anki, data)
        print_check_report(report)
        sys.exit(0)

    # Import
    result = import_cards(
        anki,
        data,
        dry_run=args.dry_run,
        on_duplicate=args.on_duplicate,
        reset_metadata=reset_metadata,
    )

    # Summary
    print()
    print("─" * 40)
    print(f"Total:    {result['total']}")
    print(f"Success:  {result['success']}")
    print(f"Replaced: {result['replaced']}")
    print(f"Updated:  {result['updated']}")
    print(f"Skipped:  {result['skipped']}")
    print(f"Failed:   {result['failed']}")

    if result["errors"]:
        print()
        print("Errors:")
        for err in result["errors"]:
            print(f"  {err}")

    sys.exit(0 if result["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
