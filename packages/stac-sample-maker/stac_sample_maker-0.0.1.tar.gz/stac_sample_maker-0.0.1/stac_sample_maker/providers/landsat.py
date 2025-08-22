"""STAC Landsat extension provider."""

from faker.providers import BaseProvider


class STACLandsatProvider(BaseProvider):
    """Provider for STAC Landsat extension data."""

    # Landsat spacecraft IDs
    LANDSAT_SPACECRAFT = ["LANDSAT_4", "LANDSAT_5", "LANDSAT_7", "LANDSAT_8", "LANDSAT_9"]

    # Landsat scene IDs pattern
    LANDSAT_SCENES = [
        "LC08_L1TP_{path:03d}{row:03d}_{date}_01_T1",
        "LC09_L1TP_{path:03d}{row:03d}_{date}_01_T1",
        "LE07_L1TP_{path:03d}{row:03d}_{date}_01_T1",
        "LT05_L1TP_{path:03d}{row:03d}_{date}_01_T1",
        "LT04_L1TP_{path:03d}{row:03d}_{date}_01_T1",
    ]

    # Collection categories
    COLLECTION_CATEGORIES = ["T1", "T2", "RT"]

    # Collection numbers
    COLLECTION_NUMBERS = ["01", "02"]

    def spacecraft_id(self) -> str:
        """Generate Landsat spacecraft ID."""
        # Weight towards newer satellites
        weights = [0.05, 0.1, 0.15, 0.35, 0.35]
        return self.generator.random.choices(self.LANDSAT_SPACECRAFT, weights=weights)[0]

    def scene_id(self) -> str:
        """Generate Landsat scene ID."""
        spacecraft = self.spacecraft_id()

        # Generate path/row (WRS-2)
        path = self.generator.random.randint(1, 233)
        row = self.generator.random.randint(1, 248)

        # Generate date
        year = self.generator.random.randint(2013, 2024)
        month = self.generator.random.randint(1, 12)
        day = self.generator.random.randint(1, 28)
        date = f"{year}{month:02d}{day:02d}"

        # Select appropriate scene ID pattern
        if spacecraft in ["LANDSAT_8"]:
            pattern = "LC08_L1TP_{path:03d}{row:03d}_{date}_01_T1"
        elif spacecraft in ["LANDSAT_9"]:
            pattern = "LC09_L1TP_{path:03d}{row:03d}_{date}_01_T1"
        elif spacecraft in ["LANDSAT_7"]:
            pattern = "LE07_L1TP_{path:03d}{row:03d}_{date}_01_T1"
        elif spacecraft in ["LANDSAT_5"]:
            pattern = "LT05_L1TP_{path:03d}{row:03d}_{date}_01_T1"
        else:  # LANDSAT_4
            pattern = "LT04_L1TP_{path:03d}{row:03d}_{date}_01_T1"

        return pattern.format(path=path, row=row, date=date)

    def wrs_path(self) -> int:
        """Generate WRS path number."""
        return self.generator.random.randint(1, 233)

    def wrs_row(self) -> int:
        """Generate WRS row number."""
        return self.generator.random.randint(1, 248)

    def collection_category(self) -> str:
        """Generate collection category."""
        # T1 is most common (highest quality)
        weights = [0.7, 0.2, 0.1]
        return self.generator.random.choices(self.COLLECTION_CATEGORIES, weights=weights)[0]

    def collection_number(self) -> str:
        """Generate collection number."""
        # Collection 02 is more recent
        weights = [0.3, 0.7]
        return self.generator.random.choices(self.COLLECTION_NUMBERS, weights=weights)[0]

    def cloud_cover_land(self) -> float:
        """Generate cloud cover over land (0-100)."""
        # Weight towards lower cloud cover
        if self.generator.random.random() < 0.6:
            return self.generator.random.uniform(0, 20)
        else:
            return self.generator.random.uniform(0, 100)

    def landsat_properties(self) -> dict[str, str | int | float]:
        """Generate complete Landsat extension properties."""
        properties: dict[str, str | int | float] = {
            "landsat:spacecraft_id": self.spacecraft_id(),
            "landsat:scene_id": self.scene_id(),
            "landsat:wrs_path": self.wrs_path(),
            "landsat:wrs_row": self.wrs_row(),
            "landsat:wrs_type": 2,  # Landsat uses WRS-2
            "landsat:correction": "L1TP",  # Standard correction level
            "landsat:collection_category": self.collection_category(),
            "landsat:collection_number": self.collection_number(),
        }

        # Add optional properties randomly
        if self.generator.random.random() < 0.8:
            properties["landsat:cloud_cover_land"] = self.cloud_cover_land()

        return properties
