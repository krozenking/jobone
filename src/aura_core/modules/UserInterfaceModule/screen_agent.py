"""Screen capture and OCR agent for Orion Vision Core."""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import easyocr
import mss
import numpy as np
import pytesseract
from PIL import Image
from pydantic import BaseModel, Field

from ..core.base_agent import BaseAgent
from ..core.exceptions import AgentError, ValidationError


class ScreenRegion(BaseModel):
    """Screen region model."""

    x: int = Field(..., ge=0, description="X coordinate")
    y: int = Field(..., ge=0, description="Y coordinate")
    width: int = Field(..., gt=0, description="Width in pixels")
    height: int = Field(..., gt=0, description="Height in pixels")


class OCRResult(BaseModel):
    """OCR result model."""

    text: str = Field(..., description="Extracted text")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    bbox: Optional[List[int]] = Field(None, description="Bounding box coordinates")
    language: str = Field("tr", description="Detected language")


class UIElement(BaseModel):
    """UI element model."""

    x: int = Field(..., description="X coordinate")
    y: int = Field(..., description="Y coordinate")
    width: int = Field(..., description="Width")
    height: int = Field(..., description="Height")
    confidence: float = Field(..., description="Match confidence")
    template_name: str = Field(..., description="Template name")


class ScreenAgent(BaseAgent):
    """Agent for screen capture and analysis operations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize ScreenAgent.

        Args:
            config: Agent configuration
        """
        super().__init__("screen_agent", config)

        # Initialize OCR reader
        self._ocr_reader: Optional[easyocr.Reader] = None
        self._initialize_ocr()

    def _initialize_ocr(self) -> None:
        """Initialize OCR reader."""
        try:
            languages = self.config.config.get("ocr_languages", ["tr", "en"])
            use_gpu = self.config.config.get("use_gpu", False)

            self._ocr_reader = easyocr.Reader(languages, gpu=use_gpu)
            self.logger.info(f"OCR reader initialized with languages: {languages}")

        except Exception as e:
            self.logger.error(f"Failed to initialize OCR reader: {e}")
            raise AgentError(
                f"Failed to initialize OCR reader: {e}",
                agent_name=self.name,
                error_code="OCR_INIT_FAILED"
            )

    async def _custom_validate_task(self, task: Dict[str, Any]) -> None:
        """Validate screen agent specific tasks."""
        task_type = task.get("type")

        if task_type not in ["capture", "ocr", "find_ui_elements"]:
            raise ValidationError(
                f"Invalid task type: {task_type}",
                field_name="type",
                error_code="INVALID_TASK_TYPE"
            )

        if task_type == "find_ui_elements":
            template_path = task.get("template_path")
            if not template_path or not Path(template_path).exists():
                raise ValidationError(
                    f"Template file not found: {template_path}",
                    field_name="template_path",
                    error_code="TEMPLATE_NOT_FOUND"
                )

    async def _execute_task(self, task: Dict[str, Any]) -> Any:
        """Execute screen agent task."""
        task_type = task.get("type")

        if task_type == "capture":
            return await self._capture_screenshot(task.get("region"))
        elif task_type == "ocr":
            return await self._perform_ocr(task)
        elif task_type == "find_ui_elements":
            return await self._find_ui_elements(task)
        else:
            raise AgentError(
                f"Unknown task type: {task_type}",
                agent_name=self.name,
                error_code="UNKNOWN_TASK_TYPE"
            )

    async def _capture_screenshot(
        self,
        region: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Capture screenshot of screen or region.

        Args:
            region: Optional region to capture (x, y, width, height)

        Returns:
            Screenshot data and metadata
        """
        try:
            with mss.mss() as sct:
                if region:
                    # Validate region
                    screen_region = ScreenRegion(**region)
                    monitor = {
                        "top": screen_region.y,
                        "left": screen_region.x,
                        "width": screen_region.width,
                        "height": screen_region.height
                    }
                else:
                    monitor = sct.monitors[1]  # Primary monitor

                # Capture screenshot
                sct_img = sct.grab(monitor)
                img_array = np.array(sct_img)

                # Convert to RGB (mss returns BGRA)
                img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGRA2RGB)

                return {
                    "image": img_rgb,
                    "shape": img_rgb.shape,
                    "region": region,
                    "monitor_info": monitor,
                    "timestamp": asyncio.get_event_loop().time()
                }

        except Exception as e:
            raise AgentError(
                f"Screenshot capture failed: {e}",
                agent_name=self.name,
                error_code="CAPTURE_FAILED"
            )

    async def _perform_ocr(self, task: Dict[str, Any]) -> List[OCRResult]:
        """Perform OCR on image or screen region.

        Args:
            task: Task containing image data or region info

        Returns:
            List of OCR results
        """
        try:
            # Get image
            if "image" in task:
                image = task["image"]
            else:
                # Capture screenshot first
                capture_result = await self._capture_screenshot(task.get("region"))
                image = capture_result["image"]

            # Perform OCR with EasyOCR
            results = []
            if self._ocr_reader:
                ocr_results = self._ocr_reader.readtext(image)

                for bbox, text, confidence in ocr_results:
                    # Convert bbox to list of ints
                    bbox_coords = [int(coord) for point in bbox for coord in point]

                    results.append(OCRResult(
                        text=text.strip(),
                        confidence=float(confidence),
                        bbox=bbox_coords,
                        language=task.get("language", "tr")
                    ))

            # Fallback to Tesseract if EasyOCR fails or not available
            if not results:
                try:
                    # Convert to PIL Image for Tesseract
                    pil_image = Image.fromarray(image)

                    # Get text with confidence
                    lang = task.get("language", "tur")
                    text = pytesseract.image_to_string(pil_image, lang=lang)

                    if text.strip():
                        results.append(OCRResult(
                            text=text.strip(),
                            confidence=0.8,  # Default confidence for Tesseract
                            language=lang
                        ))

                except Exception as tesseract_error:
                    self.logger.warning(f"Tesseract OCR failed: {tesseract_error}")

            return results

        except Exception as e:
            raise AgentError(
                f"OCR processing failed: {e}",
                agent_name=self.name,
                error_code="OCR_FAILED"
            )

    async def _find_ui_elements(self, task: Dict[str, Any]) -> List[UIElement]:
        """Find UI elements using template matching.

        Args:
            task: Task containing template path and optional image

        Returns:
            List of found UI elements
        """
        try:
            template_path = task["template_path"]
            threshold = task.get("threshold", 0.8)

            # Get image
            if "image" in task:
                image = task["image"]
            else:
                capture_result = await self._capture_screenshot(task.get("region"))
                image = capture_result["image"]

            # Load template
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                raise AgentError(
                    f"Could not load template: {template_path}",
                    agent_name=self.name,
                    error_code="TEMPLATE_LOAD_FAILED"
                )

            # Convert image to grayscale
            gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # Perform template matching
            result = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)

            # Extract UI elements
            ui_elements = []
            template_name = Path(template_path).stem
            h, w = template.shape

            for pt in zip(*locations[::-1]):
                ui_elements.append(UIElement(
                    x=int(pt[0]),
                    y=int(pt[1]),
                    width=w,
                    height=h,
                    confidence=float(result[pt[1], pt[0]]),
                    template_name=template_name
                ))

            return ui_elements

        except Exception as e:
            raise AgentError(
                f"UI element detection failed: {e}",
                agent_name=self.name,
                error_code="UI_DETECTION_FAILED"
            )


# Legacy function wrappers for backward compatibility
async def capture_screenshot(region: Optional[Dict[str, int]] = None) -> np.ndarray:
    """Legacy function for capturing screenshots."""
    agent = ScreenAgent()
    task = {"type": "capture", "region": region}
    result = await agent.execute(task)
    return result.data["image"]


async def perform_ocr(image: np.ndarray) -> str:
    """Legacy function for performing OCR."""
    agent = ScreenAgent()
    task = {"type": "ocr", "image": image}
    result = await agent.execute(task)

    if result.success and result.data:
        return " ".join([ocr_result.text for ocr_result in result.data])
    return ""


async def find_ui_elements(
    image: np.ndarray,
    template_path: str,
    threshold: float = 0.8
) -> List[Tuple[int, int, int, int]]:
    """Legacy function for finding UI elements."""
    agent = ScreenAgent()
    task = {
        "type": "find_ui_elements",
        "image": image,
        "template_path": template_path,
        "threshold": threshold
    }
    result = await agent.execute(task)

    if result.success and result.data:
        return [(elem.x, elem.y, elem.width, elem.height) for elem in result.data]
    return []
