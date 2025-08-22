"""Tests for the CLI module."""

import json
import tempfile
from unittest.mock import patch

import pytest

from stac_sample_maker.cli import main, parse_args


class TestParseArgs:
    """Tests for argument parsing."""

    def test_default_args(self) -> None:
        """Test default argument values."""
        args = parse_args(["--num-items", "5"])

        assert args.num_items == 5
        assert args.template is None
        assert args.output is None
        assert args.start is None
        assert args.end is None
        assert args.interval_percent == 0.2
        assert args.bbox is None
        assert args.seed is None
        assert args.validate is False

    def test_all_args(self) -> None:
        """Test parsing all arguments."""
        args = parse_args(
            [
                "--num-items",
                "10",
                "--template",
                "template.json",
                "--output",
                "output.ndjson",
                "--start",
                "2023-01-01T00:00:00Z",
                "--end",
                "2023-12-31T23:59:59Z",
                "--interval-percent",
                "0.5",
                "--bbox",
                "-122.5",
                "37.7",
                "-122.3",
                "37.8",
                "--seed",
                "42",
                "--validate",
            ]
        )

        assert args.num_items == 10
        assert args.template == "template.json"
        assert args.output == "output.ndjson"
        assert args.start == "2023-01-01T00:00:00Z"
        assert args.end == "2023-12-31T23:59:59Z"
        assert args.interval_percent == 0.5
        assert args.bbox == [-122.5, 37.7, -122.3, 37.8]
        assert args.seed == 42
        assert args.validate is True


class TestMain:
    """Tests for the main CLI function."""

    def test_basic_generation(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test basic item generation to stdout."""
        exit_code = main(["--num-items", "1", "--seed", "42"])

        assert exit_code == 0

        captured = capsys.readouterr()

        # Should output one JSON line to stdout
        stdout_lines = captured.out.strip().split("\n")
        assert len(stdout_lines) == 1

        # Should be valid JSON
        item = json.loads(stdout_lines[0])
        assert item["type"] == "Feature"
        assert item["stac_version"] == "1.1.0"

        # Should print summary to stderr
        assert "Generated 1 STAC items" in captured.err

    def test_file_output(self) -> None:
        """Test generating items to a file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False) as f:
            temp_path = f.name

        try:
            exit_code = main(["--num-items", "2", "--seed", "42", "--output", temp_path])

            assert exit_code == 0

            # Read the file and verify contents
            with open(temp_path) as f:
                lines = f.readlines()

            assert len(lines) == 2

            # Each line should be valid JSON
            for line in lines:
                item = json.loads(line)
                assert item["type"] == "Feature"

        finally:
            import os

            os.unlink(temp_path)

    def test_template_generation(
        self, temp_template_file: str, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test generating items from a template."""
        exit_code = main(["--template", temp_template_file, "--num-items", "1", "--seed", "42"])

        assert exit_code == 0

        captured = capsys.readouterr()
        stdout_lines = captured.out.strip().split("\n")

        item = json.loads(stdout_lines[0])

        # Should match template structure
        assert item["type"] == "Feature"
        assert "thumbnail" in item["assets"]

    def test_error_handling_invalid_bbox(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test error handling for invalid bbox."""
        exit_code = main(
            [
                "--num-items",
                "1",
                "--bbox",
                "-122.3",
                "37.7",
                "-122.5",
                "37.8",  # Invalid: minx > maxx
            ]
        )

        assert exit_code == 1

        captured = capsys.readouterr()
        assert "Error:" in captured.err

    def test_error_handling_nonexistent_template(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test error handling for nonexistent template."""
        exit_code = main(["--template", "/nonexistent/file.json", "--num-items", "1"])

        assert exit_code == 1

        captured = capsys.readouterr()
        assert "Error:" in captured.err

    @patch("stac_sample_maker.generator.VALIDATION_AVAILABLE", False)
    def test_validation_without_library(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test validation request without stac-validator installed."""
        exit_code = main(["--num-items", "1", "--validate"])

        assert exit_code == 1

        captured = capsys.readouterr()
        assert "stac-validator is not installed" in captured.err
