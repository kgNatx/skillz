#!/usr/bin/env python3
"""Validate a roadmap-data.yml sidecar against the auto-roadmap contract.

The sidecar usually drives a LIVE partner-facing page that reads it off the
repo's main branch at runtime — an invalid file means a broken or silently
fallback-rendered page. The auto-roadmap skill runs this after every apply;
it is also runnable by hand from a repo root.

Usage: validate-sidecar.py [path/to/roadmap-data.yml]
Exit codes: 0 = valid (warnings allowed) · 1 = errors · 2 = can't run.

Projects whose consuming page has its own stricter schema (e.g. a zod parse)
should point $config.validate at that instead; this script is the floor, not
the ceiling.
"""
import datetime
import os
import re
import sys

try:
    import yaml
except ImportError:
    print("validate-sidecar: PyYAML not installed (pip install pyyaml), "
          "or set $config.validate to a project-provided validator")
    sys.exit(2)

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
KEBAB = re.compile(r"^[a-z0-9][a-z0-9-]*$")
# ## Epics registry contract (project-threads SKILL.md): epics are born in the
# threads file; the sidecar epics: block is a projection and must match it.
EPICS_HEADING = re.compile(r"^#{2,3}\s+Epics\s*$")
EPIC_ENTRY = re.compile(
    r"^-\s+(e-[A-Za-z0-9-]+)\s+[—–-]+\s+(.+?)\s+[—–-]+\s+status:\s*(live|closed)\s*$"
)
DEFAULT_STATUS_VOCAB = ["in-progress", "next-up", "shipped", "later", "parked"]
DEFAULT_SUB_VOCAB = ["todo", "doing", "done"]
DESC_WORD_BUDGET = 80
NOW_MAX_CHARS = 120

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def read_epics_registry(threads_path):
    """Ids in the tracker's ## Epics registry; None when the file or the
    section is absent (pre-migration projects — cross-check is skipped)."""
    try:
        lines = open(threads_path, encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        return None
    ids, in_epics, seen = set(), False, False
    for line in lines:
        if EPICS_HEADING.match(line):
            in_epics = seen = True
            continue
        if line.startswith("#"):
            in_epics = False
        if in_epics:
            m = EPIC_ENTRY.match(line.strip())
            if m:
                ids.add(m.group(1))
    return ids if seen else None


def main(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"validate-sidecar: {path} not found")
        return 2
    except yaml.YAMLError as e:
        print(f"ERROR yaml does not parse: {e}")
        return 1

    if not isinstance(data, dict):
        print("ERROR sidecar root is not a mapping")
        return 1

    config = data.get("$config") or {}
    if not isinstance(config, dict):
        err(f"$config: must be a mapping, got {config!r}")
        config = {}
    # Vocab comes from $config by design: this is the FLOOR validator. A project
    # that widens the vocab past its page's schema must use $config.validate.
    status_vocab = config.get("status_vocab", DEFAULT_STATUS_VOCAB)
    sub_vocab = config.get("sub_state_vocab", DEFAULT_SUB_VOCAB)
    id_prefix = config.get("id_prefix", "f-")

    updated = data.get("updated")
    if isinstance(updated, datetime.date):
        err("updated: quote the date — YAML parsed it as a date object, "
            "consuming schemas expect a 'YYYY-MM-DD' string")
    elif not (isinstance(updated, str) and DATE.match(updated)):
        err(f"updated: must be YYYY-MM-DD, got {updated!r}")

    streams = data.get("streams") or []
    stream_ids = set()
    for s in streams:
        if not isinstance(s, dict) or not s.get("id"):
            err(f"stream missing id: {s!r}")
            continue
        stream_ids.add(s["id"])
        for key in ("name", "short"):
            if not s.get(key):
                err(f"stream {s['id']}: missing {key}")
    if not streams:
        err("streams: must have at least one entry")

    epics = data.get("epics") or []
    epic_ids = set()
    for e in epics:
        if not isinstance(e, dict) or not isinstance(e.get("id"), str) or not e["id"]:
            err(f"epic missing string id: {e!r}")
            continue
        if not KEBAB.match(e["id"]):
            err(f"epic {e['id']}: id must be kebab-case")
        if not e["id"].startswith("e-"):
            err(f"epic {e['id']}: id must carry the e- prefix (epics are born "
                "in the threads-file ## Epics registry)")
        if e["id"] in epic_ids:
            err(f"epic {e['id']}: duplicate id")
        epic_ids.add(e["id"])
        if not e.get("title"):
            warn(f"epic {e['id']}: no title")

    if epic_ids:
        threads_rel = config.get("threads") or "project-threads.md"
        threads_path = os.path.join(os.path.dirname(os.path.abspath(path)), threads_rel)
        registry = read_epics_registry(threads_path)
        if registry is None:
            warn(f"epics: block present but {threads_rel} has no ## Epics "
                 "registry — epics are born in the tracker; add the registry")
        else:
            for eid in sorted(epic_ids):
                if eid not in registry:
                    err(f"epic {eid}: not in {threads_rel} ## Epics registry "
                        "(the registry is canonical)")

    features = data.get("features")
    if not isinstance(features, list):
        err("features: missing or not a list")
        features = []

    all_feature_ids = {f["id"] for f in features
                       if isinstance(f, dict) and isinstance(f.get("id"), str)}
    feature_ids = set()
    for f in features:
        if not isinstance(f, dict) or not isinstance(f.get("id"), str) or not f["id"]:
            err(f"feature missing string id: {str(f)[:60]!r}")
            continue
        fid = f["id"]
        if fid in feature_ids:
            err(f"{fid}: duplicate feature id")
        feature_ids.add(fid)
        if not fid.startswith(id_prefix):
            warn(f"{fid}: id does not start with {id_prefix!r}")
        for key in ("title", "stream", "status", "desc", "owner", "ship"):
            if not f.get(key):
                err(f"{fid}: missing {key}")
        if f.get("stream") and stream_ids and f["stream"] not in stream_ids:
            err(f"{fid}: unknown stream {f['stream']!r}")
        if f.get("status") and f["status"] not in status_vocab:
            err(f"{fid}: status {f['status']!r} not in {status_vocab}")
        progress = f.get("progress")
        if not (isinstance(progress, int) and not isinstance(progress, bool)
                and 0 <= progress <= 100):
            err(f"{fid}: progress must be an int 0-100, got {progress!r}")
        if f.get("status") == "shipped" and progress not in (None, 100):
            warn(f"{fid}: shipped but progress is {progress}")
        if "shippedAt" in f:
            shipped_at = f["shippedAt"]
            # The same class as the top-level `updated` check: an UNQUOTED
            # YYYY-MM-DD is parsed by YAML as a date object, and every consuming
            # schema (the partner page's zod loader included) expects a string.
            # s418 found this at gate time — one unquoted `shippedAt` broke the
            # roadmap module at import while this validator returned 0.
            if isinstance(shipped_at, datetime.date):
                err(f"{fid}: shippedAt: quote the date — YAML parsed it as a date "
                    "object, consuming schemas expect a 'YYYY-MM-DD' string")
            elif not (isinstance(shipped_at, str) and DATE.match(shipped_at)):
                err(f"{fid}: shippedAt: must be YYYY-MM-DD, got {shipped_at!r}")
        for sub in f.get("subs") or []:
            if not isinstance(sub, dict) or not sub.get("txt"):
                err(f"{fid}: malformed sub {sub!r}")
            elif sub.get("state") not in sub_vocab:
                err(f"{fid}: sub state {sub.get('state')!r} not in {sub_vocab}")
        if "epic" in f:
            if not epic_ids:
                err(f"{fid}: epic {f['epic']!r} but sidecar has no epics: block")
            elif f["epic"] not in epic_ids:
                err(f"{fid}: unknown epic {f['epic']!r}")
            if not config.get("epics"):
                warn(f"{fid}: epic: present but $config.epics is not true — "
                     "the consuming page may not render (or accept) it yet")
        if "now" in f:
            if not isinstance(f["now"], str):
                err(f"{fid}: now: must be a string, got {f['now']!r}")
            elif len(f["now"]) > NOW_MAX_CHARS:
                err(f"{fid}: now: over {NOW_MAX_CHARS} chars")
            if not config.get("now"):
                warn(f"{fid}: now: present but $config.now is not true")
        for dep in f.get("deps") or []:
            if dep not in all_feature_ids:
                warn(f"{fid}: dep {dep!r} matches no feature id")
        desc = f.get("desc")
        if isinstance(desc, str) and len(desc.split()) > DESC_WORD_BUDGET:
            warn(f"{fid}: desc over ~{DESC_WORD_BUDGET} words — accretion smell, "
                 "consider Decompose")

    milestones = data.get("milestones")
    if not isinstance(milestones, list):
        err("milestones: missing or not a list (consuming schemas require the "
            "key — use [] when empty)")
        milestones = []
    for m in milestones:
        if not isinstance(m, dict) or not m.get("group"):
            err(f"milestone missing group: {m!r}")
            continue
        for item in m.get("items") or []:
            if (not isinstance(item, dict) or not item.get("txt")
                    or item.get("state") not in sub_vocab):
                err(f"milestone {m['group']}: malformed item {item!r} "
                    "(needs txt + a valid state)")

    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"warning {w}")
    print(f"validate-sidecar: {len(errors)} error(s), {len(warnings)} warning(s) in {path}")
    return 1 if errors else 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "roadmap-data.yml"))
    except Exception as e:  # fail closed: a crash is never a pass
        print(f"ERROR validator crashed on this input — treat the sidecar as "
              f"invalid ({type(e).__name__}: {e})")
        sys.exit(1)
