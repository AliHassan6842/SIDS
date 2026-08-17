
class ImageDecodeError(Exception):
    pass

class ImageValidationError(Exception):
    pass

class UnsupportedCropError(Exception):
    pass

class ModelNotLoadedError(Exception):
    pass

def setup_exception_handlers(app):
    @app.exception_handler(ImageDecodeError)
    async def image_decode_handler(request, exc):
        return {"error": "IMAGE_DECODE_ERROR", "message": str(exc)}, 400
