"""Tests for memory agent."""

import json
import pytest
from pathlib import Path

from orion_vision_core.agents.memory import MemoryAgent, MemoryEntry, PersonaData
from orion_vision_core.core.exceptions import AgentError, ValidationError


class TestMemoryAgent:
    """Test cases for MemoryAgent."""
    
    @pytest.fixture
    def memory_agent(self, test_config):
        """Create a memory agent for testing."""
        return MemoryAgent()
    
    @pytest.mark.asyncio
    async def test_store_memory(self, memory_agent):
        """Test storing a memory."""
        task = {
            "type": "store",
            "content": "Test memory content",
            "tags": ["test"],
            "importance": 5.0,
            "metadata": {"source": "test"}
        }
        
        result = await memory_agent.execute(task)
        
        assert result.success
        assert "memory_id" in result.data
        assert result.data["stored"] is True
    
    @pytest.mark.asyncio
    async def test_retrieve_memory(self, memory_agent):
        """Test retrieving a memory."""
        # First store a memory
        store_task = {
            "type": "store",
            "memory_id": "test_memory",
            "content": "Test content",
            "tags": ["test"]
        }
        store_result = await memory_agent.execute(store_task)
        assert store_result.success
        
        # Then retrieve it
        retrieve_task = {
            "type": "retrieve",
            "memory_id": "test_memory"
        }
        
        result = await memory_agent.execute(retrieve_task)
        
        assert result.success
        assert result.data["content"] == "Test content"
        assert "test" in result.data["tags"]
    
    @pytest.mark.asyncio
    async def test_update_memory(self, memory_agent):
        """Test updating a memory."""
        # First store a memory
        store_task = {
            "type": "store",
            "memory_id": "test_memory",
            "content": "Original content",
            "importance": 3.0
        }
        await memory_agent.execute(store_task)
        
        # Then update it
        update_task = {
            "type": "update",
            "memory_id": "test_memory",
            "content": "Updated content",
            "importance": 7.0
        }
        
        result = await memory_agent.execute(update_task)
        
        assert result.success
        assert result.data["updated"] is True
        
        # Verify the update
        retrieve_task = {
            "type": "retrieve",
            "memory_id": "test_memory"
        }
        retrieve_result = await memory_agent.execute(retrieve_task)
        
        assert retrieve_result.data["content"] == "Updated content"
        assert retrieve_result.data["importance"] == 7.0
    
    @pytest.mark.asyncio
    async def test_delete_memory(self, memory_agent):
        """Test deleting a memory."""
        # First store a memory
        store_task = {
            "type": "store",
            "memory_id": "test_memory",
            "content": "To be deleted"
        }
        await memory_agent.execute(store_task)
        
        # Then delete it
        delete_task = {
            "type": "delete",
            "memory_id": "test_memory"
        }
        
        result = await memory_agent.execute(delete_task)
        
        assert result.success
        assert result.data["deleted"] is True
        
        # Verify it's gone
        retrieve_task = {
            "type": "retrieve",
            "memory_id": "test_memory"
        }
        retrieve_result = await memory_agent.execute(retrieve_task)
        
        assert retrieve_result.success
        assert retrieve_result.data is None
    
    @pytest.mark.asyncio
    async def test_search_memories(self, memory_agent):
        """Test searching memories."""
        # Store some test memories
        memories = [
            {"memory_id": "mem1", "content": "Python programming", "tags": ["code"]},
            {"memory_id": "mem2", "content": "Machine learning", "tags": ["ai"]},
            {"memory_id": "mem3", "content": "Python data science", "tags": ["code", "data"]},
        ]
        
        for memory in memories:
            task = {"type": "store", **memory}
            await memory_agent.execute(task)
        
        # Search by content
        search_task = {
            "type": "search",
            "query": "Python"
        }
        
        result = await memory_agent.execute(search_task)
        
        assert result.success
        assert len(result.data) == 2  # Should find 2 memories with "Python"
        
        # Search by tags
        search_task = {
            "type": "search",
            "tags": ["code"]
        }
        
        result = await memory_agent.execute(search_task)
        
        assert result.success
        assert len(result.data) == 2  # Should find 2 memories with "code" tag
    
    @pytest.mark.asyncio
    async def test_get_persona(self, memory_agent):
        """Test getting persona data."""
        task = {"type": "get_persona"}
        
        result = await memory_agent.execute(task)
        
        assert result.success
        assert isinstance(result.data, dict)
        assert "tone" in result.data
        assert "roles" in result.data
    
    @pytest.mark.asyncio
    async def test_update_persona(self, memory_agent):
        """Test updating persona data."""
        task = {
            "type": "update_persona",
            "tone": "friendly and helpful",
            "language": "en",
            "preferences": {"style": "casual"}
        }
        
        result = await memory_agent.execute(task)
        
        assert result.success
        assert result.data["updated"] is True
        assert result.data["persona"]["tone"] == "friendly and helpful"
    
    @pytest.mark.asyncio
    async def test_validation_errors(self, memory_agent):
        """Test validation errors."""
        # Test invalid task type
        task = {"type": "invalid_type"}
        
        result = await memory_agent.execute(task)
        
        assert not result.success
        assert "Invalid task type" in result.error
        
        # Test missing content for store
        task = {"type": "store"}
        
        result = await memory_agent.execute(task)
        
        assert not result.success
        assert "Content is required" in result.error
        
        # Test missing memory_id for retrieve
        task = {"type": "retrieve"}
        
        result = await memory_agent.execute(task)
        
        assert not result.success
        assert "Memory ID is required" in result.error
    
    @pytest.mark.asyncio
    async def test_cleanup_memories(self, memory_agent):
        """Test memory cleanup."""
        # Store some test memories with different importance
        memories = [
            {"memory_id": "important", "content": "Important", "importance": 9.0},
            {"memory_id": "normal", "content": "Normal", "importance": 5.0},
            {"memory_id": "low", "content": "Low importance", "importance": 1.0},
        ]
        
        for memory in memories:
            task = {"type": "store", **memory}
            await memory_agent.execute(task)
        
        # Cleanup with high minimum importance
        cleanup_task = {
            "type": "cleanup",
            "min_importance": 8.0,
            "max_memories": 10
        }
        
        result = await memory_agent.execute(cleanup_task)
        
        assert result.success
        assert result.data["cleaned"] is True
        assert result.data["deleted_count"] >= 0
