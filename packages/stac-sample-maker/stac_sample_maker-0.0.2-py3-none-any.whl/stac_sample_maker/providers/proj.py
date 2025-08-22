"""STAC Projection extension provider."""

from faker.providers import BaseProvider


class STACProjectionProvider(BaseProvider):
    """Provider for STAC Projection extension data."""

    # Common EPSG codes for satellite imagery
    COMMON_EPSG = [
        4326,  # WGS84
        3857,  # Web Mercator
        32601,
        32602,
        32603,
        32604,
        32605,
        32606,  # UTM Zone 1-6 North
        32610,
        32611,
        32612,
        32613,
        32614,
        32615,  # UTM Zone 10-15 North
        32620,
        32621,
        32622,
        32623,
        32624,
        32625,  # UTM Zone 20-25 North
        32630,
        32631,
        32632,
        32633,
        32634,
        32635,  # UTM Zone 30-35 North
        32640,
        32641,
        32642,
        32643,
        32644,
        32645,  # UTM Zone 40-45 North
        32650,
        32651,
        32652,
        32653,
        32654,
        32655,  # UTM Zone 50-55 North
        32660,  # UTM Zone 60 North
    ]

    def epsg_code(self) -> int:
        """Generate an EPSG code."""
        return self.generator.random.choice(self.COMMON_EPSG)

    def proj_transform(self, epsg: int) -> list[float]:
        """Generate a projection transform matrix."""
        # Generate a realistic transform for the given EPSG
        if epsg == 4326:
            # Geographic coordinates - no transform needed
            return [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        else:
            # UTM or other projected coordinate system
            # Generate realistic pixel size (10-60 meters)
            pixel_size = self.generator.random.uniform(10.0, 60.0)
            x_origin = self.generator.random.uniform(-20000000, 20000000)
            y_origin = self.generator.random.uniform(-20000000, 20000000)
            return [pixel_size, 0.0, x_origin, 0.0, -pixel_size, y_origin]

    def proj_shape(self) -> list[int]:
        """Generate raster shape [height, width]."""
        # Typical satellite image dimensions
        sizes = [
            [1024, 1024],  # Small
            [2048, 2048],  # Medium
            [4096, 4096],  # Large
            [8192, 8192],  # Very large
            [10980, 10980],  # Sentinel-2 tile size
        ]
        weights = [0.2, 0.3, 0.3, 0.15, 0.05]
        return self.generator.random.choices(sizes, weights=weights)[0]

    def proj_bbox(self, epsg: int) -> list[float]:
        """Generate projected bounding box."""
        if epsg == 4326:
            # Geographic coordinates
            minx = self.generator.random.uniform(-180, 180)
            maxx = minx + self.generator.random.uniform(0.1, 10)
            miny = self.generator.random.uniform(-85, 85)
            maxy = miny + self.generator.random.uniform(0.1, 10)
        else:
            # Projected coordinates (in meters typically)
            minx = self.generator.random.uniform(-20000000, 20000000)
            maxx = minx + self.generator.random.uniform(1000, 100000)
            miny = self.generator.random.uniform(-20000000, 20000000)
            maxy = miny + self.generator.random.uniform(1000, 100000)

        return [minx, miny, maxx, maxy]

    def proj_centroid(self, bbox: list[float]) -> dict[str, float]:
        """Generate geographic centroid (WGS84) regardless of projection."""
        # For proj:centroid, we need geographic coordinates even if bbox is projected
        # Generate a realistic geographic centroid
        lat = self.generator.random.uniform(-85, 85)
        lon = self.generator.random.uniform(-180, 180)
        return {"lat": lat, "lon": lon}

    def proj_properties(self) -> dict[str, int | str | list | dict]:
        """Generate complete Projection extension properties."""
        epsg = self.epsg_code()
        shape = self.proj_shape()
        transform = self.proj_transform(epsg)
        bbox = self.proj_bbox(epsg)
        centroid = self.proj_centroid(bbox)

        properties: dict[str, int | str | list | dict] = {
            "proj:epsg": epsg,
            "proj:shape": shape,
            "proj:transform": transform,
            "proj:bbox": bbox,
        }

        # Add optional properties randomly
        if self.generator.random.random() < 0.7:
            properties["proj:centroid"] = centroid

        if self.generator.random.random() < 0.5:
            # Add WKT2 CRS definition for some items
            properties["proj:wkt2"] = f"EPSG:{epsg}"  # Simplified WKT2

        return properties
