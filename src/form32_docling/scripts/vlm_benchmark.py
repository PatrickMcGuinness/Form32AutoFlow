#!/usr/bin/env python3
import argparse
import logging
import sys
import time
from pathlib import Path

from docling.datamodel import vlm_model_specs
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    VlmPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def apply_kv_cache_fix():
    """Apply the KV cache fix for Transformers models as seen in form32_processor.py."""
    try:
        from docling.models.vlm_pipeline_models import hf_transformers_model
        from transformers import AutoModelForVision2Seq

        _original_process_images = hf_transformers_model.HuggingFaceTransformersVlmModel.process_images

        def _patched_process_images(self, *args, **kwargs):
            if (
                hasattr(self, 'generation_config')
                and self.generation_config is not None
                and hasattr(self.generation_config, 'use_cache')
            ):
                self.generation_config.use_cache = True

            if hasattr(self, 'use_cache'):
                self.use_cache = True

            if hasattr(self, 'vlm_model') and self.vlm_model is not None:
                model = self.vlm_model
                if hasattr(model, 'generation_config') and model.generation_config is not None:
                    model.generation_config.use_cache = True
                if hasattr(model, 'config') and hasattr(model.config, 'use_cache'):
                    model.config.use_cache = True

            return _original_process_images(self, *args, **kwargs)

        hf_transformers_model.HuggingFaceTransformersVlmModel.process_images = _patched_process_images

        _original_from_pretrained = AutoModelForVision2Seq.from_pretrained

        @classmethod
        def _patched_from_pretrained(cls, *args, **kwargs):
            model = _original_from_pretrained.__func__(cls, *args, **kwargs)
            if hasattr(model, 'config') and hasattr(model.config, 'use_cache'):
                model.config.use_cache = True
            if hasattr(model, 'generation_config') and model.generation_config is not None:
                model.generation_config.use_cache = True
            return model

        AutoModelForVision2Seq.from_pretrained = _patched_from_pretrained
        logger.info("Applied KV cache fix for Transformers")
    except Exception as e:
        logger.warning(f"Could not apply KV cache fix: {e}")

def run_benchmark(pdf_path: Path, model_id: str, backend: str):
    logger.info(f"BENCHMARK START: Model={model_id}, Backend={backend}")

    pipeline_options = VlmPipelineOptions()
    pipeline_options.images_scale = 1.0
    pipeline_options.generate_page_images = True
    pipeline_options.accelerator_options = AcceleratorOptions(
        device=AcceleratorDevice.CUDA,
        num_threads=8,
    )

    if backend == "vllm":
        # Memory-optimized VLLM settings
        vlm_options = {
            'extra_generation_config': {
                'max_model_len': 8192,
                'gpu_memory_utilization': 0.80,
                'enforce_eager': True,
            },
            'max_new_tokens': 8192,
        }
    else:
        # Transformers settings
        vlm_options = {
            'extra_generation_config': {
                'use_cache': True,
            }
        }
        apply_kv_cache_fix()

    # Try to find the model in vlm_model_specs
    base_spec = None
    if hasattr(vlm_model_specs, model_id.upper()):
        base_spec = getattr(vlm_model_specs, model_id.upper())
        logger.info(f"Using predefined spec: {model_id.upper()}")
    else:
        # Fallback to GRANITEDOCLING as base if we have a custom HF repo
        if "/" in model_id:
             base_spec = vlm_model_specs.GRANITEDOCLING_VLLM if backend == "vllm" else vlm_model_specs.GRANITEDOCLING_TRANSFORMERS
             logger.info(f"Using GRANITEDOCLING as base for custom model: {model_id}")
             # Update the repo_id (InlineVlmOptions)
             base_spec = base_spec.model_copy(update={"repo_id": model_id})
        else:
            logger.error(f"Model ID '{model_id}' not found in vlm_model_specs and not a valid repo_id")
            sys.exit(1)

    # Further update with backend options
    # We MUST merge extra_generation_config to avoid losing essential settings (like prompts/templates)
    final_vlm_options = base_spec.model_copy(update={"max_new_tokens": vlm_options.get("max_new_tokens", 8192)})

    if "extra_generation_config" in vlm_options:
        orig_config = getattr(base_spec, "extra_generation_config", {})
        new_config = {**orig_config, **vlm_options["extra_generation_config"]}
        final_vlm_options.extra_generation_config = new_config

    pipeline_options.vlm_options = final_vlm_options
    logger.info(f"VLM Options: {pipeline_options.vlm_options}")

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=VlmPipeline,
                pipeline_options=pipeline_options
            )
        }
    )

    start_time = time.time()
    try:
        result = converter.convert(str(pdf_path))
        end_time = time.time()
        elapsed = end_time - start_time

        doc = result.document
        markdown = doc.export_to_markdown()

        char_count = len(markdown)
        logger.info(f"BENCHMARK COMPLETE: {elapsed:.2f}s, Chars: {char_count}")
        if char_count > 0:
            preview = markdown[:200].replace("\n", " ")
            logger.info(f"Markdown preview: {preview}...")
        else:
            logger.warning("Markdown output is empty!")

        result_line = f"RESULT|{model_id}|{backend}|{elapsed:.2f}|{char_count}"
        print(result_line, flush=True)


    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        print(f"ERROR|{model_id}|{backend}|{e}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="VLM Performance Benchmark")
    parser.add_argument("--pdf", type=str, required=True, help="Path to PDF file")
    parser.add_argument("--model", type=str, required=True, help="Model ID or alias")
    parser.add_argument("--backend", type=str, choices=["vllm", "transformers"], default="vllm", help="Backend to use")

    args = parser.parse_args()
    pdf_path = Path(args.pdf)

    if not pdf_path.exists():
        print(f"Error: PDF path {pdf_path} does not exist")
        sys.exit(1)

    run_benchmark(pdf_path, args.model, args.backend)

if __name__ == "__main__":
    main()
