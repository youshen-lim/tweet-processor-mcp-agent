"""
Compare Claude models on every article without posting anything.

For each model and article this runs the real pipeline steps (content analysis,
then all 4 tweet variations with a fresh composer, as one weekly run does) and
records insights, tweets, truncations, grounding warnings, failures/refusals, and
token usage. It never imports the Twitter client and never reads or writes
workflow_state.json.

Usage (from the project root):
    .venv/Scripts/python.exe scripts/model_dry_run.py
    .venv/Scripts/python.exe scripts/model_dry_run.py --models claude-sonnet-5-5 --articles 1 2 3

Output: logs/model_dry_run/<timestamp>/{results.json, report.md, token_usage.jsonl}
"""

import argparse
import asyncio
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
os.chdir(PROJECT_ROOT)  # mcp-agent finds mcp_agent.config.yaml relative to the cwd

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from mcp_agent.app import MCPApp  # noqa: E402

from agents.mcp_content_analyzer_agent import MCPContentAnalyzerAgent  # noqa: E402
from agents.mcp_tweet_composer_agent import MCPTweetComposerAgent  # noqa: E402
from parsers.article_parser import ArticleParser  # noqa: E402

DEFAULT_MODELS = ["claude-sonnet-5-5", "claude-sonnet-4-5-20250929"]


def load_articles(numbers):
    parser = ArticleParser(Path(os.getenv("ARTICLES_FILE", "data/articles.md")))
    articles = [
        {"number": a.number, "title": a.title, "url": a.url, "content": a.content}
        for a in parser.parse()
        if a.has_url and a.has_content
    ]
    if numbers:
        articles = [a for a in articles if a["number"] in numbers]
    return articles


async def run_article(model, article, semaphore):
    result = {"article": article["number"], "title": article["title"], "model": model}
    async with semaphore:
        try:
            analyzer = MCPContentAnalyzerAgent()
            await analyzer.initialize(model=model)
            insights = await analyzer.analyze_article(article)
            result["insights"] = insights.key_insights
            result["themes"] = insights.themes

            composer = MCPTweetComposerAgent()
            await composer.initialize(model=model)
            tweets = await composer.compose_multiple_variations(
                article_number=article["number"],
                article_title=article["title"],
                article_url=article["url"],
                insights=insights.key_insights,
                themes=insights.themes,
                num_variations=4,
            )
            result["tweets"] = []
            for tweet in tweets:
                main = tweet.content.split("\n\n")[0]
                result["tweets"].append({
                    "variation": tweet.variation_number,
                    "main_content": main,
                    "main_chars": len(main),
                    "effective_chars": tweet.character_count,
                    "truncated": main.endswith("…"),
                    "grounding_warnings": composer._check_grounding(tweet.insights_used[0], main),
                })
        except Exception as e:  # record and keep going; one bad article must not stop the comparison
            result["error"] = f"{type(e).__name__}: {e}"
            result["stop_reason"] = getattr(e, "stop_reason", None)
    status = "FAILED" if "error" in result else "ok"
    print(f"[{model}] article {article['number']}: {status}")
    return result


def summarize(results, usage_records):
    by_model = defaultdict(list)
    for r in results:
        by_model[r["model"]].append(r)
    usage_by_model = defaultdict(lambda: {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0})
    for u in usage_records:
        agg = usage_by_model[u["model"]]
        agg["calls"] += 1
        agg["input_tokens"] += u["input_tokens"]
        agg["output_tokens"] += u["output_tokens"]
        agg["cost"] += u["estimated_cost_usd"] or 0.0

    summary = {}
    for model, rows in by_model.items():
        tweets = [t for r in rows for t in r.get("tweets", [])]
        usage = next((v for k, v in usage_by_model.items() if k.startswith(model)), None)
        summary[model] = {
            "articles": len(rows),
            "failed": sum("error" in r for r in rows),
            "refusals": sum(r.get("stop_reason") == "refusal" for r in rows),
            "tweets": len(tweets),
            "truncated": sum(t["truncated"] for t in tweets),
            "with_grounding_warnings": sum(bool(t["grounding_warnings"]) for t in tweets),
            "avg_main_chars": round(sum(t["main_chars"] for t in tweets) / len(tweets), 1) if tweets else None,
            "max_effective_chars": max((t["effective_chars"] for t in tweets), default=None),
            "usage": usage,
        }
    return summary


