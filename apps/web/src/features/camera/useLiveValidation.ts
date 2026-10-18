import { useEffect, useRef, useState, type RefObject } from "react";
import { api } from "../../api/client";
import type { IdentificationMode, ValidationReason } from "../../api/contracts";
import type { CameraState } from "./useCamera";
import { captureVideoFrame, localQualityReason } from "./imageQuality";

export type LiveValidationState =
  | "CAMERA_STARTING"
  | "SEARCHING_FOR_SUBJECT"
  | "CHECKING"
  | ValidationReason
  | "READY"
  | "VALIDATION_UNAVAILABLE";

export function useLiveValidation(
  videoRef: RefObject<HTMLVideoElement>,
  cameraState: CameraState,
  request: { mode: IdentificationMode; cropId?: string },
  active: boolean,
) {
  const [state, setState] = useState<LiveValidationState>("CAMERA_STARTING");
  const inFlightRef = useRef(false);
  const sequenceRef = useRef(0);

  useEffect(() => {
    if (!active || cameraState !== "ready") {
      return;
    }

    const controller = new AbortController();
    let disposed = false;

    const validateLatest = async () => {
      if (inFlightRef.current || disposed || !videoRef.current) return;
      inFlightRef.current = true;
      const sequence = ++sequenceRef.current;
      try {
        const frame = await captureVideoFrame(videoRef.current, true, 640, 0.72);
        const localReason = localQualityReason(frame.metrics);
        if (localReason) {
          if (!disposed && sequence === sequenceRef.current) setState(localReason);
          return;
        }
        setState("CHECKING");
        const result = await api.validateFrame(request.mode, request.cropId, frame.blob, controller.signal);
        if (!disposed && sequence === sequenceRef.current) {
          setState(result.valid ? "READY" : result.reason ?? "NO_INSECT_CANDIDATE");
        }
      } catch (error) {
        if (!disposed && !(error instanceof DOMException && error.name === "AbortError")) {
          setState("VALIDATION_UNAVAILABLE");
        }
      } finally {
        inFlightRef.current = false;
      }
    };

    void validateLatest();
    const interval = window.setInterval(() => void validateLatest(), 800);
    return () => {
      disposed = true;
      controller.abort();
      window.clearInterval(interval);
      inFlightRef.current = false;
      sequenceRef.current += 1;
    };
  }, [active, cameraState, request.cropId, request.mode, videoRef]);

  if (!active || cameraState !== "ready") {
    return cameraState === "starting" ? "CAMERA_STARTING" : "SEARCHING_FOR_SUBJECT";
  }
  return state;
}
