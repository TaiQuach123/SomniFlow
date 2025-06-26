class BaseConverter:
    def convert_and_save(self, input_path: str, output_path: str) -> None:
        """Convert input file to output file and save to output path. To be implemented by subclasses."""
        raise NotImplementedError(
            "convert_and_save() must be implemented by subclasses."
        )
