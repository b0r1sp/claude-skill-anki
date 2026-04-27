# Shared: Card Preview Format

Render each card in ASCII style before asking for approval.
Strip all HTML tags and color spans — show plain text only.

```
┌─ Card 01 · Basic ──────────────────────────────────────┐
│ FRONT                                                   │
│ What is Atomicity in ACID?                              │
├─────────────────────────────────────────────────────────┤
│ BACK                                                    │
│ A transaction is all-or-nothing — completes fully       │
│ or not at all.                                          │
├─────────────────────────────────────────────────────────┤
│ Tags: subject:DB::chapter01 · type:Basic                │
│ Ref:  lecture.pdf > Chapter 1 > Slide 5                 │
└─────────────────────────────────────────────────────────┘
```

After all cards are shown:
```
── Start import? [y] yes · [n] no ──
```

## HTML stripping rules

- Remove all `<span ...>...</span>` wrapper tags (keep inner text)
- Remove `<b>`, `<i>`, `<br>`, `<ul>`, `<li>` tags
- Replace `<br>` with a newline in the rendered output
- Do **not** include raw HTML or hex color codes in the preview
