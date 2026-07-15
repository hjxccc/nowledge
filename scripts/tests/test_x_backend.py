from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

SCRIPTS = os.path.dirname(os.path.dirname(__file__))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

from lib import planner  # noqa: E402
from lib.sources import x  # noqa: E402


class TwitterCliBackendTests(unittest.TestCase):
    @patch("lib.sources.x.subprocess.run")
    def test_authentication_preflight_accepts_authenticated_status(self, run: Mock) -> None:
        run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout=json.dumps({"ok": True, "data": {"authenticated": True}}),
            stderr="",
        )
        self.assertTrue(x._twitter_cli_authenticated("twitter"))

    @patch("lib.sources.x._twitter_cli_authenticated", return_value=True)
    @patch("lib.sources.x.subprocess.run")
    @patch("lib.sources.x.shutil.which", return_value="twitter")
    def test_maps_structured_search_results(
        self, _which: Mock, run: Mock, _authenticated: Mock
    ) -> None:
        run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout=json.dumps({
                "ok": True,
                "data": [{
                    "id": "123",
                    "text": "Agent Reach ships real X search",
                    "createdAt": "2026-07-15T08:30:00Z",
                    "author": {"username": "alice"},
                }],
            }),
            stderr="",
        )

        rows = x._search_twitter_cli("Agent Reach", 5)

        self.assertIsNotNone(rows)
        self.assertEqual(rows[0].author, "@alice")
        self.assertEqual(rows[0].published, "2026-07-15")
        self.assertEqual(rows[0].url, "https://x.com/alice/status/123")
        self.assertIn("--json", run.call_args.args[0])
        self.assertIn("Latest", run.call_args.args[0])

    @patch("lib.sources.x._twitter_cli_authenticated", return_value=True)
    @patch("lib.sources.x.subprocess.run")
    @patch("lib.sources.x.shutil.which", return_value="twitter")
    def test_bad_cli_output_returns_none(
        self, _which: Mock, run: Mock, _authenticated: Mock
    ) -> None:
        run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="not json", stderr=""
        )
        self.assertIsNone(x._search_twitter_cli("topic", 5))

    @patch("lib.sources.x._twitter_cli_authenticated", return_value=False)
    @patch("lib.sources.x.subprocess.run")
    @patch("lib.sources.x.shutil.which", return_value="twitter")
    def test_unauthenticated_cli_does_not_search(
        self, _which: Mock, run: Mock, _authenticated: Mock
    ) -> None:
        self.assertIsNone(x._search_twitter_cli("topic", 5))
        run.assert_not_called()

    @patch("lib.sources.x.subprocess.run")
    @patch("lib.sources.x.shutil.which", return_value=None)
    def test_missing_cli_does_not_spawn_process(self, _which: Mock, run: Mock) -> None:
        self.assertIsNone(x._search_twitter_cli("topic", 5))
        run.assert_not_called()

    @patch("lib.sources.x._search_syndication")
    @patch("lib.sources.x._search_twitter_cli", return_value=None)
    def test_public_search_falls_back(self, _cli: Mock, syndication: Mock) -> None:
        expected = [Mock()]
        syndication.return_value = expected
        self.assertIs(x.search("topic", 3), expected)
        syndication.assert_called_once_with("topic", 3)

    @patch("lib.sources.x._search_syndication")
    @patch("lib.sources.x._search_twitter_cli")
    def test_public_search_prefers_cli(self, cli: Mock, syndication: Mock) -> None:
        expected = [Mock()]
        cli.return_value = expected
        self.assertIs(x.search("topic", 3), expected)
        syndication.assert_not_called()

    @patch("lib.sources.x._write_cache")
    @patch("lib.sources.x._read_cache", return_value=[{"id": "old"}])
    def test_stale_fallback_refreshes_cooldown(self, _read: Mock, write: Mock) -> None:
        rows = x._reuse_stale("alice")
        self.assertEqual(rows, [{"id": "old"}])
        write.assert_called_once_with("alice", rows)


class PlannerTests(unittest.TestCase):
    def test_chinese_ai_topic_keeps_x_within_source_limit(self) -> None:
        sources = planner.plan("AI Agent 实战", lang="zh")
        self.assertIn("x", sources)
        self.assertLessEqual(len(sources), 4)


if __name__ == "__main__":
    unittest.main()
