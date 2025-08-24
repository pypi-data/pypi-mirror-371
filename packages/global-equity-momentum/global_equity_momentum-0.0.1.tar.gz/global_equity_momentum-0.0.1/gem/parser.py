"""
Argument parser for Dual Momentum Investing Strategy.
"""

import argparse
from datetime import UTC, datetime

from gem.config import DEFAULT_SYMBOLS, LOOKBACK_MONTHS, OUTPUT_DIR, SKIP_MONTHS


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for the GEM tool.

    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Dual Momentum Investing Strategy Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m gem --mode analyze
  python -m gem --mode validate
  python -m gem --mode analyze --symbols EIMI.L IWDA.L --date 2024-12-01
  python -m gem --mode validate --symbols EIMI.L IWDA.L
        """,
    )

    parser.add_argument(
        "--mode",
        "-m",
        choices=["analyze", "validate"],
        default="analyze",
        help="Mode of operation: analyze or validate (default: analyze)",
    )

    parser.add_argument(
        "--symbols",
        "-s",
        nargs="+",
        default=DEFAULT_SYMBOLS,
        help=f"List of symbols to analyze (default: {DEFAULT_SYMBOLS})",
    )

    parser.add_argument("--date", "-d", help="Target date for analysis (YYYY-MM-DD). Default: today")

    parser.add_argument("--output", "-o", help="Output file path for the chart")

    parser.add_argument(
        "--lookback-months",
        "-l",
        type=int,
        default=LOOKBACK_MONTHS,
        help=f"Number of months to look back for momentum calculation (default: {LOOKBACK_MONTHS})",
    )

    parser.add_argument(
        "--skip-months",
        "-k",
        type=int,
        default=SKIP_MONTHS,
        help=f"Number of months to skip from target date (default: {SKIP_MONTHS})",
    )

    return parser


def get_output_path(output_arg: str | None = None) -> str:
    """
    Get the output file path, either from user argument or generate default.

    Args:
        output_arg: User-specified output path

    Returns:
        str: Output file path
    """
    if output_arg:
        return output_arg

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    return str(OUTPUT_DIR / f"momentum_analysis_{timestamp}.png")
