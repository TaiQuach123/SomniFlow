from src.data_pipeline.agents.enricher.models import Context


class BaseEnricher:
    def enrich(self, context: Context) -> Context:
        """Enrich context. To be implemented by subclasses."""
        raise NotImplementedError("enrich() must be implemented by subclasses.")
