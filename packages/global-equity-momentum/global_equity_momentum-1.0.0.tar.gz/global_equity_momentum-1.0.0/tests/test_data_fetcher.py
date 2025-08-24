"""
Unit tests for data fetcher module.
"""

from datetime import UTC, datetime
from unittest.mock import Mock

import pandas as pd
import pytest
from gem.data_fetcher import DataFetcher


@pytest.fixture
def mock_ticker_data():
    return pd.DataFrame({"Close": [100.0, 101.0, 102.0]}, index=pd.date_range("2024-01-01", periods=3))


@pytest.fixture
def mock_empty_data():
    return pd.DataFrame()


@pytest.fixture
def sample_dates():
    start_date = datetime(2024, 1, 1, tzinfo=UTC)
    end_date = datetime(2024, 1, 3, tzinfo=UTC)
    return start_date, end_date


class TestDataFetcher:
    """Test DataFetcher class functionality."""

    def test_init_creates_instance(self) -> None:
        fetcher = DataFetcher()

        assert fetcher is not None
        assert fetcher.session is None

    def test_fetch_single_symbol_success(self, mock_ticker_data, sample_dates) -> None:
        with pytest.MonkeyPatch().context() as m:
            mock_ticker = Mock()
            mock_ticker.history.return_value = mock_ticker_data
            m.setattr("gem.data_fetcher.yf.Ticker", lambda x: mock_ticker)

            fetcher = DataFetcher()
            start_date, end_date = sample_dates

            result = fetcher.fetch_single_symbol("AAPL", start_date, end_date)

            assert not result.empty
            assert "AAPL" in result.columns
            assert len(result) == 3

    def test_fetch_single_symbol_empty_data(self, mock_empty_data, sample_dates) -> None:
        with pytest.MonkeyPatch().context() as m:
            mock_ticker = Mock()
            mock_ticker.history.return_value = mock_empty_data
            m.setattr("gem.data_fetcher.yf.Ticker", lambda x: mock_ticker)

            fetcher = DataFetcher()
            start_date, end_date = sample_dates

            result = fetcher.fetch_single_symbol("AAPL", start_date, end_date)

            assert result.empty

    def test_fetch_single_symbol_exception_handling(self, sample_dates) -> None:
        with pytest.MonkeyPatch().context() as m:
            m.setattr("gem.data_fetcher.yf.Ticker", Mock(side_effect=Exception("API Error")))

            fetcher = DataFetcher()
            start_date, end_date = sample_dates

            result = fetcher.fetch_single_symbol("AAPL", start_date, end_date)

            assert result.empty

    def test_fetch_data_multiple_symbols(self, sample_dates) -> None:
        with pytest.MonkeyPatch().context() as m:
            mock_data_aapl = pd.DataFrame({"Close": [100.0, 101.0]}, index=pd.date_range("2024-01-01", periods=2))
            mock_data_msft = pd.DataFrame({"Close": [200.0, 201.0]}, index=pd.date_range("2024-01-01", periods=2))

            def mock_ticker_factory(symbol):
                mock_ticker = Mock()
                if symbol == "AAPL":
                    mock_ticker.history = lambda **kwargs: mock_data_aapl
                else:
                    mock_ticker.history = lambda **kwargs: mock_data_msft
                return mock_ticker

            m.setattr("gem.data_fetcher.yf.Ticker", mock_ticker_factory)

            fetcher = DataFetcher()
            start_date, end_date = sample_dates
            symbols = ["AAPL", "MSFT"]

            result = fetcher.fetch_data(symbols, start_date, end_date)

            assert not result.empty
            assert "AAPL" in result.columns
            assert "MSFT" in result.columns
            assert len(result.columns) == 2

    def test_fetch_data_no_symbols_data(self, sample_dates) -> None:
        with pytest.MonkeyPatch().context() as m:
            mock_ticker = Mock()
            mock_ticker.history.return_value = pd.DataFrame()
            m.setattr("gem.data_fetcher.yf.Ticker", lambda x: mock_ticker)

            fetcher = DataFetcher()
            start_date, end_date = sample_dates
            symbols = ["AAPL", "MSFT"]

            result = fetcher.fetch_data(symbols, start_date, end_date)

            assert result.empty

    def test_get_latest_prices(self, mock_ticker_data) -> None:
        with pytest.MonkeyPatch().context() as m:
            mock_ticker = Mock()
            mock_ticker.history.return_value = mock_ticker_data
            m.setattr("gem.data_fetcher.yf.Ticker", lambda x: mock_ticker)

            fetcher = DataFetcher()
            symbols = ["AAPL"]

            result = fetcher.get_latest_prices(symbols)

            assert not result.empty
            assert "AAPL" in result.index
            assert result["AAPL"] == 102.0

    def test_get_latest_prices_empty_data(self) -> None:
        with pytest.MonkeyPatch().context() as m:
            mock_ticker = Mock()
            mock_ticker.history.return_value = pd.DataFrame()
            m.setattr("gem.data_fetcher.yf.Ticker", lambda x: mock_ticker)

            fetcher = DataFetcher()
            symbols = ["AAPL"]

            result = fetcher.get_latest_prices(symbols)

            assert result.empty