def write_report(out_dir, models, results, summary):
    lines = [f"# Model dry run — {datetime.now():%Y-%m-%d %H:%M}", "", "## Summary", ""]
    lines.append("| Metric | " + " | ".join(models) + " |")
    lines.append("|---|" + "---|" * len(models))
    rows = [
        ("Articles", "articles"), ("Failed", "failed"), ("Refusals", "refusals"),
        ("Tweets", "tweets"), ("Truncated (ended with …)", "truncated"),
        ("Tweets with grounding warnings", "with_grounding_warnings"),
        ("Avg main-content chars", "avg_main_chars"), ("Max effective chars", "max_effective_chars"),
    ]
    for label, key in rows:
        lines.append(f"| {label} | " + " | ".join(str(summary.get(m, {}).get(key, "—")) for m in models) + " |")
    for label, key in (("API calls", "calls"), ("Input tokens", "input_tokens"), ("Output tokens", "output_tokens")):
        lines.append(f"| {label} | " + " | ".join(str((summary.get(m, {}).get("usage") or {}).get(key, "—")) for m in models) + " |")
    lines.append("| Estimated cost (USD) | " + " | ".join(
        f"${(summary.get(m, {}).get('usage') or {}).get('cost', 0):.4f}" for m in models) + " |")

    lines += ["", "## Per article", ""]
    by_article = defaultdict(dict)
    for r in results:
        by_article[r["article"]][r["model"]] = r
    for number in sorted(by_article):
        first = next(iter(by_article[number].values()))
        lines += [f"### Article {number}: {first['title']}", ""]
        for model in models:
            r = by_article[number].get(model)
            if not r:
                continue
            lines.append(f"**{model}**")
            if "error" in r:
                lines += [f"- ❌ {r['error']}", ""]
                continue
            lines.append("- Insights:")
            lines += [f"  {i}. {text}" for i, text in enumerate(r["insights"], 1)]
            lines.append("- Tweets:")
            for t in r["tweets"]:
                flags = []
                if t["truncated"]:
                    flags.append("TRUNCATED")
                if t["grounding_warnings"]:
                    flags.append("grounding: " + "; ".join(t["grounding_warnings"]))
                flag_str = f" ⚠️ {' | '.join(flags)}" if flags else ""
                lines.append(f"  {t['variation']}. ({t['main_chars']} chars) {t['main_content']}{flag_str}")
            lines.append("")
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


async def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    ap.add_argument("--articles", nargs="+", type=int, help="article numbers (default: all)")
    ap.add_argument("--concurrency", type=int, default=4)
    args = ap.parse_args()

    out_dir = PROJECT_ROOT / "logs" / "model_dry_run" / datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    usage_log = out_dir / "token_usage.jsonl"
    os.environ["TOKEN_USAGE_LOG"] = str(usage_log)

    articles = load_articles(set(args.articles or []))
    print(f"Dry run: {len(articles)} articles x {len(args.models)} models -> {out_dir}")

    semaphore = asyncio.Semaphore(args.concurrency)
    results = []
    async with MCPApp(name="model_dry_run").run():
        for model in args.models:
            results += await asyncio.gather(*(run_article(model, a, semaphore) for a in articles))

    usage_records = []
    if usage_log.exists():
        usage_records = [json.loads(line) for line in usage_log.read_text(encoding="utf-8").splitlines()]
    summary = summarize(results, usage_records)
    (out_dir / "results.json").write_text(
        json.dumps({"summary": summary, "results": results}, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(out_dir, args.models, results, summary)
    print(json.dumps(summary, indent=2))
    print(f"Report: {out_dir / 'report.md'}")


if __name__ == "__main__":
    asyncio.run(main())
