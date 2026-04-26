"""Unit tests for scripts/anki_connect.py — mocks urllib so Anki need not be running."""

import json
import sys
import os
import unittest
from io import BytesIO
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from anki_connect import AnkiConnect, AnkiConnectError


def _mock_response(result=None, error=None, status=200):
    """Return a mock HTTP response with the given AnkiConnect payload."""
    payload = {"result": result, "error": error}
    body = json.dumps(payload).encode("utf-8")
    mock_resp = MagicMock()
    mock_resp.read.return_value = body
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


class TestInvoke(unittest.TestCase):

    @patch("urllib.request.urlopen")
    def test_returns_result_on_success(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(result=["Default", "My Deck"])
        anki = AnkiConnect()
        result = anki.invoke("deckNames")
        self.assertEqual(result, ["Default", "My Deck"])

    @patch("urllib.request.urlopen")
    def test_raises_on_anki_error(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(error="deck not found")
        anki = AnkiConnect()
        with self.assertRaises(AnkiConnectError) as ctx:
            anki.invoke("deckNames")
        self.assertIn("deck not found", str(ctx.exception))

    @patch("urllib.request.urlopen")
    def test_raises_on_connection_failure(self, mock_urlopen):
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("connection refused")
        anki = AnkiConnect()
        with self.assertRaises(AnkiConnectError) as ctx:
            anki.invoke("deckNames")
        self.assertIn("AnkiConnect", str(ctx.exception))

    @patch("urllib.request.urlopen")
    def test_raises_on_invalid_json(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"not json {"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp
        anki = AnkiConnect()
        with self.assertRaises(AnkiConnectError) as ctx:
            anki.invoke("deckNames")
        self.assertIn("Invalid JSON", str(ctx.exception))

    @patch("urllib.request.urlopen")
    def test_test_connection_returns_version(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(result=6)
        anki = AnkiConnect()
        info = anki.test_connection()
        self.assertTrue(info["connected"])
        self.assertEqual(info["version"], 6)

    @patch("urllib.request.urlopen")
    def test_params_are_sent_in_payload(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(result=None)
        anki = AnkiConnect()
        anki.invoke("createDeck", deck="My Deck")
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["action"], "createDeck")
        self.assertEqual(payload["params"]["deck"], "My Deck")
        self.assertEqual(payload["version"], 6)
