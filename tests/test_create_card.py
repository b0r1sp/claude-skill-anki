"""Unit tests for scripts/create_card.py — mocks AnkiConnect so Anki need not be running."""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


class TestCreateCardCLI(unittest.TestCase):

    def _run(self, argv, anki_mock=None):
        """Import and run create_card.main() with patched sys.argv and AnkiConnect."""
        import importlib
        import create_card
        importlib.reload(create_card)  # reset module state between tests

        if anki_mock is None:
            anki_mock = MagicMock()
            anki_mock.add_note.return_value = 99

        with patch("sys.argv", ["create_card.py"] + argv), \
             patch("create_card.AnkiConnect", return_value=anki_mock):
            try:
                create_card.main()
            except SystemExit as e:
                return e.code, anki_mock
        return 0, anki_mock

    # ── Basic card ────────────────────────────────────────────────────────────

    def test_basic_card_calls_add_note(self):
        anki = MagicMock()
        anki.add_note.return_value = 42
        code, anki = self._run(["--deck", "My Deck", "--front", "Q?", "--back", "A."], anki)
        anki.add_note.assert_called_once()
        positional, kwargs = anki.add_note.call_args
        deck = positional[0] if positional else kwargs.get("deck")
        fields = positional[2] if len(positional) > 2 else kwargs.get("fields")
        self.assertEqual(deck, "My Deck")
        self.assertEqual(fields["Front"], "Q?")
        self.assertEqual(fields["Back"], "A.")

    def test_basic_card_with_tags(self):
        anki = MagicMock()
        anki.add_note.return_value = 1
        self._run(["--deck", "D", "--front", "Q?", "--back", "A.", "--tags", "t1", "t2"], anki)
        tags = anki.add_note.call_args[1]["tags"]
        self.assertIn("t1", tags)
        self.assertIn("t2", tags)

    def test_basic_card_with_ref(self):
        anki = MagicMock()
        anki.add_note.return_value = 1
        self._run(["--deck", "D", "--front", "Q?", "--back", "A.", "--ref", "F > Ch > Slide 5"], anki)
        positional, kwargs = anki.add_note.call_args
        fields = positional[2] if len(positional) > 2 else kwargs.get("fields")
        self.assertEqual(fields["Ref"], "F > Ch > Slide 5")

    # ── Cloze card ────────────────────────────────────────────────────────────

    def test_cloze_card_calls_add_note(self):
        anki = MagicMock()
        anki.add_note.return_value = 10
        self._run(["--deck", "D", "--cloze", "X is {{c1::Y}}."], anki)
        positional, kwargs = anki.add_note.call_args
        fields = positional[2] if len(positional) > 2 else kwargs.get("fields")
        self.assertIn("Text", fields)
        self.assertEqual(fields["Text"], "X is {{c1::Y}}.")

    def test_cloze_without_deletion_marker_exits(self):
        code, _ = self._run(["--deck", "D", "--cloze", "no cloze here"])
        self.assertNotEqual(code, 0)

    # ── Argument errors ───────────────────────────────────────────────────────

    def test_missing_front_and_cloze_exits(self):
        code, _ = self._run(["--deck", "D", "--back", "A."])
        self.assertNotEqual(code, 0)

    def test_missing_back_exits(self):
        code, _ = self._run(["--deck", "D", "--front", "Q?"])
        self.assertNotEqual(code, 0)

    def test_missing_deck_exits(self):
        code, _ = self._run(["--front", "Q?", "--back", "A."])
        self.assertNotEqual(code, 0)

    # ── Dry run ───────────────────────────────────────────────────────────────

    def test_dry_run_does_not_call_add_note(self):
        anki = MagicMock()
        self._run(["--deck", "D", "--front", "Q?", "--back", "A.", "--dry-run"], anki)
        anki.add_note.assert_not_called()

    def test_dry_run_does_not_call_test_connection(self):
        anki = MagicMock()
        self._run(["--deck", "D", "--front", "Q?", "--back", "A.", "--dry-run"], anki)
        anki.test_connection.assert_not_called()


if __name__ == "__main__":
    unittest.main()
