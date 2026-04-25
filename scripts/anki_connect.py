"""
AnkiConnect REST Client

A Python client for the AnkiConnect API (https://foosoft.net/projects/anki-connect/).
AnkiConnect exposes Anki's functionality via a local REST API on port 8765.

Usage:
    from anki_connect import AnkiConnect, AnkiConnectError

    anki = AnkiConnect()
    anki.test_connection()
    anki.create_deck("My Deck")
    anki.add_note("My Deck", "Basic", {"Front": "Q?", "Back": "A."}, tags=["tag1"])
"""

import json
import urllib.request
import urllib.error
from typing import Any


class AnkiConnectError(Exception):
    """Raised when AnkiConnect returns an error or is unreachable."""
    pass


class AnkiConnect:
    """Client for the AnkiConnect REST API.

    Args:
        host: AnkiConnect hostname (default: 127.0.0.1)
        port: AnkiConnect port (default: 8765)
        timeout: Request timeout in seconds (default: 30)
    """

    API_VERSION = 6

    def __init__(self, host: str = "127.0.0.1", port: int = 8765, timeout: int = 30):
        self.url = f"http://{host}:{port}"
        self.timeout = timeout

    # ── Core ─────────────────────────────────────────────────────────

    def invoke(self, action: str, **params) -> Any:
        """Send a request to AnkiConnect and return the result.

        Args:
            action: The AnkiConnect action name (e.g. 'addNote', 'deckNames')
            **params: Action-specific parameters

        Returns:
            The result field from AnkiConnect's response.

        Raises:
            AnkiConnectError: If the request fails or AnkiConnect returns an error.
        """
        payload = {"action": action, "version": self.API_VERSION}
        if params:
            payload["params"] = params

        request_body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.url,
            data=request_body,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                response = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            raise AnkiConnectError(
                f"Cannot reach AnkiConnect at {self.url}. "
                f"Is Anki running with AnkiConnect installed? ({e})"
            ) from e
        except json.JSONDecodeError as e:
            raise AnkiConnectError(f"Invalid JSON response from AnkiConnect: {e}") from e

        if response.get("error"):
            raise AnkiConnectError(f"AnkiConnect error: {response['error']}")

        return response.get("result")

    def test_connection(self) -> dict:
        """Test the connection to AnkiConnect.

        Returns:
            dict with 'version' (int) and 'connected' (bool).

        Raises:
            AnkiConnectError: If Anki is not reachable.
        """
        version = self.invoke("version")
        return {"connected": True, "version": version}

    # ── Decks ────────────────────────────────────────────────────────

    def deck_names(self) -> list[str]:
        """Return a list of all deck names."""
        return self.invoke("deckNames")

    def create_deck(self, name: str) -> int:
        """Create a deck (including parent decks for '::' separators).

        Args:
            name: Deck name, e.g. 'Parent::Child'

        Returns:
            The deck ID.
        """
        return self.invoke("createDeck", deck=name)

    def delete_deck(self, name: str, cards_too: bool = True) -> None:
        """Delete a deck.

        Args:
            name: Deck name to delete.
            cards_too: Also delete all cards in the deck (default: True).
        """
        self.invoke("deleteDecks", decks=[name], cardsToo=cards_too)

    # ── Models (Note Types) ──────────────────────────────────────────

    def model_names(self) -> list[str]:
        """Return a list of all note type (model) names."""
        return self.invoke("modelNames")

    def model_field_names(self, model_name: str) -> list[str]:
        """Return the field names for a given note type.

        Args:
            model_name: Name of the note type, e.g. 'Basic'
        """
        return self.invoke("modelFieldNames", modelName=model_name)

    def create_model(
        self,
        name: str,
        fields: list[str],
        card_templates: list[dict],
        css: str = "",
    ) -> dict:
        """Create a new note type (model).

        Args:
            name: Model name.
            fields: List of field names, e.g. ['Front', 'Back']
            card_templates: List of dicts with 'Name', 'Front', 'Back' keys
                containing the card template HTML.
            css: Optional CSS for card styling.

        Returns:
            The created model info.
        """
        field_defs = [{"name": f} for f in fields]
        return self.invoke(
            "createModel",
            modelName=name,
            inOrderFields=fields,
            cardTemplates=card_templates,
            css=css,
        )

    def ensure_model(self, name: str, fields: list[str], card_templates: list[dict], css: str = "") -> str:
        """Get or create a note type. Returns the model name.

        If a model with the given name exists, returns it as-is.
        Otherwise creates it with the specified fields and templates.
        """
        existing = self.model_names()
        if name in existing:
            return name
        self.create_model(name, fields, card_templates, css)
        return name

    # ── Notes ────────────────────────────────────────────────────────

    def add_note(
        self,
        deck: str,
        model: str,
        fields: dict[str, str],
        tags: list[str] | None = None,
        allow_duplicate: bool = False,
    ) -> int | None:
        """Add a single note to Anki.

        Args:
            deck: Target deck name.
            model: Note type name (e.g. 'Basic', 'Cloze').
            fields: Dict mapping field names to values, e.g. {'Front': '...', 'Back': '...'}
            tags: Optional list of tags.
            allow_duplicate: Allow adding duplicate notes (default: False).

        Returns:
            The note ID, or None if a duplicate was skipped.

        Raises:
            AnkiConnectError: If the note could not be added.
        """
        note = {
            "deckName": deck,
            "modelName": model,
            "fields": fields,
            "tags": tags or [],
            "options": {
                "allowDuplicate": allow_duplicate,
                "duplicateScope": "deck",
            },
        }
        return self.invoke("addNote", note=note)

    def add_notes(self, notes: list[dict]) -> list[int | None]:
        """Add multiple notes in a single request (batch).

        Each note dict must have keys: deckName, modelName, fields, tags, options.
        Use build_note() to construct them.

        Args:
            notes: List of note dicts.

        Returns:
            List of note IDs (None for duplicates/failures).
        """
        return self.invoke("addNotes", notes=notes)

    def find_notes(self, query: str) -> list[int]:
        """Find notes matching an Anki search query.

        Args:
            query: Anki search string, e.g. 'deck:MyDeck tag:mytag'

        Returns:
            List of matching note IDs.
        """
        return self.invoke("findNotes", query=query)

    def notes_info(self, note_ids: list[int]) -> list[dict]:
        """Get detailed info for a list of note IDs.

        Returns:
            List of note info dicts.
        """
        return self.invoke("notesInfo", notes=note_ids)

    def delete_notes(self, note_ids: list[int]) -> None:
        """Delete notes by their IDs."""
        self.invoke("deleteNotes", notes=note_ids)

    def update_note_fields(self, note_id: int, fields: dict[str, str]) -> None:
        """Update the fields of an existing note.

        Args:
            note_id: The ID of the note to update.
            fields: Dict mapping field names to new values.
        """
        self.invoke("updateNoteFields", note={"id": note_id, "fields": fields})

    def update_note_tags(self, note_id: int, tags: list[str]) -> None:
        """Replace all tags on a note.

        Args:
            note_id: The note ID.
            tags: New list of tags (replaces all existing tags).
        """
        self.invoke("updateNoteTags", note=note_id, tags=" ".join(tags))

    def forget_cards(self, card_ids: list[int]) -> None:
        """Reset cards to new status, clearing review history and scheduling.

        Args:
            card_ids: List of card IDs to forget (not note IDs).
        """
        self.invoke("forgetCards", cards=card_ids)

    # ── Sync ─────────────────────────────────────────────────────────

    def sync(self) -> None:
        """Trigger an Anki sync (same as pressing the sync button)."""
        self.invoke("sync")

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def build_note(
        deck: str,
        model: str,
        fields: dict[str, str],
        tags: list[str] | None = None,
        allow_duplicate: bool = False,
    ) -> dict:
        """Build a note dict for use with add_notes().

        Args:
            deck: Target deck name.
            model: Note type name.
            fields: Field name → value mapping.
            tags: Optional tags.
            allow_duplicate: Allow duplicates within deck scope.

        Returns:
            A note dict ready for add_notes().
        """
        return {
            "deckName": deck,
            "modelName": model,
            "fields": fields,
            "tags": tags or [],
            "options": {
                "allowDuplicate": allow_duplicate,
                "duplicateScope": "deck",
            },
        }

    def get_or_create_deck(self, name: str) -> int:
        """Ensure a deck exists and return its ID."""
        return self.create_deck(name)


# ── CLI: Quick connection test ────────────────────────────────────────

if __name__ == "__main__":
    import sys

    client = AnkiConnect()
    try:
        info = client.test_connection()
        print(f"Connected to AnkiConnect v{info['version']}")
        print(f"Decks: {', '.join(client.deck_names())}")
        print(f"Models: {', '.join(client.model_names())}")
    except AnkiConnectError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
