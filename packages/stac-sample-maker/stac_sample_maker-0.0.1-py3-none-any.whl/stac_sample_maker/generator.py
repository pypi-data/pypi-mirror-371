"""STAC item generator library."""

import json
from datetime import datetime
from typing import Any

from faker import Faker

# Import all extension providers
from .providers import (
    STACCommonMetadataProvider,
    STACGeometryProvider,
    STACItemProvider,
    STACTemporalProvider,
)
from .providers.eo import STACEOProvider
from .providers.file import STACFileProvider
from .providers.landsat import STACLandsatProvider
from .providers.proj import STACProjectionProvider
from .providers.sar import STACSarProvider
from .providers.sci import STACScientificProvider
from .providers.view import STACViewProvider

STAC_VERSION = "1.1.0"

# Try to import stac-validator for optional validation
try:
    from stac_validator import stac_validator

    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False


def iso_to_dt(s: str | None) -> datetime | None:
    """Convert ISO 8601 string to datetime object."""
    if not s:
        return None
    # Accept 'Z' suffix or offset
    try:
        if s.endswith("Z"):
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        return datetime.fromisoformat(s)
    except Exception as e:
        raise ValueError(f"Invalid ISO datetime: {s}") from e


def validate_stac_item(item: dict[str, Any], strict: bool = True) -> bool:
    """Validate a STAC item against the JSON schema.

    Args:
        item: The STAC item to validate
        strict: If True, raise exceptions on validation errors. If False, return boolean.

    Returns:
        True if valid, False if invalid (when strict=False)

    Raises:
        ValueError: If validation fails and strict=True
        ImportError: If stac-validator is not installed
    """
    if not VALIDATION_AVAILABLE:
        if strict:
            raise ImportError(
                "stac-validator is not installed. Install with: "
                "pip install stac-sample-maker[validation]"
            )
        return True  # Skip validation if not available

    try:
        # Use stac_validator to validate the item
        validator = stac_validator.StacValidate()
        is_valid = validator.validate_dict(item)

        if not is_valid and strict:
            error_msg = "STAC item validation failed:\n"
            for error in validator.message:
                error_msg += f"  - {error.get('error_message', 'Unknown error')}\n"
            raise ValueError(error_msg.strip())

        return is_valid

    except Exception as e:
        if strict:
            raise ValueError(f"STAC validation error: {e}") from e
        return False


def analyze_template_item(template_item: dict[str, Any]) -> dict[str, Any]:
    """Analyze a template STAC item to extract structure information."""
    analysis = {
        "extensions": template_item.get("stac_extensions", []),
        "property_fields": [],
        "asset_keys": list(template_item.get("assets", {}).keys()),
        "has_bbox": "bbox" in template_item,
        "has_geometry": "geometry" in template_item,
        "temporal_type": None,  # "instant", "interval", or None
    }

    properties = template_item.get("properties", {})

    # Analyze temporal structure
    if "datetime" in properties and properties["datetime"] is not None:
        analysis["temporal_type"] = "instant"
    elif "start_datetime" in properties and "end_datetime" in properties:
        analysis["temporal_type"] = "interval"

    # Collect all property field names (excluding temporal fields we handle specially)
    temporal_fields = {"datetime", "start_datetime", "end_datetime", "created", "updated"}
    for key in properties.keys():
        if key not in temporal_fields:
            analysis["property_fields"].append(key)

    return analysis


