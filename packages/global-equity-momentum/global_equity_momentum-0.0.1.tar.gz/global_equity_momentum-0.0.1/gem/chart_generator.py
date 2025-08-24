"""
Chart generation module using seaborn and matplotlib.
"""

from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import yfinance as yf
from loguru import logger
from matplotlib.axes import Axes

from gem.config import CHART_STYLE, DPI, FIGURE_SIZE


class ChartGenerator:
    """Handles chart generation for momentum analysis."""

    def __init__(self) -> None:
        sns.set_style(CHART_STYLE)
        plt.rcParams["figure.facecolor"] = "white"
        plt.rcParams["axes.facecolor"] = "white"
        self._company_names_cache = {}

    def get_symbol_label(self, symbol: str | int | None) -> str:
        """Get descriptive label for symbol using company name from yfinance."""
        if symbol in self._company_names_cache:
            return self._company_names_cache[symbol]

        try:
            ticker = yf.Ticker(symbol)
            company_name = ticker.info.get("longName", symbol)

            max_company_name_length = 40
            if len(company_name) > max_company_name_length:
                company_name = company_name[: max_company_name_length - 3] + "..."

            self._company_names_cache[symbol] = company_name
            return company_name
        except Exception as e:
            logger.warning(f"Could not fetch company name for {symbol}: {e}")
            return str(symbol)

    def _format_long_name(self, company_name: str, max_length: int = 30) -> str:  # noqa: PLR0911 C901
        """Format long company names with smart truncation and line breaks."""
        if len(company_name) <= max_length:
            return company_name

        if " - " in company_name:
            parts = company_name.split(" - ")
            if len(parts[0]) <= max_length - 3:
                return parts[0] + "..."

        if " UCITS" in company_name:
            ucuts_pos = company_name.find(" UCITS")
            if ucuts_pos <= max_length - 3:
                return company_name[:ucuts_pos] + "..."

        if " ETF" in company_name:
            etf_pos = company_name.find(" ETF")
            if etf_pos <= max_length - 3:
                return company_name[:etf_pos] + "..."

        words = company_name.split()
        if len(words) > 1:
            for i in range(len(words) - 1, 0, -1):
                first_part = " ".join(words[:i])
                if len(first_part) <= max_length - 3:
                    return first_part + "..."

        return company_name[: max_length - 3] + "..."

    def create_momentum_chart(
        self,
        price_data: pd.DataFrame,
        momentum_results: pd.Series,
        best_symbol: str,
        analysis_period: tuple[datetime, datetime],
        target_date: datetime,
        output_path: Path,
    ):
        """
        Create comprehensive momentum analysis chart.

        Args:
            price_data: Historical price data
            momentum_results: Momentum calculation results
            best_symbol: Best performing symbol
            analysis_period: Tuple of (start_date, end_date)
            target_date: Target date for analysis
            output_path: Path to save the chart
        """
        logger.info("Creating momentum analysis chart")

        fig = plt.figure(figsize=FIGURE_SIZE)

        fig.patch.set_facecolor("white")

        gs = fig.add_gridspec(2, 2, height_ratios=[1.5, 1], width_ratios=[1, 1], hspace=0.3, wspace=0.4)

        fig.subplots_adjust(left=0.1, right=0.85, top=0.95, bottom=0.15)

        ax1 = fig.add_subplot(gs[0, :])
        self._create_price_evolution_chart(ax1, price_data, best_symbol, analysis_period, target_date)

        ax2 = fig.add_subplot(gs[1, 0])
        self._create_momentum_bar_chart(ax2, momentum_results, best_symbol)

        ax3 = fig.add_subplot(gs[1, 1])
        self._create_performance_table(ax3, momentum_results, price_data)

        company_name = self.get_symbol_label(best_symbol)
        recommendation_text = (
            f"CURRENT RECOMMENDATION: {company_name} ({best_symbol})\n"
            f"Based on Global Equity Momentum (GEM) strategy with 12-month lookback and 1-month skip"
        )

        fig.text(
            0.5,
            0.05,
            recommendation_text,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            bbox={"boxstyle": "round,pad=0.8", "facecolor": "lightgreen", "alpha": 0.8, "ec": "black"},
        )

        plt.savefig(output_path, dpi=DPI, bbox_inches="tight", facecolor="white", edgecolor="none", pad_inches=0.2)
        plt.close()

        logger.info(f"Chart saved to: {output_path}")

    def _create_price_evolution_chart(
        self,
        ax: Axes,
        price_data: pd.DataFrame,
        best_symbol: str,
        analysis_period: tuple[datetime, datetime],
        target_date: datetime,
    ) -> None:
        """Create normalized price evolution chart."""
        normalized_data = price_data.div(price_data.iloc[0]) * 100

        for symbol in normalized_data.columns:
            linewidth = 3 if symbol == best_symbol else 1.5
            alpha = 1.0 if symbol == best_symbol else 0.7

            company_name = self.get_symbol_label(symbol)
            label = f"{company_name} ({symbol})" if company_name != symbol else symbol

            ax.plot(normalized_data.index, normalized_data[symbol], label=label, linewidth=linewidth, alpha=alpha)

        start_date, end_date = analysis_period
        ax.set_title(
            f"Price Evolution (Normalized to 100)\n"
            f"Dual Momentum Analysis - Target: {target_date.strftime('%B %d, %Y')}\n"
            f"Analysis Period: {start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')}",
            fontsize=12,
            fontweight="bold",
            y=1,
        )

        ax.set_xlabel("Date", fontsize=10)
        ax.set_ylabel("Normalized Price", fontsize=10)

        ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8, frameon=True, fancybox=True, shadow=True)

        ax.figure.subplots_adjust(right=0.78)

        ax.grid(True, alpha=0.3)
        ax.tick_params(axis="both", which="major", labelsize=9)

    def _create_momentum_bar_chart(self, ax: Axes, momentum_results: pd.Series, best_symbol: str) -> None:
        """Create horizontal momentum bar chart."""
        sorted_momentum = momentum_results.sort_values(ascending=True)

        colors = ["gold" if symbol == best_symbol else "skyblue" for symbol in sorted_momentum.index]

        ax.barh(
            range(len(sorted_momentum)),
            sorted_momentum.values * 100,  # pyright: ignore [reportOperatorIssue]
            color=colors,
            alpha=0.8,
            edgecolor="black",
            linewidth=0.5,
            height=0.6,
        )

        ax.set_yticks(range(len(sorted_momentum)))
        y_labels = []
        for s in sorted_momentum.index:
            company_name = self.get_symbol_label(s)
            if company_name != s:
                formatted_name = self._format_long_name(company_name, 35)
                y_labels.append(f"{formatted_name}\n({s})")
            else:
                y_labels.append(s)
        ax.set_yticklabels(y_labels, fontsize=8)
        ax.set_xlabel("Total Return (%)", fontsize=10)
        ax.set_title("12-Month Momentum Rankings", fontsize=12, fontweight="bold", pad=5)

        for i, (symbol, value) in enumerate(sorted_momentum.items()):
            ax.text(
                value * 100 + (0.5 if value >= 0 else -0.5),
                i,
                f"{value:.1%}",
                ha="left" if value >= 0 else "right",
                va="center",
                fontweight="bold" if symbol == best_symbol else "normal",
                fontsize=9,
            )

        ax.grid(True, axis="x", alpha=0.3)
        ax.tick_params(axis="x", which="major", labelsize=9)

        max_return = sorted_momentum.max() * 100
        ax.set_xlim(0, max_return * 1.15)

        ax.margins(y=0.2)

        ax.set_ylim(-0.8, len(sorted_momentum) - 0.2)

        ax.set_xlim(0, max_return * 1.2)

    def _create_performance_table(self, ax: Axes, momentum_results: pd.Series, price_data: pd.DataFrame) -> None:
        """Create performance statistics table."""
        ax.axis("off")

        stats_data = []
        for symbol in momentum_results.index:
            momentum = momentum_results[symbol]

            returns = price_data[symbol].pct_change().dropna()
            volatility = returns.std() * (252**0.5)

            company_name = self.get_symbol_label(symbol)
            formatted_name = self._format_long_name(company_name, 30)
            display_name = f"{formatted_name} ({symbol})" if company_name != symbol else symbol

            stats_data.append([display_name, f"{momentum:.1%}", f"{volatility:.1%}"])

        stats_data.sort(key=lambda x: float(x[1].strip("%")), reverse=True)

        table = ax.table(
            cellText=stats_data,
            colLabels=["Symbol", "Return", "Volatility"],
            cellLoc="center",
            loc="center",
            bbox=[0, 0.1, 1, 0.8],  # pyright: ignore [reportArgumentType]
            colWidths=[0.65, 0.18, 0.17],
        )

        table.auto_set_font_size(False)
        table.set_fontsize(7)

        for i in range(len(stats_data) + 1):
            for j in range(3):
                cell = table[(i, j)]
                if i == 0:
                    cell.set_facecolor("#4CAF50")
                    cell.set_text_props(weight="bold", color="white")
                elif i == 1:
                    cell.set_facecolor("#FFD700")
                    cell.set_text_props(weight="bold")
                else:
                    cell.set_facecolor("#F5F5F5")

        ax.set_title("Performance Statistics", fontsize=12, fontweight="bold", pad=5)
