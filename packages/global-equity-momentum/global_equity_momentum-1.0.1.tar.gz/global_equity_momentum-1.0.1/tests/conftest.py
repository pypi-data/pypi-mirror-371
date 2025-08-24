"""
Shared fixtures for all tests.
"""

from datetime import UTC, datetime
from unittest.mock import Mock

import pandas as pd
import pytest


@pytest.fixture
def sample_datetime():
    """Sample datetime for testing."""
    return datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def sample_date_range():
    """Sample date range for testing."""
    start_date = datetime(2024, 1, 1, tzinfo=UTC)
    end_date = datetime(2024, 12, 31, tzinfo=UTC)
    return start_date, end_date


@pytest.fixture
def sample_price_series():
    """Sample price series for testing."""
    return pd.Series([100.0, 110.0, 120.0], index=pd.date_range("2024-01-01", periods=3))


@pytest.fixture
def sample_price_dataframe():
    """Sample price dataframe for testing."""
    return pd.DataFrame(
        {"AAPL": [100.0, 110.0, 120.0], "MSFT": [200.0, 190.0, 210.0], "GOOGL": [150.0, 160.0, 170.0]},
        index=pd.date_range("2024-01-01", periods=3),
    )


@pytest.fixture
def sample_momentum_series():
    """Sample momentum series for testing."""
    return pd.Series({"AAPL": 0.20, "MSFT": 0.05, "GOOGL": 0.13})


@pytest.fixture
def mock_yfinance_ticker():
    """Mock yfinance Ticker for testing."""
    mock_ticker = Mock()
    mock_ticker.info = {"longName": "Test Company Name"}
    mock_ticker.history.return_value = pd.DataFrame(
        {"Close": [100.0, 101.0, 102.0]}, index=pd.date_range("2024-01-01", periods=3)
    )
    return mock_ticker
