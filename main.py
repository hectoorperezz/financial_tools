#!/usr/bin/env python3
"""
Main entry point for SEC Filing Extractor.
"""
import sys
import argparse
from pathlib import Path

from sec_filing_extractor import CLI, Config, __version__


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SEC Filing Extractor - Download and extract data from SEC EDGAR filings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python main.py

  # Quick mode - download latest 10-K for AAPL
  python main.py --ticker AAPL --form 10-K --quick

  # Configure output directory and user agent
  python main.py --output-dir ./my_filings --user-agent "YourName (your@email.com)"

  # Set log level
  python main.py --log-level DEBUG

For more information, visit: https://github.com/yourusername/sec-filing-extractor
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"SEC Filing Extractor {__version__}"
    )

    parser.add_argument(
        "--ticker",
        type=str,
        help="Stock ticker symbol (e.g., AAPL)"
    )

    parser.add_argument(
        "--form",
        type=str,
        default="10-K",
        help="Form type to download (default: 10-K)"
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode: automatically download and process latest filing"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="filings",
        help="Output directory for downloaded filings (default: filings)"
    )

    parser.add_argument(
        "--user-agent",
        type=str,
        help="User-Agent header for SEC requests (should include your email)"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)"
    )

    parser.add_argument(
        "--log-file",
        type=str,
        help="Log file path (default: log to console only)"
    )

    args = parser.parse_args()

    # Create configuration
    config = Config()

    # Update config from command-line arguments
    if args.output_dir:
        config.default_output_dir = args.output_dir

    if args.user_agent:
        config.user_agent = args.user_agent

    if args.log_level:
        config.log_level = args.log_level

    if args.log_file:
        config.log_file = args.log_file

    # Re-setup logging with new config
    config.setup_logging()

    # Create CLI
    cli = CLI(config)

    try:
        if args.quick and args.ticker:
            # Quick mode
            cli.run_quick(args.ticker, args.form, download=True)
        elif args.ticker:
            # Start CLI with ticker pre-filled
            print(f"Starting with ticker: {args.ticker}")
            # For now, just run normal CLI
            # You could extend CLI to accept initial ticker
            cli.run()
        else:
            # Interactive mode
            cli.run()

    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
