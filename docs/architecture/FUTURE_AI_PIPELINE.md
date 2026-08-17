# Future AI-to-decision pipeline

This is a documented target, not an implemented pipeline.

```text
Image
  -> Image Quality Gate
  -> Crop / Problem Router
  -> Specialists
       - Pest Detector
       - Disease Classifier
       - Severity Segmenter
  -> Uncertainty / Unknown Gate
  -> Visual Embedding / Similar Cases
  -> Structured AI Result
  -> Java Core
       + Field Context
       + Survey
       + Weather
       + Thresholds
       + History
       + Verified Knowledge
  -> Decision Engine
  -> Farmer Recommendation
```

The Python stages produce versioned computational evidence. The Java stages own field interpretation, policy, authorization, and recommendations. An uncertain or unsupported input must yield an explicit request for more evidence rather than a forced diagnosis.
