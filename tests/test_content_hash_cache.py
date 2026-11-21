"""
Tests for content-hash invalidation of cached article analyses.

Each analysis_<n> entry stores a fingerprint of the article body it was made
from; an edited body triggers re-analysis, reformatting does not, and legacy
entries without a fingerprint are adopted instead of re-analyzed. All state is
built from fixtures here (conftest points WORKFLOW_STATE_FILE at tmp_path).
"""

import copy
import json
import logging
import os
import sys
from datetime import timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from workflows.mcp_tweet_processor_workflow import (  # noqa: E402
    MCPTweetProcessorWorkflow,
    article_content_hash,
)
from agents.mcp_tweet_composer_agent import Tweet  # noqa: E402
from parsers.article_parser import ArticleParser  # noqa: E402

URL = "https://www.linkedin.com/pulse/content-hash-test-aaron-lim-abc123/"
OLD_BODY = "Data quality compounds over time.\nStrategy beats tooling."
NEW_BODY = "Data quality compounds over time.\nStrategy beats tooling, every time."
SEQUENCE_FIELDS = ("current_article", "current_variation", "total_posts", "last_posted")


# --------------------------------------------------------------------------- helpers

def _article(number=2, body=OLD_BODY, url=URL, title="Test Article"):
    return {
        "number": number, "title": title, "url": url, "content": body,
        "word_count": max(len(body.split()), 1), "has_title": True, "has_url": True,
    }


def _legacy_analysis(number=2, url=URL, insights=("Old 1", "Old 2", "Old 3", "Old 4")):
    """Same keys as the live legacy entries (no content_hash)."""
    return {
        "article_number": number, "article_title": "Test Article", "article_url": url,
        "expert_references": [], "frameworks_mentioned": [],
        "key_insights": list(insights), "themes": ["AI"],
    }


def _hashed_analysis(body, **kwargs):
    entry = _legacy_analysis(**kwargs)
    entry["content_hash"] = article_content_hash(body)
    return entry


def _state(articles, analyses, current_article=2, current_variation=1):
    state = {
        "current_article": current_article,
        "current_variation": current_variation,
        "total_posts": 39,
        "last_posted": "2026-11-20T17:19:00",
        "articles_cache": articles,
    }
    state.update(analyses)
    return state


def _workflow(state):
    with patch.object(MCPTweetProcessorWorkflow, '_load_state', return_value={}):
        workflow = MCPTweetProcessorWorkflow()
    workflow.state = state
    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=Mock(logger=Mock()))
    ctx.__aexit__ = AsyncMock(return_value=None)
    workflow.mcp_app.run = Mock(return_value=ctx)

    async def compose(**kwargs):
        return [
            Tweet(article_number=kwargs["article_number"], variation_number=v,
                  content=f"Tweet {v}\n\n{kwargs['article_url']}\n\n#AI", character_count=50,
                  hashtags=["#AI"], insights_used=[], focus_theme="strategic_value")
            for v in range(1, kwargs["num_variations"] + 1)
        ]

    workflow.tweet_composer = Mock()
    workflow.tweet_composer.compose_multiple_variations = AsyncMock(side_effect=compose)
    workflow.content_analyzer = Mock()
    workflow.content_analyzer.analyze_article = AsyncMock(
        return_value=Mock(article_number=2, article_title="Test Article", article_url=URL,
                          key_insights=["New 1", "New 2", "New 3", "New 4"], themes=["AI"],
                          expert_references=[], frameworks_mentioned=[]))
    return workflow


async def _run_weekly(workflow, save=None):
    save = save or Mock()
    with patch.object(workflow, 'initialize_agents', new_callable=AsyncMock), \
         patch.object(workflow, '_sync_articles_if_docx_newer'), \
         patch.object(workflow, '_save_state', save):
        result = await workflow.run_weekly_post(post_to_twitter=False)
    return result, save


