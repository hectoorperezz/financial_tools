"""
Financial statement extraction from XBRL company facts.
"""
import csv
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from .base import BaseExtractor
from ..sec_client import SECClient
from ..config import Config
from ..exceptions import ExtractionError


logger = logging.getLogger(__name__)


class FinancialStatementExtractor(BaseExtractor):
    """
    Extracts financial statements from SEC Company Facts (XBRL data).
    """

    def __init__(
        self,
        client: Optional[SECClient] = None,
        config: Optional[Config] = None
    ):
        """
        Initialize financial statement extractor.

        Args:
            client: SEC API client for fetching company facts.
            config: Configuration object.
        """
        super().__init__(config)
        self.client = client or SECClient(self.config)

    def extract(
        self,
        cik: str,
        output_dir: Path,
        save_raw: bool = True
    ) -> Dict[str, Any]:
        """
        Extract financial statements from company facts.

        Args:
            cik: 10-digit CIK string.
            output_dir: Output directory for CSV files.
            save_raw: Whether to save raw JSON data.

        Returns:
            Dictionary with:
                - IS: Income Statement file path
                - BS: Balance Sheet file path
                - CF: Cash Flow file path
                - raw_json: Path to raw JSON (if save_raw=True)
                - statement_count: Number of statements generated

        Raises:
            ExtractionError: If extraction fails.
        """
        self.ensure_output_dir(output_dir)

        logger.info(f"Extracting financial statements for CIK {cik}")

        try:
            # Fetch company facts
            facts = self.client.get_company_facts(cik)

            # Extract US-GAAP facts
            us_gaap = facts.get("facts", {}).get("us-gaap", {})
            if not us_gaap:
                us_gaap = facts.get("facts", {})

            if not us_gaap:
                raise ExtractionError("No US-GAAP facts found in company facts")

            # Define statement concepts
            statements = {
                "IS": self.config.income_statement_concepts,
                "BS": self.config.balance_sheet_concepts,
                "CF": self.config.cash_flow_concepts,
            }

            generated = {}

            # Generate each statement
            for stmt_code, concepts in statements.items():
                csv_path = self._generate_statement(
                    us_gaap,
                    concepts,
                    output_dir / f"{stmt_code}.csv"
                )
                if csv_path:
                    generated[stmt_code] = str(csv_path)

            # Save raw JSON if requested
            if save_raw:
                raw_path = output_dir / "company_facts.json"
                self._save_raw_json(facts, raw_path)
                generated["raw_json"] = str(raw_path)

            result = {
                **generated,
                "statement_count": len([k for k in generated if k != "raw_json"]),
                "cik": cik,
            }

            logger.info(f"Generated {result['statement_count']} financial statements")
            return result

        except Exception as e:
            logger.error(f"Financial statement extraction failed: {e}")
            raise ExtractionError(f"Failed to extract financial statements: {e}") from e

    def _generate_statement(
        self,
        us_gaap: Dict,
        concepts: Tuple[str, ...],
        output_path: Path
    ) -> Optional[Path]:
        """
        Generate a single financial statement CSV.

        Args:
            us_gaap: US-GAAP facts dictionary.
            concepts: Tuple of concept names to include.
            output_path: Output CSV path.

        Returns:
            Path to generated file, or None if no data.
        """
        # Build series for each concept
        concept_series = {}
        all_dates = set()

        for concept_name in concepts:
            fact_obj = us_gaap.get(concept_name)
            if not fact_obj:
                continue

            series = self._extract_series(fact_obj)
            if series:
                concept_series[concept_name] = series
                all_dates.update(series.keys())

        if not all_dates:
            logger.warning(f"No data found for {output_path.stem}")
            return None

        # Sort dates
        sorted_dates = sorted(all_dates)

        # Write CSV
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Header
            header = ["Date"] + list(concepts)
            writer.writerow(header)

            # Data rows
            for date in sorted_dates:
                row = [date]
                for concept in concepts:
                    series = concept_series.get(concept, {})
                    value, _ = series.get(date, ("", ""))
                    row.append(value)
                writer.writerow(row)

        logger.debug(f"Generated statement: {output_path}")
        return output_path

    def _extract_series(
        self,
        fact_obj: Dict
    ) -> Dict[str, Tuple[Any, str]]:
        """
        Extract time series from a fact object.

        Args:
            fact_obj: Fact object from US-GAAP.

        Returns:
            Dictionary mapping dates to (value, filed_date) tuples.
        """
        units = fact_obj.get("units", {})

        # Try preferred units in order
        for unit in self.config.preferred_units:
            if unit in units:
                return self._parse_unit_series(units[unit])

        # If no preferred unit, try any available unit
        for unit_data in units.values():
            series = self._parse_unit_series(unit_data)
            if series:
                return series

        return {}

    def _parse_unit_series(
        self,
        unit_data: List[Dict]
    ) -> Dict[str, Tuple[Any, str]]:
        """
        Parse time series from unit data.

        Args:
            unit_data: List of observations for a unit.

        Returns:
            Dictionary mapping dates to (value, filed_date) tuples.
        """
        series = {}

        for obs in unit_data:
            # Determine date (end, instant, or filed)
            date = obs.get("end") or obs.get("instant") or obs.get("filed")
            if not date:
                continue

            value = obs.get("val")
            filed = obs.get("filed", "")

            # Keep most recent filing for each date
            existing = series.get(date)
            if existing is None or (filed and filed > existing[1]):
                series[date] = (value, filed)

        return series

    def _save_raw_json(self, facts: Dict, output_path: Path):
        """
        Save raw company facts to JSON file.

        Args:
            facts: Company facts dictionary.
            output_path: Output JSON path.
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(facts, f, ensure_ascii=False, indent=2)
            logger.debug(f"Saved raw facts to {output_path}")

        except Exception as e:
            logger.warning(f"Failed to save raw JSON: {e}")

    def extract_custom_concepts(
        self,
        cik: str,
        concepts: List[str],
        output_path: Path,
        statement_name: str = "Custom"
    ) -> Optional[Path]:
        """
        Extract custom set of concepts to a CSV file.

        Args:
            cik: 10-digit CIK string.
            concepts: List of US-GAAP concept names.
            output_path: Output CSV path.
            statement_name: Name for the statement.

        Returns:
            Path to generated file, or None if no data.

        Raises:
            ExtractionError: If extraction fails.
        """
        logger.info(f"Extracting custom concepts for CIK {cik}")

        try:
            facts = self.client.get_company_facts(cik)
            us_gaap = facts.get("facts", {}).get("us-gaap", {})
            if not us_gaap:
                us_gaap = facts.get("facts", {})

            output_path.parent.mkdir(parents=True, exist_ok=True)

            return self._generate_statement(
                us_gaap,
                tuple(concepts),
                output_path
            )

        except Exception as e:
            logger.error(f"Custom concept extraction failed: {e}")
            raise ExtractionError(f"Failed to extract custom concepts: {e}") from e
