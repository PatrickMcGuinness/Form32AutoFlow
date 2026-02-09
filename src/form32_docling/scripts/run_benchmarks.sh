#!/bin/bash

# VLM Benchmarking Runner

PDF_PATH=$1

if [ -z "$PDF_PATH" ]; then
    echo "Usage: ./run_benchmarks.sh <pdf_path>"
    exit 1
fi

LOG_FILE="benchmarks.log"
echo "--- Benchmark started at $(date) ---" >> "$LOG_FILE"

echo "Starting VLM Benchmarks for: $PDF_PATH"
echo "All detailed logs are being saved to $LOG_FILE"
echo "------------------------------------------------"
echo "Model | Backend | Time (s) | Chars"
echo "------------------------------------------------"

MODELS=(
    # "GRANITEDOCLING_VLLM|vllm"
    # "GRANITEDOCLING_TRANSFORMERS|transformers"
    "SMOLDOCLING_VLLM|vllm"
    "SMOLDOCLING_TRANSFORMERS|transformers"
    "lightonai/LightOnOCR-2-1B|vllm"
    "lightonai/LightOnOCR-2-1B|transformers"
    "rootsautomation/GutenOCR-3B|vllm"
    "rootsautomation/GutenOCR-3B|transformers"
    "SMOLVLM256_VLLM|vllm"
    "SMOLVLM256_TRANSFORMERS|transformers"
)

for ENTRY in "${MODELS[@]}"; do
    MODEL=$(echo $ENTRY | cut -d'|' -f1)
    BACKEND=$(echo $ENTRY | cut -d'|' -f2)
    
    # Run the benchmark and capture both stdout and stderr
    # We use tee to append to log but grep to extract the result line
    python -u src/form32_docling/scripts/vlm_benchmark.py --pdf "$PDF_PATH" --model "$MODEL" --backend "$BACKEND" 2>&1 | tee -a "$LOG_FILE" | grep "^RESULT" | cut -d'|' -f2- | sed 's/|/ | /g'
done


echo "------------------------------------------------"
echo "Benchmarking complete."