async def _run_pipeline(workflow, weeks):
    save = Mock()
    # Pin the posting time zone to UTC so these tests don't depend on tzdata;
    # the schedule maths is not under test here.
    with patch.object(workflow, 'initialize_agents', new_callable=AsyncMock), \
         patch.object(workflow, '_sync_articles_if_docx_newer'), \
         patch.object(workflow, '_save_state', save), \
         patch('workflows.mcp_tweet_processor_workflow.ZoneInfo', return_value=timezone.utc):
        pipeline = await workflow.generate_pipeline_preview(weeks=weeks)
    return pipeline, save


def _sequence(state):
    return {k: state[k] for k in SEQUENCE_FIELDS}


# --------------------------------------------------------------------------- hash

@pytest.mark.unit
class TestArticleContentHash:

    def test_hash_is_versioned_sha256(self):
        value = article_content_hash("abc")
        scheme, digest = value.split(":")
        assert scheme == "sha256-v1"
        assert len(digest) == 64 and int(digest, 16) >= 0
        assert article_content_hash("abc") == value

    def test_hash_ignores_whitespace_line_endings_and_nbsp(self):
        variants = ["A  b\r\nc\t d", " A b\n\nc d ", "A b\nc d", "A b c d"]
        assert len({article_content_hash(v) for v in variants}) == 1

    def test_hash_normalizes_unicode_to_nfc(self):
        assert article_content_hash("café") == article_content_hash("café")

    def test_none_hashes_like_empty(self):
        assert article_content_hash(None) == article_content_hash("")

    def test_real_edit_changes_hash(self):
        assert article_content_hash(OLD_BODY) != article_content_hash(NEW_BODY)
        assert article_content_hash("Data matters.") != article_content_hash("Data matters!")

    def test_metadata_and_crlf_do_not_change_parsed_body_hash(self, tmp_path):
        template = (
            "# Newsletter Articles\n\n---\n\n## Article #1\n\n**Title:** {title}\n\n**URL:** {url}\n\n"
            "**Content:**\n\n{body}\n\n**Metadata:**\n- Word Count: {wc}\n- Status: {status}\n\n---\n"
        )
        a = tmp_path / "a.md"
        b = tmp_path / "b.md"
        a.write_text(template.format(title="T", url=URL, body="Para one.\nPara two.",
                                     wc=4, status="Active"), encoding="utf-8")
        b.write_bytes(template.format(title="Other title", url=URL + "x", body="Para one.  \n\nPara two.",
                                      wc=999, status="Draft").replace("\n", "\r\n").encode("utf-8"))
        body_a = ArticleParser(a).parse()[0].content
        body_b = ArticleParser(b).parse()[0].content
        assert body_a and body_b
        assert article_content_hash(body_a) == article_content_hash(body_b)

    def test_converter_round_trip_is_stable(self, tmp_path):
        from convert_docx_to_md import ParsedArticle, build_markdown

        def parsed_hash(paragraphs, name):
            md = build_markdown([ParsedArticle(number=1, title="T", url=URL,
                                               content_paragraphs=paragraphs)])
            path = tmp_path / name
            path.write_text(md, encoding="utf-8")
            return article_content_hash(ArticleParser(path).parse()[0].content)

        original = parsed_hash(["First paragraph.", "Second paragraph."], "one.md")
        reconverted = parsed_hash(["First paragraph.", "Second   paragraph."], "two.md")
        edited = parsed_hash(["First paragraph.", "Second paragraph, revised."], "three.md")
        assert original == reconverted
        assert original != edited


# --------------------------------------------------------------------------- weekly path

