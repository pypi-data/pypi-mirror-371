"""STAC Electro-Optical (EO) extension provider."""

from faker.providers import BaseProvider


class STACEOProvider(BaseProvider):
    """Provider for STAC EO data generation."""

    # Common EO bands for satellite imagery
    EO_BANDS = [
        {
            "name": "B01",
            "common_name": "coastal",
            "description": "Coastal aerosol",
            "center_wavelength": 0.443,
            "full_width_half_max": 0.027,
        },
        {
            "name": "B02",
            "common_name": "blue",
            "description": "Blue",
            "center_wavelength": 0.490,
            "full_width_half_max": 0.098,
        },
        {
            "name": "B03",
            "common_name": "green",
            "description": "Green",
            "center_wavelength": 0.560,
            "full_width_half_max": 0.045,
        },
        {
            "name": "B04",
            "common_name": "red",
            "description": "Red",
            "center_wavelength": 0.665,
            "full_width_half_max": 0.038,
        },
        {
            "name": "B05",
            "common_name": "rededge",
            "description": "Red edge 1",
            "center_wavelength": 0.705,
            "full_width_half_max": 0.019,
        },
        {
            "name": "B06",
            "common_name": "rededge",
            "description": "Red edge 2",
            "center_wavelength": 0.740,
            "full_width_half_max": 0.018,
        },
        {
            "name": "B07",
            "common_name": "rededge",
            "description": "Red edge 3",
            "center_wavelength": 0.783,
            "full_width_half_max": 0.028,
        },
        {
            "name": "B08",
            "common_name": "nir",
            "description": "Near infrared",
            "center_wavelength": 0.842,
            "full_width_half_max": 0.145,
        },
        {
            "name": "B8A",
            "common_name": "nir08",
            "description": "Near infrared narrow",
            "center_wavelength": 0.865,
            "full_width_half_max": 0.033,
        },
        {
            "name": "B09",
            "common_name": "nir09",
            "description": "Water vapour",
            "center_wavelength": 0.945,
            "full_width_half_max": 0.026,
        },
        {
            "name": "B10",
            "common_name": "cirrus",
            "description": "Cirrus",
            "center_wavelength": 1.375,
            "full_width_half_max": 0.075,
        },
        {
            "name": "B11",
            "common_name": "swir16",
            "description": "Short wave infrared 1",
            "center_wavelength": 1.610,
            "full_width_half_max": 0.143,
        },
        {
            "name": "B12",
            "common_name": "swir22",
            "description": "Short wave infrared 2",
            "center_wavelength": 2.190,
            "full_width_half_max": 0.242,
        },
    ]

    def cloud_cover(self) -> float:
        """Generate cloud cover percentage (0-100)."""
        # Weight towards lower cloud cover for better imagery
        if self.generator.random.random() < 0.6:
            return self.generator.random.uniform(0, 20)
        else:
            return self.generator.random.uniform(0, 100)

    def snow_cover(self) -> float:
        """Generate snow cover percentage (0-100)."""
        # Most images have little to no snow
        if self.generator.random.random() < 0.8:
            return 0.0
        else:
            return self.generator.random.uniform(0, 50)

    def sun_azimuth(self) -> float:
        """Generate sun azimuth angle in degrees (0-360)."""
        return self.generator.random.uniform(0, 360)

    def sun_elevation(self) -> float:
        """Generate sun elevation angle in degrees (0-90)."""
        # Weight towards reasonable sun angles
        return self.generator.random.uniform(10, 80)

    def gsd(self) -> float:
        """Generate Ground Sample Distance in meters."""
        # Common GSD values for satellite imagery
        gsd_options = [10.0, 20.0, 30.0, 60.0]
        weights = [0.4, 0.3, 0.2, 0.1]  # Favor higher resolution
        return self.generator.random.choices(gsd_options, weights=weights)[0]

    def eo_bands(self, num_bands: int | None = None) -> list[dict]:
        """Generate EO band information."""
        if num_bands is None:
            # Randomly select number of bands (3-13)
            num_bands = self.generator.random.randint(3, len(self.EO_BANDS))

        # Select random bands from the available ones
        selected_bands = self.generator.random.sample(
            self.EO_BANDS, min(num_bands, len(self.EO_BANDS))
        )

        # Add some variation to the wavelengths
        bands = []
        for band in selected_bands:
            band_copy = band.copy()
            # Add small random variation to center wavelength (±2%)
            variation = self.generator.random.uniform(-0.02, 0.02)
            band_copy["center_wavelength"] = band["center_wavelength"] * (1 + variation)
            bands.append(band_copy)

        return sorted(bands, key=lambda x: x["center_wavelength"])

    def eo_properties(self) -> dict:
        """Generate complete EO extension properties."""
        properties = {
            "eo:cloud_cover": self.cloud_cover(),
        }

        # Add optional properties randomly
        if self.generator.random.random() < 0.3:
            properties["eo:snow_cover"] = self.snow_cover()

        return properties

    def eo_asset_bands(self, asset_type: str = "data") -> list[dict]:
        """Generate band information for an asset."""
        if asset_type == "thumbnail":
            # Thumbnails typically use RGB bands
            return [
                {"name": "red", "common_name": "red"},
                {"name": "green", "common_name": "green"},
                {"name": "blue", "common_name": "blue"},
            ]
        else:
            # Data assets get full band information
            return self.eo_bands()
