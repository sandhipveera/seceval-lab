// =============================================================================
// BENIGN CANARY LAB — Promptfoo custom provider backed by an OAuth'd vendor CLI.
// HOST-RUN ONLY. This is the GENERATION/attacker model for Promptfoo's red-team
// synthesis + iterative strategies (jailbreak, jailbreak:composite). Instead of
// an API key + cloud endpoint, it subprocesses the user's already OAuth-signed-in
// vendor CLI (codex / claude / gemini) — billed to the subscription, NO API keys.
//
// It mirrors the proven invocations + JSONL parsing in redteam-pyrit/cli_target.py
// (and the reference transports) so behavior matches the PyRIT path exactly:
//   codex  : `codex exec --json --model <m> -`   (stdin = prompt; parse JSONL)
//   claude : `claude --print --output-format json --model <m> --system-prompt ""`
//   gemini : `gemini --model <m> --output-format json`  (stdin = prompt)
//
// Env:
//   ADVERSARIAL_CLI        codex | claude | gemini   (default codex)
//   ADVERSARIAL_CLI_MODEL  optional model override
// =============================================================================
'use strict';
const { execFileSync } = require('child_process');

const DEFAULT_MODELS = { codex: 'gpt-5.5', claude: 'claude-sonnet-4-6', gemini: 'gemini-2.5-pro' };

function contentToText(content) {
  if (typeof content === 'string') return content;
  if (!Array.isArray(content)) return '';
  const parts = [];
  for (const item of content) {
    if (typeof item === 'string') parts.push(item);
    else if (item && typeof item === 'object') {
      const t = item.text || item.content;
      if (typeof t === 'string') parts.push(t);
    }
  }
  return parts.join('\n').trim();
}

function extractFromEvent(ev) {
  if (!ev || typeof ev !== 'object') return '';
  for (const k of ['output', 'result', 'message', 'text']) {
    if (typeof ev[k] === 'string') return ev[k];
  }
  const c = contentToText(ev.content);
  if (c) return c;
  if (ev.item && typeof ev.item === 'object') {
    for (const k of ['output', 'result', 'message', 'text']) {
      if (typeof ev.item[k] === 'string') return ev.item[k];
    }
    const ic = contentToText(ev.item.content);
    if (ic) return ic;
  }
  return '';
}

// Final assistant message from Codex JSON or JSONL output (mirrors cli_target._extract_codex_text).
function extractCodexText(output) {
  const text = (output || '').trim();
  if (!text) return text;
  try {
    const parsed = JSON.parse(text);
    const ex = extractFromEvent(parsed);
    if (ex) return ex;
  } catch (_) { /* fall through to JSONL */ }
  const messages = [];
  for (const line of text.split('\n')) {
    const s = line.trim();
    if (!s) continue;
    let ev;
    try { ev = JSON.parse(s); } catch (_) { continue; }
    if (ev && (ev.type === 'error' || ev.type === 'turn.failed')) {
      const msg = ev.message || (ev.error && ev.error.message);
      throw new Error(`codex CLI error: ${msg}`);
    }
    const ex = extractFromEvent(ev);
    if (ex) messages.push(ex);
  }
  return messages.length ? messages[messages.length - 1] : text;
}

function cliComplete(cli, model, prompt, timeoutMs) {
  cli = (cli || 'codex').toLowerCase();
  model = model || DEFAULT_MODELS[cli] || '';
  const opts = { input: prompt, encoding: 'utf8', timeout: timeoutMs, maxBuffer: 16 * 1024 * 1024 };
  if (cli === 'codex') {
    const out = execFileSync('codex', ['exec', '--json', '--model', model, '-'], opts);
    return extractCodexText(out);
  }
  if (cli === 'claude') {
    const out = execFileSync('claude', ['--print', '--output-format', 'json', '--model', model, '--system-prompt', ''], opts);
    try {
      const parsed = JSON.parse(out.trim());
      if (parsed.is_error) throw new Error(`claude CLI error: ${parsed.result || 'unknown'}`);
      return parsed.result || out;
    } catch (_) { return out.trim(); }
  }
  if (cli === 'gemini') {
    const out = execFileSync('gemini', ['--model', model, '--output-format', 'json'], opts);
    try {
      const parsed = JSON.parse(out.trim());
      if (parsed.error) throw new Error(`gemini CLI error: ${JSON.stringify(parsed.error)}`);
      return parsed.response || parsed.result || out;
    } catch (_) { return out.trim(); }
  }
  throw new Error(`unknown ADVERSARIAL_CLI=${cli} (expected codex|claude|gemini)`);
}

class CliProvider {
  constructor(options) {
    this.providerId = (options && options.id) || 'cli-oauth';
    this.cli = process.env.ADVERSARIAL_CLI || 'codex';
    this.model = process.env.ADVERSARIAL_CLI_MODEL || '';
  }
  id() { return this.providerId; }
  async callApi(prompt /*, context */) {
    try {
      const text = cliComplete(this.cli, this.model, String(prompt || ''), 180000);
      return { output: text };
    } catch (e) {
      return { error: String((e && e.message) || e) };
    }
  }
}

module.exports = CliProvider;
