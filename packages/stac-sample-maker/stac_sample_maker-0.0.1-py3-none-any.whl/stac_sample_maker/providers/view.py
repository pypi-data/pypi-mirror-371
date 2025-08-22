"""STAC View Geometry extension provider."""

from faker.providers import BaseProvider


class STACViewProvider(BaseProvider):
    """Provider for STAC View Geometry extension data."""

    def off_nadir(self) -> float:
        """Generate off-nadir angle in degrees (0-45)."""
        # Most satellite images are near-nadir
        if self.generator.random.random() < 0.7:
            return self.generator.random.uniform(0, 15)
        else:
            return self.generator.random.uniform(15, 45)

    def incidence_angle(self) -> float:
        """Generate incidence angle in degrees (0-60)."""
        return self.generator.random.uniform(0, 60)

    def azimuth(self) -> float:
        """Generate azimuth angle in degrees (0-360)."""
        return self.generator.random.uniform(0, 360)

    def sun_azimuth(self) -> float:
        """Generate sun azimuth angle in degrees (0-360)."""
        return self.generator.random.uniform(0, 360)

    def sun_elevation(self) -> float:
        """Generate sun elevation angle in degrees (0-90)."""
        # Weight towards reasonable sun angles
        return self.generator.random.uniform(10, 80)

    def view_properties(self) -> dict[str, float | int]:
        """Generate complete View Geometry extension properties."""
        properties: dict[str, float | int] = {}

        # Add properties randomly (not all are always present)
        if self.generator.random.random() < 0.8:
            properties["view:off_nadir"] = self.off_nadir()

        if self.generator.random.random() < 0.6:
            properties["view:incidence_angle"] = self.incidence_angle()

        if self.generator.random.random() < 0.7:
            properties["view:azimuth"] = self.azimuth()

        if self.generator.random.random() < 0.9:
            properties["view:sun_azimuth"] = self.sun_azimuth()
            properties["view:sun_elevation"] = self.sun_elevation()

        return properties
