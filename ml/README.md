# Machine-learning research

`ml` contains research and evidence-generation workflows, never the production serving architecture.

- `datasets`: manifests, provenance, licensing, class mappings, and reproducible split definitions; raw images are not committed.
- `experiments`: versioned experiment configurations and summaries.
- `training`: reusable training workflows.
- `evaluation`: metrics, gold/field holdouts, regressions, and promotion gates.
- `exports`: reproducible conversion definitions and export manifests, not large weights by default.
- `model-registry`: model cards, checksums, dataset/training links, and promotion metadata.
- `notebooks`: bounded exploration; notebooks do not become runtime modules.
- `scripts`: focused research automation.

Large model formats are ignored by default. A tiny model fixture may be committed only under `ml/model-registry/fixtures` after review, with a documented license, checksum, purpose, and size justification.
