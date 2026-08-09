#!/usr/bin/env python3
"""Obfuscation encoder for attack a5. Same codec as stub-model/app.py's decode side and
doc-server/app.py's obfuscated-doc variant (duplicated per build-context isolation -- see the
cross-reference note in stub-model/app.py). Wraps an instruction in a base64 block plus a
zero-width-space-threaded homoglyph copy, both of which stub-model's model_normalize() reverses.
"""
import base64

_TO_HOMOGLYPH = {
    "a": "а", "e": "е", "o": "о", "p": "р", "c": "с",
    "x": "х", "y": "у", "i": "і", "s": "ѕ",
}
_ZWSP = "​"


def _homoglyph_smuggle(instruction: str) -> str:
    out = []
    for ch in instruction:
        out.append(_TO_HOMOGLYPH.get(ch.lower(), ch) if ch.isalpha() else ch)
        out.append(_ZWSP)
    return "".join(out)


def base64_homoglyph(instruction: str) -> str:
    """Innocuous-looking cover text + a base64 blob + a zero-width/homoglyph-smuggled copy. A
    naive gateway pattern-matcher sees only the cover text and a blob of noise; stub-model
    reconstructs the instruction from either encoding."""
    b64 = base64.b64encode(instruction.encode("utf-8")).decode("ascii")
    smuggled = _homoglyph_smuggle(instruction)
    cover = "Quick question, ref code: "
    return f"{cover}{b64} \U0001F600{smuggled}"


ENCODERS = {"base64_homoglyph": base64_homoglyph}
