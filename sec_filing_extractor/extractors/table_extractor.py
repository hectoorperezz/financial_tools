"""
Table extraction from HTML filings.
"""
import csv
import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from html.parser import HTMLParser

from .base import BaseExtractor
from ..config import Config
from ..exceptions import ExtractionError


logger = logging.getLogger(__name__)


class SimpleTableParser(HTMLParser):
    """
    Simple HTML parser for extracting tables.

    Handles nested tables by tracking depth. Does not handle colspan/rowspan.
    """

    def __init__(self):
        """Initialize the parser."""
        super().__init__()
        self.tables: List[List[List[str]]] = []
        self._in_table_depth = 0
        self._current_table: Optional[List[List[str]]] = None
        self._current_row: Optional[List[str]] = None
        self._in_cell = False
        self._cell_buffer: List[str] = []

    def handle_starttag(self, tag: str, attrs):
        """Handle opening tags."""
        tag_lower = tag.lower()

        if tag_lower == "table":
            if self._in_table_depth == 0:
                self._current_table = []
            self._in_table_depth += 1

        elif self._in_table_depth > 0:
            if tag_lower == "tr":
                self._current_row = []
            elif tag_lower in ("td", "th"):
                self._in_cell = True
                self._cell_buffer = []

    def handle_endtag(self, tag: str):
        """Handle closing tags."""
        tag_lower = tag.lower()

        if tag_lower == "table":
            if self._in_table_depth > 0:
                self._in_table_depth -= 1
                if self._in_table_depth == 0 and self._current_table is not None:
                    self.tables.append(self._current_table)
                    self._current_table = None

        elif self._in_table_depth > 0:
            if tag_lower in ("td", "th"):
                if self._in_cell:
                    text = self._clean_text("".join(self._cell_buffer))
                    if self._current_row is not None:
                        self._current_row.append(text)
                self._in_cell = False
                self._cell_buffer = []

            elif tag_lower == "tr":
                if self._current_row is not None and self._current_table is not None:
                    self._current_table.append(self._current_row)
                self._current_row = None

    def handle_data(self, data: str):
        """Handle text data."""
        if self._in_table_depth > 0 and self._in_cell:
            self._cell_buffer.append(data)

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Clean cell text by normalizing whitespace.

        Args:
            text: Raw text.

        Returns:
            Cleaned text.
        """
        text = re.sub(r"\s+", " ", text or "")
        return text.strip()


class TableExtractor(BaseExtractor):
    """
    Extracts tables from HTML filing documents.
    """

    def extract(
        self,
        source: Path,
        output_dir: Path,
        min_columns: Optional[int] = None,
        max_tables: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Extract tables from HTML file.

        Args:
            source: HTML file path.
            output_dir: Output directory for CSV files.
            min_columns: Minimum columns to consider a table valid.
            max_tables: Maximum number of tables to extract.

        Returns:
            Dictionary with:
                - csv_files: List of CSV file paths
                - json_file: Path to JSON file with all tables
                - table_count: Number of tables extracted

        Raises:
            ExtractionError: If extraction fails.
        """
        self.validate_source(source)
        self.ensure_output_dir(output_dir)

        if min_columns is None:
            min_columns = self.config.min_table_columns
        if max_tables is None:
            max_tables = self.config.max_tables_per_file

        logger.info(f"Extracting tables from {source}")

        try:
            # Read and parse HTML
            html_content = source.read_text(errors="ignore")
            parser = SimpleTableParser()
            parser.feed(html_content)

            # Filter tables
            filtered_tables = []
            for table in parser.tables:
                # Find widest row
                max_cols = max((len(row) for row in table if isinstance(row, list)), default=0)
                if max_cols >= min_columns:
                    filtered_tables.append(table)

                if len(filtered_tables) >= max_tables:
                    break

            logger.info(f"Found {len(filtered_tables)} valid tables")

            # Export to CSV files
            csv_files = []
            stem = source.stem

            for i, table in enumerate(filtered_tables, start=1):
                csv_path = output_dir / f"{stem}_table_{i}.csv"
                self._write_table_csv(table, csv_path)
                csv_files.append(csv_path)

            # Export to JSON
            json_path = output_dir / f"{stem}_tables.json"
            self._write_tables_json(filtered_tables, json_path, source)

            result = {
                "csv_files": [str(p) for p in csv_files],
                "json_file": str(json_path),
                "table_count": len(filtered_tables),
                "source": str(source)
            }

            logger.info(f"Extracted {len(filtered_tables)} tables")
            return result

        except Exception as e:
            logger.error(f"Table extraction failed: {e}")
            raise ExtractionError(f"Failed to extract tables: {e}") from e

    def _write_table_csv(self, table: List[List[str]], output_path: Path):
        """
        Write a single table to CSV.

        Args:
            table: Table data as list of rows.
            output_path: Output CSV path.
        """
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for row in table:
                    writer.writerow(row)
            logger.debug(f"Wrote table to {output_path}")

        except Exception as e:
            logger.warning(f"Failed to write CSV {output_path}: {e}")
            raise

    def _write_tables_json(
        self,
        tables: List[List[List[str]]],
        output_path: Path,
        source: Path
    ):
        """
        Write all tables to JSON file.

        Args:
            tables: List of tables.
            output_path: Output JSON path.
            source: Source file path.
        """
        try:
            data = {
                "source": str(source),
                "table_count": len(tables),
                "tables": tables
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.debug(f"Wrote tables JSON to {output_path}")

        except Exception as e:
            logger.warning(f"Failed to write JSON {output_path}: {e}")
            raise
