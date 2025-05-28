"""Base agent class for Orion Vision Core."""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field

from .config import get_config
from .exceptions import AgentError, TimeoutError, ValidationError
from .logging import LoggerMixin


class AgentStatus(BaseModel):
    """Agent status model."""

    name: str
    status: str = Field(..., pattern="^(idle|running|paused|error|stopped)$")
    last_activity: float = Field(default_factory=time.time)
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)


class AgentResult(BaseModel):
    """Agent execution result model."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC, LoggerMixin):
    """Base class for all Orion agents."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the agent.

        Args:
            name: Agent name
            config: Agent-specific configuration
        """
        self.name = name
        self.config = get_config().get_agent_config(name)
        if config:
            self.config.config.update(config)

        self.status = AgentStatus(name=name, status="idle")
        self._is_running = False
        self._lock = asyncio.Lock()

        self.logger.info(f"Initialized agent: {name}")

    @property
    def is_running(self) -> bool:
        """Check if agent is currently running."""
        return self._is_running

    @property
    def is_enabled(self) -> bool:
        """Check if agent is enabled."""
        return self.config.enabled

    async def execute(
        self,
        task: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> AgentResult:
        """Execute a task with the agent.

        Args:
            task: Task to execute
            timeout: Optional timeout in seconds

        Returns:
            Agent execution result

        Raises:
            AgentError: If agent is not enabled or already running
            TimeoutError: If execution times out
            ValidationError: If task validation fails
        """
        if not self.is_enabled:
            raise AgentError(
                f"Agent {self.name} is not enabled",
                agent_name=self.name,
                error_code="AGENT_DISABLED"
            )

        async with self._lock:
            if self._is_running:
                raise AgentError(
                    f"Agent {self.name} is already running",
                    agent_name=self.name,
                    error_code="AGENT_BUSY"
                )

            self._is_running = True
            self.status.status = "running"
            self.status.last_activity = time.time()

            start_time = time.time()

            try:
                # Validate task
                await self._validate_task(task)

                # Execute with timeout
                timeout = timeout or self.config.timeout_seconds
                result_data = await asyncio.wait_for(
                    self._execute_task(task),
                    timeout=timeout
                )

                execution_time = time.time() - start_time

                result = AgentResult(
                    success=True,
                    data=result_data,
                    execution_time=execution_time,
                    metadata={
                        "agent_name": self.name,
                        "task_type": task.get("type", "unknown"),
                        "timestamp": time.time(),
                    }
                )

                self.status.status = "idle"
                self.status.error_message = None
                self.status.metrics["last_execution_time"] = execution_time
                self.status.metrics["total_executions"] = (
                    self.status.metrics.get("total_executions", 0) + 1
                )

                self.logger.info(
                    f"Agent {self.name} completed task",
                    execution_time=execution_time,
                    task_type=task.get("type", "unknown")
                )

                return result

            except asyncio.TimeoutError:
                execution_time = time.time() - start_time
                error_msg = f"Agent {self.name} execution timed out after {timeout}s"

                self.status.status = "error"
                self.status.error_message = error_msg

                self.logger.error(error_msg, execution_time=execution_time)

                raise TimeoutError(
                    error_msg,
                    timeout_seconds=timeout,
                    error_code="AGENT_TIMEOUT",
                    details={"agent_name": self.name, "execution_time": execution_time}
                )

            except Exception as e:
                execution_time = time.time() - start_time
                error_msg = f"Agent {self.name} execution failed: {str(e)}"

                self.status.status = "error"
                self.status.error_message = error_msg
                self.status.metrics["total_errors"] = (
                    self.status.metrics.get("total_errors", 0) + 1
                )

                self.logger.error(
                    error_msg,
                    execution_time=execution_time,
                    error=str(e),
                    exc_info=True
                )

                result = AgentResult(
                    success=False,
                    error=error_msg,
                    execution_time=execution_time,
                    metadata={
                        "agent_name": self.name,
                        "task_type": task.get("type", "unknown"),
                        "timestamp": time.time(),
                        "exception_type": type(e).__name__,
                    }
                )

                return result

            finally:
                self._is_running = False
                self.status.last_activity = time.time()

    async def _validate_task(self, task: Dict[str, Any]) -> None:
        """Validate task before execution.

        Args:
            task: Task to validate

        Raises:
            ValidationError: If task is invalid
        """
        if not isinstance(task, dict):
            raise ValidationError(
                "Task must be a dictionary",
                field_name="task",
                error_code="INVALID_TASK_TYPE"
            )

        # Allow subclasses to add custom validation
        await self._custom_validate_task(task)

    async def _custom_validate_task(self, task: Dict[str, Any]) -> None:
        """Custom task validation for subclasses.

        Args:
            task: Task to validate
        """
        pass

    @abstractmethod
    async def _execute_task(self, task: Dict[str, Any]) -> Any:
        """Execute the actual task logic.

        Args:
            task: Task to execute

        Returns:
            Task execution result
        """
        pass

    async def stop(self) -> None:
        """Stop the agent gracefully."""
        self.logger.info(f"Stopping agent: {self.name}")
        self.status.status = "stopped"
        # Allow subclasses to implement custom stop logic
        await self._custom_stop()

    async def _custom_stop(self) -> None:
        """Custom stop logic for subclasses."""
        pass

    def get_status(self) -> AgentStatus:
        """Get current agent status."""
        return self.status.model_copy()

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics."""
        return {
            "name": self.name,
            "status": self.status.status,
            "is_enabled": self.is_enabled,
            "is_running": self.is_running,
            "last_activity": self.status.last_activity,
            "metrics": self.status.metrics.copy(),
        }
