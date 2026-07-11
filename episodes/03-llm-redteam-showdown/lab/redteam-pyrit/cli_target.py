#!/usr/bin/env python3
# =============================================================================
# BENIGN CANARY LAB — Custom PyRIT chat target backed by an OAuth'd vendor CLI
# -----------------------------------------------------------------------------
# HOST-RUN ONLY. This is the "adversarial chat" for the multi-turn PyRIT path.
# Instead of an API key + cloud endpoint, it subprocesses the user's already
# OAuth-signed-in vendor CLI (codex / claude / gemini) — billed to the user's
# subscription, NO API keys, NO tokens spent through PyRIT's HTTP client.
#
# The CLI invocations + JSON/JSONL output parsing MIRROR the user's proven
# transports at:
#   audit-evidence-compiler/src/aec/agent/transports/{openai,anthropic,gemini}_cli.py
# so the exact `codex exec --json --model <m> -` (stdin=prompt, parse JSONL for
# the final assistant text), `claude --print --output-format json ...`, and
# `gemini --model <m> --output-format json` behaviors are reused verbatim.
#
# BENIGN: this target just relays the attacker-model's generated prompt text to
# the CLI and returns the CLI's reply. No jailbreak strings are embedded here.
#
# VALIDATE ON FIRST RUN (PyRIT custom-target API — cannot be executed offline):
#   1. Confirm the base class is `PromptChatTarget` and that the method PyRIT
#      calls is `async def send_prompt_async(self, *, prompt_request:
#      PromptRequestResponse) -> PromptRequestResponse` (plus `_validate_request`).
#   2. Confirm `pyrit.models.construct_response_from_request(request=...,
#      response_text_pieces=[...])` exists; else the defensive builder below is used.
#   3. Confirm how the latest user text is exposed on the request piece
#      (`.converted_value` on the last request piece is used here).
# All PyRIT imports are done defensively so importing this module never crashes
# the fallback loop in run_host.py.
# =============================================================================
from __future__ import annotations

import json
import os
import shutil
import subprocess

# --- Vendor defaults (mirror the reference transports) -----------------------
DEFAULT_MODELS = {
    "codex": os.environ.get("ADVERSARIAL_CLI_MODEL", "") or "gpt-5.5",
    "claude": os.environ.get("ADVERSARIAL_CLI_MODEL", "") or "claude-sonnet-4-6",
    "gemini": os.environ.get("ADVERSARIAL_CLI_MODEL", "") or "gemini-2.5-pro",
}


# --- CLI text extraction (mirrors openai_cli.py's JSONL parsing) -------------
def _content_to_text(content) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts = []
    for item in content:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, dict):
            text = item.get("text") or item.get("content")
            if isinstance(text, str):
                parts.append(text)
    return "\n".join(parts).strip()


def _extract_text_from_event(event) -> str:
    if not isinstance(event, dict):
        return ""
    for key in ("output", "result", "message", "text"):
        value = event.get(key)
        if isinstance(value, str):
            return value
    content = _content_to_text(event.get("content"))
    if content:
        return content
    item = event.get("item")
    if isinstance(item, dict):
        for key in ("output", "result", "message", "text"):
            value = item.get(key)
            if isinstance(value, str):
                return value
        content = _content_to_text(item.get("content"))
        if content:
            return content
    return ""


def _extract_codex_text(output: str) -> str:
    """Final assistant message from Codex JSON or JSONL output (mirrors
    openai_cli._extract_codex_text)."""
    text = output.strip()
    if not text:
        return text
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None
    else:
        extracted = _extract_text_from_event(parsed)
        if extracted:
            return extracted
    messages = []
    for line in text.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        # Surface CLI-reported errors (mirrors openai_cli error handling).
        if isinstance(event, dict) and event.get("type") in ("error", "turn.failed"):
            msg = event.get("message") or (event.get("error") or {}).get("message")
            raise RuntimeError(f"codex CLI error: {msg}")
        extracted = _extract_text_from_event(event)
        if extracted:
            messages.append(extracted)
    return messages[-1] if messages else text


# --- The plain synchronous CLI driver (also used by the fallback loop) -------
def cli_complete(cli: str, model: str, system: str, user: str, timeout: int = 180) -> str:
    """Run one vendor-CLI completion and return the assistant text.

    Reuses the EXACT invocations from the reference transports:
      codex  : `codex exec --json --model <m> -`  (stdin = "system\\n---\\nuser")
      claude : `claude --print --output-format json --model <m> --system-prompt <s>`
               (stdin = user)
      gemini : `gemini --model <m> --output-format json`
               (stdin = "system\\n---\\nuser")

    `cli` is codex | claude | gemini (default codex). Raises RuntimeError on a
    non-zero exit or a CLI-reported error so callers can record a note.
    """
    cli = (cli or "codex").lower()
    model = model or DEFAULT_MODELS.get(cli, "")

    if cli == "codex":
        prompt = f"{system}\n\n---\n\n{user}" if system else user
        proc = subprocess.run(
            ["codex", "exec", "--json", "--model", model, "-"],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"codex CLI exited {proc.returncode}: "
                f"{proc.stderr.decode('utf-8', errors='replace')}"
            )
        return _extract_codex_text(proc.stdout.decode("utf-8"))

    if cli == "claude":
        proc = subprocess.run(
            [
                "claude", "--print", "--output-format", "json",
                "--model", model, "--system-prompt", system or "",
            ],
            input=user.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"claude CLI exited {proc.returncode}: "
                f"{proc.stderr.decode('utf-8', errors='replace')}"
            )
        output = proc.stdout.decode("utf-8").strip()
        try:
            parsed = json.loads(output)
            if parsed.get("is_error"):
                raise RuntimeError(
                    f"claude CLI runtime error: {parsed.get('result', 'unknown')}"
                )
            result_text = parsed.get("result", "")
            if "Not logged in" in result_text or "Please run /login" in result_text:
                raise RuntimeError(f"claude OAuth expired; run: claude /login. Said: {result_text}")
            return parsed.get("result", output)
        except json.JSONDecodeError:
            return output

    if cli == "gemini":
        prompt = f"{system}\n\n---\n\n{user}" if system else user
        proc = subprocess.run(
            ["gemini", "--model", model, "--output-format", "json"],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"gemini CLI exited {proc.returncode}: "
                f"{proc.stderr.decode('utf-8', errors='replace')}"
            )
        output = proc.stdout.decode("utf-8").strip()
        try:
            parsed = json.loads(output)
            if parsed.get("error"):
                raise RuntimeError(f"gemini CLI error: {parsed['error']}")
            return parsed.get("response", parsed.get("result", output))
        except json.JSONDecodeError:
            return output

    raise RuntimeError(f"unknown ADVERSARIAL_CLI={cli!r} (expected codex|claude|gemini)")


