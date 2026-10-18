# Opt-in Active Learning and Retraining

This workflow is deliberately manual. It never promotes a model and never adds an unreviewed image to training.

1. Export private inference evidence as JSONL with `sample_id`, relative `image_path`, `capture_group`, `crop_slug`, `status`, model metadata, and ranked `predictions`.
2. Select uncertain or unknown samples:

   ```powershell
   .venv\Scripts\python.exe ml\active_learning\select_review_candidates.py `
     --config ml\active_learning\configs\sids-multicrop-v2.json `
     --inference-jsonl <private-inference.jsonl> --image-root <private-image-root> `
     --output ml\data\prepared\review-queues\batch-001.jsonl
   ```

3. A human reviewer changes every queue row to `approved` or `rejected`, supplies `reviewer_id` and `reviewed_at`, and supplies normalized `annotations` for approved rows. An approved negative has `annotations: []`.
4. Seal the completed batch. Pending rows, changed bytes, invalid boxes, labels outside the selected crop, and missing reviewer evidence fail closed:

   ```powershell
   .venv\Scripts\python.exe ml\active_learning\seal_review_batch.py `
     --config ml\active_learning\configs\sids-multicrop-v2.json `
     --reviewed-jsonl <completed-review.jsonl> --image-root <private-image-root> `
     --batch-id batch-001 --output ml\data\prepared\reviewed-batches\batch-001.json
   ```

5. Materialize a new version. Capture groups are assigned as a unit; existing public/field holdouts are not moved. Exact or dHash-distance-at-most-2 matches to the base dataset fail closed:

   ```powershell
   .venv\Scripts\python.exe ml\active_learning\materialize_retrain_candidate.py `
     --config ml\active_learning\configs\sids-multicrop-v2.json `
     --base-dataset ml\data\prepared\sids-multicrop-pest-detection-v2.0 `
     --sealed-batch ml\data\prepared\reviewed-batches\batch-001.json `
     --image-root <private-image-root> --output-version sids-multicrop-pest-detection-v2.1-candidate
   ```

6. Retrain into `ml/runs/`, evaluate public test and the new grouped field holdout, repeat rejection/runtime probes, and compare every gate in the config. Promotion requires a separate reviewed manifest change under `models/`; none of these scripts writes there.

Private field images, review queues, sealed batches, prepared datasets, and runs remain Git-ignored. Track only aggregate, privacy-safe reports and version manifests.
