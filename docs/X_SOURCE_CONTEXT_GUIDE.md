# X/Twitter Source Context Guide

Tweet Processor can use an optional local source-context file while composing
tweets. The article still remains the source of truth. Source context only helps
the composer choose audience language, objections, and framing.

## When To Use It

Use source context when you have public X/Twitter signals that clarify how
readers talk about a topic:

- public search results
- public replies to your earlier posts
- public competitor or customer-language examples
- public objections, questions, or recurring phrases
- reviewed notes from a separate research pass

Do not use it for private DMs, private account exports, cookies, access tokens,
unreviewed scraped data, or confidential research. Keep those out of the repo.

## Configure The File

Create a local file that is not committed:

```powershell
New-Item -ItemType Directory -Force data
notepad data/source_context.md
```

Then set:

```env
SOURCE_CONTEXT_FILE=data/source_context.md
```

`data/source_context.*` is ignored by Git, so local source packets and notes do
not get committed by accident.

## Suggested Packet Format

Keep packets short and reviewed:

```markdown
# X/Twitter Source Context

Topic: AI implementation planning
Collection date: 2026-01-21
Use only for framing, not factual claims.

Audience questions:
- How do teams know when a pilot is ready for production?
- What proof should leaders ask for before expanding AI tools?

Common language:
- rollout checklist
- business owner approval
- measurable adoption

Avoid:
- claiming new statistics
- naming private accounts
- copying replies verbatim without review
```

## Optional TweetClaw Collection Path

If you use OpenClaw, TweetClaw can collect public X/Twitter context before you
run Tweet Processor:

```bash
openclaw plugins install npm:@xquik/tweetclaw@1.6.31
```

Use TweetClaw for source collection only. Tweet Processor still owns article
analysis, tweet generation, review, scheduling, and posting.

Useful links:

- [TweetClaw GitHub](https://github.com/Xquik-dev/tweetclaw)
- [TweetClaw npm registry metadata](https://registry.npmjs.org/@xquik%2ftweetclaw)

## Run Safely

Preview first:

```powershell
python run_tweet_processor.py --preview
```

Review the generated tweet. It should be grounded in the article insight. The
source context should only shape wording and audience angle.

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.
