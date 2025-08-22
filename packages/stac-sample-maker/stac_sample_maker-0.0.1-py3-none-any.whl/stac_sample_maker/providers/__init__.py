"""STAC extension providers package."""

from datetime import datetime, timedelta, timezone
from typing import Any

from faker.providers import BaseProvider


class STACTemporalProvider(BaseProvider):
    """Provider for STAC temporal data generation."""

    def datetime_between_dates(self, start: datetime, end: datetime) -> datetime:
        """Generate a random datetime between start and end."""
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        # ensure start <= end
        if end < start:
            start, end = end, start
        delta = end - start
        seconds = delta.total_seconds()
        if seconds <= 0:
            return start
        offset = self.generator.random.random() * seconds
        return start + timedelta(seconds=offset)

    def temporal_properties(
        self, start: datetime, end: datetime, use_interval: bool = False
    ) -> dict:
        """Generate temporal properties for a STAC item."""
        if use_interval:
            t0 = self.datetime_between_dates(start, end)
            t1 = self.datetime_between_dates(t0, end)
            return {
                "datetime": None,
                "start_datetime": t0.isoformat().replace("+00:00", "Z"),
                "end_datetime": t1.isoformat().replace("+00:00", "Z"),
            }
        else:
            t = self.datetime_between_dates(start, end)
            return {"datetime": t.isoformat().replace("+00:00", "Z")}


class STACGeometryProvider(BaseProvider):
    """Provider for STAC geometry and spatial data generation."""

    def point_in_bbox(self, bbox: tuple[float, float, float, float]) -> tuple[float, float]:
        """Generate a random point within the given bounding box."""
        minx, miny, maxx, maxy = bbox
        lon = self.generator.random.uniform(minx, maxx)
        lat = self.generator.random.uniform(miny, maxy)
        return lon, lat

    def geojson_point(self, lon: float, lat: float) -> dict:
        """Create a GeoJSON Point geometry."""
        return {"type": "Point", "coordinates": [lon, lat]}

    def bbox_for_point(self, lon: float, lat: float) -> list[float]:
        """Compute bounding box for a point."""
        return [lon, lat, lon, lat]


