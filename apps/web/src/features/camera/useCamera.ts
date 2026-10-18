import { useCallback, useEffect, useRef, useState } from "react";

export type CameraState = "idle" | "starting" | "ready" | "denied" | "unavailable" | "error";

export function useCamera(enabled: boolean) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [state, setState] = useState<CameraState>("idle");
  const [facingMode, setFacingMode] = useState<"environment" | "user">("environment");
  const [restartKey, setRestartKey] = useState(0);

  const stop = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
  }, []);

  useEffect(() => {
    if (!enabled) {
      stop();
      return;
    }

    let cancelled = false;
    const start = async () => {
      stop();
      if (!navigator.mediaDevices?.getUserMedia) {
        setState("unavailable");
        return;
      }
      setState("starting");
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: false,
          video: {
            facingMode: { ideal: facingMode },
            width: { ideal: 1920 },
            height: { ideal: 1080 },
          },
        });
        if (cancelled) {
          stream.getTracks().forEach((track) => track.stop());
          return;
        }
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
        }
        setState("ready");
      } catch (error) {
        if (cancelled) return;
        const name = error instanceof DOMException ? error.name : "";
        if (name === "NotAllowedError" || name === "SecurityError") setState("denied");
        else if (name === "NotFoundError" || name === "OverconstrainedError") setState("unavailable");
        else setState("error");
      }
    };

    void start();
    return () => {
      cancelled = true;
      stop();
    };
  }, [enabled, facingMode, restartKey, stop]);

  return {
    videoRef,
    state: enabled ? state : "idle",
    facingMode,
    retry: () => setRestartKey((value) => value + 1),
    switchCamera: () => setFacingMode((value) => (value === "environment" ? "user" : "environment")),
  };
}
