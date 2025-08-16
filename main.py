#!/usr/bin/env python3
"""
BIP39 seed-plate helper — 24 words, two 12×12 plates.
Layout matches your photo but ROTATED so:
  rows   = word numbers (1..12 per plate)
  header = bit weights to punch (2048..1)
The skinny '*' column from the metal plate is NOT used.

Put 'bip39_en.txt' (2048 English words) next to this file.
"""

from pathlib import Path
from difflib import get_close_matches
import sys

BIP39_FILE = "./bip39_en.txt"
POWERS_DESC = [2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1]
MAX_WORDS = 24
PLATE_ROWS = 12  # 12 words per plate

def load_bip39() -> list[str]:
    p = Path(BIP39_FILE)
    if not p.exists():
        sys.exit(f"Word list file not found: {p.resolve()}")
    words = [w.strip() for w in p.read_text(encoding="utf-8").splitlines() if w.strip()]
    if len(words) != 2048:
        sys.exit(f"Unexpected word list length: {len(words)} (expected 2048).")
    return words

def one_based_index(word: str, wordlist: list[str]) -> int:
    try:
        return wordlist.index(word) + 1
    except ValueError:
        hint = get_close_matches(word, wordlist, n=3, cutoff=0.75)
        msg = f"Word '{word}' not in BIP39 list."
        if hint:
            msg += f" Did you mean: {', '.join(hint)}?"
        raise ValueError(msg)

def rows_to_punch(idx1: int) -> list[int]:
    return [p for p in POWERS_DESC if (idx1 & p) != 0]

def render_plate_rotated(block_indices: list[int], plate_no: int, start_word_no: int) -> None:
    """
    Rows = word numbers; Columns = bit weights (2048..1).
    '●' = punch, '·' = empty. The '*' column on real plate is omitted.
    """
    print(f"\n=== PLATE {plate_no} — words {start_word_no}–{start_word_no + len(block_indices) - 1} ===")

    # header row with bit weights
    header = "     " + " ".join(f"{p:>4}" for p in POWERS_DESC)
    print(header)
    print("     " + " ".join("----" for _ in POWERS_DESC))

    # each row = a word (global index on the left)
    for r, idx1 in enumerate(block_indices, start=start_word_no):
        marks = " ".join("  ● " if (idx1 & p) != 0 else "  · " for p in POWERS_DESC)
        print(f"{r:>3} |{marks}  ({idx1})")

def _self_check():
    # Verify that for every possible index 1..2048, the punched weights sum back to the index
    for i in range(1, 2049):
        s = sum(p for p in POWERS_DESC if (i & p) != 0)
        assert s == i, f"Bit-sum mismatch for {i}: got {s}"
    print("OK: bit columns sum to the 1-based index for all 1..2048.")


def main():
    wordlist = load_bip39()
    print(
        "Enter your 24 BIP-39 words one by one (English).\n"
        "- Type 'back' to remove the last word.\n"
        "- Exactly 24 words are required."
    )

    words, indices = [], []
    while len(words) < MAX_WORDS:
        raw = input(f"Word #{len(words)+1:02d}: ").strip().lower()
        if raw in ("back", "undo"):
            if words:
                w, i = words.pop(), indices.pop()
                print(f"Removed '{w}' (index {i}).")
            else:
                print("Nothing to remove.")
            continue
        if raw == "":
            print("Please enter a word (or 'back').")
            continue
        try:
            idx1 = one_based_index(raw, wordlist)
        except ValueError as e:
            print(e); continue

        words.append(raw)
        indices.append(idx1)
        print(f"  → '{raw}': index={idx1}; rows (by value)={rows_to_punch(idx1)}")

    print("\n=== SUMMARY (24 words) ===")
    for i, (w, idx1) in enumerate(zip(words, indices), start=1):
        print(f"{i:>2}. {w:<10} -> {idx1:>4}   rows: {rows_to_punch(idx1)}")

    render_plate_rotated(indices[:PLATE_ROWS], plate_no=1, start_word_no=1)
    render_plate_rotated(indices[PLATE_ROWS:], plate_no=2, start_word_no=13)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        _self_check()
        sys.exit(0)
    main()
