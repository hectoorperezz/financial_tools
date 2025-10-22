# SEC Filing Extractor

A robust, object-oriented Python toolkit for downloading and extracting data from SEC EDGAR filings. Extract tables, text sections, and financial statements from 10-K, 10-Q, 8-K, and other SEC filings with ease.

## Features

- **Company Lookup**: Resolve ticker symbols to CIK numbers
- **Filing Discovery**: Search and browse recent SEC filings
- **Bulk Download**: Download complete filing packages including exhibits
- **Table Extraction**: Parse HTML tables and export to CSV/JSON
- **Section Extraction**: Extract text items (Item 1, 1A, 7, etc.) as Markdown
- **Financial Statements**: Convert XBRL data to standard financial statements (Income Statement, Balance Sheet, Cash Flows)
- **Intelligent Caching**: Rate limiting and retry logic for SEC API compliance
- **Extensible Architecture**: Object-oriented design for easy customization

## Installation

### From Source

```bash
git clone https://github.com/yourusername/sec-filing-extractor.git
cd sec-filing-extractor
pip install -r requirements.txt
```

### Using Setup

```bash
python setup.py install
```

## Quick Start

### Interactive CLI Mode

```bash
python main.py
```

This launches an interactive interface that guides you through:
1. Looking up a company by ticker
2. Browsing recent filings
3. Downloading and extracting data

### Quick Mode

Download and process the latest 10-K for Apple:

```bash
python main.py --ticker AAPL --form 10-K --quick
```

### Programmatic Usage

```python
from sec_filing_extractor import FilingManager, Config

# Create configuration
config = Config(
    user_agent="YourName (your@email.com)",
    default_output_dir="./filings"
)

# Initialize manager
with FilingManager(config) as manager:
    # Search for company
    company = manager.search_company("AAPL")
    print(f"Found: {company['name']}")

    # Get recent 10-K filings
    filings = manager.get_filings("AAPL", form_types=("10-K",), limit=5)

    # Download and process the latest filing
    filing = filings[0]
    result = manager.process_filing_complete(
        filing,
        extract_tables=True,
        extract_sections=True,
        extract_financials=True
    )

    print(f"Files saved to: {result['download']['filing_dir']}")
```

## Architecture

### Core Components

#### Config
Configuration management with support for environment variables and runtime updates.

```python
from sec_filing_extractor import Config

config = Config(
    user_agent="YourName (your@email.com)",
    default_output_dir="filings",
    log_level="INFO",
    request_delay=0.2
)
```

#### SECClient
HTTP client for SEC EDGAR API with rate limiting and retry logic.

```python
from sec_filing_extractor import SECClient

with SECClient(config) as client:
    submissions = client.get_company_submissions("0000320193")
    facts = client.get_company_facts("0000320193")
```

#### CompanyLookup
Resolve ticker symbols to CIK numbers.

```python
from sec_filing_extractor import CompanyLookup

lookup = CompanyLookup(config=config)
cik = lookup.get_cik_from_ticker("AAPL")
company_info = lookup.get_company_info("AAPL")
```

#### FilingDownloader
Download filings and related files.

```python
from sec_filing_extractor import FilingDownloader

downloader = FilingDownloader(config=config)
filings = downloader.get_recent_filings(cik, form_types=("10-K",))
files = downloader.download_filing(filings[0])
```

#### Extractors
Extract specific data from filings.

```python
from sec_filing_extractor.extractors import (
    TableExtractor,
    SectionExtractor,
    FinancialStatementExtractor
)

# Extract tables
table_extractor = TableExtractor(config)
tables = table_extractor.extract(html_file, output_dir)

# Extract sections
section_extractor = SectionExtractor(config)
sections = section_extractor.extract(html_file, output_dir)

# Extract financials
financial_extractor = FinancialStatementExtractor(config=config)
financials = financial_extractor.extract(cik, output_dir)
```

#### FilingManager
High-level orchestration of all operations.

```python
from sec_filing_extractor import FilingManager

manager = FilingManager(config)
result = manager.process_filing_complete(
    filing,
    extract_tables=True,
    extract_sections=True,
    extract_financials=True
)
```

## Project Structure

```
sec-filing-extractor/
├── sec_filing_extractor/
│   ├── __init__.py           # Package exports
│   ├── config.py             # Configuration management
│   ├── exceptions.py         # Custom exceptions
│   ├── sec_client.py         # SEC API client
│   ├── company_lookup.py     # Ticker/CIK resolution
│   ├── filing_downloader.py  # Filing download logic
│   ├── filing_manager.py     # High-level orchestration
│   ├── cli.py                # CLI interface
│   └── extractors/
│       ├── __init__.py
│       ├── base.py           # Base extractor class
│       ├── table_extractor.py
│       ├── section_extractor.py
│       └── financial_extractor.py
├── main.py                   # Entry point
├── requirements.txt          # Dependencies
├── setup.py                  # Package setup
└── README.md                 # This file
```