class STACCommonMetadataProvider(BaseProvider):
    """Provider for STAC common metadata fields."""

    # Common licenses
    LICENSES = [
        "Apache-2.0",
        "CC-BY-4.0",
        "CC-BY-SA-4.0",
        "CC0-1.0",
        "MIT",
        "ODbL-1.0",
        "PDDL-1.0",
        "proprietary",
        "other",
    ]

    # Common platforms/satellites
    PLATFORMS = [
        "landsat-8",
        "landsat-9",
        "landsat-7",
        "landsat-5",
        "sentinel-1a",
        "sentinel-1b",
        "sentinel-2a",
        "sentinel-2b",
        "terra",
        "aqua",
        "worldview-2",
        "worldview-3",
        "worldview-4",
        "quickbird-2",
        "geoeye-1",
        "pleiades-1a",
        "pleiades-1b",
        "spot-6",
        "spot-7",
        "kompsat-3",
        "kompsat-3a",
    ]

    # Common instruments
    INSTRUMENTS = [
        "oli",
        "tirs",
        "etm+",
        "tm",
        "msi",
        "c-sar",
        "modis",
        "aster",
        "wv110",
        "wv60",
        "bgis2000",
        "pan",
        "naomi",
        "aeiss",
    ]

    # Common constellations
    CONSTELLATIONS = [
        "landsat",
        "sentinel-1",
        "sentinel-2",
        "modis",
        "worldview",
        "pleiades",
        "spot",
        "kompsat",
    ]

    # Common missions
    MISSIONS = ["landsat", "copernicus", "eos", "digitalglobe", "airbus", "spot", "kari"]

    def keywords(self) -> list[str]:
        """Generate keywords for the item."""
        keyword_pools = [
            ["satellite", "earth observation", "remote sensing"],
            ["optical", "multispectral", "panchromatic", "thermal", "radar"],
            ["agriculture", "forestry", "urban", "coastal", "arctic"],
            ["landsat", "sentinel", "modis", "worldview", "pleiades"],
            ["ndvi", "land cover", "change detection", "monitoring"],
        ]

        keywords = []
        for pool in keyword_pools:
            if self.generator.random.random() < 0.6:  # 60% chance to pick from each pool
                keywords.extend(
                    self.generator.random.sample(pool, k=self.generator.random.randint(1, 2))
                )

        return keywords[:8]  # Limit to 8 keywords max

    def license_info(self) -> str:
        """Generate license information."""
        # Weight towards open licenses
        weights = [0.15, 0.2, 0.15, 0.2, 0.1, 0.05, 0.05, 0.05, 0.05]
        return self.generator.random.choices(self.LICENSES, weights=weights)[0]

    def platform(self) -> str:
        """Generate platform name."""
        return self.generator.random.choice(self.PLATFORMS)

    def instruments(self) -> list[str]:
        """Generate list of instruments."""
        num_instruments = self.generator.random.randint(1, 3)
        return self.generator.random.sample(
            self.INSTRUMENTS, k=min(num_instruments, len(self.INSTRUMENTS))
        )

    def constellation(self) -> str:
        """Generate constellation name."""
        return self.generator.random.choice(self.CONSTELLATIONS)

    def mission(self) -> str:
        """Generate mission name."""
        return self.generator.random.choice(self.MISSIONS)

    def gsd(self) -> float:
        """Generate Ground Sample Distance."""
        # Common GSD values
        gsd_options = [
            0.3,
            0.5,
            0.6,
            1.0,
            1.5,
            2.0,
            3.0,
            4.0,
            10.0,
            15.0,
            20.0,
            30.0,
            60.0,
            250.0,
            500.0,
            1000.0,
        ]
        weights = [
            0.05,
            0.05,
            0.05,
            0.1,
            0.1,
            0.1,
            0.1,
            0.1,
            0.15,
            0.05,
            0.05,
            0.1,
            0.05,
            0.02,
            0.02,
            0.01,
        ]
        return self.generator.random.choices(gsd_options, weights=weights)[0]

    def provider_list(self) -> list[dict[str, str | list[str]]]:
        """Generate providers array."""
        provider_names = [
            "NASA",
            "ESA",
            "USGS",
            "Planet Labs",
            "Maxar Technologies",
            "Airbus Defence and Space",
            "DigitalGlobe",
            "BlackSky",
            "Sentinel Hub",
            "Google Earth Engine",
            "Amazon Web Services",
        ]

        provider_roles = [
            ["producer"],
            ["processor"],
            ["licensor"],
            ["host"],
            ["producer", "licensor"],
            ["processor", "host"],
        ]

        num_providers = self.generator.random.randint(1, 3)
        providers = []

        for _ in range(num_providers):
            name = self.generator.random.choice(provider_names)
            roles = self.generator.random.choice(provider_roles)

            provider = {"name": name, "roles": roles}

            # Add optional fields randomly
            if self.generator.random.random() < 0.7:
                provider["url"] = (
                    f"https://www.{name.lower().replace(' ', '').replace('.', '')}.com"
                )

            if self.generator.random.random() < 0.4:
                provider["description"] = self.generator.sentence(nb_words=10)

            providers.append(provider)

        return providers

    def common_metadata_properties(self) -> dict[str, Any]:
        """Generate all common metadata properties."""
        properties: dict[str, Any] = {}

        # Add optional common metadata fields randomly
        if self.generator.random.random() < 0.8:
            properties["keywords"] = self.keywords()

        if self.generator.random.random() < 0.9:
            properties["license"] = self.license_info()

        if self.generator.random.random() < 0.7:
            properties["providers"] = self.provider_list()

        # Instrument metadata (70% chance)
        if self.generator.random.random() < 0.7:
            properties["platform"] = self.platform()
            properties["instruments"] = self.instruments()

            if self.generator.random.random() < 0.6:
                properties["constellation"] = self.constellation()

            if self.generator.random.random() < 0.5:
                properties["mission"] = self.mission()

            if self.generator.random.random() < 0.8:
                properties["gsd"] = self.gsd()

        # Add updated timestamp sometimes
        if self.generator.random.random() < 0.3:
            # Updated timestamp should be after created
            now = datetime.now(timezone.utc)
            updated_time = now - timedelta(days=self.generator.random.randint(0, 30))
            properties["updated"] = updated_time.isoformat().replace("+00:00", "Z")

        return properties


