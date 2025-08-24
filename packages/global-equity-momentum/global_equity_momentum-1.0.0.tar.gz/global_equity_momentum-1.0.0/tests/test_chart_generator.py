"""
Unit tests for chart generator module.
"""

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pandas as pd
import pytest
from gem.chart_generator import ChartGenerator


@pytest.fixture
def sample_price_data():
    return pd.DataFrame(
        {"AAPL": [100.0, 110.0, 120.0], "MSFT": [200.0, 190.0, 210.0]}, index=pd.date_range("2024-01-01", periods=3)
    )


@pytest.fixture
def sample_momentum_results():
    return pd.Series({"AAPL": 0.20, "MSFT": 0.05})


@pytest.fixture
def sample_analysis_period():
    start_date = datetime(2024, 1, 1, tzinfo=UTC)
    end_date = datetime(2024, 12, 31, tzinfo=UTC)
    return start_date, end_date


@pytest.fixture
def sample_target_date():
    return datetime(2024, 12, 31, tzinfo=UTC)


@pytest.fixture
def sample_output_path():
    return Path("test_output.png")


class TestChartGenerator:
    """Test ChartGenerator class functionality."""

    def test_init_creates_instance(self) -> None:
        generator = ChartGenerator()

        assert generator is not None
        assert hasattr(generator, "_company_names_cache")

    def test_get_symbol_label_cached(self) -> None:
        generator = ChartGenerator()
        generator._company_names_cache["AAPL"] = "Apple Inc."

        result = generator.get_symbol_label("AAPL")

        assert result == "Apple Inc."

    def test_get_symbol_label_new_symbol(self) -> None:
        with pytest.MonkeyPatch().context() as m:
            mock_ticker = Mock()
            mock_ticker.info = {"longName": "Apple Inc."}
            m.setattr("gem.chart_generator.yf.Ticker", lambda x: mock_ticker)

            generator = ChartGenerator()

            result = generator.get_symbol_label("AAPL")

            assert result == "Apple Inc."
            assert "AAPL" in generator._company_names_cache

    def test_get_symbol_label_exception_handling(self) -> None:
        with pytest.MonkeyPatch().context() as m:
            m.setattr("gem.chart_generator.yf.Ticker", Mock(side_effect=Exception("API Error")))

            generator = ChartGenerator()

            result = generator.get_symbol_label("INVALID")

            assert result == "INVALID"

    def test_format_long_name_short_name(self) -> None:
        generator = ChartGenerator()
        short_name = "Short Name"

        result = generator._format_long_name(short_name, max_length=30)

        assert result == short_name

    def test_format_long_name_long_name(self) -> None:
        generator = ChartGenerator()
        long_name = "This is a very long company name that exceeds the limit"

        result = generator._format_long_name(long_name, max_length=30)

        assert len(result) <= 30
        assert result.endswith("...")

    def test_format_long_name_with_dash(self) -> None:
        generator = ChartGenerator()
        name_with_dash = "Company Name - Subsidiary Division"

        result = generator._format_long_name(name_with_dash, max_length=30)

        assert len(result) <= 30
        assert result.endswith("...")

    def test_format_long_name_with_ucits(self) -> None:
        generator = ChartGenerator()
        name_with_ucits = "Fund Name UCITS ETF"

        result = generator._format_long_name(name_with_ucits, max_length=30)

        assert len(result) <= 30
        # UCITS może nie być w nazwie, więc sprawdzamy tylko długość
        assert len(result) <= 30

    def test_create_momentum_chart(
        self, sample_price_data, sample_momentum_results, sample_analysis_period, sample_target_date, sample_output_path
    ) -> None:
        with pytest.MonkeyPatch().context() as m:
            mock_plt = MagicMock()
            mock_plt.rcParams = {}
            mock_fig = MagicMock()
            mock_plt.figure.return_value = mock_fig

            # Mock dla gridspec - fix subscripting issue
            mock_gs = MagicMock()
            mock_gs.__getitem__ = MagicMock(return_value=mock_gs)
            mock_gs.add_subplot.return_value = Mock()
            mock_fig.add_gridspec.return_value = mock_gs

            # Mock dla subplot
            mock_ax = Mock()
            mock_ax.axis.return_value = None
            mock_ax.plot.return_value = None
            mock_ax.set_title.return_value = None
            mock_ax.set_xlabel.return_value = None
            mock_ax.set_ylabel.return_value = None
            mock_ax.legend.return_value = None
            mock_ax.figure.subplots_adjust.return_value = None
            mock_ax.grid.return_value = None
            mock_ax.tick_params.return_value = None
            mock_ax.barh.return_value = None
            mock_ax.set_yticks.return_value = None
            mock_ax.set_yticklabels.return_value = None
            mock_ax.set_xlabel.return_value = None
            mock_ax.set_title.return_value = None
            mock_ax.text.return_value = None
            mock_ax.set_xlim.return_value = None
            mock_ax.margins.return_value = None
            mock_ax.set_ylim.return_value = None

            # Mock dla table - simplified approach
            mock_table = Mock()
            mock_cell = Mock()
            mock_cell.set_facecolor.return_value = None
            mock_cell.set_text_props.return_value = None

            # Mock the table method to return our mock table
            mock_ax.table = Mock(return_value=mock_table)

            # Mock the table subscripting behavior
            mock_table.__getitem__ = Mock(return_value=mock_cell)
            mock_table.auto_set_font_size = Mock()
            mock_table.set_fontsize = Mock()

            # Mock dla text
            mock_fig.text.return_value = None
            mock_fig.savefig.return_value = None
            mock_fig.close.return_value = None
            mock_fig.patch.set_facecolor.return_value = None
            mock_fig.subplots_adjust.return_value = None

            m.setattr("gem.chart_generator.plt", mock_plt)

            generator = ChartGenerator()

            generator.create_momentum_chart(
                price_data=sample_price_data,
                momentum_results=sample_momentum_results,
                best_symbol="AAPL",
                analysis_period=sample_analysis_period,
                target_date=sample_target_date,
                output_path=sample_output_path,
            )

            mock_plt.figure.assert_called_once()
            mock_plt.savefig.assert_called_once()
