"""Tests for the generator module."""

import json
import os
import tempfile
from typing import Any

import pytest

from stac_sample_maker.generator import (
    analyze_template_item,
    generate_stac_items,
    generate_stac_items_from_template,
    iso_to_dt,
    validate_stac_item,
    write_ndjson,
)


class TestIsoToDatetime:
    """Tests for iso_to_dt function."""

    def test_iso_to_dt_with_z_suffix(self) -> None:
        """Test parsing ISO datetime with Z suffix."""
        dt = iso_to_dt("2023-06-15T10:30:00Z")
        assert dt is not None
        assert dt.year == 2023
        assert dt.month == 6
        assert dt.day == 15

    def test_iso_to_dt_with_offset(self) -> None:
        """Test parsing ISO datetime with timezone offset."""
        dt = iso_to_dt("2023-06-15T10:30:00+00:00")
        assert dt is not None
        assert dt.year == 2023

    def test_iso_to_dt_with_none(self) -> None:
        """Test parsing None returns None."""
        assert iso_to_dt(None) is None

    def test_iso_to_dt_with_empty_string(self) -> None:
        """Test parsing empty string returns None."""
        assert iso_to_dt("") is None

    def test_iso_to_dt_with_invalid_format(self) -> None:
        """Test parsing invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid ISO datetime"):
            iso_to_dt("not-a-date")


class TestGenerateStacItems:
    """Tests for generate_stac_items function."""

    def test_generate_single_item(self) -> None:
        """Test generating a single STAC item."""
        items = generate_stac_items(num_items=1, seed=42)

        assert len(items) == 1
        item = items[0]

        # Basic STAC item structure
        assert item["type"] == "Feature"
        assert item["stac_version"] == "1.1.0"
        assert "id" in item
        assert "bbox" in item
        assert "geometry" in item
        assert "properties" in item
        assert "links" in item
        assert "assets" in item
        assert "stac_extensions" in item

    def test_generate_multiple_items(self) -> None:
        """Test generating multiple STAC items."""
        items = generate_stac_items(num_items=5, seed=42)

        assert len(items) == 5

        # All items should have unique IDs
        ids = [item["id"] for item in items]
        assert len(set(ids)) == 5

    def test_generate_with_bbox(self) -> None:
        """Test generating items within a bounding box."""
        bbox = (-122.5, 37.7, -122.3, 37.8)
        items = generate_stac_items(num_items=3, bbox=bbox, seed=42)

        for item in items:
            item_bbox = item["bbox"]
            # Generated bbox should be within the specified bbox
            assert item_bbox[0] >= bbox[0]  # minx
            assert item_bbox[1] >= bbox[1]  # miny
            assert item_bbox[2] <= bbox[2]  # maxx
            assert item_bbox[3] <= bbox[3]  # maxy

    def test_generate_with_date_range(self) -> None:
        """Test generating items within a date range."""
        items = generate_stac_items(
            num_items=3, start_date="2023-01-01T00:00:00Z", end_date="2023-12-31T23:59:59Z", seed=42
        )

        for item in items:
            props = item["properties"]
            if "datetime" in props and props["datetime"]:
                dt_str = props["datetime"]
                assert dt_str.startswith("2023")

    def test_generate_with_intervals(self) -> None:
        """Test generating items with time intervals."""
        items = generate_stac_items(
            num_items=10,
            interval_percent=1.0,  # All items should have intervals
            seed=42,
        )

        for item in items:
            props = item["properties"]
            # Should have start/end datetime and null datetime
            assert props["datetime"] is None
            assert "start_datetime" in props
            assert "end_datetime" in props

    def test_generate_with_invalid_bbox(self) -> None:
        """Test that invalid bbox raises ValueError."""
        with pytest.raises(ValueError, match="bbox must be"):
            generate_stac_items(num_items=1, bbox=(-122.3, 37.7, -122.5, 37.8))

    def test_generate_with_invalid_interval_percent(self) -> None:
        """Test that invalid interval_percent raises ValueError."""
        with pytest.raises(ValueError, match="interval_percent must be between 0 and 1"):
            generate_stac_items(num_items=1, interval_percent=1.5)

    def test_reproducibility_with_seed(self) -> None:
        """Test that same seed produces same results."""
        items1 = generate_stac_items(num_items=2, seed=42)
        items2 = generate_stac_items(num_items=2, seed=42)

        assert items1[0]["id"] == items2[0]["id"]
        assert items1[1]["id"] == items2[1]["id"]


class TestGenerateFromTemplate:
    """Tests for generate_stac_items_from_template function."""

    def test_generate_from_template(self, temp_template_file: str) -> None:
        """Test generating items from a template."""
        items = generate_stac_items_from_template(
            template_path=temp_template_file, num_items=3, seed=42
        )

        assert len(items) == 3

        # All items should have the same structure as template
        for item in items:
            assert item["type"] == "Feature"
            assert item["stac_version"] == "1.1.0"
            assert len(item["stac_extensions"]) == 0  # Template has no extensions
            assert "thumbnail" in item["assets"]

    def test_generate_from_interval_template(self, temp_interval_template_file: str) -> None:
        """Test generating items from an interval template."""
        items = generate_stac_items_from_template(
            template_path=temp_interval_template_file, num_items=2, seed=42
        )

        for item in items:
            props = item["properties"]
            # Should preserve interval structure
            assert props["datetime"] is None
            assert "start_datetime" in props
            assert "end_datetime" in props
            assert "data" in item["assets"]

    def test_template_with_nonexistent_file(self) -> None:
        """Test that nonexistent template file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            generate_stac_items_from_template(template_path="/nonexistent/file.json", num_items=1)


