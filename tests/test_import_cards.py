"""Unit tests for scripts/import_cards.py — mocks AnkiConnect so Anki need not be running."""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from import_cards import (
    _strip_html,
    _strip_cloze,
    _build_fields,
    find_duplicate_notes,
    check_cards,
    import_cards,
    _do_replace,
    _do_update,
)
from anki_connect import AnkiConnectError

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_note(note_id=1, front="Existing front", card_ids=None):
    return {
        "noteId": note_id,
        "fields": {"Front": {"value": front, "order": 0}},
        "cards": card_ids or [101],
        "tags": [],
    }


# ── _strip_html ───────────────────────────────────────────────────────────────

class TestStripHtml(unittest.TestCase):

    def test_removes_span_tags(self):
        self.assertEqual(_strip_html('<span style="color:red">hello</span>'), "hello")

    def test_removes_bold(self):
        self.assertEqual(_strip_html("<b>bold</b>"), "bold")

    def test_removes_br(self):
        self.assertEqual(_strip_html("line1<br>line2"), "line1line2")

    def test_plain_text_unchanged(self):
        self.assertEqual(_strip_html("no tags here"), "no tags here")

    def test_nested_tags(self):
        self.assertEqual(_strip_html("<b><span>nested</span></b>"), "nested")


# ── _strip_cloze ──────────────────────────────────────────────────────────────

class TestStripCloze(unittest.TestCase):

    def test_unwraps_single_cloze(self):
        self.assertEqual(_strip_cloze("X is {{c1::the answer}}."), "X is the answer.")

    def test_unwraps_multiple_cloze(self):
        result = _strip_cloze("{{c1::A}} and {{c2::B}}")
        self.assertEqual(result, "A and B")

    def test_no_cloze_unchanged(self):
        self.assertEqual(_strip_cloze("plain text"), "plain text")


# ── _build_fields ─────────────────────────────────────────────────────────────

class TestBuildFields(unittest.TestCase):

    def test_basic_card(self):
        card = {"type": "basic", "front": "Q?", "back": "A.", "ref": "File > Ch > Slide 1"}
        fields = _build_fields(card)
        self.assertEqual(fields, {"Front": "Q?", "Back": "A.", "Ref": "File > Ch > Slide 1"})

    def test_cloze_card(self):
        card = {"type": "cloze", "text": "X is {{c1::Y}}.", "ref": "File > Ch > Slide 2"}
        fields = _build_fields(card)
        self.assertEqual(fields, {"Text": "X is {{c1::Y}}.", "Ref": "File > Ch > Slide 2"})

    def test_missing_ref_defaults_to_empty(self):
        card = {"type": "basic", "front": "Q?", "back": "A."}
        fields = _build_fields(card)
        self.assertEqual(fields["Ref"], "")


# ── find_duplicate_notes ──────────────────────────────────────────────────────

class TestFindDuplicateNotes(unittest.TestCase):

    def test_returns_empty_when_no_match(self):
        anki = MagicMock()
        anki.find_notes.return_value = []
        card = {"type": "basic", "front": "What is X?"}
        result = find_duplicate_notes(anki, "My Deck", card)
        self.assertEqual(result, [])

    def test_returns_notes_when_match_found(self):
        note = _make_note()
        anki = MagicMock()
        anki.find_notes.return_value = [1]
        anki.notes_info.return_value = [note]
        card = {"type": "basic", "front": "What is X?"}
        result = find_duplicate_notes(anki, "My Deck", card)
        self.assertEqual(result, [note])

    def test_cloze_strips_cloze_syntax_for_search(self):
        anki = MagicMock()
        anki.find_notes.return_value = []
        card = {"type": "cloze", "text": "X is {{c1::the answer}}."}
        find_duplicate_notes(anki, "My Deck", card)
        query_arg = anki.find_notes.call_args[0][0]
        self.assertNotIn("{{c1::", query_arg)
        self.assertIn("X is the answer", query_arg)

    def test_returns_empty_on_anki_error(self):
        anki = MagicMock()
        anki.find_notes.side_effect = AnkiConnectError("timeout")
        card = {"type": "basic", "front": "Q?"}
        result = find_duplicate_notes(anki, "My Deck", card)
        self.assertEqual(result, [])

    def test_unknown_type_returns_empty(self):
        anki = MagicMock()
        card = {"type": "image_occlusion"}
        result = find_duplicate_notes(anki, "My Deck", card)
        self.assertEqual(result, [])
        anki.find_notes.assert_not_called()


# ── check_cards ───────────────────────────────────────────────────────────────

