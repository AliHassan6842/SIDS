package com.agrosense.sync.api;

import com.agrosense.sync.api.dto.*;
import com.agrosense.sync.application.SyncApplicationService;
import com.agrosense.sync.application.command.*;
import com.agrosense.sync.domain.model.IdempotencyRecord;
import com.agrosense.sync.domain.model.SyncEvent;
import com.agrosense.sync.domain.model.SyncOperation;
import jakarta.validation.Valid;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * REST Controller providing HTTP endpoints for edge and offline mobile synchronization.
 */
@RestController
@RequestMapping("/api/v1/sync")
public class SyncController {

    private final SyncApplicationService syncApplicationService;

    public SyncController(SyncApplicationService syncApplicationService) {
        this.syncApplicationService = syncApplicationService;
    }

    /**
     * Pushes a batch of offline sync events to the server.
     */
    @PostMapping("/push")
    public ResponseEntity<SyncPushResponse> pushBatch(@Valid @RequestBody SyncPushRequest request) {
        List<SyncEventCommandItem> commandItems = request.events().stream()
                .map(dto -> new SyncEventCommandItem(
                        dto.clientEventId(),
                        dto.entityId(),
                        dto.entityType(),
                        SyncOperation.fromString(dto.operation()),
                        dto.baseVersion(),
                        dto.payload(),
                        dto.createdAtDevice(),
                        dto.preferredStrategy()
                ))
                .collect(Collectors.toList());

        ProcessSyncBatchCommand command = new ProcessSyncBatchCommand(
                request.deviceId(),
                request.farmId(),
                request.userId(),
                request.defaultStrategy(),
                commandItems
        );

        SyncBatchResult result = syncApplicationService.processSyncBatch(command);

        List<SyncEventResultDto> resultDtos = result.eventResults().stream()
                .map(this::mapToResultDto)
                .collect(Collectors.toList());

        SyncPushResponse response = new SyncPushResponse(
                result.totalEvents(),
                result.appliedCount(),
                result.duplicateCount(),
                result.conflictCount(),
                result.failedCount(),
                resultDtos,
                result.serverTimestamp()
        );

        return ResponseEntity.ok(response);
    }

    /**
     * Pulls changes recorded on the server since a specified timestamp for delta sync.
     */
    @GetMapping("/pull")
    public ResponseEntity<SyncPullResponse> pullChanges(
            @RequestParam UUID farmId,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) OffsetDateTime since,
            @RequestParam(required = false) List<String> entityTypes,
            @RequestParam(required = false, defaultValue = "100") Integer limit) {

        PullSyncChangesQuery query = new PullSyncChangesQuery(
                farmId,
                since,
                entityTypes,
                limit
        );

        PullSyncResult result = syncApplicationService.pullChanges(query);

        List<PullEntityItemDto> eventDtos = result.events().stream()
                .map(this::mapToPullDto)
                .collect(Collectors.toList());

        SyncPullResponse response = new SyncPullResponse(
                result.farmId(),
                result.serverTimestamp(),
                eventDtos,
                result.hasMore()
        );

        return ResponseEntity.ok(response);
    }

    /**
     * Checks the idempotency status of a clientEventId.
     */
    @GetMapping("/idempotency/{clientEventId}")
    public ResponseEntity<IdempotencyStatusResponse> checkIdempotencyStatus(@PathVariable String clientEventId) {
        Optional<IdempotencyRecord> recordOpt = syncApplicationService.checkIdempotency(clientEventId);

        if (recordOpt.isPresent()) {
            IdempotencyRecord record = recordOpt.get();
            return ResponseEntity.ok(new IdempotencyStatusResponse(
                    record.getClientEventId(),
                    true,
                    record.getResourceId(),
                    record.getResourceType(),
                    record.getCreatedAt()
            ));
        }

        return ResponseEntity.ok(new IdempotencyStatusResponse(
                clientEventId,
                false,
                null,
                null,
                null
        ));
    }

    private SyncEventResultDto mapToResultDto(SyncEventProcessingResult res) {
        ConflictDetailDto conflictDetails = null;
        if (res.conflictDetected()) {
            conflictDetails = new ConflictDetailDto(
                    res.baseVersion(),
                    res.serverVersion(),
                    res.status().name(),
                    res.message()
            );
        }

        return new SyncEventResultDto(
                res.clientEventId(),
                res.entityId(),
                res.entityType(),
                res.status(),
                res.baseVersion(),
                res.resolvedVersion(),
                res.conflictDetected(),
                res.message(),
                conflictDetails
        );
    }

    private PullEntityItemDto mapToPullDto(SyncEvent event) {
        return new PullEntityItemDto(
                event.getId(),
                event.getClientEventId(),
                event.getDeviceId(),
                event.getEntityId(),
                event.getEntityType(),
                event.getBaseVersion(),
                event.getCreatedAtDevice(),
                event.getServerReceivedAt()
        );
    }
}
