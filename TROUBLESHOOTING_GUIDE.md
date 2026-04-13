# Tweet Processor Troubleshooting Guide

## Issue Summary

Based on the diagnostic analysis, two critical issues have been identified:

### 1. **Manual Execution Stall** ✅ DIAGNOSED
**Status**: Application hangs during tweet composition phase  
**Root Cause**: MCP Agent LLM API call timeout or hanging  
**Location**: `src/agents/mcp_tweet_composer_agent.py` line 235

### 2. **Task Scheduler Execution Failure** 🔍 NEEDS VERIFICATION
**Status**: Application does not execute successfully via Windows Task Scheduler  
**Likely Causes**: Working directory, Python path, or environment variable issues

---

## Problem 1: Manual Execution Stall

### Symptoms
- Application starts successfully
- Shows configuration and "Running tweet processor..."
- Hangs indefinitely with no output
- Last log entry shows: "Composing tweet variation 1"
- No error messages displayed

### Root Cause Analysis

From the logs (`logs/tweet-processor-20260122_113045.jsonl`):
```json
{"level":"INFO","timestamp":"2026-01-22T11:30:32.508598","message":"Composing tweet variation 1"}
{"level":"INFO","timestamp":"2026-01-22T11:30:35.248370","message":"Model claude-sonnet-4-5-20250929 (provider=anthropic) not found in costs, using default estimate"}
{"level":"INFO","timestamp":"2026-01-22T11:30:40.027049","message":"Model claude-sonnet-4-5-20250929 (provider=anthropic) not found in costs, using default estimate"}
{"level":"INFO","timestamp":"2026-01-22T11:30:42.671274","message":"Model claude-sonnet-4-5-20250929 (provider=anthropic) not found in costs, using default estimate"}
```

**The application is stuck waiting for Anthropic API response during tweet composition.**

### Potential Causes

1. **API Timeout**: Anthropic API not responding or taking too long
2. **Network Issues**: Firewall, proxy, or connectivity problems
3. **API Key Issues**: Invalid or rate-limited API key
4. **MCP Agent Hanging**: Async context not properly managed
5. **Missing Error Handling**: No timeout configured for LLM calls

### Solutions

#### Solution 1: Add Timeout to LLM Calls (RECOMMENDED)

Edit `src/agents/mcp_tweet_composer_agent.py`:

```python
# Around line 235, replace:
tweet_content = await self.llm.generate_str(message=prompt)

# With:
import asyncio
try:
    tweet_content = await asyncio.wait_for(
        self.llm.generate_str(message=prompt),
        timeout=60.0  # 60 second timeout
    )
except asyncio.TimeoutError:
    print("⚠️  LLM request timed out after 60 seconds")
    raise Exception("Tweet composition timed out - please check API connectivity")
```

#### Solution 2: Verify API Key and Connectivity

```bash
# Test Anthropic API connectivity
python -c "import anthropic; client = anthropic.Anthropic(api_key='YOUR_KEY'); print(client.messages.create(model='claude-sonnet-4-5-20250929', max_tokens=10, messages=[{'role':'user','content':'test'}]))"
```

#### Solution 3: Add Verbose Logging

Edit `src/agents/mcp_tweet_composer_agent.py` to add debug logging:

```python
# Before line 235
print(f"🔍 Calling Anthropic API with prompt length: {len(prompt)} chars")
print(f"🔍 Model: {os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-5-20250929')}")

tweet_content = await self.llm.generate_str(message=prompt)

print(f"✅ Received response: {len(tweet_content)} chars")
```

#### Solution 4: Check for OneDrive Sync Issues

The error "The cloud file provider exited unexpectedly" suggests OneDrive sync issues with log files.

**Fix**:
1. Move the project to a local folder (not OneDrive)
2. Or exclude the `logs/` folder from OneDrive sync
3. Right-click `logs` folder → "Always keep on this device"

---

## Problem 2: Task Scheduler Execution Failure

### Common Issues with Task Scheduler

