"""
Tests for card_guidelines compliance and the mnemonic generation module.

Covers:
- validate_card() — required fields, tag schema, cloze format, ref format
- mnemonic.py — fantasy word, sentence, HTML color coding, edge cases
- JSON examples embedded in references/card_guidelines.md are valid
"""

import json
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from mnemonic import build_mnemonic, fantasy_word, mnemonic_sentence, MNEMONIC_COLORS

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
GUIDELINES_PATH = os.path.join(os.path.dirname(__file__), "..", "references", "card_guidelines.md")

# ── Card validator (inline — no extra module needed) ──────────────────────────

REQUIRED_TAG_PREFIXES = ("subject:", "type:", "source:", "origin:")
VALID_TYPES = {"basic", "cloze"}
VALID_CARD_TYPES_TAG = {"Basic", "Cloze", "ImageOcclusion"}
REF_PATTERN = re.compile(r".+ > .+ > Slide \d+")


def validate_card(card: dict) -> list[str]:
    """Return a list of validation error strings. Empty = valid."""
    errors = []
    card_type = card.get("type", "")

    if card_type not in VALID_TYPES:
        errors.append(f"Unknown card type: '{card_type}'")

    if card_type == "basic":
        if not card.get("front"):
            errors.append("Basic card missing 'front'")
        if not card.get("back"):
            errors.append("Basic card missing 'back'")

    if card_type == "cloze":
        text = card.get("text", "")
        if not text:
            errors.append("Cloze card missing 'text'")
        elif not re.search(r"\{\{c\d+::", text):
            errors.append("Cloze card 'text' has no {{cN::}} deletion")

    tags = card.get("tags", [])
    for prefix in REQUIRED_TAG_PREFIXES:
        if not any(t.startswith(prefix) for t in tags):
            errors.append(f"Missing required tag with prefix '{prefix}'")

    type_tags = [t for t in tags if t.startswith("type:")]
    for t in type_tags:
        value = t.split(":", 1)[1]
        if value not in VALID_CARD_TYPES_TAG:
            errors.append(f"Invalid type tag value: '{value}'")

    return errors


# ── validate_card tests ───────────────────────────────────────────────────────

class TestValidateCard(unittest.TestCase):

    def _valid_basic(self, **overrides):
        card = {
            "type": "basic",
            "front": "What is X?",
            "back": "X is Y",
            "tags": [
                "subject:DB::chapter01",
                "type:Basic",
                "source:lecture.pdf",
                "origin:lecture.pdf > Ch 1 > Slide 5",
            ],
            "ref": "lecture.pdf > Ch 1 > Slide 5",
        }
        card.update(overrides)
        return card

    def _valid_cloze(self, **overrides):
        card = {
            "type": "cloze",
            "text": "X is {{c1::Y}}.",
            "tags": [
                "subject:DB::chapter01",
                "type:Cloze",
                "source:lecture.pdf",
                "origin:lecture.pdf > Ch 1 > Slide 6",
            ],
            "ref": "lecture.pdf > Ch 1 > Slide 6",
        }
        card.update(overrides)
        return card

    def test_valid_basic_card(self):
        self.assertEqual(validate_card(self._valid_basic()), [])

    def test_valid_cloze_card(self):
        self.assertEqual(validate_card(self._valid_cloze()), [])

    def test_basic_missing_front(self):
        errors = validate_card(self._valid_basic(front=""))
        self.assertTrue(any("front" in e for e in errors))

    def test_basic_missing_back(self):
        errors = validate_card(self._valid_basic(back=""))
        self.assertTrue(any("back" in e for e in errors))

    def test_cloze_missing_text(self):
        errors = validate_card(self._valid_cloze(text=""))
        self.assertTrue(any("text" in e for e in errors))

    def test_cloze_without_deletion(self):
        errors = validate_card(self._valid_cloze(text="No deletion here."))
        self.assertTrue(any("deletion" in e for e in errors))

    def test_unknown_type(self):
        card = self._valid_basic(type="image_occlusion")
        errors = validate_card(card)
        self.assertTrue(any("Unknown card type" in e for e in errors))

    def test_missing_subject_tag(self):
        card = self._valid_basic()
        card["tags"] = [t for t in card["tags"] if not t.startswith("subject:")]
        errors = validate_card(card)
        self.assertTrue(any("subject:" in e for e in errors))

    def test_missing_type_tag(self):
        card = self._valid_basic()
        card["tags"] = [t for t in card["tags"] if not t.startswith("type:")]
        errors = validate_card(card)
        self.assertTrue(any("type:" in e for e in errors))

    def test_missing_source_tag(self):
        card = self._valid_basic()
        card["tags"] = [t for t in card["tags"] if not t.startswith("source:")]
        errors = validate_card(card)
        self.assertTrue(any("source:" in e for e in errors))

    def test_missing_origin_tag(self):
        card = self._valid_basic()
        card["tags"] = [t for t in card["tags"] if not t.startswith("origin:")]
        errors = validate_card(card)
        self.assertTrue(any("origin:" in e for e in errors))

    def test_invalid_type_tag_value(self):
        card = self._valid_basic()
        card["tags"] = [t if not t.startswith("type:") else "type:Unknown" for t in card["tags"]]
        errors = validate_card(card)
        self.assertTrue(any("Invalid type tag" in e for e in errors))

    def test_fixture_valid_cards_all_pass(self):
        fixture = os.path.join(FIXTURES, "valid_cards.json")
        with open(fixture, encoding="utf-8") as f:
            data = json.load(f)
        for card in data["cards"]:
            errors = validate_card(card)
            self.assertEqual(errors, [], f"Card failed validation: {card}\nErrors: {errors}")