class TestAnalyzeTemplate:
    """Tests for analyze_template_item function."""

    def test_analyze_instant_template(self, sample_stac_item: dict[str, Any]) -> None:
        """Test analyzing a template with instant datetime."""
        analysis = analyze_template_item(sample_stac_item)

        assert analysis["temporal_type"] == "instant"
        assert analysis["extensions"] == []
        assert "thumbnail" in analysis["asset_keys"]
        assert analysis["has_bbox"] is True
        assert analysis["has_geometry"] is True

    def test_analyze_interval_template(self, interval_stac_item: dict[str, Any]) -> None:
        """Test analyzing a template with interval datetime."""
        analysis = analyze_template_item(interval_stac_item)

        assert analysis["temporal_type"] == "interval"
        assert "data" in analysis["asset_keys"]

    def test_analyze_template_with_extensions(self) -> None:
        """Test analyzing a template with extensions."""
        template = {
            "type": "Feature",
            "stac_version": "1.1.0",
            "id": "test",
            "properties": {"datetime": "2023-01-01T00:00:00Z"},
            "stac_extensions": ["https://stac-extensions.github.io/eo/v1.1.0/schema.json"],
            "assets": {},
        }

        analysis = analyze_template_item(template)
        assert len(analysis["extensions"]) == 1
        assert "eo" in analysis["extensions"][0]


class TestValidateStacItem:
    """Tests for validate_stac_item function."""

    def test_validate_without_validator_strict(self, sample_stac_item: dict[str, Any]) -> None:
        """Test validation without stac-validator installed (strict mode)."""
        # This should raise ImportError when stac-validator is not available
        try:
            validate_stac_item(sample_stac_item, strict=True)
        except ImportError as e:
            assert "stac-validator is not installed" in str(e)

    def test_validate_without_validator_non_strict(self, sample_stac_item: dict[str, Any]) -> None:
        """Test validation without stac-validator installed (non-strict mode)."""
        # This should return True when stac-validator is not available
        result = validate_stac_item(sample_stac_item, strict=False)
        assert result is True


class TestWriteNdjson:
    """Tests for write_ndjson function."""

    def test_write_ndjson(self) -> None:
        """Test writing items to NDJSON file."""
        items = [{"id": "item-1", "type": "Feature"}, {"id": "item-2", "type": "Feature"}]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False) as f:
            temp_path = f.name

        try:
            write_ndjson(temp_path, items)

            # Read back and verify
            with open(temp_path) as f:
                lines = f.readlines()

            assert len(lines) == 2

            # Each line should be valid JSON
            item1 = json.loads(lines[0])
            item2 = json.loads(lines[1])

            assert item1["id"] == "item-1"
            assert item2["id"] == "item-2"

        finally:
            os.unlink(temp_path)
