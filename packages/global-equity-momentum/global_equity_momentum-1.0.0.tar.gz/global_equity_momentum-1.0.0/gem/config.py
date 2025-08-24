"""
Configuration settings for Dual Momentum Investing Strategy.
"""

from pathlib import Path

DEFAULT_SYMBOLS = [
    "EIMI.L",
    "IWDA.L",
    "CBU0.L",
    "IB01.L",
    "CNDX.L",
    "CSP1.L",
]

LOOKBACK_MONTHS = 12
SKIP_MONTHS = 1

CHART_STYLE = "whitegrid"
CHART_PALETTE = "husl"
FIGURE_SIZE = (16, 12)
DPI = 300

OUTPUT_DIR = Path.cwd() / "output"
