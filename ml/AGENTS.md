# ML research instructions

- Research must be reproducible; every experiment records configuration, code revision, dependency environment, and seed.
- Every dataset records source provenance, authority, jurisdiction where relevant, license, checksum, class mapping, and version.
- Do not commit raw public datasets, large images, trained weights, or checkpoints by default.
- Generate deterministic train/validation/test splits and never change them silently.
- Prevent duplicate and near-duplicate leakage across splits.
- Never move real-field holdout data into training without a dataset version increment and explicit review.
- Keep public-dataset results distinguishable from real-field results.
- Version experiment outcomes; report macro metrics because class imbalance matters.
- Benchmark accuracy, latency, memory, model size, license, and deployment cost.
- No production promotion occurs without approved evaluation gates, model metadata, and integrity checks.
