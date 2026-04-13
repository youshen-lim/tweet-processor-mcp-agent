#!/usr/bin/env python3
"""Clear the stale articles_cache from workflow_state.json."""

import json

def main():
    # Load the current state
    with open('workflow_state.json', 'r') as f:
        state = json.load(f)
    
    # Report before count
    cached_count = len(state.get('articles_cache', []))
    print(f"Before: {cached_count} cached articles")
    
    # Clear the cache
    state['articles_cache'] = []
    
    # Save back
    with open('workflow_state.json', 'w') as f:
        json.dump(state, f, indent=2)
    
    print("Cache cleared successfully!")
    print("Run 'python run_tweet_processor.py --status' to verify all 15 articles are now recognized.")

if __name__ == "__main__":
    main()

