"""Tests for the cp command functionality."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from ai_cli.cli import app
from ai_cli.core.history import ResponseEntry, ResponseHistory
from ai_cli.ui.selector import ResponseSelector


class TestCpCommand:
    """Test cp command functionality."""

    def test_cp_command_help(self):
        """Test cp command help."""
        from ai_cli.utils.text import strip_rich_formatting

        runner = CliRunner()
        result = runner.invoke(app, ["cp", "--help"])
        assert result.exit_code == 0

        # Strip ANSI/Rich formatting from output for reliable text searching
        clean_output = strip_rich_formatting(result.output)
        assert "Copy AI response to clipboard" in clean_output
        assert "--show" in clean_output

    @patch("ai_cli.cli.copy_to_clipboard")
    @patch("ai_cli.cli.ResponseHistory")
    def test_cp_command_latest_success(self, mock_history_class, mock_copy):
        """Test copying latest response successfully."""
        # Setup mock
        mock_history = MagicMock()
        mock_history_class.return_value = mock_history
        mock_response = ResponseEntry(
            timestamp="2024-01-01T00:00:00Z",
            prompt="Test prompt",
            response="Test response",
            model="test-model",
            preview="Test response",
        )
        mock_history.get_latest.return_value = mock_response
        mock_copy.return_value = True

        runner = CliRunner()
        result = runner.invoke(app, ["cp"])

        assert result.exit_code == 0
        mock_copy.assert_called_once()
        mock_history.get_latest.assert_called_once()

    @patch("ai_cli.cli.ResponseHistory")
    def test_cp_command_no_history(self, mock_history_class):
        """Test cp command with no history."""
        # Setup mock
        mock_history = MagicMock()
        mock_history_class.return_value = mock_history
        mock_history.get_latest.return_value = None

        runner = CliRunner()
        result = runner.invoke(app, ["cp"])

        assert result.exit_code == 0
        assert "No response history found" in result.output

    @patch("ai_cli.cli.copy_to_clipboard")
    @patch("ai_cli.cli.ResponseSelector")
    @patch("ai_cli.cli.ResponseHistory")
    def test_cp_command_show_success(
        self, mock_history_class, mock_selector_class, mock_copy
    ):
        """Test cp command with --show option."""
        # Setup mocks
        mock_history = MagicMock()
        mock_history_class.return_value = mock_history
        mock_responses = [
            ResponseEntry(
                timestamp="2024-01-01T00:00:00Z",
                prompt="Test prompt",
                response="Test response",
                model="test-model",
                preview="Test response",
            )
        ]
        mock_history.get_responses.return_value = mock_responses

        mock_selector = MagicMock()
        mock_selector_class.return_value = mock_selector
        mock_selector.select_response.return_value = "Test response"
        mock_copy.return_value = True

        runner = CliRunner()
        result = runner.invoke(app, ["cp", "--show"])

        assert result.exit_code == 0
        mock_selector.select_response.assert_called_once_with(mock_responses)
        mock_copy.assert_called_once()

    @patch("ai_cli.cli.ResponseSelector")
    @patch("ai_cli.cli.ResponseHistory")
    def test_cp_command_show_cancelled(self, mock_history_class, mock_selector_class):
        """Test cp command with --show option when user cancels."""
        # Setup mocks
        mock_history = MagicMock()
        mock_history_class.return_value = mock_history
        mock_responses = []
        mock_history.get_responses.return_value = mock_responses

        mock_selector = MagicMock()
        mock_selector_class.return_value = mock_selector
        mock_selector.select_response.return_value = None

        runner = CliRunner()
        result = runner.invoke(app, ["cp", "--show"])

        assert result.exit_code == 0
        assert "No response selected" in result.output


class TestResponseHistory:
    """Test ResponseHistory functionality."""

    def test_response_history_init(self):
        """Test ResponseHistory initialization."""
        history = ResponseHistory(max_responses=10, preview_length=30)
        assert history.max_responses == 10
        assert history.preview_length == 30

    def test_create_preview_short_text(self):
        """Test preview creation for short text."""
        history = ResponseHistory(preview_length=50)
        text = "Short response"
        preview = history._create_preview(text)
        assert preview == "Short response"

    def test_create_preview_long_text(self):
        """Test preview creation for long text."""
        history = ResponseHistory(preview_length=10)
        text = "This is a very long response that should be truncated"
        preview = history._create_preview(text)
        assert preview == "This is a ..."
        assert len(preview) == 13  # 10 chars + "..."

    def test_create_preview_strips_whitespace(self):
        """Test preview creation strips whitespace."""
        history = ResponseHistory(preview_length=50)
        text = "  \n  Response with whitespace  \n  "
        preview = history._create_preview(text)
        assert preview == "Response with whitespace"


class TestTextProcessing:
    """Test text processing utilities."""

    def test_strip_ansi_color_codes(self):
        """Test stripping ANSI color codes from text."""
        from ai_cli.utils.text import _strip_basic_formatting

        # Test the exact cases from the bug reports
        test_cases = [
            # Exact user-reported problematic strings
            (
                "[1;33m 1 Google Text-to-Speech: Google's Text-to-Speech engine",
                " 1 Google Text-to-Speech: Google's Text-to-Speech engine",
            ),
            (
                "The capital of the USA is mWashington, D.C.0m",
                "The capital of the USA is Washington, D.C.",
            ),
            ("<ox1b>[1;33m 1 ElevenLabs:", " 1 ElevenLabs:"),
            (
                "The capital of the USA is [1mWashington, D.C.[0m",
                "The capital of the USA is Washington, D.C.",
            ),
            (
                "The capital of the USA is <0x1b>[1mWashington, D.C.<0x1b>0m",
                "The capital of the USA is Washington, D.C.",
            ),
            # Standard ANSI sequences
            ("[0m", ""),
            ("[1;31mRed text[0m", "Red text"),
            ("[33mYellow[0m", "Yellow"),
            ("Normal [1;33mYellow[0m Normal", "Normal Yellow Normal"),
            ("\x1b[1;33mProper ANSI\x1b[0m", "Proper ANSI"),
            # Hex representations
            ("<0x1b>[31mRed<0x1b>[0m", "Red"),
            ("<ox1b>[1;33m text", " text"),
            ("<0x1b>[1m text", " text"),
            # Bold markdown
            ("**Washington, D.C.**", "Washington, D.C."),
            ("Text with **bold** content", "Text with bold content"),
            # Various m...0m patterns
            ("mText here0m and normal text", "Text here and normal text"),
            ("mWashington, D.C.0m", "Washington, D.C."),
            ("Text with mBold Text0m content", "Text with Bold Text content"),
            # Edge cases
            ("[1m[0m", ""),
            ("[1;33m[0m", ""),
            ("m0m", ""),
        ]

        for input_text, expected in test_cases:
            result = _strip_basic_formatting(input_text)
            assert (
                result == expected
            ), f"Failed for '{input_text}': got '{result}', expected '{expected}'"


class TestResponseSelector:
    """Test ResponseSelector functionality."""

    def test_selector_init(self):
        """Test ResponseSelector initialization."""
        mock_console = MagicMock()
        selector = ResponseSelector(mock_console)
        assert selector.console == mock_console

    def test_select_response_empty_list(self):
        """Test select_response with empty response list."""
        mock_console = MagicMock()
        selector = ResponseSelector(mock_console)
        result = selector.select_response([])
        assert result is None
        mock_console.print.assert_called_once_with(
            "[yellow]No response history found[/yellow]"
        )

    @patch("ai_cli.ui.selector.questionary.select")
    def test_select_response_user_cancels(self, mock_select):
        """Test select_response when user cancels."""
        mock_select.return_value.ask.return_value = None
        mock_console = MagicMock()
        selector = ResponseSelector(mock_console)
        responses = [
            ResponseEntry(
                timestamp="2024-01-01T00:00:00Z",
                prompt="Test",
                response="Test response",
                model="test-model",
                preview="Test response",
            )
        ]
        result = selector.select_response(responses)
        assert result is None

    @patch("ai_cli.ui.selector.questionary.select")
    def test_select_response_success(self, mock_select):
        """Test successful response selection."""
        mock_select.return_value.ask.return_value = "1. Test response"
        mock_console = MagicMock()
        selector = ResponseSelector(mock_console)
        responses = [
            ResponseEntry(
                timestamp="2024-01-01T00:00:00Z",
                prompt="Test",
                response="Full test response",
                model="test-model",
                preview="Test response",
            )
        ]
        result = selector.select_response(responses)
        assert result == "Full test response"