#### Issue 1: Working Directory Not Set
**Symptom**: Script runs manually but fails in Task Scheduler  
**Cause**: Task Scheduler doesn't set working directory automatically

**Fix**: In Task Scheduler:
1. Open Task → Actions tab → Edit action
2. Set "Start in (optional)" to: `C:\Users\Youshen\OneDrive\augment-projects\Tweet Processor using LastMile MCP Agent Cloud`

#### Issue 2: Python Not in PATH
**Symptom**: "Python is not recognized" error  
**Cause**: Task Scheduler uses different environment variables

**Fix**: Use full Python path in batch file:
```batch
REM Instead of:
python run_tweet_processor.py --post

REM Use:
"C:\Users\Youshen\AppData\Local\Programs\Python\Python313\python.exe" run_tweet_processor.py --post
```

#### Issue 3: Environment Variables Not Loaded
**Symptom**: Script fails to find .env file or API keys  
**Cause**: Task Scheduler doesn't load user environment

**Fix**: Ensure .env file is in the correct location and batch file sets working directory

#### Issue 4: Virtual Environment Not Activated
**Symptom**: Import errors or module not found  
**Cause**: Virtual environment not activated

**Fix**: Update `run_tweet_processor.bat`:
```batch
REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)
```

### Recommended Task Scheduler Configuration

1. **General Tab**:
   - ✅ Run whether user is logged on or not
   - ✅ Run with highest privileges
   - Configure for: Windows 10

2. **Triggers Tab**:
   - Weekly, every Thursday at 11:30 AM
   - Enabled: ✅

3. **Actions Tab**:
   - Action: Start a program
   - Program/script: `C:\Users\Youshen\OneDrive\augment-projects\Tweet Processor using LastMile MCP Agent Cloud\run_tweet_processor.bat`
   - Start in: `C:\Users\Youshen\OneDrive\augment-projects\Tweet Processor using LastMile MCP Agent Cloud`

4. **Conditions Tab**:
   - ❌ Start the task only if the computer is on AC power (uncheck this)
   - ✅ Wake the computer to run this task

5. **Settings Tab**:
   - ✅ Allow task to be run on demand
   - ✅ Run task as soon as possible after a scheduled start is missed
   - If the task fails, restart every: 1 minute, up to 3 times

---

## Next Steps

### Immediate Actions

1. **Fix the manual execution stall**:
   - Add timeout to LLM calls (Solution 1)
   - Add verbose logging (Solution 3)
   - Test manually: `python run_tweet_processor.py`

2. **Move project out of OneDrive** (if possible):
   - Copy to `C:\Projects\Tweet-Processor\`
   - Update all paths in Task Scheduler

3. **Test Task Scheduler**:
   - Right-click task → Run
   - Check `posting_log.txt` for output
   - Review Task Scheduler History tab for errors

### Verification Steps

```bash
# 1. Test manual execution
cd "C:\Users\Youshen\OneDrive\augment-projects\Tweet Processor using LastMile MCP Agent Cloud"
python run_tweet_processor.py --status

# 2. Test with timeout
python run_tweet_processor.py

# 3. Test Task Scheduler (run manually)
# Right-click task in Task Scheduler → Run

# 4. Check logs
type posting_log.txt
```

---

## Monitoring and Debugging

### Enable Debug Logging

Add to `.env`:
```env
LOG_LEVEL=DEBUG
MCP_AGENT_LOG_LEVEL=DEBUG
```

### Check Task Scheduler History

1. Open Task Scheduler
2. Select your task
3. Click "History" tab (enable if disabled)
4. Look for error codes and messages

### Common Error Codes

- `0x1`: Incorrect function / General error
- `0x2`: File not found
- `0xFFFFFFFF`: Application crashed
- `0x41301`: Task is currently running

---

## Contact Information

If issues persist after trying these solutions, collect the following information:

1. Full error message from Task Scheduler History
2. Contents of `posting_log.txt`
3. Latest log file from `logs/` directory
4. Output of: `python --version` and `where python`

