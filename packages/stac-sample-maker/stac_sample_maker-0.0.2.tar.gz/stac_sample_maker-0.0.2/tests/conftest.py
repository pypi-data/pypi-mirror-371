"""Test configuration and fixtures."""

import json
import tempfile
from typing import Any

import pytest


@pytest.fixture
def sample_stac_item() -> dict[str, Any]:
    """Sample valid STAC item for testing."""
    return {
        "type": "Feature",
        "stac_version": "1.1.0",
        "id": "test-item-001",
        "bbox": [-122.5, 37.7, -122.3, 37.8],
        "geometry": {"type": "Point", "coordinates": [-122.4, 37.75]},
        "properties": {
            "datetime": "2023-06-15T10:30:00Z",
            "license": "CC-BY-4.0",
            "title": "Test STAC Item",
            "description": "A sample STAC item for testing",
        },
        "links": [],
        "assets": {
            "thumbnail": {
                "href": "https://example.com/thumbnail.jpg",
                "type": "image/jpeg",
                "roles": ["thumbnail"],
            }
        },
        "stac_extensions": [],
    }


@pytest.fixture
def interval_stac_item() -> dict[str, Any]:
    """Sample STAC item with interval datetime for testing."""
    return {
        "type": "Feature",
        "stac_version": "1.1.0",
        "id": "test-interval-item",
        "bbox": [-122.5, 37.7, -122.3, 37.8],
        "geometry": {"type": "Point", "coordinates": [-122.4, 37.75]},
        "properties": {
            "datetime": None,
            "start_datetime": "2023-06-15T10:00:00Z",
            "end_datetime": "2023-06-15T11:00:00Z",
            "license": "Apache-2.0",
            "title": "Test Interval Item",
            "description": "A sample STAC item with time interval",
        },
        "links": [],
        "assets": {
            "data": {
                "href": "https://example.com/data.tif",
                "type": "image/tiff",
                "roles": ["data"],
            }
        },
        "stac_extensions": [],
    }


@pytest.fixture
def temp_template_file(sample_stac_item: dict[str, Any]) -> str:
    """Create a temporary template file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_stac_item, f)
        return f.name


@pytest.fixture
def temp_interval_template_file(interval_stac_item: dict[str, Any]) -> str:
    """Create a temporary interval template file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(interval_stac_item, f)
        return f.name
