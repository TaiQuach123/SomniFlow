from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    PictureDescriptionApiOptions,
    PictureDescriptionVlmOptions,
)
from src.data_pipeline.config import data_pipeline_config


def get_picture_description_options(
    model: str, prompt: str, use_api: bool = True
) -> PictureDescriptionApiOptions | PictureDescriptionVlmOptions:
    if use_api:
        return PictureDescriptionApiOptions(
            url="http://localhost:1234/v1/chat/completions",
            params=dict(model=model, max_completion_tokens=500, temperature=0),
            prompt=prompt,
            timeout=90,
        )
    else:
        return PictureDescriptionVlmOptions(
            repo_id=model,
            prompt=prompt,
            generation_config=dict(max_new_tokens=500, temperature=0),
        )


def get_pdf_pipeline_options(
    vision_model_name: str = data_pipeline_config.vision_model_name,
    prompt: str = data_pipeline_config.image_description_prompt,
) -> PdfPipelineOptions:
    return PdfPipelineOptions(
        do_picture_description=True,
        enable_remote_services=True,
        generate_picture_images=True,
        images_scale=2,
        picture_description_options=get_picture_description_options(
            model=vision_model_name,
            prompt=prompt,
        ),
    )
