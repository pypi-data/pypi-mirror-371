"""STAC SAR extension provider."""

from faker.providers import BaseProvider


class STACSarProvider(BaseProvider):
    """Provider for STAC SAR extension data."""

    # Common SAR instrument modes
    INSTRUMENT_MODES = [
        "IW",  # Interferometric Wide Swath
        "EW",  # Extra Wide Swath
        "SM",  # StripMap
        "WV",  # Wave
        "S1",  # Sentinel-1 specific
        "S2",  # Sentinel-1 specific
        "S3",  # Sentinel-1 specific
        "S4",  # Sentinel-1 specific
        "S5",  # Sentinel-1 specific
        "S6",  # Sentinel-1 specific
    ]

    # SAR frequency bands
    FREQUENCY_BANDS = ["P", "L", "S", "C", "X", "Ku", "K", "Ka"]

    # Polarizations
    POLARIZATIONS = ["HH", "VV", "HV", "VH"]

    # Product types
    PRODUCT_TYPES = [
        "GRD",  # Ground Range Detected
        "SLC",  # Single Look Complex
        "OCN",  # Ocean
        "RAW",  # Raw
    ]

    def instrument_mode(self) -> str:
        """Generate SAR instrument mode."""
        return self.generator.random.choice(self.INSTRUMENT_MODES)

    def frequency_band(self) -> str:
        """Generate SAR frequency band."""
        # C-band is most common for current satellites
        weights = [0.05, 0.1, 0.1, 0.6, 0.1, 0.02, 0.02, 0.01]
        return self.generator.random.choices(self.FREQUENCY_BANDS, weights=weights)[0]

    def center_frequency(self, band: str) -> float:
        """Generate center frequency in GHz based on band."""
        frequency_ranges = {
            "P": (0.3, 1.0),
            "L": (1.0, 2.0),
            "S": (2.0, 4.0),
            "C": (4.0, 8.0),
            "X": (8.0, 12.0),
            "Ku": (12.0, 18.0),
            "K": (18.0, 27.0),
            "Ka": (27.0, 40.0),
        }
        min_freq, max_freq = frequency_ranges.get(band, (4.0, 8.0))
        return self.generator.random.uniform(min_freq, max_freq)

    def polarizations(self) -> list[str]:
        """Generate list of polarizations."""
        # Common combinations
        combinations = [
            ["VV"],
            ["HH"],
            ["VV", "VH"],
            ["HH", "HV"],
            ["VV", "VH", "HH", "HV"],
        ]
        weights = [0.3, 0.3, 0.2, 0.15, 0.05]
        return self.generator.random.choices(combinations, weights=weights)[0]

    def product_type(self) -> str:
        """Generate SAR product type."""
        # GRD is most common
        weights = [0.7, 0.2, 0.05, 0.05]
        return self.generator.random.choices(self.PRODUCT_TYPES, weights=weights)[0]

    def resolution_range(self) -> float:
        """Generate range resolution in meters."""
        return self.generator.random.uniform(1.0, 40.0)

    def resolution_azimuth(self) -> float:
        """Generate azimuth resolution in meters."""
        return self.generator.random.uniform(1.0, 40.0)

    def pixel_spacing_range(self) -> float:
        """Generate range pixel spacing in meters."""
        return self.generator.random.uniform(1.0, 40.0)

    def pixel_spacing_azimuth(self) -> float:
        """Generate azimuth pixel spacing in meters."""
        return self.generator.random.uniform(1.0, 40.0)

    def looks_range(self) -> int:
        """Generate number of range looks."""
        return self.generator.random.randint(1, 10)

    def looks_azimuth(self) -> int:
        """Generate number of azimuth looks."""
        return self.generator.random.randint(1, 10)

    def looks_equivalent_number(self) -> float:
        """Generate equivalent number of looks."""
        return self.generator.random.uniform(1.0, 50.0)

    def observation_direction(self) -> str:
        """Generate observation direction."""
        return self.generator.random.choice(["left", "right"])

    def sar_properties(self) -> dict[str, str | float | int | list[str]]:
        """Generate complete SAR extension properties."""
        band = self.frequency_band()
        properties: dict[str, str | float | int | list[str]] = {
            "sar:instrument_mode": self.instrument_mode(),
            "sar:frequency_band": band,
            "sar:center_frequency": self.center_frequency(band),
            "sar:polarizations": self.polarizations(),
            "sar:product_type": self.product_type(),
        }

        # Add optional properties randomly
        if self.generator.random.random() < 0.8:
            properties["sar:resolution_range"] = self.resolution_range()
            properties["sar:resolution_azimuth"] = self.resolution_azimuth()

        if self.generator.random.random() < 0.7:
            properties["sar:pixel_spacing_range"] = self.pixel_spacing_range()
            properties["sar:pixel_spacing_azimuth"] = self.pixel_spacing_azimuth()

        if self.generator.random.random() < 0.6:
            properties["sar:looks_range"] = self.looks_range()
            properties["sar:looks_azimuth"] = self.looks_azimuth()

        if self.generator.random.random() < 0.5:
            properties["sar:looks_equivalent_number"] = self.looks_equivalent_number()

        if self.generator.random.random() < 0.9:
            properties["sar:observation_direction"] = self.observation_direction()

        return properties
