# Fetched dataset boundary

This directory is for immutable source archives and source-layout extracts fetched from dataset publishers. Large fetched files are ignored by Git.

`FETCH_MANIFEST.json` records provenance, terms, remote identifiers, expected size/checksum, local relative path, and fetch status. Prepared class subsets and deterministic splits belong in `../prepared/`; experiments belong in `../../runs/`; promoted model artifacts belong in the model registry/export boundary.

Do not train directly from an undocumented download and do not commit raw public datasets.
