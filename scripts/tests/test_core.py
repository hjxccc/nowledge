from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = os.path.dirname(os.path.dirname(__file__))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

from gate import check_sources  # noqa: E402
import ground  # noqa: E402
from lib.cluster import mmr_pick  # noqa: E402
from lib.common import Candidate  # noqa: E402
from lib.fusion import per_source_cap, weighted_rrf  # noqa: E402
from lib.planner import classify, plan  # noqa: E402


def candidate(source: str, title: str, url: str, score: float = 0.0) -> Candidate:
    item = Candidate(source=source, title=title, url=url)
    item.final_score = score
    return item


class PlannerTests(unittest.TestCase):
    def test_chinese_research_topic_keeps_arxiv(self) -> None:
        topic = "注意力机制 蒸馏算法"
        self.assertEqual(classify(topic), "ai-research")
        sources = plan(topic, lang="zh")
        self.assertIn("arxiv", sources)
        self.assertLessEqual(len(sources), 4)


class RankingTests(unittest.TestCase):
    def test_mmr_compares_quality_and_diversity_on_same_scale(self) -> None:
        high = candidate("a", "high", "https://example.com/high", 0.0200)
        near = candidate("b", "near", "https://example.com/near", 0.0190)
        low = candidate("c", "low", "https://example.com/low", 0.0001)
        high.entities, near.entities, low.entities = {"ai", "agent"}, {"ai"}, {"other"}

        picked = mmr_pick([high, near, low], k=2)

        self.assertEqual([item.title for item in picked], ["high", "near"])

    def test_rrf_fuses_tracking_url_variants(self) -> None:
        a = candidate("a", "same", "https://example.com/post?utm_source=x")
        b = candidate("b", "same", "https://example.com/post")
        fused = weighted_rrf({"a": [a], "b": [b]})
        self.assertEqual(len(fused), 1)
        self.assertGreater(fused[0].rrf_score, 1 / 61)

    def test_per_source_cap_prevents_quick_mode_monopoly(self) -> None:
        rows = [candidate("context7", str(i), f"https://docs.example/{i}") for i in range(5)]
        rows += [candidate("hackernews", "community", "https://news.example/1")]
        balanced = per_source_cap(rows, cap=3)
        self.assertEqual(sum(x.source == "context7" for x in balanced), 3)
        self.assertIn("hackernews", {x.source for x in balanced})

    def test_quick_run_balances_two_live_sources(self) -> None:
        class Adapter:
            def __init__(self, source: str, count: int) -> None:
                self.source, self.count = source, count

            def search(self, _topic: str, _limit: int) -> list[Candidate]:
                return [
                    Candidate(
                        source=self.source,
                        title=f"{self.source}-{i}",
                        url=f"https://{self.source}.example/{i}",
                    )
                    for i in range(self.count)
                ]

        adapters = {"docs": Adapter("docs", 5), "community": Adapter("community", 1)}
        with patch.dict(ground.ADAPTERS, adapters, clear=True):
            rows = ground.run(
                "topic", ["docs", "community"], per_source=5, reps=6,
                quick=True, backfill=False,
            )

        self.assertEqual(sum(x["source"] == "docs" for x in rows), 3)
        self.assertIn("community", {x["source"] for x in rows})


class GateTests(unittest.TestCase):
    def test_sources_require_raw_material_guardrail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sources = os.path.join(tmp, "sources")
            os.makedirs(sources)
            with open(os.path.join(sources, "raw.md"), "w", encoding="utf-8") as f:
                f.write("role: principle\nA useful source")
            self.assertFalse(check_sources(tmp)[0][0])


class ReviewCliTests(unittest.TestCase):
    def run_review(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "review.py"), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_add_rejects_empty_question(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_review("add", "--file", os.path.join(tmp, "progress.json"))
            self.assertNotEqual(result.returncode, 0)

    def test_grade_requires_exactly_one_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "progress.json")
            added = self.run_review("add", "--file", path, "--q", "What changed?")
            self.assertEqual(added.returncode, 0, added.stderr)
            missing = self.run_review("grade", "--file", path, "--id", "1")
            both = self.run_review("grade", "--file", path, "--id", "1", "--pass", "--fail")
            self.assertNotEqual(missing.returncode, 0)
            self.assertNotEqual(both.returncode, 0)

    def test_grade_rejects_unknown_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "progress.json")
            added = self.run_review("add", "--file", path, "--q", "What changed?")
            self.assertEqual(added.returncode, 0, added.stderr)
            result = self.run_review("grade", "--file", path, "--id", "99", "--pass")
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
