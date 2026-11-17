#!/usr/bin/env python3
"""Tests for threads-board.py. Run: python3 test_threads_board.py"""
import importlib.util
import os
import tempfile
import unittest

_SPEC = importlib.util.spec_from_file_location(
    "threads_board",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "threads-board.py"),
)
tb = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(tb)


def write_tracker(text):
    f = tempfile.NamedTemporaryFile(
        "w", suffix=".md", delete=False, encoding="utf-8")
    f.write(text)
    f.close()
    return f.name


TRACKER = """# Threads

session: s214

## Epics
- e-lantern — earnings intelligence: ingest → scoring → digest — status: live
- e-onboard-v2 — partner onboarding rework — status: closed
not an entry line
- malformed entry without status

## t-lantern-ingest — Earnings-call ingestion pipeline
- status: active
- card: f-earnings-intel
- epic: e-lantern
- next: wire transcript fetcher into the queue worker
- last-touched: 2026-07-12 (s214) — fetcher scaffolded

Prose here.

## t-old-idea — Some parked idea
- status: parked
- card: none
- epic: e-onboard-v2
- last-touched: 2026-05-01 — set aside for launch

## Session log
Free space, ignored.
"""


class TestParseRegistry(unittest.TestCase):
    def setUp(self):
        self.path = write_tracker(TRACKER)
        self.addCleanup(os.unlink, self.path)
        self.threads, self.epics, self.session = tb.parse(self.path)

    def test_registry_entries_parsed(self):
        self.assertEqual(
            self.epics["e-lantern"],
            {"desc": "earnings intelligence: ingest → scoring → digest",
             "status": "live"})
        self.assertEqual(self.epics["e-onboard-v2"]["status"], "closed")
        self.assertEqual(len(self.epics), 2)  # malformed lines ignored

    def test_threads_still_parse(self):
        ids = [t["id"] for t in self.threads]
        self.assertEqual(ids, ["t-lantern-ingest", "t-old-idea"])
        self.assertEqual(self.threads[0]["epic"], "e-lantern")

    def test_no_registry_section(self):
        path = write_tracker(
            "## t-a — A\n- status: active\n- last-touched: 2026-07-12 — x\n")
        self.addCleanup(os.unlink, path)
        threads, epics, session = tb.parse(path)
        self.assertEqual(epics, {})
        self.assertEqual(len(threads), 1)
        self.assertIsNone(session)


def render_tracker(text, condensed=True):
    path = write_tracker(text)
    try:
        threads, epics, session = tb.parse(path)
        by_status = {}
        for t in threads:
            by_status.setdefault(t.get("status", "unknown"), []).append(t)
        return tb.render(by_status, epics, condensed, session=session)
    finally:
        os.unlink(path)


class TestSlugCharset(unittest.TestCase):
    def test_slug_with_a_dot_parses(self):
        # A frozen slug may carry a version ("-v2.4"); the heading pattern once rejected
        # the dot, so the thread vanished from every lane and every check (found s497).
        path = write_tracker(
            "### t-arm-dark-under-v2.4 \u2014 a versioned slug\n- status: next\n- next: do it\n"
            "- last-touched: 2026-10-06 (s497) \u2014 x\n"
        )
        try:
            threads, _epics, _session = tb.parse(path)
        finally:
            os.unlink(path)
        self.assertEqual([t["id"] for t in threads], ["t-arm-dark-under-v2.4"])


class TestEpicRollupAndValidation(unittest.TestCase):
    def test_rollup_uses_registry_desc(self):
        out = render_tracker(TRACKER)
        self.assertIn("e-lantern: earnings intelligence: ingest", out)
        self.assertIn("(1 live)", out)

    def test_rollup_without_registry_falls_back_to_slug(self):
        out = render_tracker(
            "## t-a — A\n- status: active\n- epic: e-solo\n"
            "- last-touched: 2026-07-12 — x\n")
        self.assertIn("epics: e-solo (1 live)", out)

    def test_unknown_epic_flagged_when_registry_exists(self):
        out = render_tracker(
            "## Epics\n- e-lantern — desc — status: live\n\n"
            "## t-a — A\n- status: active\n- epic: e-ghost\n"
            "- last-touched: 2026-07-12 — x\n")
        self.assertIn("not in ## Epics registry", out)
        self.assertIn("t-a(e-ghost)", out)

    def test_known_epic_not_flagged(self):
        out = render_tracker(TRACKER)
        self.assertNotIn("not in ## Epics registry", out)


class TestSessionCounter(unittest.TestCase):
    def test_parses_s_prefixed(self):
        path = write_tracker(TRACKER)
        self.addCleanup(os.unlink, path)
        _, _, session = tb.parse(path)
        self.assertEqual(session, 214)

    def test_parses_bare_number(self):
        path = write_tracker("session: 42\n\n## t-a — A\n- status: active\n")
        self.addCleanup(os.unlink, path)
        _, _, session = tb.parse(path)
        self.assertEqual(session, 42)

    def test_rendered_in_header_rule(self):
        out = render_tracker(TRACKER)
        self.assertIn("── project threads · last wrap s214 ─", out)

    def test_absent_header_unchanged(self):
        out = render_tracker(
            "## t-a — A\n- status: active\n- last-touched: 2026-07-12 — x\n")
        self.assertIn("── project threads ──", out)
        self.assertNotIn("last wrap", out)

    def test_ignored_below_first_section(self):
        # Contract: the mirror lives above any ## section; a stray
        # "session:" line in prose or a Session log must not be read.
        path = write_tracker(
            "## t-a — A\n- status: active\n\n## Session log\nsession: s999\n")
        self.addCleanup(os.unlink, path)
        _, _, session = tb.parse(path)
        self.assertIsNone(session)


class TestTriageDue(unittest.TestCase):
    def test_quiet_when_healthy(self):
        out = render_tracker(
            "## t-a — A\n- status: parked\n- last-touched: 2026-07-12 — x\n")
        self.assertNotIn("triage due", out)

    def test_missing_dates_trigger(self):
        out = render_tracker("## t-a — A\n- status: parked\n")
        self.assertIn("triage due: 1 parked/backlog, 1 missing dates", out)

    def test_count_threshold_triggers(self):
        blocks = "".join(
            f"## t-p{i} — P{i}\n- status: backlog\n- last-touched: 2026-07-12 — x\n\n"
            for i in range(16))
        out = render_tracker(blocks)
        self.assertIn("triage due: 16 parked/backlog", out)
        self.assertNotIn("missing dates", out)

    def test_closed_epic_triggers(self):
        out = render_tracker(TRACKER)  # t-old-idea is parked on closed e-onboard-v2
        self.assertIn("1 on closed epics", out)

    def test_parked_on_live_epic_triggers(self):
        out = render_tracker(
            "## Epics\n- e-go — desc — status: live\n\n"
            "## t-a — A\n- status: parked\n- epic: e-go\n"
            "- last-touched: 2026-07-12 — x\n")
        self.assertIn("1 parked on live epics", out)


if __name__ == "__main__":
    unittest.main()
