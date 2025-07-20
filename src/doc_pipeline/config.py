from dataclasses import dataclass

IMAGE_DESCRIPTION_PROMPT = """You are given an image extracted from a scientific research article related to insomnia.

Your task is to describe the image in a clear, concise, and informative way, using no more than three sentences.

- Focus on what the image shows (e.g., charts, brain activity, sleep patterns, correlations, experimental setup).
- If possible, mention its relevance to insomnia (e.g., what variable is being measured, what population is studied).
- Avoid interpreting or speculating beyond the visible content.
- Use precise, technical language appropriate for scientific content, but keep the explanation readable and embedding-friendly.

Do not include references to figure numbers or captions. Only provide the description text."""


@dataclass
class DocumentPipelineConfig:
    vision_model_name: str = (
        "Mungert/Qwen2.5-VL-3B-Instruct-GGUF/Qwen2.5-VL-3B-Instruct-q4_k_s.gguf"
    )
    embedding_model_name: str = "jinaai/jina-embeddings-v4"
    max_tokens: int = 512
    page_break_placeholder: str = "<!-- PAGE BREAK -->"
    image_description_prompt: str = IMAGE_DESCRIPTION_PROMPT
    use_remote_services: bool = True


document_pipeline_config = DocumentPipelineConfig()
