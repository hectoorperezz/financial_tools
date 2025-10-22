"""
Configuration management for SEC Filing Extractor.
"""
import os
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    """Configuration settings for SEC Filing Extractor."""

    # API Configuration
    user_agent: str = "SEC Filing Extractor (contact@example.com)"
    sec_api_base: str = "https://data.sec.gov"
    sec_files_base: str = "https://www.sec.gov"

    # Rate Limiting
    request_delay: float = 0.2  # seconds between requests
    max_retries: int = 3
    retry_delay: float = 1.0

    # Download Configuration
    default_output_dir: str = "filings"
    include_exhibits: bool = False
    chunk_size: int = 16384  # 16KB chunks for streaming

    # Extraction Configuration
    min_table_columns: int = 2
    max_tables_per_file: int = 200

    # Logging Configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # File Types
    supported_form_types: tuple = ("10-K", "10-Q", "8-K", "20-F", "6-K")

    # XBRL Configuration
    preferred_units: tuple = ("USD", "shares")

    # Financial Statement Concepts
    income_statement_concepts: tuple = field(default_factory=lambda: (
        "Revenues",
        "SalesRevenueNet",
        "CostOfRevenue",
        "GrossProfit",
        "OperatingExpenses",
        "ResearchAndDevelopmentExpense",
        "SellingGeneralAndAdministrativeExpense",
        "OperatingIncomeLoss",
        "InterestExpense",
        "IncomeTaxExpenseBenefit",
        "NetIncomeLoss",
    ))

    balance_sheet_concepts: tuple = field(default_factory=lambda: (
        "Assets",
        "AssetsCurrent",
        "Liabilities",
        "LiabilitiesCurrent",
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        "RetainedEarningsAccumulatedDeficit",
        "CashAndCashEquivalentsAtCarryingValue",
        "InventoryNet",
        "CommonStockSharesOutstanding",
    ))

    cash_flow_concepts: tuple = field(default_factory=lambda: (
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByUsedInInvestingActivities",
        "NetCashProvidedByUsedInFinancingActivities",
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "DepreciationDepletionAndAmortization",
        "PaymentsForRepurchaseOfCommonStock",
        "ProceedsFromIssuanceOfLongTermDebt",
        "RepaymentsOfLongTermDebt",
        "PaymentsOfDividends",
    ))

    def __post_init__(self):
        """Initialize logging after dataclass initialization."""
        self.setup_logging()

    def setup_logging(self):
        """Configure logging based on settings."""
        log_level = getattr(logging, self.log_level.upper(), logging.INFO)

        handlers = [logging.StreamHandler()]
        if self.log_file:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            handlers.append(logging.FileHandler(self.log_file))

        logging.basicConfig(
            level=log_level,
            format=self.log_format,
            handlers=handlers,
            force=True
        )

    @property
    def headers(self) -> dict:
        """Get HTTP headers for SEC requests."""
        return {"User-Agent": self.user_agent}

    @property
    def output_dir(self) -> Path:
        """Get output directory as Path object."""
        return Path(self.default_output_dir)

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            user_agent=os.getenv("SEC_USER_AGENT", cls.user_agent),
            default_output_dir=os.getenv("SEC_OUTPUT_DIR", cls.default_output_dir),
            log_level=os.getenv("SEC_LOG_LEVEL", cls.log_level),
            log_file=os.getenv("SEC_LOG_FILE"),
        )

    def update(self, **kwargs):
        """Update configuration with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # Re-setup logging if log settings changed
        if any(k in kwargs for k in ('log_level', 'log_file', 'log_format')):
            self.setup_logging()
