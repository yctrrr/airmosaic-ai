"""Review explicitly selected sanitized task records, without source execution."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import stat
import sys

MAX_BYTES = 262144
MAX_FILES = 16
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
BLOCKED = {".git", ".ssh", ".aws", ".azure", ".env", ".config", ".codex", ".agents", "auth", "authentication",
           "credentials", "credential", "config", "configuration", "cookies", "profiles",
           "browser-state", "secrets", "history", "histories", "screenpipe", "screenshots"}
BLOCKED.update({"token", "tokens", "password", "passwords", "api-key", "api_key", "apikey",
                "session", "sessions", "browser", "screen-capture", "screen-captures", "private",
                "plan", "plans", "harness", "id_rsa", "id_ed25519", "id_ecdsa",
                "known_hosts", "authorized_keys"})
SENSITIVE = re.compile(
    r"(?i)(?:\b[a-z][a-z0-9+.-]*://|www\.|[a-z]:[\\/]|\\\\|(?<![\w])/[a-z][\w.-]*(?:/|\b)|"
    r"[\w.+-]+@[\w.-]+\.[a-z]{2,}|-----BEGIN |\b(?:sk|ghp|github_pat)[-_][\w-]+|\bAKIA[A-Z0-9]{16}\b|"
    r"\b(?:password|passwd|api[_ -]?key|(?:access[_ -]?|refresh[_ -]?|auth[_ -]?)?token|secret|cookie|authorization)[\"']?\s*[:=]|"
    r"\bbearer\s+\S+)"
)


class Refusal(Exception):
    """Only fixed public codes belong in messages."""


def fail(code: str) -> None:
    raise Refusal(code)


def is_link(path: Path) -> bool:
    for node in (path, *path.parents):
        if node.is_symlink():
            return True
        if node.exists() and getattr(node.lstat(), "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 1024):
            return True
    return False


def outside_git(path: Path) -> Path:
    if not path.is_absolute() or not path.is_dir() or is_link(path):
        fail("unsafe-root")
    path = path.resolve()
    if any((node / ".git").exists() for node in (path, *path.parents)):
        fail("git-root-refused")
    return path


def inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def read_selected(relative: str, root: Path) -> tuple[bytes, str]:
    # Explicit relative file names only. Reject links before resolve/read.
    if not isinstance(relative, str) or "\\" in relative or ":" in relative:
        fail("unsafe-input-path")
    parts = Path(relative).parts
    if not parts or Path(relative).is_absolute() or any(p in {"..", "."} or p.lower() in BLOCKED or Path(p).stem.lower() in BLOCKED or p.startswith(".") for p in parts):
        fail("unsafe-input-path")
    path = root / relative
    if is_link(path) or not path.is_file() or not inside(path.resolve(), root):
        fail("unsafe-input-file")
    if any((node / ".git").exists() for node in path.parents if inside(node, root)):
        fail("nested-git-refused")
    if path.suffix.lower() not in {".json", ".md", ".txt"} or path.stat().st_nlink != 1:
        fail("unsupported-input-file")
    if path.stat().st_size > MAX_BYTES:
        fail("input-size-limit")
    payload = path.read_bytes()
    if len(payload) > MAX_BYTES:
        fail("input-size-limit")
    try:
        text = payload.decode("utf-8")
    except UnicodeError:
        fail("input-encoding")
    return payload, text


def parse_json(text: str) -> object:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                fail("duplicate-json-field")
            result[key] = value
        return result
    try:
        return json.loads(text, object_pairs_hook=unique,
                          parse_constant=lambda _: fail("invalid-json-number"))
    except (ValueError, RecursionError):
        fail("invalid-json")


def public_text(value: object, limit: int = 2048) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        fail("invalid-public-text")
    if SENSITIVE.search(value) or any(ord(c) < 32 and c not in "\n\t" for c in value):
        fail("sensitive-proposal-or-catalog")
    return value


def load_catalog(text: str) -> list[dict]:
    data = parse_json(text)
    if not isinstance(data, dict) or set(data) != {"skills"} or not isinstance(data["skills"], list) or len(data["skills"]) > 200:
        fail("invalid-catalog")
    skills = []
    for item in data["skills"]:
        if not isinstance(item, dict) or set(item) != {"name", "description"}:
            fail("invalid-catalog")
        name, description = public_text(item["name"], 63), public_text(item["description"], 1024)
        if not NAME.fullmatch(name) or any(s["name"] == name for s in skills):
            fail("invalid-catalog-name")
        skills.append({"name": name, "description": description})
    return skills


def records(text: str, suffix: str, catalog: list[dict], ordinal: int) -> list[dict]:
    """Only retain controlled names/statuses and generated record ordinals."""
    if suffix != ".json":
        # Reviewed prose is evidence of lexical mentions only, never observed success.
        entries = [{"status": "reported", "outcome": "unknown", "summary": text}]
    else:
        data = parse_json(text)
        if not isinstance(data, dict) or set(data) != {"schema_version", "records"} or type(data["schema_version"]) is not int or data["schema_version"] != 1:
            fail("invalid-record-schema")
        entries = data["records"]
    if not isinstance(entries, list) or len(entries) > 100:
        fail("record-count-limit")
    output = []
    names = {s["name"] for s in catalog}
    for index, entry in enumerate(entries, 1):
        if not isinstance(entry, dict) or set(entry) - {"id", "status", "outcome", "summary", "skills"}:
            fail("invalid-record")
        status, outcome = entry.get("status"), entry.get("outcome")
        if status not in {"observed", "reported", "stale"} or outcome not in {"success", "failure", "unknown"}:
            fail("invalid-record-state")
        summary = entry.get("summary", "")
        selected = entry.get("skills", [])
        if not isinstance(summary, str) or len(summary) > 16000 or not isinstance(selected, list) or any(not isinstance(n, str) or n not in names for n in selected):
            fail("invalid-record-content")
        evidence = []
        for skill in catalog:
            name = skill["name"]
            # No arbitrary input tokens are emitted; only controlled public metadata.
            terms = sorted(set(re.findall(r"[a-z][a-z0-9-]{3,}", skill["description"].lower())))
            matches = [term for term in terms if re.search(r"(?<![\w-])" + re.escape(term) + r"(?![\w-])", summary.lower())]
            exact = bool(re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", summary.lower()))
            if name in selected or exact or matches:
                evidence.append({"skill": name, "explicit_record_name": name in selected,
                                 "exact_name_mention": exact, "description_terms": matches})
        output.append({"evidence_id": f"input-{ordinal}-record-{index}", "status": status,
                       "outcome": outcome, "matches": evidence,
                       "sensitive_content_omitted": bool(SENSITIVE.search(summary))})
    return output


def route(evidence: list[dict]) -> dict:
    current = [e for e in evidence if e["status"] == "observed"]
    matched = sorted({m["skill"] for e in current for m in e["matches"] if m["explicit_record_name"] or m["exact_name_mention"]})
    decision = "novel" if not matched else "compose" if len(matched) > 1 else "revise" if any(e["outcome"] == "failure" for e in current) else "reuse"
    return {"suggested_route": decision, "skill_names": matched,
            "basis": "observed-record-explicit-or-exact-name-only",
            "unverified_claims": sum(e["status"] != "observed" for e in evidence),
            "scientific_acceptance": False, "requires_agent_review": True}


def proposal(text: str, evidence: list[dict], catalog: list[dict]) -> dict:
    data = parse_json(text)
    allowed = {"schema_version", "sanitized", "authorship", "route", "skill_names", "evidence_ids", "draft"}
    if not isinstance(data, dict) or set(data) - allowed or type(data.get("schema_version")) is not int or data.get("schema_version") != 1 or data.get("sanitized") is not True or data.get("authorship") not in {"current-agent", "supplied-reviewed"}:
        fail("invalid-proposal")
    if data.get("route") not in {"reuse", "revise", "compose", "novel"}:
        fail("invalid-proposal-route")
    skills, ids = data.get("skill_names"), data.get("evidence_ids")
    if not isinstance(skills, list) or any(not isinstance(n, str) or n not in {s["name"] for s in catalog} for n in skills):
        fail("invalid-proposal-skills")
    if not isinstance(ids, list) or not ids or any(not isinstance(i, str) or i not in {e["evidence_id"] for e in evidence} for i in ids):
        fail("invalid-proposal-evidence")
    draft = data.get("draft")
    if draft is not None:
        fields = {"name", "description", "description_zh", "version", "compatibility", "instructions", "instructions_zh"}
        if not isinstance(draft, dict) or set(draft) != fields:
            fail("invalid-draft")
        for key in fields:
            public_text(draft[key], 12000 if key.startswith("instructions") else 1024)
        if not NAME.fullmatch(draft["name"]) or len(draft["name"]) > 63 or not re.fullmatch(r"\d+\.\d+\.\d+", draft["version"]):
            fail("invalid-draft-metadata")
        if any("\n" in draft[k] for k in fields - {"instructions", "instructions_zh"}):
            fail("invalid-draft-metadata")
        # Draft prose only: no data tables, fenced code, images or external resources.
        if any(re.search(r"```|~~~|\|.*\||!\[|\]\(", draft[k]) for k in ("instructions", "instructions_zh")):
            fail("draft-resource-review-required")
    return data


def run(args) -> dict:
    task, assets, config, auth = [outside_git(Path(p)) for p in (args.task_root, args.assets_root, args.config_root, args.auth_root)]
    if any(part.lower() in BLOCKED or Path(part).stem.lower() in BLOCKED for part in task.parts):
        fail("sensitive-task-root")
    roots = [assets, config, auth]
    if any(inside(a, b) or inside(b, a) for i, a in enumerate(roots) for b in roots[i + 1:]):
        fail("storage-roots-overlap")
    if inside(task, config) or inside(task, auth) or inside(config, task) or inside(auth, task):
        fail("task-config-auth-overlap")
    if not NAME.fullmatch(args.task_id) or len(args.task_id) > 50:
        fail("invalid-task-id")
    if not 1 <= len(args.input) <= MAX_FILES or len(set(args.input)) != len(args.input):
        fail("input-count-or-duplicate")
    _, catalog_text = read_selected(args.catalog, task)
    catalog = load_catalog(catalog_text)
    evidence, sources = [], []
    for ordinal, selected in enumerate(args.input, 1):
        payload, text = read_selected(selected, task)
        evidence.extend(records(text, Path(selected).suffix.lower(), catalog, ordinal))
        sources.append({"input_ordinal": ordinal, "sha256": hashlib.sha256(payload).hexdigest()})
    reviewed = proposal(read_selected(args.proposal, task)[1], evidence, catalog) if args.proposal else None
    result = {"schema_version": 1, "sources": sources, "evidence": evidence, "routing": route(evidence),
              "proposal": reviewed, "source_execution": False, "repository_writes": False,
              "promotion": "manual-review-only", "matching": "controlled-public-name-and-description-lexical-evidence"}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%MZ")
    parent = assets / "results" / "skill_maintenance"
    # Revalidate existing descendants; mkdir never follows a linked result directory.
    for path in (assets / "results", parent):
        if is_link(path) or (path.exists() and not path.is_dir()) or (path / ".git").exists():
            fail("unsafe-output-parent")
        path.mkdir(exist_ok=True)
    destination = parent / f"{stamp}_{args.task_id}"
    if destination.exists() or is_link(destination):
        fail("output-collision")
    destination.mkdir()  # Exclusive; concurrent attempts cannot overwrite.
    (destination / "review.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if reviewed and reviewed.get("draft"):
        draft = reviewed["draft"]
        folder = destination / "draft" / draft["name"]
        folder.mkdir(parents=True)
        for filename, desc_key, body_key, selector in (
            ("SKILL.md", "description", "instructions", "**English** | [中文](SKILL_ZH.md)"),
            ("SKILL_ZH.md", "description_zh", "instructions_zh", "[English](SKILL.md) | **中文**"),
        ):
            header = "---\n" + "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in
                      (("name", draft["name"]), ("description", draft[desc_key]), ("compatibility", draft["compatibility"])))
            header += f'\nmetadata:\n  version: "{draft["version"]}"\n---\n\n'
            (folder / filename).write_text(header + "<!-- README-I18N:START -->\n\n" + selector + "\n\n<!-- README-I18N:END -->\n\n" + draft[body_key] + "\n", encoding="utf-8")
    # Paths and source content never appear on stdout.
    return {"status": "review-written", "route": result["routing"]["suggested_route"], "draft_written": bool(reviewed and reviewed.get("draft"))}


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, '{"status":"refused","code":"invalid-arguments"}\n')


def main(argv=None) -> int:
    parser = SafeParser(description=__doc__, allow_abbrev=False)
    for field in ("task-root", "assets-root", "config-root", "auth-root", "catalog", "task-id"):
        parser.add_argument("--" + field, required=True)
    parser.add_argument("--input", action="append", required=True)
    parser.add_argument("--proposal")
    args = parser.parse_args(argv)
    try:
        result = run(args)
        code = 0
    except Refusal as exc:
        result, code = {"status": "refused", "code": str(exc)}, 2
    except (OSError, ValueError, TypeError, RecursionError, RuntimeError):
        result, code = {"status": "refused", "code": "maintenance-failed"}, 2
    print(json.dumps(result))
    return code


if __name__ == "__main__":
    sys.exit(main())
