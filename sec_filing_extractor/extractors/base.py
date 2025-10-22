"""
Base extractor class.
"""
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Any, Dict

from ..config import Config
from ..exceptions import ExtractionError


logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """
    Abstract base class for all extractors.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize extractor.

        Args:
            config: Configuration object.
        """
        self.config = config or Config()
        logger.info(f"{self.__class__.__name__} initialized")

    @abstractmethod
    def extract(self, source: Path, output_dir: Path, **kwargs) -> Dict[str, Any]:
        """
        Extract data from source file.

        Args:
            source: Source file path.
            output_dir: Output directory for extracted data.
            **kwargs: Additional extractor-specific parameters.

        Returns:
            Dictionary with extraction results.

        Raises:
            ExtractionError: If extraction fails.
        """
        pass

    def validate_source(self, source: Path):
        """
        Validate that source file exists and is readable.

        Args:
            source: Source file path.

        Raises:
            ExtractionError: If source is invalid.
        """
        if not source.exists():
            raise ExtractionError(f"Source file not found: {source}")

        if not source.is_file():
            raise ExtractionError(f"Source is not a file: {source}")

        if not source.stat().st_size:
            raise ExtractionError(f"Source file is empty: {source}")

    def ensure_output_dir(self, output_dir: Path) -> Path:
        """
        Ensure output directory exists.

        Args:
            output_dir: Output directory path.

        Returns:
            Path object for output directory.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