class TestCheckCards(unittest.TestCase):

    def _make_data(self, cards):
        return {"deck": "My Deck", "cards": cards}

    def test_all_new_no_duplicates(self):
        anki = MagicMock()
        anki.find_notes.return_value = []
        data = self._make_data([
            {"type": "basic", "front": "Q1?", "back": "A1"},
            {"type": "basic", "front": "Q2?", "back": "A2"},
        ])
        report = check_cards(anki, data)
        self.assertEqual(report["total"], 2)
        self.assertEqual(report["new"], 2)
        self.assertEqual(report["duplicates"], [])

    def test_one_duplicate_learned(self):
        note = _make_note(card_ids=[101])
        anki = MagicMock()
        anki.find_notes.side_effect = [[1], []]
        anki.notes_info.return_value = [note]
        anki.cards_info.return_value = [{"reviews": 5, "interval": 10, "factor": 2500, "lapses": 1}]
        data = self._make_data([
            {"type": "basic", "front": "Q1?", "back": "A1"},
            {"type": "basic", "front": "Q2?", "back": "A2"},
        ])
        report = check_cards(anki, data)
        self.assertEqual(report["total"], 2)
        self.assertEqual(report["new"], 1)
        self.assertEqual(len(report["duplicates"]), 1)
        self.assertTrue(report["duplicates"][0]["learned"])
        self.assertEqual(report["duplicates"][0]["reviews"], 5)

    def test_one_duplicate_never_reviewed(self):
        note = _make_note(card_ids=[101])
        anki = MagicMock()
        anki.find_notes.side_effect = [[1], []]
        anki.notes_info.return_value = [note]
        anki.cards_info.return_value = [{"reviews": 0, "interval": 0, "factor": 2500, "lapses": 0}]
        data = self._make_data([
            {"type": "basic", "front": "Q1?", "back": "A1"},
            {"type": "basic", "front": "Q2?", "back": "A2"},
        ])
        report = check_cards(anki, data)
        self.assertFalse(report["duplicates"][0]["learned"])


# ── import_cards ──────────────────────────────────────────────────────────────

class TestImportCards(unittest.TestCase):

    def _make_data(self, cards=None):
        return {
            "deck": "My Deck",
            "cards": cards or [
                {"type": "basic", "front": "Q?", "back": "A.", "tags": [], "ref": ""},
            ],
        }

    def test_dry_run_does_not_call_anki(self):
        anki = MagicMock()
        result = import_cards(anki, self._make_data(), dry_run=True)
        anki.add_note.assert_not_called()
        self.assertEqual(result["success"], 1)

    def test_success_increments_counter(self):
        anki = MagicMock()
        anki.add_note.return_value = 42
        result = import_cards(anki, self._make_data())
        self.assertEqual(result["success"], 1)
        self.assertEqual(result["failed"], 0)

    def test_skip_mode_on_duplicate(self):
        anki = MagicMock()
        anki.add_note.return_value = None  # duplicate
        note = _make_note()
        anki.find_notes.return_value = [1]
        anki.notes_info.return_value = [note]
        result = import_cards(anki, self._make_data(), on_duplicate="skip")
        self.assertEqual(result["skipped"], 1)
        self.assertEqual(result["success"], 0)

    def test_replace_mode_deletes_then_adds(self):
        anki = MagicMock()
        anki.add_note.side_effect = [None, 99]  # first call = duplicate, second = new note
        note = _make_note(note_id=7)
        anki.find_notes.return_value = [7]
        anki.notes_info.return_value = [note]
        result = import_cards(anki, self._make_data(), on_duplicate="replace")
        anki.delete_notes.assert_called_once_with([7])
        self.assertEqual(result["replaced"], 1)

    def test_update_mode_updates_fields_and_tags(self):
        anki = MagicMock()
        anki.add_note.return_value = None  # duplicate
        note = _make_note(note_id=5, card_ids=[201])
        anki.find_notes.return_value = [5]
        anki.notes_info.return_value = [note]
        card = {"type": "basic", "front": "Q?", "back": "New A.", "tags": ["new_tag"], "ref": ""}
        result = import_cards(anki, {"deck": "My Deck", "cards": [card]},
                              on_duplicate="update", reset_metadata=False)
        anki.update_note_fields.assert_called_once()
        anki.update_note_tags.assert_called_once_with(5, ["new_tag"])
        self.assertEqual(result["updated"], 1)

    def test_update_mode_resets_metadata_when_requested(self):
        anki = MagicMock()
        anki.add_note.return_value = None
        note = _make_note(note_id=5, card_ids=[201])
        anki.find_notes.return_value = [5]
        anki.notes_info.return_value = [note]
        card = {"type": "basic", "front": "Q?", "back": "A.", "tags": [], "ref": ""}
        import_cards(anki, {"deck": "My Deck", "cards": [card]},
                     on_duplicate="update", reset_metadata=True)
        anki.forget_cards.assert_called_once_with([201])

    def test_unknown_card_type_goes_to_failed(self):
        anki = MagicMock()
        data = {"deck": "My Deck", "cards": [
            {"type": "image_occlusion", "front": "Q?", "back": "A.", "tags": [], "ref": ""}
        ]}
        result = import_cards(anki, data)
        self.assertEqual(result["failed"], 1)
        self.assertEqual(len(result["errors"]), 1)

    def test_anki_error_goes_to_failed(self):
        anki = MagicMock()
        anki.add_note.side_effect = AnkiConnectError("network error")
        result = import_cards(anki, self._make_data())
        self.assertEqual(result["failed"], 1)

    def test_fixture_valid_cards_json_loads(self):
        fixture = os.path.join(os.path.dirname(__file__), "fixtures", "valid_cards.json")
        with open(fixture, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("deck", data)
        self.assertIn("cards", data)
        self.assertEqual(len(data["cards"]), 2)


if __name__ == "__main__":
    unittest.main()
