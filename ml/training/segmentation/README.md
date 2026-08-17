# Segmentation and Severity Training Framework

## Status: BLOCKED

**Full dataset-dependent training for segmentation is explicitly BLOCKED.**

### Reason
Adequate segmentation data (pixel-level annotations) is currently unavailable. As per architectural guidelines, we **must not** fabricate masks from classification datasets to claim real severity accuracy.

### Available Functionality
The runtime interfaces and mask logic are implemented and working. You can use the `severity_calculator.py` to calculate visible sample severity from existing masks (`affected_pixels / valid_plant_pixels`).

- `severity_calculator.py`: Contains the working mask logic.
- `trainer.py`: Contains the training framework stubs which will raise `NotImplementedError` if invoked.

Once adequate segmentation datasets are obtained, this module can be unblocked and training pipelines fully implemented.
