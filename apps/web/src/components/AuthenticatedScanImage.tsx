import { type ReactNode, useEffect, useState } from "react";
import { api } from "../api/client";

interface AuthenticatedScanImageProps {
  scanId: string;
  alt: string;
  className?: string;
  loading?: "eager" | "lazy";
  fallback?: ReactNode;
}

export function AuthenticatedScanImage({ scanId, alt, className, loading, fallback = null }: AuthenticatedScanImageProps) {
  const [source, setSource] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    let objectUrl = "";
    api.scanImage(scanId, controller.signal).then((blob) => {
      objectUrl = URL.createObjectURL(blob);
      setSource(objectUrl);
    }).catch((reason: unknown) => {
      if (!(reason instanceof DOMException && reason.name === "AbortError")) setSource("");
    });
    return () => {
      controller.abort();
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [scanId]);

  return source ? <img src={source} alt={alt} className={className} loading={loading} /> : fallback;
}
