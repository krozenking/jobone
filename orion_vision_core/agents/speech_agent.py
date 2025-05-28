"""Speech recognition agent for Orion Vision Core."""

import asyncio
import io
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
from pydantic import BaseModel, Field

from ..core.base_agent import BaseAgent
from ..core.exceptions import AgentError, ValidationError


class AudioFormat(BaseModel):
    """Audio format specification."""

    sample_rate: int = Field(16000, description="Sample rate in Hz")
    channels: int = Field(1, description="Number of audio channels")
    bit_depth: int = Field(16, description="Bit depth")
    format: str = Field("wav", description="Audio format")


class TranscriptionRequest(BaseModel):
    """Speech transcription request model."""

    audio_data: Optional[bytes] = Field(None, description="Raw audio data")
    audio_file_path: Optional[str] = Field(None, description="Path to audio file")
    language: Optional[str] = Field("auto", description="Language code (auto-detect if None)")
    model_size: str = Field("base", description="Whisper model size")
    temperature: float = Field(0.0, ge=0, le=1, description="Sampling temperature")
    audio_format: AudioFormat = Field(default_factory=lambda: AudioFormat(), description="Audio format")


class TranscriptionResult(BaseModel):
    """Speech transcription result model."""

    text: str = Field(..., description="Transcribed text")
    language: Optional[str] = Field(None, description="Detected language")
    confidence: float = Field(0.0, ge=0, le=1, description="Confidence score")
    segments: List[Dict[str, Any]] = Field(default_factory=list, description="Transcription segments")
    processing_time: float = Field(..., description="Processing time in seconds")
    model_used: str = Field(..., description="Model used for transcription")