@pytest.mark.integration
@pytest.mark.asyncio
class TestWeeklyAnalysisCache:

    async def test_matching_hash_reuses_without_analyzer_or_save(self):
        wf = _workflow(_state([_article()], {"analysis_2": _hashed_analysis(OLD_BODY)}))
        result, save = await _run_weekly(wf)
        assert result["status"] == "success"
        wf.content_analyzer.analyze_article.assert_not_awaited()
        save.assert_not_called()
        insights = wf.tweet_composer.compose_multiple_variations.await_args.kwargs["insights"]
        assert insights[0] == "Old 1"

    async def test_whitespace_only_change_reuses(self, caplog):
        wf = _workflow(_state([_article(body="Data quality compounds over time.\r\n\r\n  Strategy beats tooling. ")],
                              {"analysis_2": _hashed_analysis(OLD_BODY)}))
        with caplog.at_level(logging.WARNING):
            result, _ = await _run_weekly(wf)
        assert result["status"] == "success"
        wf.content_analyzer.analyze_article.assert_not_awaited()
        assert "invalidated" not in caplog.text

    async def test_title_only_change_reuses(self):
        wf = _workflow(_state([_article(title="A Brand New Title")],
                              {"analysis_2": _hashed_analysis(OLD_BODY)}))
        result, _ = await _run_weekly(wf)
        assert result["status"] == "success"
        wf.content_analyzer.analyze_article.assert_not_awaited()

    async def test_legacy_entry_adopted_without_analyzer_or_extra_save(self):
        state = _state([_article()], {"analysis_2": _legacy_analysis()})
        wf = _workflow(state)
        before = _sequence(state)
        result, save = await _run_weekly(wf)
        assert result["status"] == "success"
        wf.content_analyzer.analyze_article.assert_not_awaited()
        save.assert_not_called()
        assert wf.state["analysis_2"]["content_hash"] == article_content_hash(OLD_BODY)
        assert wf.state["analysis_2"]["key_insights"] == ["Old 1", "Old 2", "Old 3", "Old 4"]
        assert _sequence(wf.state) == before

    async def test_unknown_hash_scheme_adopted_not_reanalyzed(self):
        entry = _legacy_analysis()
        entry["content_hash"] = "sha256-v0:deadbeef"
        wf = _workflow(_state([_article()], {"analysis_2": entry}))
        result, _ = await _run_weekly(wf)
        assert result["status"] == "success"
        wf.content_analyzer.analyze_article.assert_not_awaited()
        assert wf.state["analysis_2"]["content_hash"] == article_content_hash(OLD_BODY)

    async def test_eager_adoption_covers_all_legacy_entries(self):
        articles = [_article(number=n, url=URL.replace("abc123", f"n{n}"), body=f"Body {n}")
                    for n in range(1, 6)]
        analyses = {f"analysis_{n}": _legacy_analysis(number=n, url=URL.replace("abc123", f"n{n}"))
                    for n in range(1, 6)}
        analyses["analysis_4"]["article_url"] = URL.replace("abc123", "moved")   # URL mismatch
        analyses["analysis_9"] = _legacy_analysis(number=9)                       # article removed
        state = _state(articles, analyses, current_article=1)
        wf = _workflow(state)
        before = _sequence(state)
        result, save = await _run_weekly(wf)
        assert result["status"] == "success"
        for n in (1, 2, 3, 5):
            assert wf.state[f"analysis_{n}"]["content_hash"] == article_content_hash(f"Body {n}")
        assert "content_hash" not in wf.state["analysis_4"]
        assert "content_hash" not in wf.state["analysis_9"]
        wf.content_analyzer.analyze_article.assert_not_awaited()
        save.assert_not_called()
        assert _sequence(wf.state) == before

    async def test_new_analysis_is_stored_with_hash(self):
        wf = _workflow(_state([_article()], {}))
        result, save = await _run_weekly(wf)
        assert result["status"] == "success"
        wf.content_analyzer.analyze_article.assert_awaited_once()
        assert wf.state["analysis_2"]["content_hash"] == article_content_hash(OLD_BODY)
        save.assert_called_once()

    async def test_real_change_reanalyzes_and_logs_prefixes(self, caplog):
        wf = _workflow(_state([_article(body=NEW_BODY)], {"analysis_2": _hashed_analysis(OLD_BODY)}))
        with caplog.at_level(logging.WARNING):
            result, save = await _run_weekly(wf)
        assert result["status"] == "success"
        wf.content_analyzer.analyze_article.assert_awaited_once()
        assert wf.state["analysis_2"]["key_insights"][0] == "New 1"
        assert wf.state["analysis_2"]["content_hash"] == article_content_hash(NEW_BODY)
        assert wf.tweet_composer.compose_multiple_variations.await_args.kwargs["insights"][0] == "New 1"
        save.assert_called_once()
        old_prefix = article_content_hash(OLD_BODY).split(":")[1][:12]
        new_prefix = article_content_hash(NEW_BODY).split(":")[1][:12]
        assert "Article #2 invalidated" in caplog.text
        assert old_prefix in caplog.text and new_prefix in caplog.text

    async def test_mid_rotation_change_keeps_sequence_fields(self, caplog):
        state = _state([_article(body=NEW_BODY)], {"analysis_2": _hashed_analysis(OLD_BODY)},
                       current_variation=3)
        wf = _workflow(state)
        before = _sequence(state)
        with caplog.at_level(logging.WARNING):
            result, _ = await _run_weekly(wf)
        assert result["status"] == "success"
        assert result["tweet"]["variation_number"] == 3
        assert wf.tweet_composer.compose_multiple_variations.await_args.kwargs["num_variations"] == 3
        assert _sequence(wf.state) == before
        assert "mid-rotation (Variation 3)" in caplog.text and "variations 1-2" in caplog.text

    async def test_url_change_still_raises_and_skips_analyzer(self):
        cached = _hashed_analysis(OLD_BODY)
        moved = URL.replace("abc123", "moved1")
        wf = _workflow(_state([_article(body=NEW_BODY, url=moved)], {"analysis_2": copy.deepcopy(cached)}))
        result, save = await _run_weekly(wf)
        assert result["status"] == "error"
        assert "URL mismatch" in result["error"]
        wf.content_analyzer.analyze_article.assert_not_awaited()
        assert wf.state["analysis_2"] == cached
        save.assert_not_called()

    @pytest.mark.parametrize("cached_url", [None, ""])
    async def test_unverifiable_cached_url_is_reanalyzed_not_adopted(self, cached_url, caplog):
        entry = _legacy_analysis(url=cached_url)
        if cached_url is None:
            del entry["article_url"]
        state = _state([_article()], {"analysis_2": entry})
        wf = _workflow(state)
        before = _sequence(state)
        with caplog.at_level(logging.WARNING):
            result, save = await _run_weekly(wf)
        assert result["status"] == "success"
        wf.content_analyzer.analyze_article.assert_awaited_once()
        assert wf.state["analysis_2"]["article_url"] == URL
        assert wf.state["analysis_2"]["content_hash"] == article_content_hash(OLD_BODY)
        assert wf.state["analysis_2"]["key_insights"][0] == "New 1"
        save.assert_called_once()
        assert "has no article_url" in caplog.text
        assert _sequence(wf.state) == before

    async def test_eager_adoption_skips_unverifiable_url(self):
        entry = _legacy_analysis()
        del entry["article_url"]
        wf = _workflow(_state([_article(number=1, url=URL.replace("abc123", "n1"))],
                              {"analysis_2": entry, "analysis_1": _legacy_analysis(number=1, url="")}))
        wf._adopt_legacy_analysis_hashes(wf.state["articles_cache"] + [_article()])
        assert "content_hash" not in wf.state["analysis_1"]
        assert "content_hash" not in wf.state["analysis_2"]

    async def test_failed_reanalysis_keeps_old_entry(self):
        cached = _hashed_analysis(OLD_BODY)
        wf = _workflow(_state([_article(body=NEW_BODY)], {"analysis_2": copy.deepcopy(cached)}))
        wf.content_analyzer.analyze_article = AsyncMock(side_effect=RuntimeError("LLM timeout"))
        result, save = await _run_weekly(wf)
        assert result["status"] == "error"
        assert wf.state["analysis_2"] == cached
        save.assert_not_called()

    async def test_empty_body_keeps_cached_analysis(self, caplog):
        cached = _hashed_analysis(OLD_BODY)
        wf = _workflow(_state([_article(body="")], {"analysis_2": copy.deepcopy(cached)}))
        wf.state["articles_cache"][0]["word_count"] = 100   # metadata says it has content
        with caplog.at_level(logging.WARNING):
            result, _ = await _run_weekly(wf)
        assert result["status"] == "success"
        wf.content_analyzer.analyze_article.assert_not_awaited()
        assert wf.state["analysis_2"] == cached
        assert "empty body" in caplog.text

    async def test_post_persists_adoption_to_temp_state_file(self, tmp_path):
        state_file = tmp_path / "workflow_state.json"
        assert os.environ["WORKFLOW_STATE_FILE"] == str(state_file)
        articles = [_article(number=n, url=URL.replace("abc123", f"n{n}"), body=f"Body {n}")
                    for n in (1, 2)]
        analyses = {f"analysis_{n}": _legacy_analysis(number=n, url=URL.replace("abc123", f"n{n}"))
                    for n in (1, 2)}
        state_file.write_text(json.dumps(_state(articles, analyses, current_variation=4)), encoding="utf-8")

        workflow = MCPTweetProcessorWorkflow()          # reads the temp file
        fixture_wf = _workflow(workflow.state)
        client = Mock()
        client.post_tweet.return_value = {"tweet_id": "123", "posted_at": "2026-11-23T11:30:00"}
        with patch.object(fixture_wf, 'initialize_agents', new_callable=AsyncMock), \
             patch.object(fixture_wf, '_sync_articles_if_docx_newer'), \
             patch('mcp_servers.twitter_server.TwitterClient', return_value=client):
            result = await fixture_wf.run_weekly_post(post_to_twitter=True)

        assert result["status"] == "success"
        saved = json.loads(state_file.read_text(encoding="utf-8"))
        for n in (1, 2):
            assert saved[f"analysis_{n}"]["content_hash"] == article_content_hash(f"Body {n}")
            assert saved[f"analysis_{n}"]["key_insights"] == ["Old 1", "Old 2", "Old 3", "Old 4"]
        assert (saved["current_article"], saved["current_variation"], saved["total_posts"]) == (1, 1, 40)
        fixture_wf.content_analyzer.analyze_article.assert_not_awaited()


