"""Memory management agent for Orion Vision Core."""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from ..core.base_agent import BaseAgent
from ..core.config import get_config
from ..core.exceptions import AgentError, ValidationError


class MemoryEntry(BaseModel):
    """Memory entry model."""

    id: str = Field(..., description="Unique memory ID")
    content: Any = Field(..., description="Memory content")
    timestamp: float = Field(default_factory=time.time, description="Creation timestamp")
    tags: List[str] = Field(default_factory=list, description="Memory tags")
    importance: float = Field(1.0, ge=0, le=10, description="Memory importance (0-10)")
    access_count: int = Field(0, ge=0, description="Number of times accessed")
    last_accessed: Optional[float] = Field(None, description="Last access timestamp")
    expires_at: Optional[float] = Field(None, description="Expiration timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PersonaData(BaseModel):
    """Persona data model."""

    tone: str = Field(..., description="Personality tone")
    roles: str = Field(..., description="Roles")
    language: str = Field("tr", description="Primary language")
    response_style: str = Field("professional", description="Response style")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    context: Dict[str, Any] = Field(default_factory=dict, description="Current context")


class MemoryAgent(BaseAgent):
    """Agent for memory management operations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize MemoryAgent.

        Args:
            config: Agent configuration
        """
        super().__init__("memory_agent", config)

        self._config = get_config()
        self._memory_file = self._config.memory_dir / "orion_memory_v2.json"
        self._persona_file = self._config.config_dir / "persona.json"

        # In-memory storage
        self._memories: Dict[str, MemoryEntry] = {}
        self._persona: Optional[PersonaData] = None

        # Load existing data
        self._load_memory()
        self._load_persona()

    def _load_memory(self) -> None:
        """Load memory from file."""
        try:
            if self._memory_file.exists():
                with open(self._memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Convert to MemoryEntry objects
                if isinstance(data, dict):
                    for memory_id, memory_data in data.items():
                        if isinstance(memory_data, dict):
                            # Ensure required fields
                            if 'id' not in memory_data:
                                memory_data['id'] = memory_id

                            try:
                                self._memories[memory_id] = MemoryEntry(**memory_data)
                            except Exception as e:
                                self.logger.warning(f"Failed to load memory entry {memory_id}: {e}")

                self.logger.info(f"Loaded {len(self._memories)} memory entries")
            else:
                self.logger.info("No existing memory file found, starting with empty memory")

        except Exception as e:
            self.logger.error(f"Failed to load memory: {e}")
            self._memories = {}

    def _load_persona(self) -> None:
        """Load persona from file."""
        try:
            if self._persona_file.exists():
                with open(self._persona_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Map old format to new format
                persona_data = {
                    "tone": data.get("ton", "dürüst, stratejik, sakin"),
                    "roles": data.get("roller", "danışman, analizci, teknik asistan"),
                    "language": data.get("language", "tr"),
                    "response_style": data.get("response_style", "professional"),
                    "preferences": data.get("preferences", {}),
                    "context": data.get("context", {}),
                }

                self._persona = PersonaData(**persona_data)
                self.logger.info("Loaded persona data")
            else:
                # Create default persona
                self._persona = PersonaData(
                    tone="dürüst, stratejik, sakin",
                    roles="danışman, analizci, teknik asistan",
                    language="tr",
                    response_style="professional"
                )
                self.logger.info("Created default persona")

        except Exception as e:
            self.logger.error(f"Failed to load persona: {e}")
            self._persona = PersonaData(
                tone="dürüst, stratejik, sakin",
                roles="danışman, analizci, teknik asistan",
                language="tr",
                response_style="professional"
            )

    async def _custom_validate_task(self, task: Dict[str, Any]) -> None:
        """Validate memory agent specific tasks."""
        task_type = task.get("type")

        valid_types = [
            "store", "retrieve", "update", "delete", "search",
            "get_persona", "update_persona", "cleanup", "export", "import"
        ]

        if task_type not in valid_types:
            raise ValidationError(
                f"Invalid task type: {task_type}",
                field_name="type",
                error_code="INVALID_TASK_TYPE"
            )

        # Validate required fields for specific tasks
        if task_type in ["store", "update"] and "content" not in task:
            raise ValidationError(
                "Content is required for store/update operations",
                field_name="content",
                error_code="MISSING_CONTENT"
            )

        if task_type in ["retrieve", "update", "delete"] and "memory_id" not in task:
            raise ValidationError(
                "Memory ID is required for retrieve/update/delete operations",
                field_name="memory_id",
                error_code="MISSING_MEMORY_ID"
            )

    async def _execute_task(self, task: Dict[str, Any]) -> Any:
        """Execute memory agent task."""
        task_type = task.get("type")

        if task_type == "store":
            return await self._store_memory(task)
        elif task_type == "retrieve":
            return await self._retrieve_memory(task)
        elif task_type == "update":
            return await self._update_memory(task)
        elif task_type == "delete":
            return await self._delete_memory(task)
        elif task_type == "search":
            return await self._search_memories(task)
        elif task_type == "get_persona":
            return await self._get_persona()
        elif task_type == "update_persona":
            return await self._update_persona(task)
        elif task_type == "cleanup":
            return await self._cleanup_memories(task)
        elif task_type == "export":
            return await self._export_memories(task)
        elif task_type == "import":
            return await self._import_memories(task)
        else:
            raise AgentError(
                f"Unknown task type: {task_type}",
                agent_name=self.name,
                error_code="UNKNOWN_TASK_TYPE"
            )

    async def _store_memory(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Store a new memory entry."""
        try:
            memory_id = task.get("memory_id", f"mem_{int(time.time() * 1000)}")
            content = task["content"]
            tags = task.get("tags", [])
            importance = task.get("importance", 1.0)
            expires_in = task.get("expires_in")  # seconds
            metadata = task.get("metadata", {})

            # Calculate expiration
            expires_at = None
            if expires_in:
                expires_at = time.time() + expires_in

            # Create memory entry
            memory_entry = MemoryEntry(
                id=memory_id,
                content=content,
                tags=tags,
                importance=importance,
                expires_at=expires_at,
                metadata=metadata
            )

            self._memories[memory_id] = memory_entry
            await self._save_memory()

            self.logger.info(f"Stored memory: {memory_id}")

            return {
                "memory_id": memory_id,
                "stored": True,
                "timestamp": memory_entry.timestamp
            }

        except Exception as e:
            raise AgentError(
                f"Failed to store memory: {e}",
                agent_name=self.name,
                error_code="STORE_FAILED"
            )

    async def _retrieve_memory(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieve a memory entry."""
        try:
            memory_id = task["memory_id"]

            if memory_id not in self._memories:
                return None

            memory_entry = self._memories[memory_id]

            # Check if expired
            if memory_entry.expires_at and time.time() > memory_entry.expires_at:
                del self._memories[memory_id]
                await self._save_memory()
                return None

            # Update access statistics
            memory_entry.access_count += 1
            memory_entry.last_accessed = time.time()

            self.logger.info(f"Retrieved memory: {memory_id}")

            return {
                "memory_id": memory_id,
                "content": memory_entry.content,
                "timestamp": memory_entry.timestamp,
                "tags": memory_entry.tags,
                "importance": memory_entry.importance,
                "access_count": memory_entry.access_count,
                "metadata": memory_entry.metadata
            }

        except Exception as e:
            raise AgentError(
                f"Failed to retrieve memory: {e}",
                agent_name=self.name,
                error_code="RETRIEVE_FAILED"
            )

    async def _update_memory(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing memory entry."""
        try:
            memory_id = task["memory_id"]

            if memory_id not in self._memories:
                raise AgentError(
                    f"Memory not found: {memory_id}",
                    agent_name=self.name,
                    error_code="MEMORY_NOT_FOUND"
                )

            memory_entry = self._memories[memory_id]

            # Update fields
            if "content" in task:
                memory_entry.content = task["content"]
            if "tags" in task:
                memory_entry.tags = task["tags"]
            if "importance" in task:
                memory_entry.importance = task["importance"]
            if "metadata" in task:
                memory_entry.metadata.update(task["metadata"])

            await self._save_memory()

            self.logger.info(f"Updated memory: {memory_id}")

            return {
                "memory_id": memory_id,
                "updated": True,
                "timestamp": time.time()
            }

        except Exception as e:
            raise AgentError(
                f"Failed to update memory: {e}",
                agent_name=self.name,
                error_code="UPDATE_FAILED"
            )

    async def _delete_memory(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a memory entry."""
        try:
            memory_id = task["memory_id"]

            if memory_id not in self._memories:
                return {"memory_id": memory_id, "deleted": False, "reason": "not_found"}

            del self._memories[memory_id]
            await self._save_memory()

            self.logger.info(f"Deleted memory: {memory_id}")

            return {
                "memory_id": memory_id,
                "deleted": True,
                "timestamp": time.time()
            }

        except Exception as e:
            raise AgentError(
                f"Failed to delete memory: {e}",
                agent_name=self.name,
                error_code="DELETE_FAILED"
            )

    async def _search_memories(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search memories by content, tags, or metadata."""
        try:
            query = task.get("query", "")
            tags = task.get("tags", [])
            min_importance = task.get("min_importance", 0)
            max_results = task.get("max_results", 100)

            results = []

            for memory_id, memory_entry in self._memories.items():
                # Check expiration
                if memory_entry.expires_at and time.time() > memory_entry.expires_at:
                    continue

                # Check importance
                if memory_entry.importance < min_importance:
                    continue

                # Check tags
                if tags and not any(tag in memory_entry.tags for tag in tags):
                    continue

                # Check content
                if query:
                    content_str = str(memory_entry.content).lower()
                    if query.lower() not in content_str:
                        continue

                results.append({
                    "memory_id": memory_id,
                    "content": memory_entry.content,
                    "timestamp": memory_entry.timestamp,
                    "tags": memory_entry.tags,
                    "importance": memory_entry.importance,
                    "access_count": memory_entry.access_count,
                    "metadata": memory_entry.metadata
                })

            # Sort by importance and access count
            results.sort(key=lambda x: (x["importance"], x["access_count"]), reverse=True)

            return results[:max_results]

        except Exception as e:
            raise AgentError(
                f"Failed to search memories: {e}",
                agent_name=self.name,
                error_code="SEARCH_FAILED"
            )

    async def _get_persona(self) -> Dict[str, Any]:
        """Get current persona data."""
        if self._persona:
            return self._persona.model_dump()
        return {}

    async def _update_persona(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Update persona data."""
        try:
            if not self._persona:
                self._persona = PersonaData(
                    tone="dürüst, stratejik, sakin",
                    roles="danışman, analizci, teknik asistan",
                    language="tr",
                    response_style="professional"
                )

            # Update fields
            if "tone" in task:
                self._persona.tone = task["tone"]
            if "roles" in task:
                self._persona.roles = task["roles"]
            if "language" in task:
                self._persona.language = task["language"]
            if "response_style" in task:
                self._persona.response_style = task["response_style"]
            if "preferences" in task:
                self._persona.preferences.update(task["preferences"])
            if "context" in task:
                self._persona.context.update(task["context"])

            await self._save_persona()

            self.logger.info("Updated persona data")

            return {
                "updated": True,
                "timestamp": time.time(),
                "persona": self._persona.model_dump()
            }

        except Exception as e:
            raise AgentError(
                f"Failed to update persona: {e}",
                agent_name=self.name,
                error_code="PERSONA_UPDATE_FAILED"
            )

    async def _cleanup_memories(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up expired and low-importance memories."""
        try:
            max_age_days = task.get("max_age_days", 30)
            min_importance = task.get("min_importance", 1.0)
            max_memories = task.get("max_memories", 1000)

            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 60 * 60

            deleted_count = 0
            expired_count = 0

            # Remove expired memories
            expired_ids = []
            for memory_id, memory_entry in self._memories.items():
                if memory_entry.expires_at and current_time > memory_entry.expires_at:
                    expired_ids.append(memory_id)

            for memory_id in expired_ids:
                del self._memories[memory_id]
                expired_count += 1

            # Remove old low-importance memories
            if len(self._memories) > max_memories:
                # Sort by importance and age
                memory_items = list(self._memories.items())
                memory_items.sort(key=lambda x: (x[1].importance, x[1].timestamp))

                # Remove oldest, lowest importance memories
                to_remove = len(self._memories) - max_memories
                for i in range(to_remove):
                    memory_id = memory_items[i][0]
                    del self._memories[memory_id]
                    deleted_count += 1

            # Remove very old memories
            cutoff_time = current_time - max_age_seconds
            old_ids = []
            for memory_id, memory_entry in self._memories.items():
                if (memory_entry.timestamp < cutoff_time and
                    memory_entry.importance < min_importance):
                    old_ids.append(memory_id)

            for memory_id in old_ids:
                del self._memories[memory_id]
                deleted_count += 1

            await self._save_memory()

            self.logger.info(f"Cleaned up memories: {expired_count} expired, {deleted_count} deleted")

            return {
                "cleaned": True,
                "expired_count": expired_count,
                "deleted_count": deleted_count,
                "remaining_count": len(self._memories),
                "timestamp": time.time()
            }

        except Exception as e:
            raise AgentError(
                f"Failed to cleanup memories: {e}",
                agent_name=self.name,
                error_code="CLEANUP_FAILED"
            )

    async def _export_memories(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Export memories to file."""
        try:
            export_path = task.get("export_path", "memory_export.json")
            include_expired = task.get("include_expired", False)

            export_data = {}
            current_time = time.time()

            for memory_id, memory_entry in self._memories.items():
                # Skip expired if not including them
                if (not include_expired and
                    memory_entry.expires_at and
                    current_time > memory_entry.expires_at):
                    continue

                export_data[memory_id] = memory_entry.model_dump()

            # Write to file
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)

            self.logger.info(f"Exported {len(export_data)} memories to {export_path}")

            return {
                "exported": True,
                "export_path": export_path,
                "count": len(export_data),
                "timestamp": time.time()
            }

        except Exception as e:
            raise AgentError(
                f"Failed to export memories: {e}",
                agent_name=self.name,
                error_code="EXPORT_FAILED"
            )

    async def _import_memories(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Import memories from file."""
        try:
            import_path = task["import_path"]
            overwrite = task.get("overwrite", False)

            # Load data from file
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            imported_count = 0
            skipped_count = 0

            for memory_id, memory_data in import_data.items():
                # Skip if exists and not overwriting
                if memory_id in self._memories and not overwrite:
                    skipped_count += 1
                    continue

                try:
                    # Ensure required fields
                    if 'id' not in memory_data:
                        memory_data['id'] = memory_id

                    memory_entry = MemoryEntry(**memory_data)
                    self._memories[memory_id] = memory_entry
                    imported_count += 1

                except Exception as e:
                    self.logger.warning(f"Failed to import memory {memory_id}: {e}")
                    skipped_count += 1

            await self._save_memory()

            self.logger.info(f"Imported {imported_count} memories from {import_path}")

            return {
                "imported": True,
                "import_path": import_path,
                "imported_count": imported_count,
                "skipped_count": skipped_count,
                "timestamp": time.time()
            }

        except Exception as e:
            raise AgentError(
                f"Failed to import memories: {e}",
                agent_name=self.name,
                error_code="IMPORT_FAILED"
            )

    async def _save_memory(self) -> None:
        """Save memories to file."""
        try:
            self._memory_file.parent.mkdir(parents=True, exist_ok=True)

            # Convert to serializable format
            save_data = {}
            for memory_id, memory_entry in self._memories.items():
                save_data[memory_id] = memory_entry.model_dump()

            # Write to file
            with open(self._memory_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False, default=str)

        except Exception as e:
            raise AgentError(
                f"Failed to save memory: {e}",
                agent_name=self.name,
                error_code="SAVE_FAILED"
            )

    async def _save_persona(self) -> None:
        """Save persona to file."""
        try:
            self._persona_file.parent.mkdir(parents=True, exist_ok=True)

            if self._persona:
                # Convert to old format for compatibility
                save_data = {
                    "ton": self._persona.tone,
                    "roller": self._persona.roles,
                    "language": self._persona.language,
                    "response_style": self._persona.response_style,
                    "preferences": self._persona.preferences,
                    "context": self._persona.context,
                }

                with open(self._persona_file, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            raise AgentError(
                f"Failed to save persona: {e}",
                agent_name=self.name,
                error_code="PERSONA_SAVE_FAILED"
            )


# Legacy class for backward compatibility
class MemoryManager:
    """Legacy memory manager for backward compatibility."""

    def __init__(self, persona_file: str, memory_file: str):
        """Initialize legacy memory manager."""
        self.persona_file = persona_file
        self.memory_file = memory_file
        self._agent = MemoryAgent()

    def load_json(self, file_path: str) -> Dict[str, Any]:
        """Load JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_persona(self) -> Dict[str, Any]:
        """Get persona data."""
        import asyncio
        return asyncio.run(self._agent._get_persona())

    def get_memory(self) -> Dict[str, Any]:
        """Get all memories."""
        return {
            memory_id: entry.model_dump()
            for memory_id, entry in self._agent._memories.items()
        }

    def update_memory(self, new_memory: Any) -> None:
        """Update memory (legacy method)."""
        import asyncio
        memory_id = f"legacy_{int(time.time() * 1000)}"
        task = {
            "type": "store",
            "memory_id": memory_id,
            "content": new_memory,
            "tags": ["legacy"],
            "importance": 5.0
        }
        asyncio.run(self._agent.execute(task))

    def save_memory(self, memory_file: str) -> None:
        """Save memory to file."""
        import asyncio
        asyncio.run(self._agent._save_memory())
