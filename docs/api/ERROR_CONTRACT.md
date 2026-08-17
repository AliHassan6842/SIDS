# API error foundation

The canonical F0 error-envelope specification is `packages/contracts/errors/README.md`.

Every future Java, Python, and asynchronous boundary must preserve the stable `code`, safe `message`, correlation `requestId`, explicit `retryable` flag, and bounded `details` object. Transport adapters may map status codes, but they must not silently change the meaning of an error code.
