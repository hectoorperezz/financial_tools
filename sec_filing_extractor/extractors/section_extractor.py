"""
Text section extraction from HTML filings.
"""
import re
import logging
import html as html_lib
from pathlib import Path
from typing import Dict, Any, List, Tuple

from .base import BaseExtractor
from ..config import Config
from ..exceptions import ExtractionError


logger = logging.getLogger(__name__)


class SectionExtractor(BaseExtractor):
    """
    Extracts text sections (Items) from HTML filing documents.
    """

    def extract(
        self,
        source: Path,
        output_dir: Path,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract text sections from HTML file.

        Identifies ITEM headers and extracts text content into Markdown files.

        Args:
            source: HTML file path.
            output_dir: Output directory for Markdown files.

        Returns:
            Dictionary with:
                - sections: Dict mapping item IDs to file paths
                - index_file: Path to index file
                - section_count: Number of sections extracted

        Raises:
            ExtractionError: If extraction fails.
        """
        self.validate_source(source)
        self.ensure_output_dir(output_dir)

        logger.info(f"Extracting sections from {source}")

        try:
            # Read and preprocess HTML
            raw_html = source.read_text(errors="ignore")
            text = self._html_to_text(raw_html)

            # Find section boundaries
            sections = self._find_sections(text)

            if not sections:
                logger.warning("No sections found in document")
                return {
                    "sections": {},
                    "index_file": None,
                    "section_count": 0,
                    "source": str(source)
                }

            # Write section files
            section_files = {}
            for item_id, title, content in sections:
                md_path = self._write_section(
                    output_dir,
                    item_id,
                    title,
                    content
                )
                section_files[item_id] = str(md_path)

            # Write index
            index_path = self._write_index(output_dir, sections)

            result = {
                "sections": section_files,
                "index_file": str(index_path),
                "section_count": len(sections),
                "source": str(source)
            }

            logger.info(f"Extracted {len(sections)} sections")
            return result

        except Exception as e:
            logger.error(f"Section extraction failed: {e}")
            raise ExtractionError(f"Failed to extract sections: {e}") from e

    def _html_to_text(self, html: str) -> str:
        """
        Convert HTML to plain text.

        Args:
            html: Raw HTML content.

        Returns:
            Plain text with preserved structure.
        """
        # Remove scripts and styles
        text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
        text = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)

        # Preserve line breaks from block elements
        text = re.sub(r"<(br|/p|/div|/tr|/h\d)>", "\n", text, flags=re.I)

        # Remove remaining tags
        text = re.sub(r"<[^>]+>", " ", text)

        # Unescape HTML entities
        text = html_lib.unescape(text)

        # Normalize whitespace
        text = re.sub(r"\r\n|\r", "\n", text)
        text = re.sub(r"\u00a0", " ", text)  # non-breaking space
        text = re.sub(r"[\t ]+", " ", text)

        # Collapse multiple line breaks
        text = re.sub(r"\n{2,}", "\n\n", text)

        return text

    def _find_sections(self, text: str) -> List[Tuple[str, str, str]]:
        """
        Find section boundaries in text.

        Looks for "ITEM X" headers.

        Args:
            text: Plain text content.

        Returns:
            List of tuples (item_id, title, content).
        """
        # Pattern matches: "ITEM 1", "ITEM 1A", "ITEM 7A", etc.
        pattern = re.compile(r"(?im)^\s*item\s+(\d+[a-z]?)\.?\s*(.*)$")
        matches = list(pattern.finditer(text))

        if not matches:
            return []

        sections = []
        for i, match in enumerate(matches):
            item_id = match.group(1).upper()
            title = match.group(2).strip()

            # Content is from end of current match to start of next
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

            content = text[start:end].strip()

            # Clean up excessive whitespace
            content = re.sub(r"\n{3,}", "\n\n", content)

            sections.append((item_id, title, content))

        return sections

    def _write_section(
        self,
        output_dir: Path,
        item_id: str,
        title: str,
        content: str
    ) -> Path:
        """
        Write a section to a Markdown file.

        Args:
            output_dir: Output directory.
            item_id: Item identifier (e.g., "1", "1A").
            title: Section title.
            content: Section content.

        Returns:
            Path to written file.
        """
        filename = f"Item_{item_id}.md"
        output_path = output_dir / filename

        header = f"## Item {item_id}"
        if title:
            header += f" {title}"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header + "\n\n")
            f.write(content + "\n")

        logger.debug(f"Wrote section {item_id} to {output_path}")
        return output_path

    def _write_index(
        self,
        output_dir: Path,
        sections: List[Tuple[str, str, str]]
    ) -> Path:
        """
        Write an index of all sections.

        Args:
            output_dir: Output directory.
            sections: List of section tuples.

        Returns:
            Path to index file.
        """
        index_path = output_dir / "sections_index.md"

        with open(index_path, "w", encoding="utf-8") as f:
            f.write("## Extracted Items\n\n")

            # Sort by item ID
            sorted_sections = sorted(sections, key=lambda x: self._sort_key(x[0]))

            for item_id, title, _ in sorted_sections:
                filename = f"Item_{item_id}.md"
                line = f"- Item {item_id}"
                if title:
                    line += f": {title}"
                line += f" → `{filename}`\n"
                f.write(line)

        logger.debug(f"Wrote index to {index_path}")
        return index_path

    @staticmethod
    def _sort_key(item_id: str) -> Tuple:
        """
        Generate sort key for item ID.

        Args:
            item_id: Item identifier (e.g., "1", "1A", "15").

        Returns:
            Tuple for sorting (number, letter).
        """
        match = re.match(r"(\d+)([A-Z]?)", item_id)
        if match:
            num = int(match.group(1))
            letter = match.group(2) or ""
            return (num, letter)
        return (0, item_id)
