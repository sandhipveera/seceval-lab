# Vigil wrapper — confirm before publishing

Vigil (deadbits/vigil-llm) is powerful but its packaging has drifted. Two things
to confirm on your pinned version when you build:

1. **Install + config.** Pin a known-good commit (`pip install "git+https://…@<sha>"`).
   Provide `conf/server.conf` enabling the scanners you want inspected: the
   `transformer` (deberta injection model), `yara` rules, and `vectordb`
   similarity scanner. Place YARA rules + any datasets under `signatures/`.

2. **Vector DB seed.** Vigil's strongest signal is similarity to known-attack
   embeddings. The Dockerfile calls a seed step (`python -m vigil.utils.seed …`)
   whose exact module path varies by release — adjust it to your pin's documented
   seeding command (often a `vigil-server --setup`-style CLI or a loader script),
   pointed at the **bundled** signatures so no network is needed at runtime.

3. **`perform_scan()` return shape.** `app.py` parses it defensively (any non-empty
   match ⇒ flagged) so a shape change won't crash the wrapper — but confirm the
   score field (`similarity`/`distance`) matches your pin for a meaningful score.

If the vectordb scanner can't be seeded offline in time, running with just the
transformer + YARA scanners is a valid (weaker) configuration — just say so in
the write-up. Do NOT invent the catch/miss numbers; report what the run shows.
