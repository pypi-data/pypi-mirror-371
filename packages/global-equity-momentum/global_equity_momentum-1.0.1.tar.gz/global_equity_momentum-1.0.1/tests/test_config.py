"""
Unit tests for configuration module.
"""

from pathlib import Path

from gem.config import (
    CHART_PALETTE,
    CHART_STYLE,
    DEFAULT_SYMBOLS,
    DPI,
    FIGURE_SIZE,
    LOOKBACK_MONTHS,
    OUTPUT_DIR,
    SKIP_MONTHS,
)


class TestConfig:
    """Test configuration constants and settings."""

    def test_default_symbols_are_list(self) -> None:
        assert isinstance(DEFAULT_SYMBOLS, list)
        assert all(isinstance(symbol, str) for symbol in DEFAULT_SYMBOLS)
        assert len(DEFAULT_SYMBOLS) > 0

    def test_default_symbols_contain_expected_values(self) -> None:
        expected_symbols = ["EIMI.L", "IWDA.L", "CBU0.L", "IB01.L", "CNDX.L", "CSP1.L"]
        assert expected_symbols == DEFAULT_SYMBOLS

    def test_lookback_months_is_valid(self) -> None:
        assert isinstance(LOOKBACK_MONTHS, int)
        assert LOOKBACK_MONTHS > 0
        assert LOOKBACK_MONTHS == 12

    def test_skip_months_is_valid(self) -> None:
        assert isinstance(SKIP_MONTHS, int)
        assert SKIP_MONTHS >= 0
        assert SKIP_MONTHS == 1

    def test_chart_style_is_string(self) -> None:
        assert isinstance(CHART_STYLE, str)
        assert CHART_STYLE == "whitegrid"

    def test_chart_palette_is_string(self) -> None:
        assert isinstance(CHART_PALETTE, str)
        assert CHART_PALETTE == "husl"

    def test_figure_size_is_tuple(self) -> None:
        assert isinstance(FIGURE_SIZE, tuple)
        assert len(FIGURE_SIZE) == 2
        assert all(isinstance(dim, int) for dim in FIGURE_SIZE)
        assert FIGURE_SIZE == (16, 12)

    def test_dpi_is_positive_integer(self) -> None:
        assert isinstance(DPI, int)
        assert DPI > 0
        assert DPI == 300

    def test_output_dir_is_path(self) -> None:
        assert isinstance(OUTPUT_DIR, Path)
        assert OUTPUT_DIR.name == "output"
