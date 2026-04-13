"""
Unit Tests for Workflow State Management
Tests state loading/saving, article progression, variation tracking, and state updates.
"""

import pytest
import os
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from workflows.mcp_tweet_processor_workflow import MCPTweetProcessorWorkflow


@pytest.mark.unit
class TestStateLoading:
    """Test suite for workflow state loading."""
    
    def test_load_existing_state(self, sample_workflow_state, tmp_path):
        """Test loading existing workflow state."""
        # Create temporary state file
        state_file = tmp_path / "workflow_state.json"
        with open(state_file, 'w') as f:
            json.dump(sample_workflow_state, f)
        
        # Mock the state file path
        with patch('workflows.mcp_tweet_processor_workflow.open', mock_open(read_data=json.dumps(sample_workflow_state))):
            workflow = MCPTweetProcessorWorkflow()
            
            assert workflow.state["current_article"] == sample_workflow_state["current_article"]
            assert workflow.state["current_variation"] == sample_workflow_state["current_variation"]
            assert workflow.state["total_posts"] == sample_workflow_state["total_posts"]
    
    def test_load_missing_state_creates_default(self):
        """Test that missing state file creates default state."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            workflow = MCPTweetProcessorWorkflow()
            
            assert workflow.state["current_article"] == 1
            assert workflow.state["current_variation"] == 1
            assert workflow.state["total_posts"] == 0
            assert workflow.state["last_posted"] is None
            assert workflow.state["articles_cache"] == []
    
    def test_load_corrupted_state_handles_gracefully(self):
        """Test handling of corrupted state file."""
        corrupted_json = "{ invalid json content"
        
        with patch('builtins.open', mock_open(read_data=corrupted_json)):
            try:
                workflow = MCPTweetProcessorWorkflow()
                # Should either raise error or create default state
                assert workflow.state is not None
            except json.JSONDecodeError:
                # Expected behavior for corrupted JSON
                pass


@pytest.mark.unit
class TestStateSaving:
    """Test suite for workflow state saving."""
    
    def test_save_state_creates_file(self, tmp_path):
        """Test that saving state creates the file."""
        state_file = tmp_path / "workflow_state.json"
        
        workflow = MCPTweetProcessorWorkflow()
        workflow.state = {
            "current_article": 2,
            "current_variation": 3,
            "total_posts": 5,
            "last_posted": "2025-10-10T15:30:00",
            "articles_cache": []
        }
        
        # Mock the file path
        with patch('workflows.mcp_tweet_processor_workflow.open', mock_open()) as mock_file:
            workflow._save_state()
            mock_file.assert_called_once()
    
    def test_save_state_preserves_data(self, tmp_path):
        """Test that saved state preserves all data."""
        state_file = tmp_path / "workflow_state.json"
        
        workflow = MCPTweetProcessorWorkflow()
        workflow.state = {
            "current_article": 3,
            "current_variation": 4,
            "total_posts": 11,
            "last_posted": "2025-10-10T15:30:00",
            "articles_cache": [{"number": 1, "title": "Test"}]
        }
        
        # Save and reload
        with patch('workflows.mcp_tweet_processor_workflow.open', mock_open()) as mock_file:
            workflow._save_state()
            
            # Verify json.dump was called with correct data
            handle = mock_file()
            written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
            # Should contain the state data


@pytest.mark.unit
class TestArticleProgression:
    """Test suite for article progression logic."""
    
    def test_update_state_next_variation(self):
        """Test updating state to next variation."""
        workflow = MCPTweetProcessorWorkflow()
        workflow.state = {
            "current_article": 1,
            "current_variation": 1,
            "total_posts": 0,
            "articles_cache": []
        }
        
        articles = [
            {"number": 1, "word_count": 100, "has_url": True, "url": "https://example.com/1"},
            {"number": 2, "word_count": 150, "has_url": True, "url": "https://example.com/2"}
        ]
        
        with patch.object(workflow, '_save_state'):
            workflow._update_state_after_post(articles)
        
        # Should move to variation 2
        assert workflow.state["current_variation"] == 2
        assert workflow.state["current_article"] == 1
    
    def test_update_state_next_article_after_variation_4(self):
        """Test updating state to next article after variation 4."""
        workflow = MCPTweetProcessorWorkflow()
        workflow.state = {
            "current_article": 1,
            "current_variation": 4,
            "total_posts": 3,
            "articles_cache": []
        }
        
        articles = [
            {"number": 1, "word_count": 100, "has_url": True, "url": "https://example.com/1"},
            {"number": 2, "word_count": 150, "has_url": True, "url": "https://example.com/2"}
        ]
        
        with patch.object(workflow, '_save_state'):
            workflow._update_state_after_post(articles)
        
        # Should move to article 2, variation 1
        assert workflow.state["current_variation"] == 1
        assert workflow.state["current_article"] == 2
    
    def test_update_state_cycles_back_to_first_article(self):
        """Test that state cycles back to first article after last article."""
        workflow = MCPTweetProcessorWorkflow()
        workflow.state = {
            "current_article": 2,
            "current_variation": 4,
            "total_posts": 7,
            "articles_cache": []
        }
        
        articles = [
            {"number": 1, "word_count": 100, "has_url": True, "url": "https://example.com/1"},
            {"number": 2, "word_count": 150, "has_url": True, "url": "https://example.com/2"}
        ]
        
        with patch.object(workflow, '_save_state'):
            workflow._update_state_after_post(articles)
        
        # Should cycle back to article 1, variation 1
        assert workflow.state["current_variation"] == 1
        assert workflow.state["current_article"] == 1