class SpeechAgent(BaseAgent):
    """Agent for speech recognition and transcription."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize SpeechAgent.

        Args:
            config: Agent configuration
        """
        super().__init__("speech_agent", config)

        # Model configuration
        self._model_size = self.config.config.get("model_size", "base")
        self._language = self.config.config.get("language", "auto")
        self._use_gpu = self.config.config.get("use_gpu", False)

        # Initialize models
        self._whisper_model = None
        self._fallback_available = False

        self._initialize_models()

    def _initialize_models(self) -> None:
        """Initialize speech recognition models."""
        try:
            # Try to import and initialize Whisper
            self._initialize_whisper()

        except Exception as e:
            self.logger.warning(f"Failed to initialize speech models: {e}")
            self._whisper_model = None

    def _initialize_whisper(self) -> None:
        """Initialize Whisper model."""
        try:
            # Try OpenAI Whisper first
            try:
                import whisper

                device = "cuda" if self._use_gpu else "cpu"
                self._whisper_model = whisper.load_model(
                    self._model_size,
                    device=device
                )
                self._model_type = "openai_whisper"
                self.logger.info(f"OpenAI Whisper model loaded: {self._model_size} on {device}")

            except ImportError:
                # Fallback to whisper-cpp if available
                try:
                    import whispercpp

                    self._whisper_model = whispercpp.Whisper()
                    self._model_type = "whisper_cpp"
                    self.logger.info("Whisper-cpp model loaded")

                except ImportError:
                    self.logger.warning("No Whisper implementation available")
                    self._model_type = "none"

        except Exception as e:
            raise AgentError(
                f"Failed to initialize Whisper model: {e}",
                agent_name=self.name,
                error_code="WHISPER_INIT_FAILED"
            )

    async def _custom_validate_task(self, task: Dict[str, Any]) -> None:
        """Validate speech agent specific tasks."""
        task_type = task.get("type")

        if task_type not in ["transcribe", "transcribe_file", "transcribe_stream"]:
            raise ValidationError(
                f"Invalid task type: {task_type}",
                field_name="type",
                error_code="INVALID_TASK_TYPE"
            )

        # Check if we have audio data or file path
        if task_type in ["transcribe", "transcribe_stream"]:
            if "audio_data" not in task:
                raise ValidationError(
                    "Audio data is required for transcription",
                    field_name="audio_data",
                    error_code="MISSING_AUDIO_DATA"
                )

        if task_type == "transcribe_file":
            if "audio_file_path" not in task:
                raise ValidationError(
                    "Audio file path is required for file transcription",
                    field_name="audio_file_path",
                    error_code="MISSING_FILE_PATH"
                )

            file_path = Path(task["audio_file_path"])
            if not file_path.exists():
                raise ValidationError(
                    f"Audio file not found: {file_path}",
                    field_name="audio_file_path",
                    error_code="FILE_NOT_FOUND"
                )

    async def _execute_task(self, task: Dict[str, Any]) -> TranscriptionResult:
        """Execute speech agent task."""
        task_type = task.get("type")

        if task_type == "transcribe":
            return await self._transcribe_audio(task)
        elif task_type == "transcribe_file":
            return await self._transcribe_file(task)
        elif task_type == "transcribe_stream":
            return await self._transcribe_stream(task)
        else:
            raise AgentError(
                f"Unknown task type: {task_type}",
                agent_name=self.name,
                error_code="UNKNOWN_TASK_TYPE"
            )

    async def _transcribe_audio(self, task: Dict[str, Any]) -> TranscriptionResult:
        """Transcribe audio data."""
        try:
            # Create transcription request
            request = TranscriptionRequest(
                audio_data=task["audio_data"],
                language=task.get("language", self._language),
                model_size=task.get("model_size", self._model_size),
                temperature=task.get("temperature", 0.0),
                audio_format=AudioFormat(**task.get("audio_format", {}))
            )

            start_time = time.time()

            # Perform transcription
            if self._model_type == "openai_whisper":
                result = await self._transcribe_with_openai_whisper(request)
            elif self._model_type == "whisper_cpp":
                result = await self._transcribe_with_whisper_cpp(request)
            else:
                raise AgentError(
                    "No speech recognition model available",
                    agent_name=self.name,
                    error_code="NO_MODEL_AVAILABLE"
                )

            processing_time = time.time() - start_time
            result.processing_time = processing_time
            result.model_used = f"{self._model_type}_{self._model_size}"

            self.logger.info(
                f"Transcription completed",
                text_length=len(result.text),
                processing_time=processing_time,
                language=result.language
            )

            return result

        except Exception as e:
            raise AgentError(
                f"Audio transcription failed: {e}",
                agent_name=self.name,
                error_code="TRANSCRIPTION_FAILED"
            )

    async def _transcribe_file(self, task: Dict[str, Any]) -> TranscriptionResult:
        """Transcribe audio file."""
        try:
            file_path = Path(task["audio_file_path"])

            # Read audio file
            with open(file_path, "rb") as f:
                audio_data = f.read()

            # Create modified task with audio data
            audio_task = task.copy()
            audio_task["audio_data"] = audio_data
            audio_task["type"] = "transcribe"

            return await self._transcribe_audio(audio_task)

        except Exception as e:
            raise AgentError(
                f"File transcription failed: {e}",
                agent_name=self.name,
                error_code="FILE_TRANSCRIPTION_FAILED"
            )

    async def _transcribe_stream(self, task: Dict[str, Any]) -> TranscriptionResult:
        """Transcribe streaming audio data."""
        # For now, treat streaming the same as regular transcription
        # In the future, this could handle real-time streaming
        return await self._transcribe_audio(task)

    async def _transcribe_with_openai_whisper(self, request: TranscriptionRequest) -> TranscriptionResult:
        """Transcribe using OpenAI Whisper."""
        try:
            import tempfile

            if not request.audio_data:
                raise AgentError(
                    "No audio data provided",
                    agent_name=self.name,
                    error_code="NO_AUDIO_DATA"
                )

            if not self._whisper_model:
                raise AgentError(
                    "Whisper model not initialized",
                    agent_name=self.name,
                    error_code="MODEL_NOT_INITIALIZED"
                )

            # Create temporary file for audio data
            with tempfile.NamedTemporaryFile(suffix=f".{request.audio_format.format}", delete=False) as temp_file:
                temp_file.write(request.audio_data)
                temp_path = temp_file.name

            try:
                # Transcribe with Whisper
                result = self._whisper_model.transcribe(
                    temp_path,
                    language=None if request.language == "auto" else request.language,
                    temperature=request.temperature,
                    verbose=False
                )

                # Extract segments
                segments = []
                if "segments" in result:
                    segments = [
                        {
                            "start": seg.get("start", 0),
                            "end": seg.get("end", 0),
                            "text": seg.get("text", ""),
                            "confidence": seg.get("avg_logprob", 0)
                        }
                        for seg in result["segments"]
                    ]

                return TranscriptionResult(
                    text=result["text"].strip(),
                    language=result.get("language"),
                    confidence=0.0,  # OpenAI Whisper doesn't provide overall confidence
                    segments=segments,
                    processing_time=0.0,  # Will be set by caller
                    model_used=""  # Will be set by caller
                )

            finally:
                # Clean up temporary file
                Path(temp_path).unlink(missing_ok=True)

        except Exception as e:
            raise AgentError(
                f"OpenAI Whisper transcription failed: {e}",
                agent_name=self.name,
                error_code="OPENAI_WHISPER_FAILED"
            )

    async def _transcribe_with_whisper_cpp(self, request: TranscriptionRequest) -> TranscriptionResult:
        """Transcribe using Whisper-cpp."""
        try:
            import numpy as np

            if not request.audio_data:
                raise AgentError(
                    "No audio data provided",
                    agent_name=self.name,
                    error_code="NO_AUDIO_DATA"
                )

            if not self._whisper_model:
                raise AgentError(
                    "Whisper model not initialized",
                    agent_name=self.name,
                    error_code="MODEL_NOT_INITIALIZED"
                )

            # Convert audio data to numpy array
            # This is a simplified conversion - in practice, you'd need proper audio processing
            audio_np = np.frombuffer(request.audio_data, dtype=np.float32)

            # Transcribe with whisper-cpp
            text = self._whisper_model.transcribe(audio_np.tolist())

            return TranscriptionResult(
                text=text.strip() if text else "",
                language=request.language if request.language != "auto" else "en",
                confidence=0.0,  # Whisper-cpp doesn't provide confidence
                segments=[],  # Whisper-cpp doesn't provide segments
                processing_time=0.0,  # Will be set by caller
                model_used=""  # Will be set by caller
            )

        except Exception as e:
            raise AgentError(
                f"Whisper-cpp transcription failed: {e}",
                agent_name=self.name,
                error_code="WHISPER_CPP_FAILED"
            )

    async def _custom_stop(self) -> None:
        """Custom stop logic for speech agent."""
        # Clean up models if needed
        if self._whisper_model:
            try:
                # Some models might need explicit cleanup
                if hasattr(self._whisper_model, 'close'):
                    self._whisper_model.close()
            except Exception as e:
                self.logger.warning(f"Error cleaning up speech model: {e}")


# Legacy function for backward compatibility
async def transcribe_audio(audio_data: bytes, language: str = "auto") -> str:
    """Legacy function for audio transcription."""
    agent = SpeechAgent()
    task = {
        "type": "transcribe",
        "audio_data": audio_data,
        "language": language
    }
    result = await agent.execute(task)

    if result.success:
        return result.data.text
    else:
        return f"Error: {result.error}"


async def transcribe_file(file_path: str, language: str = "auto") -> str:
    """Legacy function for file transcription."""
    agent = SpeechAgent()
    task = {
        "type": "transcribe_file",
        "audio_file_path": file_path,
        "language": language
    }
    result = await agent.execute(task)

    if result.success:
        return result.data.text
    else:
        return f"Error: {result.error}"
