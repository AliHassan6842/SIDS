package com.agrosense.storage;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.agrosense.shared.error.ApiException;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import javax.imageio.ImageIO;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockMultipartFile;

class ImageSanitizerTest {
    @Test
    void rejectsMalformedImageBytes() {
        ImageSanitizer sanitizer = new ImageSanitizer(1024, 1_000_000);
        MockMultipartFile file = new MockMultipartFile("image", "capture.jpg", "image/jpeg", new byte[] {1, 2, 3, 4});

        assertInvalidImage(() -> sanitizer.sanitize(file));
    }

    @Test
    void rejectsImageAboveByteLimit() {
        ImageSanitizer sanitizer = new ImageSanitizer(3, 1_000_000);
        MockMultipartFile file = new MockMultipartFile("image", "capture.jpg", "image/jpeg", new byte[] {(byte) 0xff, (byte) 0xd8, (byte) 0xff, 0});

        assertThatThrownBy(() -> sanitizer.sanitize(file))
            .isInstanceOfSatisfying(ApiException.class, exception -> {
                assertThat(exception.code()).isEqualTo("IMAGE_TOO_LARGE");
                assertThat(exception.status().value()).isEqualTo(413);
            });
    }

    @Test
    void rejectsDimensionsBelowMinimum() throws Exception {
        ImageSanitizer sanitizer = new ImageSanitizer(1_000_000, 1_000_000);
        MockMultipartFile file = png(223, 300);

        assertInvalidImage(() -> sanitizer.sanitize(file));
    }

    @Test
    void rejectsDimensionsAbovePixelLimit() throws Exception {
        ImageSanitizer sanitizer = new ImageSanitizer(1_000_000, 50_000);
        MockMultipartFile file = png(300, 300);

        assertInvalidImage(() -> sanitizer.sanitize(file));
    }

    @Test
    void reencodesValidPngAsJpeg() throws Exception {
        ImageSanitizer sanitizer = new ImageSanitizer(1_000_000, 1_000_000);

        byte[] sanitized = sanitizer.sanitize(png(300, 300));

        assertThat(sanitized).startsWith((byte) 0xff, (byte) 0xd8, (byte) 0xff);
    }

    private MockMultipartFile png(int width, int height) throws Exception {
        BufferedImage image = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
        ByteArrayOutputStream output = new ByteArrayOutputStream();
        ImageIO.write(image, "png", output);
        return new MockMultipartFile("image", "capture.png", "image/png", output.toByteArray());
    }

    private void assertInvalidImage(org.assertj.core.api.ThrowableAssert.ThrowingCallable operation) {
        assertThatThrownBy(operation)
            .isInstanceOfSatisfying(ApiException.class, exception -> {
                assertThat(exception.code()).isEqualTo("INVALID_IMAGE");
                assertThat(exception.status().value()).isEqualTo(400);
            });
    }
}
