"""
Mnemonic builder for Anki card creation.

Builds color-coded HTML mnemonics from a list of syllable/blend pairs,
following the card guidelines mnemonic system.

Usage:
    from mnemonic import build_mnemonic

    items = [
        {"syllable": "Opp", "blend": "Opportunities"},
        {"syllable": "Mob", "blend": "Mobst"},
        {"syllable": "Exe", "blend": "Exentually"},
        {"syllable": "Clo", "blend": "Close"},
    ]
    html = build_mnemonic(items)
"""

# Color palette — position 1-6, wraps for longer lists
MNEMONIC_COLORS = [
    "#e24b4a",  # 1 Red
    "#378add",  # 2 Blue
    "#639922",  # 3 Green
    "#ef9f27",  # 4 Amber
    "#7f77dd",  # 5 Purple
    "#1d9e75",  # 6 Teal
]


def _color(text: str, position: int) -> str:
    """Wrap text in a color span for the given 1-based position."""
    hex_color = MNEMONIC_COLORS[(position - 1) % len(MNEMONIC_COLORS)]
    return f'<span style="color:{hex_color}">{text}</span>'


def build_mnemonic(items: list[dict]) -> str:
    """Build a color-coded HTML mnemonic block.

    Args:
        items: List of dicts, each with:
            - "syllable": str — the syllable extracted from the term
            - "blend":    str — creative blended word for the sentence

    Returns:
        HTML string with fantasy word and blended sentence, both color-coded.

    Raises:
        ValueError: If items is empty.
        KeyError:   If any item is missing 'syllable' or 'blend'.
    """
    if not items:
        raise ValueError("items must not be empty")

    # Validate all items up front
    for i, item in enumerate(items):
        if "syllable" not in item:
            raise KeyError(f"Item {i} is missing 'syllable'")
        if "blend" not in item:
            raise KeyError(f"Item {i} is missing 'blend'")

    # Build fantasy word — colored syllables concatenated
    fantasy_parts = [_color(item["syllable"], i + 1) for i, item in enumerate(items)]
    fantasy_word = "".join(fantasy_parts)

    # Build blended sentence — colored blend words joined by spaces
    sentence_parts = [_color(item["blend"], i + 1) for i, item in enumerate(items)]
    sentence = " ".join(sentence_parts)

    return (
        f'Mnemonic: <b>{fantasy_word}</b>\n'
        f'— <i>"{sentence}"</i>'
    )


def fantasy_word(items: list[dict]) -> str:
    """Return the plain-text fantasy word (syllables concatenated, no HTML)."""
    if not items:
        raise ValueError("items must not be empty")
    return "".join(item["syllable"] for item in items)


def mnemonic_sentence(items: list[dict]) -> str:
    """Return the plain-text blended sentence (blends joined, no HTML)."""
    if not items:
        raise ValueError("items must not be empty")
    return " ".join(item["blend"] for item in items)
