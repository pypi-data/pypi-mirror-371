"""
Unit tests for main module.
"""

from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest
from gem.__main__ import (
    analyze,
    calculate_analysis_period,
    run_analysis,
    run_validation,
    validate_symbols,
)


@pytest.fixture
def sample_target_date():
    return datetime(2025, 7, 1, tzinfo=UTC)


@pytest.fixture
def sample_symbols():
    return ["AAPL", "MSFT"]


@pytest.fixture
def mock_data_fetcher():
    with pytest.MonkeyPatch().context() as m:
        mock_fetcher = Mock()
        mock_fetcher.fetch_data.return_value = Mock()
        mock_fetcher.fetch_single_symbol.return_value = Mock()
        m.setattr("gem.__main__.DataFetcher", lambda: mock_fetcher)
        yield mock_fetcher


@pytest.fixture
def mock_momentum_calculator():
    with pytest.MonkeyPatch().context() as m:
        mock_calc = Mock()
        mock_calc.calculate_momentum.return_value = Mock()
        m.setattr("gem.__main__.MomentumCalculator", lambda: mock_calc)
        yield mock_calc


@pytest.fixture
def mock_chart_generator():
    with pytest.MonkeyPatch().context() as m:
        mock_gen = Mock()
        mock_gen.create_momentum_chart.return_value = None
        mock_gen.get_symbol_label.return_value = "Test Company"
        m.setattr("gem.__main__.ChartGenerator", lambda: mock_gen)
        yield mock_gen


class TestCalculateAnalysisPeriod:
    """Test analysis period calculation functionality."""

    def test_calculate_analysis_period_july_2025(self, sample_target_date) -> None:
        start_date, end_date = calculate_analysis_period(sample_target_date, 12, 1)

        assert start_date == datetime(2024, 6, 1, tzinfo=UTC)
        assert end_date == datetime(2025, 5, 31, tzinfo=UTC)

    def test_calculate_analysis_period_different_lookback(self, sample_target_date) -> None:
        start_date, end_date = calculate_analysis_period(sample_target_date, 6, 1)

        assert start_date == datetime(2024, 12, 1, tzinfo=UTC)
        assert end_date == datetime(2025, 5, 31, tzinfo=UTC)

    def test_calculate_analysis_period_different_skip(self, sample_target_date) -> None:
        start_date, end_date = calculate_analysis_period(sample_target_date, 12, 2)

        assert start_date == datetime(2024, 5, 1, tzinfo=UTC)
        assert end_date == datetime(2025, 4, 30, tzinfo=UTC)


class TestRunAnalysis:
    """Test analysis execution functionality."""

    @patch("gem.__main__.sys.exit")
    def test_run_analysis_success(
        self, mock_sys_exit, sample_symbols, mock_data_fetcher, mock_momentum_calculator, mock_chart_generator
    ) -> None:
        with pytest.MonkeyPatch().context() as m:
            mock_price_data = Mock()
            mock_price_data.empty = False
            mock_data_fetcher.fetch_data.return_value = mock_price_data

            mock_momentum_results = Mock()
            mock_momentum_results.idxmax.return_value = "AAPL"
            mock_momentum_results.sort_values.return_value.items.return_value = [("AAPL", 0.2), ("MSFT", 0.1)]
            mock_momentum_results.sort_values.return_value = mock_momentum_results
            mock_momentum_calculator.calculate_momentum.return_value = mock_momentum_results

            m.setattr("gem.__main__.get_output_path", lambda: "test.png")

            run_analysis(sample_symbols)

            mock_data_fetcher.fetch_data.assert_called_once()
            mock_momentum_calculator.calculate_momentum.assert_called_once()
            mock_chart_generator.create_momentum_chart.assert_called_once()


class TestRunValidation:
    """Test validation execution functionality."""

    @patch("gem.__main__.sys.exit")
    def test_run_validation_success(
        self, mock_sys_exit, sample_symbols, mock_data_fetcher, mock_chart_generator
    ) -> None:
        with pytest.MonkeyPatch().context():
            mock_data = Mock()
            mock_data.empty = False
            mock_data_fetcher.fetch_single_symbol.return_value = mock_data

            run_validation(sample_symbols)

            assert mock_data_fetcher.fetch_single_symbol.call_count == 2


class TestAnalyze:
    """Test analyze function functionality."""

    @patch("gem.__main__.sys.exit")
    def test_analyze_with_default_symbols(
        self, mock_sys_exit, mock_data_fetcher, mock_momentum_calculator, mock_chart_generator
    ) -> None:
        with pytest.MonkeyPatch().context() as m:
            mock_price_data = Mock()
            mock_price_data.empty = False
            mock_data_fetcher.fetch_data.return_value = mock_price_data

            mock_momentum_results = Mock()
            mock_momentum_results.idxmax.return_value = "EIMI.L"
            mock_momentum_results.sort_values.return_value.items.return_value = [("EIMI.L", 0.2), ("IWDA.L", 0.1)]
            mock_momentum_results.sort_values.return_value = mock_momentum_results
            mock_momentum_calculator.calculate_momentum.return_value = mock_momentum_results

            m.setattr("gem.__main__.get_output_path", lambda: "test.png")

            analyze()

            mock_data_fetcher.fetch_data.assert_called_once()

    @patch("gem.__main__.sys.exit")
    def test_analyze_with_custom_symbols(
        self, mock_sys_exit, sample_symbols, mock_data_fetcher, mock_momentum_calculator, mock_chart_generator
    ) -> None:
        with pytest.MonkeyPatch().context() as m:
            mock_price_data = Mock()
            mock_price_data.empty = False
            mock_data_fetcher.fetch_data.return_value = mock_price_data

            mock_momentum_results = Mock()
            mock_momentum_results.idxmax.return_value = "AAPL"
            mock_momentum_results.sort_values.return_value.items.return_value = [("AAPL", 0.2), ("MSFT", 0.1)]
            mock_momentum_results.sort_values.return_value = mock_momentum_results
            mock_momentum_calculator.calculate_momentum.return_value = mock_momentum_results

            m.setattr("gem.__main__.get_output_path", lambda: "test.png")

            analyze(symbols=sample_symbols)

            mock_data_fetcher.fetch_data.assert_called_once()


class TestValidateSymbols:
    """Test symbol validation functionality."""

    @patch("gem.__main__.sys.exit")
    def test_validate_symbols(self, mock_sys_exit, sample_symbols, mock_data_fetcher, mock_chart_generator) -> None:
        with pytest.MonkeyPatch().context():
            mock_data = Mock()
            mock_data.empty = False
            mock_data_fetcher.fetch_single_symbol.return_value = mock_data

            validate_symbols(sample_symbols)

            assert mock_data_fetcher.fetch_single_symbol.call_count == 2
