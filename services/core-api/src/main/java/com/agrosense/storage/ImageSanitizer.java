package com.agrosense.storage;

import com.agrosense.shared.error.ApiException;
import java.awt.image.BufferedImage;
import java.awt.Graphics2D;
import java.io.*;
import java.util.Iterator;
import javax.imageio.*;
import javax.imageio.stream.ImageInputStream;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

@Component
public class ImageSanitizer {
    private final long maxBytes;
    private final long maxPixels;
    public ImageSanitizer(@Value("${sids.upload.max-bytes}") long maxBytes, @Value("${sids.upload.max-pixels}") long maxPixels) {
        this.maxBytes = maxBytes; this.maxPixels = maxPixels;
    }
    public byte[] sanitize(MultipartFile file) {
        if (file.isEmpty()) throw invalid("Image is empty.");
        if (file.getSize() > maxBytes) throw tooLarge();
        try {
            byte[] bytes = file.getBytes();
            if (bytes.length == 0) throw invalid("Image is empty.");
            if (bytes.length > maxBytes) throw tooLarge();
            boolean jpeg = bytes.length >= 3 && (bytes[0] & 0xff) == 0xff && (bytes[1] & 0xff) == 0xd8 && (bytes[2] & 0xff) == 0xff;
            boolean png = bytes.length >= 8 && (bytes[0] & 0xff) == 0x89 && bytes[1] == 0x50 && bytes[2] == 0x4e && bytes[3] == 0x47;
            if (!(jpeg || png)) throw invalid("Only valid JPEG and PNG images are accepted.");
            try (ImageInputStream stream = ImageIO.createImageInputStream(new ByteArrayInputStream(bytes))) {
                Iterator<ImageReader> readers = ImageIO.getImageReaders(stream);
                if (!readers.hasNext()) throw invalid("Image could not be decoded.");
                ImageReader reader = readers.next();
                try {
                    reader.setInput(stream, true, true);
                    int width = reader.getWidth(0), height = reader.getHeight(0);
                    if (width < 224 || height < 224 || (long) width * height > maxPixels) throw invalid("Image dimensions are not allowed.");
                    BufferedImage decoded = reader.read(0);
                    BufferedImage rgb = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
                    Graphics2D graphics = rgb.createGraphics();
                    try { graphics.drawImage(decoded, 0, 0, null); }
                    finally { graphics.dispose(); }
                    ByteArrayOutputStream output = new ByteArrayOutputStream();
                    if (!ImageIO.write(rgb, "jpeg", output)) throw invalid("Image could not be safely re-encoded.");
                    return output.toByteArray();
                } finally { reader.dispose(); }
            }
        } catch (ApiException e) { throw e; }
        catch (IOException | RuntimeException e) { throw invalid("Image could not be safely decoded."); }
    }
    private ApiException invalid(String message) { return new ApiException(HttpStatus.BAD_REQUEST, "INVALID_IMAGE", message, true); }
    private ApiException tooLarge() { return new ApiException(HttpStatus.PAYLOAD_TOO_LARGE, "IMAGE_TOO_LARGE", "Image exceeds the byte limit.", true); }
}
