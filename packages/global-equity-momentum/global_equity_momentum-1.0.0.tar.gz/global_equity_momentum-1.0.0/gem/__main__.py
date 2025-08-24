"""
Dual Momentum Investing Strategy 12-month lookback period with 1-month skip.
"""

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

from loguru import logger

from gem.chart_generator import ChartGenerator
from gem.config import DEFAULT_SYMBOLS
from gem.data_fetcher import DataFetcher
from gem.momentum_calculator import MomentumCalculator
from gem.parser import create_parser, get_output_path


def calculate_analysis_period(
    target_date: datetime, lookback_months: int, skip_months: int
) -> tuple[datetime, datetime]:
    """
    Calculate analysis period with configurable lookback and skip months.

    Args:
        target_date: The target date for analysis
        lookback_months: Number of months to look back
        skip_months: Number of months to skip from target date

    For July 1, 2025 with 12-month lookback and 1-month skip:
    -> period from June 1, 2024 to May 31, 2025
    """
    # First, move back by skip_months from the target date
    end_date = target_date.replace(day=1)
    for _ in range(skip_months):
        end_date = end_date - timedelta(days=1)
        end_date = end_date.replace(day=1)

    # Then move back by one more day to get to the end of the previous month
    end_date = end_date - timedelta(days=1)

    # Calculate start_date by going back lookback_months from end_date
    start_date = end_date.replace(day=1)
    for _ in range(lookback_months - 1):
        start_date = start_date - timedelta(days=1)
        start_date = start_date.replace(day=1)

    return start_date, end_date


def run_analysis(
    symbols: list[str],
    target_date: str | None = None,
    output_file: str | None = None,
    lookback_months: int = 12,
    skip_months: int = 1,
):
    """Run the analysis mode."""
    try:
        logger.info(f"Using symbols: {symbols}")
        logger.info(f"Lookback months: {lookback_months}, Skip months: {skip_months}")

        target_dt = datetime.strptime(target_date, "%Y-%m-%d%z") if target_date else datetime.now(UTC)

        logger.info(f"Analyzing for target date: {target_dt.strftime('%Y-%m-%d')}")

        start_date, end_date = calculate_analysis_period(target_dt, lookback_months, skip_months)
        logger.info(f"Analysis period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

        logger.info("Fetching market data...")
        data_fetcher = DataFetcher()
        price_data = data_fetcher.fetch_data(symbols, start_date, end_date)

        if price_data.empty:
            logger.error("No data fetched. Please check symbols and date range.")
            sys.exit(1)

        logger.info("Calculating momentum...")
        momentum_calc = MomentumCalculator()
        momentum_results = momentum_calc.calculate_momentum(price_data)

        best_symbol = cast("str", momentum_results.idxmax())
        logger.info(f"Best performing symbol: {best_symbol}")

        logger.info("Generating chart...")
        chart_gen = ChartGenerator()

        if not output_file:
            output_file = get_output_path()

        chart_gen.create_momentum_chart(
            price_data=price_data,
            momentum_results=momentum_results,
            best_symbol=best_symbol,
            analysis_period=(start_date, end_date),
            target_date=target_dt,
            output_path=Path(output_file),
        )

        logger.info("🎯 Dual Momentum Analysis Results")
        logger.info("=" * 40)
        logger.info(f"Target Date: {target_dt.strftime('%Y-%m-%d')}")
        logger.info(f"Analysis Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

        chart_gen = ChartGenerator()
        best_company_name = chart_gen.get_symbol_label(best_symbol)
        logger.info(f"Best Performer: {best_company_name} ({best_symbol})")
        logger.info(f"Chart saved to: {output_file}")

        logger.info("📊 Momentum Rankings:")
        for symbol, momentum in momentum_results.sort_values(ascending=False).items():
            indicator = "🏆" if symbol == best_symbol else "  "
            company_name = chart_gen.get_symbol_label(str(symbol))
            if company_name != symbol:
                logger.info(f"{indicator} {company_name} ({symbol}): {momentum:.2%}")
            else:
                logger.info(f"{indicator} {symbol}: {momentum:.2%}")

        logger.info("Analysis completed successfully")

    except Exception as e:
        logger.exception(f"Analysis failed: {e!s}")
        logger.error(f"❌ Error: {e!s}")
        sys.exit(1)


def run_validation(symbols: list[str]):
    """Run the validation mode."""
    try:
        logger.info(f"Validating symbols: {symbols}")

        data_fetcher = DataFetcher()
        chart_gen = ChartGenerator()
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=30)

        logger.info("🔍 Symbol Validation Results")
        logger.info("=" * 40)

        for symbol in symbols:
            try:
                data = data_fetcher.fetch_single_symbol(symbol, start_date, end_date)
                if not data.empty:
                    company_name = chart_gen.get_symbol_label(symbol)
                    if company_name != symbol:
                        logger.info(f"✅ {symbol}: {company_name}")
                    else:
                        logger.info(f"✅ {symbol}: Valid")
                else:
                    logger.error(f"❌ {symbol}: No data available")
            except Exception as e:
                logger.error(f"❌ {symbol}: Error - {e!s}")

        logger.info("Validation completed successfully")

    except Exception as e:
        logger.exception(f"Validation failed: {e!s}")
        logger.error(f"❌ Error: {e!s}")
        sys.exit(1)


def main():
    """
    Dual Momentum Investing Strategy Tool.

    Use --mode analyze or --mode validate to specify operation.
    """
    parser = create_parser()
    args = parser.parse_args()

    try:
        if args.mode == "analyze":
            logger.info("Running in ANALYSIS mode")
            run_analysis(
                symbols=args.symbols,
                target_date=args.date,
                output_file=args.output,
                lookback_months=args.lookback_months,
                skip_months=args.skip_months,
            )
        elif args.mode == "validate":
            logger.info("Running in VALIDATION mode")
            run_validation(symbols=args.symbols)

    except Exception as e:
        logger.exception(f"Operation failed: {e!s}")
        logger.error(f"❌ Error: {e!s}")
        sys.exit(1)


def analyze(
    symbols: list[str] | None = None,
    target_date: str | None = None,
    output_file: str | None = None,
    lookback_months: int = 12,
    skip_months: int = 1,
):
    """
    Perform dual momentum analysis and generate chart.
    """
    if symbols is None:
        symbols = DEFAULT_SYMBOLS

    run_analysis(symbols, target_date, output_file, lookback_months, skip_months)


def validate_symbols(symbols: list[str]):
    """
    Validate if symbols are available in Yahoo Finance.
    """
    run_validation(symbols)


if __name__ == "__main__":
    main()
