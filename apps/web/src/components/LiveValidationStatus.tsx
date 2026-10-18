import type { LiveValidationState } from "../features/camera/useLiveValidation";

const messages: Record<LiveValidationState, string> = {
  CAMERA_STARTING: "Starting camera…",
  SEARCHING_FOR_SUBJECT: "Place the insect inside the guide area",
  CHECKING: "Checking image quality…",
  TOO_DARK: "Add more light",
  TOO_BRIGHT: "Reduce glare",
  TOO_BLURRY: "Hold the camera steady",
  SUBJECT_TOO_SMALL: "Move closer to the insect",
  NO_INSECT_CANDIDATE: "No insect found in the guide area",
  INVALID_IMAGE: "Camera frame could not be read",
  READY: "Ready to capture",
  VALIDATION_UNAVAILABLE: "Live check unavailable — try gallery upload",
};

export function LiveValidationStatus({ state }: { state: LiveValidationState }) {
  const tone = state === "READY" ? "ready" : state === "CHECKING" || state === "CAMERA_STARTING" ? "checking" : "warning";
  return (
    <div className={`validation-status validation-status--${tone}`} role="status" aria-live="polite">
      <span aria-hidden="true" />
      {messages[state]}
    </div>
  );
}
