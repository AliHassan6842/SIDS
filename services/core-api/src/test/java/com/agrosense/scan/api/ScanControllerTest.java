package com.agrosense.scan.api;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import com.agrosense.scan.application.ScanService;
import com.agrosense.scan.domain.IdentificationMode;
import com.agrosense.shared.error.ApiException;
import com.agrosense.shared.error.GlobalExceptionHandler;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.multipart.MaxUploadSizeExceededException;

class ScanControllerTest {
    private ScanService scans;
    private MockMvc mvc;

    @BeforeEach
    void setUp() {
        scans = mock(ScanService.class);
        mvc = MockMvcBuilders.standaloneSetup(new ScanController(scans))
            .setControllerAdvice(new GlobalExceptionHandler()).build();
    }

    @Test
    void rejectsUnsupportedCropBeforePrivateAiCall() throws Exception {
        UUID cropId = UUID.randomUUID();
        when(scans.validate(eq(IdentificationMode.CROP_PEST), eq(cropId), any(), anyString())).thenThrow(
            new ApiException(HttpStatus.BAD_REQUEST, "UNSUPPORTED_CROP", "Crop is not supported by the current model.", false));

        mvc.perform(multipart("/api/v1/vision/validate-frame")
                .file(image()).param("cropId", cropId.toString()).requestAttr("requestId", "request-1"))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.code").value("UNSUPPORTED_CROP"));

        verify(scans).validate(eq(IdentificationMode.CROP_PEST), eq(cropId), any(), eq("request-1"));
    }

    @Test
    void mapsMultipartLimitFailureToPayloadTooLarge() throws Exception {
        UUID cropId = UUID.randomUUID();
        when(scans.validate(eq(IdentificationMode.CROP_PEST), eq(cropId), any(), anyString())).thenThrow(new MaxUploadSizeExceededException(8));

        mvc.perform(multipart("/api/v1/vision/validate-frame")
                .file(image()).param("cropId", cropId.toString()).requestAttr("requestId", "request-2"))
            .andExpect(status().isPayloadTooLarge())
            .andExpect(jsonPath("$.code").value("IMAGE_TOO_LARGE"));
    }

    private MockMultipartFile image() {
        return new MockMultipartFile("image", "capture.jpg", "image/jpeg", new byte[] {1, 2, 3});
    }
}
