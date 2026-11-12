# The Axon vault image, for a TDX confidential VM (Phala Cloud / dstack, as used by NEAR Shade Agents).
# Built by .github/workflows/vault-image.yml and deployed by digest, so the TEE measures this exact image.
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY axon/ axon/
ENV AXON_STATE=/app/state
# Build the hidden test set reproducibly from public MedQuAD (same seed as the laptop demo); keep only the vault's part.
RUN python -m axon prepare-data && rm -rf data/contributors data/raw
# Pre-download the base model so the measured image is self-contained.
RUN python -c "from transformers import AutoModelForCausalLM, AutoTokenizer as T; m='HuggingFaceTB/SmolLM2-135M-Instruct'; T.from_pretrained(m); AutoModelForCausalLM.from_pretrained(m)"
EXPOSE 8700
CMD ["sh", "-c", "python -m axon vault --host 0.0.0.0 --operator \"$AXON_OPERATOR\""]