class STACItemProvider(BaseProvider):
    """Provider for complete STAC item generation."""

    def stac_item(
        self,
        idx: int,
        dt_range: tuple[datetime | None, datetime | None],
        interval: bool,
        bbox: tuple[float, float, float, float] | None,
        extensions: list[str] | None = None,
    ) -> dict:
        """Generate a complete STAC item."""
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        start, end = dt_range

        if start is None:
            start = now - timedelta(days=3650)
        if end is None:
            end = now

        # Get temporal properties using the temporal provider
        temporal_props = self.generator.temporal_properties(start, end, interval)

        # geometry
        if bbox is None:
            bbox = (-180.0, -90.0, 180.0, 90.0)

        lon, lat = self.generator.point_in_bbox(bbox)
        geometry = self.generator.geojson_point(lon, lat)
        bbox_list = self.generator.bbox_for_point(lon, lat)

        # ids & common properties
        item_id = f"item-{idx:06d}"

        # Start with temporal and basic properties
        all_properties = {
            **temporal_props,
            **self.generator.common_metadata_properties(),
            "title": self.generator.sentence(nb_words=6),
            "description": self.generator.paragraph(nb_sentences=3),
            "created": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

        # Add extension properties based on what's available
        extension_schemas = []
        assets = {
            "thumbnail": {
                "href": self.generator.image_url(),
                "roles": ["thumbnail"],
                "type": "image/jpeg",
            }
        }

        # Check for EO extension
        if hasattr(self.generator, "eo_properties"):
            all_properties.update(self.generator.eo_properties())
            extension_schemas.append("https://stac-extensions.github.io/eo/v1.1.0/schema.json")
            assets["thumbnail"]["eo:bands"] = self.generator.eo_asset_bands("thumbnail")
            assets["data"] = {
                "href": f"s3://satellite-data/{item_id}/{item_id}.tif",
                "roles": ["data"],
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                "eo:bands": self.generator.eo_asset_bands("data"),
            }

        # Check for File extension
        if hasattr(self.generator, "file_properties"):
            file_props = self.generator.file_properties()
            for asset_key in assets:
                assets[asset_key].update(file_props)
            extension_schemas.append("https://stac-extensions.github.io/file/v2.1.0/schema.json")

        # Check for Projection extension
        if hasattr(self.generator, "proj_properties"):
            all_properties.update(self.generator.proj_properties())
            extension_schemas.append(
                "https://stac-extensions.github.io/projection/v1.1.0/schema.json"
            )

        # Check for View extension
        if hasattr(self.generator, "view_properties"):
            all_properties.update(self.generator.view_properties())
            extension_schemas.append("https://stac-extensions.github.io/view/v1.0.0/schema.json")

        # Check for SAR extension
        if hasattr(self.generator, "sar_properties"):
            all_properties.update(self.generator.sar_properties())
            extension_schemas.append("https://stac-extensions.github.io/sar/v1.0.0/schema.json")

        # Check for Scientific Citation extension
        if hasattr(self.generator, "sci_properties"):
            all_properties.update(self.generator.sci_properties())
            extension_schemas.append(
                "https://stac-extensions.github.io/scientific/v1.0.0/schema.json"
            )

        # Check for Landsat extension
        if hasattr(self.generator, "landsat_properties"):
            all_properties.update(self.generator.landsat_properties())
            extension_schemas.append("https://stac-extensions.github.io/landsat/v2.0.0/schema.json")

        item = {
            "type": "Feature",
            "stac_version": "1.1.0",
            "id": item_id,
            "bbox": bbox_list,
            "geometry": geometry,
            "properties": all_properties,
            "links": [],
            "assets": assets,
            "stac_extensions": extension_schemas,
        }

        return item