def generate_stac_items_from_template(
    template_path: str,
    num_items: int,
    start_date: str | None = None,
    end_date: str | None = None,
    bbox: tuple[float, float, float, float] | None = None,
    seed: int | None = None,
    validate: bool = False,
) -> list[dict[str, Any]]:
    """Generate synthetic STAC items based on a template item structure."""

    # Load and analyze template
    with open(template_path) as f:
        template_item = json.load(f)

    analysis = analyze_template_item(template_item)

    # Setup Faker with seed
    fake = Faker()
    if seed is not None:
        fake.seed_instance(seed)

    # Add all providers
    fake.add_provider(STACTemporalProvider)
    fake.add_provider(STACGeometryProvider)
    fake.add_provider(STACCommonMetadataProvider)
    fake.add_provider(STACItemProvider)
    fake.add_provider(STACEOProvider)
    fake.add_provider(STACFileProvider)
    fake.add_provider(STACProjectionProvider)
    fake.add_provider(STACViewProvider)
    fake.add_provider(STACSarProvider)
    fake.add_provider(STACScientificProvider)
    fake.add_provider(STACLandsatProvider)

    # Parse date range
    start = iso_to_dt(start_date)
    end = iso_to_dt(end_date)

    # Generate items with same structure
    items: list[dict[str, Any]] = []
    for i in range(num_items):
        use_interval = analysis["temporal_type"] == "interval"

        # Generate base item
        item = fake.stac_item(i + 1, (start, end), use_interval, bbox, None)

        # Override with template structure
        item["stac_extensions"] = analysis["extensions"]

        # Keep only properties that were in the template
        template_props = template_item.get("properties", {})
        new_props = {}

        # Copy temporal fields based on template structure
        if analysis["temporal_type"] == "instant" and "datetime" in item["properties"]:
            new_props["datetime"] = item["properties"]["datetime"]
        elif analysis["temporal_type"] == "interval":
            new_props["datetime"] = None  # Set to None for intervals
            if "start_datetime" in item["properties"]:
                new_props["start_datetime"] = item["properties"]["start_datetime"]
            if "end_datetime" in item["properties"]:
                new_props["end_datetime"] = item["properties"]["end_datetime"]

        # Add created/updated if they were in template
        if "created" in template_props:
            new_props["created"] = item["properties"].get(
                "created", datetime.now().isoformat() + "Z"
            )
        if "updated" in template_props:
            new_props["updated"] = item["properties"].get("updated")

        # Copy other properties that match template fields
        for field in analysis["property_fields"]:
            if field in item["properties"]:
                new_props[field] = item["properties"][field]
            else:
                # If the field exists in template but not generated, try to create appropriate synthetic data
                template_value = template_props.get(field)
                if isinstance(template_value, str):
                    new_props[field] = fake.sentence()
                elif isinstance(template_value, int | float):
                    new_props[field] = (
                        fake.random.uniform(0, 100)
                        if isinstance(template_value, float)
                        else fake.random.randint(0, 100)
                    )
                elif isinstance(template_value, list):
                    new_props[field] = [fake.word() for _ in range(len(template_value))]
                elif isinstance(template_value, bool):
                    new_props[field] = fake.boolean()
                else:
                    new_props[field] = template_value  # Keep original if we can't synthesize

        item["properties"] = new_props

        # Match asset structure from template
        if analysis["asset_keys"]:
            template_assets = template_item.get("assets", {})
            new_assets = {}

            for asset_key in analysis["asset_keys"]:
                template_asset = template_assets[asset_key]
                new_asset = {
                    "href": f"https://example.com/data/{item['id']}/{asset_key}.tif",
                    "type": template_asset.get("type", "image/tiff"),
                    "roles": template_asset.get("roles", ["data"]),
                }

                # Copy other asset properties that we can generate
                if "eo:bands" in template_asset and hasattr(fake, "eo_asset_bands"):
                    new_asset["eo:bands"] = fake.eo_asset_bands(asset_key)
                if any(k.startswith("file:") for k in template_asset.keys()) and hasattr(
                    fake, "file_properties"
                ):
                    file_props = fake.file_properties()
                    new_asset.update(file_props)

                new_assets[asset_key] = new_asset

            item["assets"] = new_assets

        # Validate item if requested
        if validate:
            validate_stac_item(item, strict=True)

        items.append(item)

    return items


def generate_stac_items(
    num_items: int,
    start_date: str | None = None,
    end_date: str | None = None,
    interval_percent: float = 0.2,
    bbox: tuple[float, float, float, float] | None = None,
    seed: int | None = None,
    extensions: list[str] | None = None,
    validate: bool = False,
) -> list[dict]:
    """Generate synthetic STAC items with configurable extensions."""

    # Validate interval_percent
    if interval_percent < 0 or interval_percent > 1:
        raise ValueError("interval_percent must be between 0 and 1")

    # Validate bbox
    if bbox is not None and (bbox[0] > bbox[2] or bbox[1] > bbox[3]):
        raise ValueError("bbox must be [minx miny maxx maxy] with min<=max")

    # Setup Faker with seed
    fake = Faker()
    if seed is not None:
        fake.seed_instance(seed)

    # Add all providers
    fake.add_provider(STACTemporalProvider)
    fake.add_provider(STACGeometryProvider)
    fake.add_provider(STACCommonMetadataProvider)
    fake.add_provider(STACItemProvider)
    fake.add_provider(STACEOProvider)
    fake.add_provider(STACFileProvider)
    fake.add_provider(STACProjectionProvider)
    fake.add_provider(STACViewProvider)
    fake.add_provider(STACSarProvider)
    fake.add_provider(STACScientificProvider)
    fake.add_provider(STACLandsatProvider)

    # Parse date range
    start = iso_to_dt(start_date)
    end = iso_to_dt(end_date)

    # Generate items
    items: list[dict] = []
    for i in range(num_items):
        use_interval = fake.random.random() < interval_percent
        item = fake.stac_item(i + 1, (start, end), use_interval, bbox, extensions)

        # Validate item if requested
        if validate:
            validate_stac_item(item, strict=True)

        items.append(item)

    return items


def write_ndjson(path: str, items: list[dict]) -> None:
    """Write list of STAC items to NDJSON file."""
    with open(path, "w") as f:
        for item in items:
            f.write(json.dumps(item, separators=(",", ":")) + "\n")
