#!/usr/bin/env python3
"""Read-only posture checks (Round 2b / Axis 2). NOTHING here sends a payload -- see the hard
safety constraint in CLAUDE_CODE_BUILD.md. P1 is a bare GET with no credentials. P2 is a version
string comparison. P3 is a text scan of docker-compose.yml for `@sha256:` digest pins. No exploit
code, no SQLi strings, no CVE proof-of-concept of any kind lives in this file or anywhere in this
repo.
"""
import re

import requests

# Patched-range knowledge for the 2026 advisories referenced in POST.md. Only LiteLLM has a
# publicly documented CVE range in this lab's scope; Portkey and Bifrost get an honest "no
# advisory range tracked here" rather than a fabricated one.
PATCHED_RANGES = {
    "litellm": {"min_patched": "1.83.7-stable", "advisory": "CVE-2026-42208 (pre-auth SQLi), "
                "CVE-2026-42203 (SSTI), CVE-2026-42271 (command injection)"},
}


def _version_ge(v: str, floor: str) -> bool:
    """Best-effort dotted-version comparison, tolerant of a trailing '-stable' suffix. Not a full
    semver/PEP 440 implementation -- good enough for this lab's fixed pinned strings."""
    def parts(s):
        s = s.split("-", 1)[0]
        return [int(x) for x in re.findall(r"\d+", s)]
    return parts(v) >= parts(floor)


def check_p1_admin_reachability(admin_url: str) -> dict:
    if not admin_url:
        return {"check": "P1_admin_unauth_reachability", "result": "not-configured",
                "evidence": "GATEWAY_ADMIN_URL not set (baseline run, no gateway)"}
    try:
        r = requests.get(admin_url, timeout=10)
        has_data = bool((r.text or "").strip())
        result = "reachable-unauthenticated" if r.status_code // 100 == 2 else "protected-or-error"
        return {"check": "P1_admin_unauth_reachability", "result": result,
                "evidence": f"GET {admin_url} -> HTTP {r.status_code}, "
                            f"body_bytes={len(r.content)}, returned_data={has_data}"}
    except Exception as e:
        return {"check": "P1_admin_unauth_reachability", "result": "unreachable",
                "evidence": f"GET {admin_url} -> transport error: {e}"}


def check_p2_version_range(gateway: str, version: str) -> dict:
    if gateway not in PATCHED_RANGES or not version:
        return {"check": "P2_version_in_patched_range", "result": "no-advisory-tracked",
                "evidence": f"version={version or 'unknown'}; this lab tracks no CVE range for "
                            f"'{gateway}' -- recorded honestly rather than assumed safe"}
    floor = PATCHED_RANGES[gateway]["min_patched"]
    try:
        ok = _version_ge(version, floor)
    except Exception:
        return {"check": "P2_version_in_patched_range", "result": "unparseable",
                "evidence": f"could not compare version={version!r} to floor={floor!r}"}
    return {"check": "P2_version_in_patched_range",
            "result": "in-patched-range" if ok else "BELOW-PATCHED-RANGE",
            "evidence": f"version={version}, min_patched={floor}, "
                        f"advisory={PATCHED_RANGES[gateway]['advisory']}"}


def check_p3_digest_pinning(compose_path: str) -> dict:
    try:
        text = open(compose_path).read()
    except Exception as e:
        return {"check": "P3_digest_pinning", "result": "error",
                "evidence": f"could not read {compose_path}: {e}"}

    image_lines = [l.strip() for l in text.splitlines() if re.match(r"^\s*image:\s*\S+", l)]
    build_lines = [l.strip() for l in text.splitlines() if re.match(r"^\s*build:\s*\S+", l)]
    pinned = [l for l in image_lines if "@sha256:" in l]
    unpinned = [l for l in image_lines if "@sha256:" not in l]

    evidence = (
        f"image: entries={len(image_lines)} (pinned_by_digest={len(pinned)}, "
        f"floating_tag={len(unpinned)}: {unpinned}); "
        f"build: contexts={len(build_lines)} (base-image pinning lives in each Dockerfile's FROM "
        f"line, not visible to this check since only docker-compose.yml is mounted into the "
        f"runner -- verify gateways/*/Dockerfile and stub-model/Dockerfile etc. directly)"
    )
    result = "fully-pinned" if image_lines and not unpinned else "NOT-fully-pinned"
    return {"check": "P3_digest_pinning", "result": result, "evidence": evidence}
