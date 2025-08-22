"""Tests for provider modules."""

from faker import Faker

from stac_sample_maker.providers import (
    STACCommonMetadataProvider,
    STACGeometryProvider,
    STACTemporalProvider,
)
from stac_sample_maker.providers.eo import STACEOProvider
from stac_sample_maker.providers.file import STACFileProvider
from stac_sample_maker.providers.proj import STACProjectionProvider


class TestSTACTemporalProvider:
    """Tests for temporal provider."""

    def test_datetime_between_dates(self) -> None:
        """Test generating datetime between dates."""
        fake = Faker()
        fake.add_provider(STACTemporalProvider)

        from datetime import datetime, timezone

        start = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end = datetime(2023, 12, 31, tzinfo=timezone.utc)

        dt = fake.datetime_between_dates(start, end)
        assert start <= dt <= end

    def test_temporal_properties_instant(self) -> None:
        """Test generating instant temporal properties."""
        fake = Faker()
        fake.add_provider(STACTemporalProvider)

        from datetime import datetime

        start = datetime(2023, 1, 1)
        end = datetime(2023, 12, 31)

        props = fake.temporal_properties(start, end, use_interval=False)

        assert "datetime" in props
        assert "start_datetime" not in props
        assert "end_datetime" not in props
        assert props["datetime"].endswith("Z")

    def test_temporal_properties_interval(self) -> None:
        """Test generating interval temporal properties."""
        fake = Faker()
        fake.add_provider(STACTemporalProvider)

        from datetime import datetime

        start = datetime(2023, 1, 1)
        end = datetime(2023, 12, 31)

        props = fake.temporal_properties(start, end, use_interval=True)

        assert props["datetime"] is None
        assert "start_datetime" in props
        assert "end_datetime" in props
        assert props["start_datetime"].endswith("Z")
        assert props["end_datetime"].endswith("Z")


class TestSTACGeometryProvider:
    """Tests for geometry provider."""

    def test_point_in_bbox(self) -> None:
        """Test generating point within bbox."""
        fake = Faker()
        fake.add_provider(STACGeometryProvider)

        bbox = (-122.5, 37.7, -122.3, 37.8)
        lon, lat = fake.point_in_bbox(bbox)

        assert bbox[0] <= lon <= bbox[2]
        assert bbox[1] <= lat <= bbox[3]

    def test_geojson_point(self) -> None:
        """Test creating GeoJSON point."""
        fake = Faker()
        fake.add_provider(STACGeometryProvider)

        geom = fake.geojson_point(-122.4, 37.75)

        assert geom["type"] == "Point"
        assert geom["coordinates"] == [-122.4, 37.75]

    def test_bbox_for_point(self) -> None:
        """Test creating bbox for point."""
        fake = Faker()
        fake.add_provider(STACGeometryProvider)

        bbox = fake.bbox_for_point(-122.4, 37.75)

        assert bbox == [-122.4, 37.75, -122.4, 37.75]


class TestSTACCommonMetadataProvider:
    """Tests for common metadata provider."""

    def test_keywords(self) -> None:
        """Test generating keywords."""
        fake = Faker()
        fake.add_provider(STACCommonMetadataProvider)

        keywords = fake.keywords()

        assert isinstance(keywords, list)
        assert len(keywords) <= 8
        assert all(isinstance(kw, str) for kw in keywords)

    def test_license_info(self) -> None:
        """Test generating license."""
        fake = Faker()
        fake.add_provider(STACCommonMetadataProvider)

        license_val = fake.license_info()

        assert license_val in STACCommonMetadataProvider.LICENSES

    def test_platform(self) -> None:
        """Test generating platform."""
        fake = Faker()
        fake.add_provider(STACCommonMetadataProvider)

        platform = fake.platform()

        assert platform in STACCommonMetadataProvider.PLATFORMS

    def test_gsd(self) -> None:
        """Test generating GSD."""
        fake = Faker()
        fake.add_provider(STACCommonMetadataProvider)

        gsd = fake.gsd()

        assert isinstance(gsd, float)
        assert gsd > 0


class TestSTACEOProvider:
    """Tests for EO provider."""

    def test_cloud_cover(self) -> None:
        """Test generating cloud cover."""
        fake = Faker()
        fake.add_provider(STACEOProvider)

        cloud_cover = fake.cloud_cover()

        assert 0 <= cloud_cover <= 100

    def test_eo_bands(self) -> None:
        """Test generating EO bands."""
        fake = Faker()
        fake.add_provider(STACEOProvider)

        bands = fake.eo_bands(num_bands=3)

        assert len(bands) == 3
        assert all("name" in band for band in bands)
        assert all("center_wavelength" in band for band in bands)

    def test_eo_properties(self) -> None:
        """Test generating EO properties."""
        fake = Faker()
        fake.add_provider(STACEOProvider)

        props = fake.eo_properties()

        assert "eo:cloud_cover" in props
        assert 0 <= props["eo:cloud_cover"] <= 100


class TestSTACFileProvider:
    """Tests for file provider."""

    def test_file_size(self) -> None:
        """Test generating file size."""
        fake = Faker()
        fake.add_provider(STACFileProvider)

        size = fake.file_size()

        assert isinstance(size, int)
        assert size > 0

    def test_checksum(self) -> None:
        """Test generating checksums."""
        fake = Faker()
        fake.add_provider(STACFileProvider)

        md5_checksum = fake.checksum("md5")
        assert len(md5_checksum) == 32
        assert all(c in "0123456789abcdef" for c in md5_checksum)

        sha1_checksum = fake.checksum("sha1")
        assert len(sha1_checksum) == 40

        sha256_checksum = fake.checksum("sha256")
        assert len(sha256_checksum) == 64

    def test_file_properties(self) -> None:
        """Test generating file properties."""
        fake = Faker()
        fake.add_provider(STACFileProvider)

        props = fake.file_properties()

        assert "file:size" in props
        assert isinstance(props["file:size"], int)


class TestSTACProjectionProvider:
    """Tests for projection provider."""

    def test_epsg_code(self) -> None:
        """Test generating EPSG code."""
        fake = Faker()
        fake.add_provider(STACProjectionProvider)

        epsg = fake.epsg_code()

        assert epsg in STACProjectionProvider.COMMON_EPSG

    def test_proj_transform(self) -> None:
        """Test generating projection transform."""
        fake = Faker()
        fake.add_provider(STACProjectionProvider)

        transform = fake.proj_transform(32611)

        assert len(transform) == 6
        assert all(isinstance(val, float) for val in transform)

    def test_proj_shape(self) -> None:
        """Test generating projection shape."""
        fake = Faker()
        fake.add_provider(STACProjectionProvider)

        shape = fake.proj_shape()

        assert len(shape) == 2
        assert all(isinstance(dim, int) for dim in shape)
        assert all(dim > 0 for dim in shape)
