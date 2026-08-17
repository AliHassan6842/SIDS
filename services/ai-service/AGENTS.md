# AI service instructions

- This is production inference only: no exploratory notebooks, dataset downloads, or training scripts.
- Consume only approved, integrity-checked exported models.
- Do not mutate the business database directly or make pesticide, dosage, threshold, authorization, or agronomic-policy decisions.
- Validate all inputs with Pydantic and bound upload bytes, decoded dimensions, processing time, and concurrency.
- Return stable, deterministic structured schemas including model and dataset versions.
- Make unknown, out-of-distribution, uncertain, and requires-more-evidence results explicit.
- Isolate model loading and keep preprocessing versioned and reproducible.
- Treat model files as untrusted until format, origin, checksum, and loader safety are verified.
- Test corrupt, oversized, adversarial, and malicious input cases.