# --------------------------------------------------------------------------- pipeline path

@pytest.mark.integration
@pytest.mark.asyncio
class TestPipelineAnalysisCache:

    async def test_real_change_reanalyzes_once_across_weeks(self):
        state = _state([_article(body=NEW_BODY)], {"analysis_2": _hashed_analysis(OLD_BODY)},
                       current_variation=2)
        wf = _workflow(state)
        before = _sequence(state)
        pipeline, save = await _run_pipeline(wf, weeks=3)
        assert [p["variation_number"] for p in pipeline] == [2, 3, 4]
        wf.content_analyzer.analyze_article.assert_awaited_once()
        save.assert_called_once()
        assert wf.state["analysis_2"]["content_hash"] == article_content_hash(NEW_BODY)
        assert _sequence(wf.state) == before

    async def test_never_adopts_or_writes_legacy_entries(self):
        legacy = _legacy_analysis()
        state = _state([_article()], {"analysis_2": copy.deepcopy(legacy)}, current_variation=1)
        wf = _workflow(state)
        before = _sequence(state)
        pipeline, save = await _run_pipeline(wf, weeks=3)
        assert len(pipeline) == 3
        wf.content_analyzer.analyze_article.assert_not_awaited()
        save.assert_not_called()
        assert wf.state["analysis_2"] == legacy
        assert _sequence(wf.state) == before

    async def test_matching_hash_reuses(self):
        wf = _workflow(_state([_article()], {"analysis_2": _hashed_analysis(OLD_BODY)}))
        pipeline, save = await _run_pipeline(wf, weeks=1)
        assert len(pipeline) == 1
        wf.content_analyzer.analyze_article.assert_not_awaited()
        save.assert_not_called()

    async def test_unverifiable_cached_url_is_reanalyzed(self):
        entry = _legacy_analysis()
        del entry["article_url"]
        state = _state([_article()], {"analysis_2": entry})
        wf = _workflow(state)
        before = _sequence(state)
        pipeline, save = await _run_pipeline(wf, weeks=1)
        assert len(pipeline) == 1
        wf.content_analyzer.analyze_article.assert_awaited_once()
        assert wf.state["analysis_2"]["article_url"] == URL
        assert wf.state["analysis_2"]["content_hash"] == article_content_hash(OLD_BODY)
        save.assert_called_once()
        assert _sequence(wf.state) == before