# ── Mnemonic: plain text helpers ──────────────────────────────────────────────

class TestMnemonicPlainText(unittest.TestCase):

    def _items(self):
        return [
            {"syllable": "Opp", "blend": "Opportunities"},
            {"syllable": "Mob", "blend": "Mobst"},
            {"syllable": "Exe", "blend": "Exentually"},
            {"syllable": "Clo", "blend": "Close"},
        ]

    def test_fantasy_word_concatenates_syllables(self):
        self.assertEqual(fantasy_word(self._items()), "OppMobExeClo")

    def test_sentence_joins_blends(self):
        self.assertEqual(mnemonic_sentence(self._items()), "Opportunities Mobst Exentually Close")

    def test_empty_items_raises(self):
        with self.assertRaises(ValueError):
            fantasy_word([])
        with self.assertRaises(ValueError):
            mnemonic_sentence([])


# ── Mnemonic: HTML output ─────────────────────────────────────────────────────

class TestBuildMnemonic(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(FIXTURES, "mnemonic_cases.json"), encoding="utf-8") as f:
            self.cases = json.load(f)

    def test_empty_items_raises_value_error(self):
        with self.assertRaises(ValueError):
            build_mnemonic([])

    def test_missing_syllable_key_raises(self):
        with self.assertRaises(KeyError):
            build_mnemonic([{"blend": "Alpha"}])

    def test_missing_blend_key_raises(self):
        with self.assertRaises(KeyError):
            build_mnemonic([{"syllable": "Al"}])

    def test_output_contains_fantasy_word_text(self):
        items = self.cases[0]["items"]
        html = build_mnemonic(items)
        self.assertIn(self.cases[0]["expected_fantasy_word"], re.sub(r"<[^>]+>", "", html))

    def test_output_contains_sentence_text(self):
        items = self.cases[0]["items"]
        html = build_mnemonic(items)
        plain = re.sub(r"<[^>]+>", "", html)
        for word in self.cases[0]["expected_sentence"].split():
            self.assertIn(word, plain)

    def test_first_position_uses_red(self):
        items = [{"syllable": "Opp", "blend": "Opportunities"}]
        html = build_mnemonic(items)
        self.assertIn(MNEMONIC_COLORS[0], html)  # #e24b4a

    def test_second_position_uses_blue(self):
        items = [
            {"syllable": "Opp", "blend": "Opp"},
            {"syllable": "Mob", "blend": "Mob"},
        ]
        html = build_mnemonic(items)
        self.assertIn(MNEMONIC_COLORS[1], html)  # #378add

    def test_all_six_palette_colors_used_for_six_items(self):
        case = next(c for c in self.cases if c["description"] == "6-item uses all palette colors")
        html = build_mnemonic(case["items"])
        for color in MNEMONIC_COLORS:
            self.assertIn(color, html, f"Expected color {color} not found in HTML")

    def test_seventh_item_wraps_to_first_color(self):
        case = next(c for c in self.cases if "7-item" in c["description"])
        html = build_mnemonic(case["items"])
        # The 7th item's syllable should use the same color as the 1st
        spans = re.findall(r'<span style="color:(#[0-9a-f]+)">([^<]+)</span>', html)
        colors_in_order = [color for color, _ in spans]
        # Position 7 wraps to position 1 → same color as position 1
        self.assertEqual(colors_in_order[6], colors_in_order[0])

    def test_fixture_cases_fantasy_word_matches(self):
        for case in self.cases:
            with self.subTest(case["description"]):
                result = fantasy_word(case["items"])
                self.assertEqual(result, case["expected_fantasy_word"])

    def test_fixture_cases_sentence_matches(self):
        for case in self.cases:
            with self.subTest(case["description"]):
                result = mnemonic_sentence(case["items"])
                self.assertEqual(result, case["expected_sentence"])

    def test_html_structure_contains_bold_and_italic(self):
        items = [{"syllable": "At", "blend": "Atomically"}]
        html = build_mnemonic(items)
        self.assertIn("<b>", html)
        self.assertIn("<i>", html)


# ── JSON examples in card_guidelines.md ──────────────────────────────────────

class TestGuidelinesJsonExamples(unittest.TestCase):

    def _extract_json_blocks(self, markdown: str) -> list[str]:
        """Extract all ```json ... ``` blocks from markdown."""
        return re.findall(r"```json\s+(.*?)```", markdown, re.DOTALL)

    def test_json_blocks_are_valid_json(self):
        with open(GUIDELINES_PATH, encoding="utf-8") as f:
            content = f.read()
        blocks = self._extract_json_blocks(content)
        self.assertGreater(len(blocks), 0, "No JSON blocks found in card_guidelines.md")
        for i, block in enumerate(blocks):
            with self.subTest(block_index=i):
                try:
                    json.loads(block)
                except json.JSONDecodeError as e:
                    self.fail(f"JSON block {i} in card_guidelines.md is invalid: {e}")

    def test_card_examples_pass_validation(self):
        with open(GUIDELINES_PATH, encoding="utf-8") as f:
            content = f.read()
        blocks = self._extract_json_blocks(content)
        for i, block in enumerate(blocks):
            try:
                data = json.loads(block)
            except json.JSONDecodeError:
                continue  # already caught above
            if "cards" not in data:
                continue
            for card in data["cards"]:
                with self.subTest(block_index=i, card_front=card.get("front", card.get("text", "?"))):
                    errors = validate_card(card)
                    self.assertEqual(errors, [], f"Card in guidelines block {i} failed: {errors}")


if __name__ == "__main__":
    unittest.main()
