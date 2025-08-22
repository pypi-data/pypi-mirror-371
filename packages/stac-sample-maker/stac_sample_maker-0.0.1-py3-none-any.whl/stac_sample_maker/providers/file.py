"""STAC File Info extension provider."""

from faker.providers import BaseProvider


class STACFileProvider(BaseProvider):
    """Provider for STAC File Info extension data."""

    def file_size(self) -> int:
        """Generate file size in bytes."""
        # Typical sizes for satellite imagery files
        size_ranges = [
            (1024 * 1024, 50 * 1024 * 1024),  # 1MB - 50MB for thumbnails
            (50 * 1024 * 1024, 500 * 1024 * 1024),  # 50MB - 500MB for medium res
            (500 * 1024 * 1024, 2 * 1024 * 1024 * 1024),  # 500MB - 2GB for high res
        ]

        # Weight towards medium sizes
        weights = [0.2, 0.6, 0.2]
        selected_range = self.generator.random.choices(size_ranges, weights=weights)[0]
        return self.generator.random.randint(selected_range[0], selected_range[1])

    def checksum(self, algorithm: str = "md5") -> str:
        """Generate a checksum."""
        if algorithm == "md5":
            # MD5 is 32 hex characters
            return self.generator.hexify("^" * 32).lower()
        elif algorithm == "sha1":
            # SHA1 is 40 hex characters
            return self.generator.hexify("^" * 40).lower()
        elif algorithm == "sha256":
            # SHA256 is 64 hex characters
            return self.generator.hexify("^" * 64).lower()
        else:
            # Default to MD5
            return self.generator.hexify("^" * 32).lower()

    def file_header_size(self) -> int:
        """Generate file header size in bytes."""
        # Typical header sizes for GeoTIFF files
        return self.generator.random.randint(1024, 8192)

    def file_properties(self) -> dict[str, int | str]:
        """Generate complete File extension properties for an asset."""
        properties: dict[str, int | str] = {
            "file:size": self.file_size(),
        }

        # Add optional properties randomly
        if self.generator.random.random() < 0.8:
            # Most files have checksums - just use the hash value
            algorithm = self.generator.random.choice(["md5", "sha1", "sha256"])
            properties["file:checksum"] = self.checksum(algorithm)

        if self.generator.random.random() < 0.3:
            # Some files report header size
            properties["file:header_size"] = self.file_header_size()

        return properties
