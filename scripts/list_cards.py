#!/usr/bin/env python3
"""
Query and list Anki notes via AnkiConnect.

Usage:
    python list_cards.py --query "tag:python added:7"
    python list_cards.py --deck "My Deck" --added 30
    python list_cards.py --tag python --tag anki
    python list_cards.py --due --limit 10
    python list_cards.py --new
    python list_cards.py --deck "My Deck" --query "Front:*TCP*"
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anki_connect import AnkiConnect, AnkiConnectError


def build_query(args) -> str:
    parts = []
    if args.query:
        parts.append(args.query)
    if args.deck:
        parts.append(f'deck:"{args.deck}"')
    if args.tag:
        for tag in args.tag:
            parts.append(f"tag:{tag}")
    if args.added:
        parts.append(f"added:{args.added}")
    if args.due:
        parts.append("is:due")
    if args.new:
        parts.append("is:new")
    return " ".join(parts)


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def main():
    parser = argparse.ArgumentParser(
        description="Query and list Anki notes via AnkiConnect.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: python list_cards.py --deck 'My Deck' --added 7",
    )
    parser.add_argument("--query", "-q", metavar="QUERY", help="Raw Anki search query")
    parser.add_argument("--deck", "-d", metavar="DECK", help="Filter by deck name")
    parser.add_argument("--tag", "-t", metavar="TAG", action="append",
                        help="Filter by tag (repeatable: -t python -t anki)")
    parser.add_argument("--added", "-a", type=int, metavar="DAYS",
                        help="Notes added in last N days")
    parser.add_argument("--due", action="store_true", help="Due cards only")
    parser.add_argument("--new", action="store_true", help="New cards only")
    parser.add_argument("--limit", "-l", type=int, default=20,
                        help="Max notes to show (default: 20, 0 = all)")
    parser.add_argument("--host", default="127.0.0.1", help="AnkiConnect host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="AnkiConnect port (default: 8765)")
    args = parser.parse_args()

    query = build_query(args)
    if not query:
        parser.error(
            "Provide at least one filter: --query, --deck, --tag, --added, --due, --new"
        )

    anki = AnkiConnect(host=args.host, port=args.port)
    try:
        anki.test_connection()
    except AnkiConnectError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        note_ids = anki.find_notes(query)
    except AnkiConnectError as e:
        print(f"Query error: {e}", file=sys.stderr)
        sys.exit(1)

    total = len(note_ids)
    if not total:
        print("No notes found.")
        return

    limit = args.limit if args.limit > 0 else total
    page_ids = note_ids[:limit]
    notes = anki.notes_info(page_ids)

    print(f"Found {total} note(s) (showing {len(notes)}):\n")
    for note in notes:
        fields = note["fields"]
        first_value = strip_html(list(fields.values())[0]["value"])[:72]
        tags = "  [" + ", ".join(note["tags"]) + "]" if note.get("tags") else ""
        print(f"  {note['noteId']}  {first_value}{tags}")

    if total > limit:
        print(f"\n  … and {total - limit} more. Use --limit 0 to show all.")


if __name__ == "__main__":
    main()