## Configuration

### Environment Variables

```bash
export SEC_USER_AGENT="YourName (your@email.com)"
export SEC_OUTPUT_DIR="./my_filings"
export SEC_LOG_LEVEL="DEBUG"
export SEC_LOG_FILE="sec_extractor.log"
```

### Programmatic Configuration

```python
config = Config()
config.update(
    user_agent="YourName (your@email.com)",
    default_output_dir="./filings",
    log_level="DEBUG",
    request_delay=0.3,
    max_retries=5
)
```

## Command-Line Options

```
usage: main.py [-h] [--version] [--ticker TICKER] [--form FORM] [--quick]
               [--output-dir OUTPUT_DIR] [--user-agent USER_AGENT]
               [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
               [--log-file LOG_FILE]

Options:
  --ticker TICKER       Stock ticker symbol (e.g., AAPL)
  --form FORM           Form type to download (default: 10-K)
  --quick               Quick mode: auto-download latest filing
  --output-dir DIR      Output directory (default: filings)
  --user-agent AGENT    User-Agent for SEC requests
  --log-level LEVEL     Logging level (default: INFO)
  --log-file FILE       Log file path
```

## Examples

### Extract Tables Only

```python
from pathlib import Path
from sec_filing_extractor.extractors import TableExtractor

extractor = TableExtractor()
result = extractor.extract(
    source=Path("filing.html"),
    output_dir=Path("output/tables"),
    min_columns=2,
    max_tables=100
)

print(f"Extracted {result['table_count']} tables")
```

### Extract Custom XBRL Concepts

```python
from sec_filing_extractor.extractors import FinancialStatementExtractor

extractor = FinancialStatementExtractor()
concepts = [
    "Revenues",
    "CostOfRevenue",
    "GrossProfit",
    "OperatingIncomeLoss"
]

extractor.extract_custom_concepts(
    cik="0000320193",
    concepts=concepts,
    output_path=Path("custom_metrics.csv")
)
```

### Batch Processing

```python
from sec_filing_extractor import FilingManager

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
manager = FilingManager()

for ticker in tickers:
    try:
        filings = manager.get_filings(ticker, form_types=("10-K",), limit=1)
        result = manager.process_filing_complete(filings[0])
        print(f"✓ Processed {ticker}")
    except Exception as e:
        print(f"✗ Failed {ticker}: {e}")
```

## Error Handling

The library provides specific exceptions for different error cases:

```python
from sec_filing_extractor.exceptions import (
    TickerNotFoundError,
    FilingNotFoundError,
    DownloadError,
    ExtractionError,
    RateLimitError
)

try:
    manager.search_company("INVALID")
except TickerNotFoundError:
    print("Ticker not found in SEC database")
except RateLimitError:
    print("SEC API rate limit exceeded")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Logging

Configure logging to track operations:

```python
config = Config(
    log_level="DEBUG",
    log_file="sec_extractor.log"
)
```

Or use Python's logging directly:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## SEC API Compliance

This tool is designed to comply with SEC EDGAR access guidelines:

- **User-Agent**: Always set a descriptive User-Agent with contact info
- **Rate Limiting**: Built-in delays between requests (default 0.2s)
- **Retry Logic**: Exponential backoff for failed requests
- **Respectful Access**: Follows SEC's fair access policy

## Output Formats

### Tables
- **CSV**: Individual table files (`table_1.csv`, `table_2.csv`, ...)
- **JSON**: All tables in one file with metadata

### Sections
- **Markdown**: One file per Item (`Item_1.md`, `Item_7.md`, ...)
- **Index**: List of all sections with links

### Financial Statements
- **IS.csv**: Income Statement (multi-year)
- **BS.csv**: Balance Sheet (multi-year)
- **CF.csv**: Cash Flow Statement (multi-year)
- **company_facts.json**: Raw XBRL data

## Requirements

- Python 3.8+
- requests >= 2.31.0
- urllib3 >= 2.0.0

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool is for educational and research purposes. Users are responsible for complying with SEC EDGAR access policies and terms of use.

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/yourusername/sec-filing-extractor/issues
- Documentation: https://github.com/yourusername/sec-filing-extractor/wiki

## Changelog

### Version 2.0.0 (Current)
- Complete refactor to object-oriented architecture
- Added comprehensive error handling
- Improved logging and configuration
- Added type hints throughout
- Better rate limiting and retry logic
- Extensible extractor framework
- CLI improvements with quick mode

### Version 1.0.0 (Legacy)
- Initial procedural implementation
- Basic filing download and extraction
