package com.agrosense.scan.api;

import static com.agrosense.ai.AiContracts.ValidateResponse;
import static com.agrosense.scan.api.ScanDtos.ScanResult;

import com.agrosense.scan.application.ScanService;
import com.agrosense.scan.domain.IdentificationMode;
import com.agrosense.shared.security.CurrentUser;
import jakarta.servlet.http.HttpServletRequest;
import java.util.List;
import java.util.UUID;
import org.springframework.http.*;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/v1")
public class ScanController {
    private final ScanService scans;
    public ScanController(ScanService scans) { this.scans = scans; }
    @PostMapping(value="/vision/validate-frame", consumes=MediaType.MULTIPART_FORM_DATA_VALUE)
    public ValidateResponse validate(@RequestParam(defaultValue="CROP_PEST") IdentificationMode mode,
                                     @RequestParam(required=false) UUID cropId, @RequestPart MultipartFile image,
                                     HttpServletRequest request) {
        return scans.validate(mode, cropId, image, request.getAttribute("requestId").toString());
    }
    @PostMapping(value="/scans", consumes=MediaType.MULTIPART_FORM_DATA_VALUE) @ResponseStatus(HttpStatus.CREATED)
    public ScanResult create(@AuthenticationPrincipal CurrentUser user,
                             @RequestParam(defaultValue="CROP_PEST") IdentificationMode mode,
                             @RequestParam(required=false) UUID cropId,
                             @RequestParam(defaultValue="false") boolean trainingConsent,
                             @RequestPart MultipartFile image, HttpServletRequest request) {
        return scans.create(user.id(), mode, cropId, trainingConsent, image,
            request.getAttribute("requestId").toString());
    }
    @GetMapping("/scans") public List<ScanResult> list(@AuthenticationPrincipal CurrentUser user) { return scans.list(user.id()); }
    @GetMapping("/scans/{scanId}") public ScanResult get(@AuthenticationPrincipal CurrentUser user, @PathVariable UUID scanId) { return scans.get(scanId, user.id()); }
    @GetMapping(value="/scans/{scanId}/image", produces=MediaType.IMAGE_JPEG_VALUE)
    public ResponseEntity<byte[]> image(@AuthenticationPrincipal CurrentUser user, @PathVariable UUID scanId) {
        return ResponseEntity.ok().cacheControl(CacheControl.noStore()).body(scans.image(scanId, user.id()));
    }
}
