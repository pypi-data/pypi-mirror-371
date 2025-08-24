"""
Unit tests for argument parser module.
"""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from gem.parser import create_parser, get_output_path


@pytest.fixture
def mock_datetime():
    mock_now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with pytest.MonkeyPatch().context() as m:
        mock_dt = Mock()
        mock_dt.now = Mock(return_value=mock_now)
        m.setattr("gem.parser.datetime", mock_dt)
        yield mock_now


@pytest.fixture
def mock_output_dir():
    with pytest.MonkeyPatch().context() as m:
        mock_dir = Mock()
        mock_dir.exists.return_value = True
        mock_dir.__truediv__ = Mock(return_value="output/momentum_analysis_20240101_120000.png")
        m.setattr("gem.parser.OUTPUT_DIR", mock_dir)
        yield mock_dir


class TestParser:
    """Test argument parser functionality."""

    def test_create_parser_returns_argument_parser(self) -> None:
        parser = create_parser()

        assert parser is not None
        assert hasattr(parser, "parse_args")

    def test_parser_has_required_arguments(self) -> None:
        parser = create_parser()
        actions = [action.dest for action in parser._actions]

        expected_args = ["mode", "symbols", "date", "output", "lookback_months", "skip_months"]
        for arg in expected_args:
            assert arg in actions

    def test_mode_argument_choices(self) -> None:
        parser = create_parser()
        mode_action = next(action for action in parser._actions if action.dest == "mode")

        assert mode_action.choices == ["analyze", "validate"]

    def test_mode_argument_default(self) -> None:
        parser = create_parser()
        args = parser.parse_args([])

        assert args.mode == "analyze"

    def test_symbols_argument_default(self) -> None:
        parser = create_parser()
        args = parser.parse_args([])

        assert args.symbols == ["EIMI.L", "IWDA.L", "CBU0.L", "IB01.L", "CNDX.L", "CSP1.L"]

    def test_lookback_months_argument_default(self) -> None:
        parser = create_parser()
        args = parser.parse_args([])

        assert args.lookback_months == 12

    def test_skip_months_argument_default(self) -> None:
        parser = create_parser()
        args = parser.parse_args([])

        assert args.skip_months == 1

    def test_parser_with_custom_arguments(self) -> None:
        parser = create_parser()
        test_args = [
            "--mode",
            "validate",
            "--symbols",
            "AAPL",
            "MSFT",
            "--date",
            "2024-01-01",
            "--output",
            "test.png",
            "--lookback-months",
            "6",
            "--skip-months",
            "2",
        ]

        args = parser.parse_args(test_args)

        assert args.mode == "validate"
        assert args.symbols == ["AAPL", "MSFT"]
        assert args.date == "2024-01-01"
        assert args.output == "test.png"
        assert args.lookback_months == 6
        assert args.skip_months == 2


class TestGetOutputPath:
    """Test output path generation functionality."""

    def test_get_output_path_with_custom_arg(self) -> None:
        custom_path = "custom_output.png"

        result = get_output_path(custom_path)

        assert result == custom_path

    def test_get_output_path_generates_default(self, mock_datetime, mock_output_dir) -> None:
        result = get_output_path(None)

        expected_filename = "momentum_analysis_20240101_120000.png"
        assert result.endswith(expected_filename)

    def test_get_output_path_creates_directory_if_not_exists(self, mock_datetime) -> None:
        with pytest.MonkeyPatch().context() as m:
            mock_output_dir = Mock()
            mock_output_dir.exists.return_value = False
            mock_output_dir.__truediv__ = Mock(return_value="output/momentum_analysis_20240101_120000.png")
            m.setattr("gem.parser.OUTPUT_DIR", mock_output_dir)

            get_output_path(None)

            mock_output_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)
