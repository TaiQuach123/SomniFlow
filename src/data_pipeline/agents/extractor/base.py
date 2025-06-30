class BaseExtractor:
    def extract(self, json_path: str) -> dict:
        """Extract metadata from a JSON file. To be implemented by subclasses."""
        raise NotImplementedError("extract() must be implemented by subclasses.")
