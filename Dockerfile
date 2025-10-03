FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY credentials/ ./credentials/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV USE_REAL_APIS=true
ENV ENABLE_TWITTER_POSTING=true

# Run workflow
CMD ["python", "src/workflows/tweet_processor_workflow.py"]

