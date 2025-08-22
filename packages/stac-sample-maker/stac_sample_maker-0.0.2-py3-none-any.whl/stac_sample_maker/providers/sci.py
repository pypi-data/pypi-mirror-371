"""STAC Scientific Citation extension provider."""

from faker.providers import BaseProvider


class STACScientificProvider(BaseProvider):
    """Provider for STAC Scientific Citation extension data."""

    # Common journal names for remote sensing
    JOURNALS = [
        "Remote Sensing of Environment",
        "IEEE Transactions on Geoscience and Remote Sensing",
        "International Journal of Remote Sensing",
        "Remote Sensing",
        "ISPRS Journal of Photogrammetry and Remote Sensing",
        "IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing",
        "Photogrammetric Engineering & Remote Sensing",
        "Canadian Journal of Remote Sensing",
        "European Journal of Remote Sensing",
        "Journal of Applied Remote Sensing",
    ]

    def doi(self) -> str:
        """Generate a DOI."""
        # Format: 10.{registrant}/{suffix}
        registrant = self.generator.random.randint(1000, 9999)
        suffix = self.generator.random_element(
            [
                f"rs{self.generator.random.randint(100000, 999999)}",
                f"data.{self.generator.random.randint(1000, 9999)}.{self.generator.random.randint(100, 999)}",
                f"earth/{self.generator.random.randint(10000, 99999)}",
            ]
        )
        return f"10.{registrant}/{suffix}"

    def citation(self) -> str:
        """Generate a citation string."""
        # Generate author names
        num_authors = self.generator.random.randint(1, 5)
        authors = []
        for _ in range(num_authors):
            last_name = self.generator.last_name()
            first_initial = self.generator.random_letter().upper()
            authors.append(f"{last_name}, {first_initial}.")

        author_string = "; ".join(authors)

        # Generate publication details
        year = self.generator.random.randint(2010, 2024)
        journal = self.generator.random.choice(self.JOURNALS)
        volume = self.generator.random.randint(1, 200)
        pages = (
            f"{self.generator.random.randint(1, 500)}-{self.generator.random.randint(501, 1000)}"
        )

        return f"{author_string} ({year}). {self.generator.sentence(nb_words=8)}. {journal}, {volume}, {pages}."

    def publication_year(self) -> int:
        """Generate publication year."""
        # Weight towards recent years
        if self.generator.random.random() < 0.6:
            return self.generator.random.randint(2018, 2024)
        else:
            return self.generator.random.randint(2010, 2017)

    def sci_properties(self) -> dict[str, str | int | list]:
        """Generate complete Scientific Citation extension properties."""
        properties: dict[str, str | int | list] = {}

        # Add properties randomly (not all datasets have all properties)
        if self.generator.random.random() < 0.8:
            properties["sci:doi"] = self.doi()

        if self.generator.random.random() < 0.9:
            properties["sci:citation"] = self.citation()

        if self.generator.random.random() < 0.7:
            properties["sci:publications"] = [{"doi": self.doi(), "citation": self.citation()}]

        return properties
