# Tweet Processor container image.
#
# The image holds code and the article source only. No secrets are baked in:
# API keys and tokens come from the environment at run time (--env-file .env),
# and .dockerignore is an allowlist, so .env, mcp_agent.secrets.yaml,
# credentials/ and workflow_state.json never enter the build context.
#
# Build:
#   docker build -t tweet-processor .
#
# Run (state and logs persist in named volumes; default command is --status):
#   docker run --rm --env-file .env \
#     -v tweet-state:/app/state -v tweet-logs:/app/logs \
#     tweet-processor --preview
#
# Commands: --status (default), --preview, --pipeline, --post, --help.
# To continue an existing sequence, copy your workflow_state.json into the
# state volume first; otherwise the run starts from Article #1.

FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    WORKFLOW_STATE_FILE=/app/state/workflow_state.json

WORKDIR /app

# Dependencies first so code edits don't invalidate this layer.
# tzdata (in requirements.txt) supplies the IANA zones for POSTING_TIMEZONE.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Application code, config (no secrets) and the article source.
COPY run_tweet_processor.py mcp_agent.config.yaml ./
COPY src/ ./src/
COPY scripts/convert_docx_to_md.py ./scripts/
COPY data/articles.md ./data/

# Run as an unprivileged user. It needs write access to /app because the app
# writes logs/, the state file and --pipeline output (tweet_pipeline.*) there.
RUN useradd --create-home --uid 10001 app \
    && mkdir -p /app/state /app/logs \
    && chown -R app:app /app
USER app

VOLUME ["/app/state", "/app/logs"]

ENTRYPOINT ["python", "run_tweet_processor.py"]
CMD ["--status"]