def cli_on_path(cli: str) -> bool:
    """True if the chosen vendor CLI binary is on PATH."""
    return shutil.which((cli or "codex").lower()) is not None


# --- PyRIT custom target (imported defensively) ------------------------------
# We import the PyRIT base class + model helpers here. If PyRIT is not installed
# (or its API drifted), importing this class raises, and run_host.py catches it
# and drops to the self-contained CLI-driver fallback loop.
try:
    from pyrit.prompt_target import PromptChatTarget  # VALIDATE: base class name

    _PYRIT_BASE = PromptChatTarget
    _PYRIT_IMPORT_ERROR = None
except Exception as _e:  # PyRIT missing / renamed -> fallback handles it
    _PYRIT_BASE = object
    _PYRIT_IMPORT_ERROR = _e


def _construct_response(request, text: str):
    """Wrap CLI text back into a PromptRequestResponse.

    Prefer PyRIT's helper; fall back to building the objects defensively if the
    helper's name/signature drifted. VALIDATE ON FIRST RUN.
    """
    # Preferred: the documented helper.
    try:
        from pyrit.models import construct_response_from_request

        return construct_response_from_request(
            request=request, response_text_pieces=[text]
        )
    except Exception:
        pass
    # Defensive fallback: build the pieces by hand.
    from pyrit.models import PromptRequestPiece, PromptRequestResponse

    piece = PromptRequestPiece(
        role="assistant",
        original_value=text,
        converted_value=text,
        conversation_id=getattr(request, "conversation_id", None),
    )
    return PromptRequestResponse(request_pieces=[piece])


class CLIChatTarget(_PYRIT_BASE):
    """A PyRIT chat target that relays prompts to an OAuth'd vendor CLI.

    Env:
      ADVERSARIAL_CLI       codex | claude | gemini   (default codex)
      ADVERSARIAL_CLI_MODEL optional model override    (default per vendor)

    Implements the abstract `_send_prompt_to_target_async(*, prompt_request)`
    (confirmed required by pyrit 0.14.0 at runtime); the base class supplies the
    public `send_prompt_async` wrapper and memory handling.
    """

    def __init__(self, cli: str | None = None, model: str | None = None):
        if _PYRIT_IMPORT_ERROR is not None:
            raise RuntimeError(f"PyRIT not importable: {_PYRIT_IMPORT_ERROR}")
        try:
            super().__init__()
        except Exception:
            # Some PyRIT base classes require kwargs; ignore and proceed — the
            # only behavior we rely on is send_prompt_async. VALIDATE ON FIRST RUN.
            pass
        self._cli = (cli or os.environ.get("ADVERSARIAL_CLI", "codex")).lower()
        self._model = model or os.environ.get("ADVERSARIAL_CLI_MODEL", "") or \
            DEFAULT_MODELS.get(self._cli, "")

    # PyRIT 0.14's PromptChatTarget marks `_send_prompt_to_target_async` as the
    # abstract method to implement; the base provides the public `send_prompt_async`
    # wrapper (memory handling) that calls this. We pull the latest user text, call
    # the CLI off the event loop so we don't block it, and wrap the reply back.
    async def _send_prompt_to_target_async(self, *, normalized_conversation):  # noqa: ANN001
        # PyRIT 0.14 (confirmed from installed source) calls this with the
        # normalized conversation (list[Message]); the LAST Message is the current
        # turn, and its first message_piece holds the text (.converted_value). We
        # relay that to the OAuth'd CLI and wrap the reply with
        # construct_response_from_request, returning a list[Message].
        import asyncio
        from pyrit.models import construct_response_from_request

        message = normalized_conversation[-1]
        request = message.message_pieces[0]
        user_text = request.converted_value

        def _run():
            return cli_complete(self._cli, self._model, system="", user=user_text)

        reply_text = await asyncio.to_thread(_run)
        response_entry = construct_response_from_request(
            request=request, response_text_pieces=[reply_text]
        )
        return [response_entry]

    def _validate_request(self, *, normalized_conversation) -> None:  # noqa: ANN001
        # Matches the PyRIT 0.14 abstract signature. Permissive: just ensure the
        # conversation isn't empty (the base already checks piece structure).
        if not normalized_conversation:
            raise ValueError("CLIChatTarget: empty normalized_conversation")

    def is_json_response_supported(self) -> bool:
        # Some PyRIT versions call this on chat targets; be conservative.
        return False
