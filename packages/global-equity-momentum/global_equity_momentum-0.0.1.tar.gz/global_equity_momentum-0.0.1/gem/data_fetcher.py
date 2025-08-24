from datetime import UTC, datetime

import pandas as pd
import yfinance as yf
from loguru import logger


class DataFetcher:
    def __init__(self) -> None:
        self.session = None

    def fetch_single_symbol(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval="1d", auto_adjust=True, prepost=True)

            if data.empty:
                logger.warning(f"No data returned for {symbol}")
                return pd.DataFrame()

            data = data[["Close"]].rename(columns={"Close": symbol})  # pyright: ignore [reportCallIssue]
            logger.info(f"Fetched {len(data)} records for {symbol}")

            return data

        except Exception as e:
            logger.exception(f"Error fetching data for {symbol}: {e!s}")
            return pd.DataFrame()

    def fetch_data(self, symbols: list[str], start_date: datetime, end_date: datetime) -> pd.DataFrame:
        logger.info(f"Fetching data for {len(symbols)} symbols")

        all_data = []

        for symbol in symbols:
            symbol_data = self.fetch_single_symbol(symbol, start_date, end_date)
            if not symbol_data.empty:
                all_data.append(symbol_data)

        if not all_data:
            logger.error("No data fetched for any symbol")
            return pd.DataFrame()

        combined_data = pd.concat(all_data, axis=1)
        combined_data = combined_data.ffill()
        combined_data = combined_data.dropna(how="all")

        logger.info(f"Combined dataset shape: {combined_data.shape}")
        logger.info(f"Date range: {combined_data.index.min()} to {combined_data.index.max()}")

        return combined_data

    def get_latest_prices(self, symbols: list[str]) -> pd.Series:
        end_date = datetime.now(UTC)
        start_date = datetime.now(UTC).replace(day=1)

        data = self.fetch_data(symbols, start_date, end_date)

        if data.empty:
            return pd.Series()

        return data.iloc[-1]
