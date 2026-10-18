import { useEffect, useRef, useState, type ChangeEvent } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import type { Crop, IdentificationMode, Pest, ScanResult } from "../api/contracts";
import { EmptyState, ErrorState, LoadingState } from "../components/AsyncState";
import { Icon } from "../components/Icon";
import { LiveValidationStatus } from "../components/LiveValidationStatus";
import { captureVideoFrame } from "../features/camera/imageQuality";
import { useCamera } from "../features/camera/useCamera";
import { useLiveValidation } from "../features/camera/useLiveValidation";

type IdentifyStage = "select" | "camera" | "review" | "submitting";

export function IdentifyPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [stage, setStage] = useState<IdentifyStage>("select");
  const [mode, setMode] = useState<IdentificationMode>(() => searchParams.get("mode") === "GENERAL_INSECT" ? "GENERAL_INSECT" : "CROP_PEST");
  const [crops, setCrops] = useState<Crop[] | null>(null);
  const [generalPests, setGeneralPests] = useState<Pest[] | null>(null);
  const [generalError, setGeneralError] = useState("");
  const [generalReloadKey, setGeneralReloadKey] = useState(0);
  const [cropId, setCropId] = useState("");
  const [image, setImage] = useState<Blob | null>(null);
  const [imageUrl, setImageUrl] = useState("");
  const [error, setError] = useState("");
  const [trainingConsent, setTrainingConsent] = useState(false);
  const submitController = useRef<AbortController | null>(null);
  const galleryRef = useRef<HTMLInputElement>(null);
  const { videoRef, state: cameraState, retry: retryCamera, switchCamera } = useCamera(stage === "camera");
  const selectionReady = mode === "GENERAL_INSECT" || Boolean(cropId);
  const validation = useLiveValidation(
    videoRef,
    cameraState,
    { mode, cropId: mode === "CROP_PEST" ? cropId : undefined },
    stage === "camera" && selectionReady,
  );

  useEffect(() => {
    const controller = new AbortController();
    api.crops({}, controller.signal)
      .then((items) => {
        const supported = items.filter((crop) => crop.identificationSupported);
        setCrops(supported);
        if (supported.length === 1) setCropId(supported[0]!.id);
      })
      .catch((reason: unknown) => {
        if (!(reason instanceof DOMException && reason.name === "AbortError")) setError(reason instanceof Error ? reason.message : "Supported crops could not be loaded.");
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    api.pests({ kind: "GENERAL_INSECT" }, controller.signal)
      .then((items) => { setGeneralPests(items); setGeneralError(""); })
      .catch((reason: unknown) => {
        if (!(reason instanceof DOMException && reason.name === "AbortError")) {
          setGeneralPests([]);
          setGeneralError(reason instanceof Error ? reason.message : "Supported insect groups could not be loaded.");
        }
      });
    return () => controller.abort();
  }, [generalReloadKey]);

  useEffect(() => () => {
    if (imageUrl) URL.revokeObjectURL(imageUrl);
    submitController.current?.abort();
  }, [imageUrl]);

  const selectedCrop = crops?.find((crop) => crop.id === cropId);

  const setCapturedImage = (blob: Blob) => {
    if (imageUrl) URL.revokeObjectURL(imageUrl);
    setImage(blob);
    setImageUrl(URL.createObjectURL(blob));
    setError("");
    setStage("review");
  };

  const capture = async () => {
    if (!videoRef.current || validation !== "READY") return;
    try {
      const frame = await captureVideoFrame(videoRef.current, false, 2048, 0.92);
      setCapturedImage(frame.blob);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The image could not be captured.");
    }
  };

  const chooseFile = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    if (!new Set(["image/jpeg", "image/png"]).has(file.type)) {
      setError("Choose a JPEG or PNG image.");
      return;
    }
    if (file.size > 12 * 1024 * 1024) {
      setError("Choose an image smaller than 12 MB.");
      return;
    }
    setCapturedImage(file);
  };

  const identify = async () => {
    if (!image || (mode === "CROP_PEST" && !cropId)) return;
    submitController.current?.abort();
    const controller = new AbortController();
    submitController.current = controller;
    setStage("submitting");
    setError("");
    try {
      const result: ScanResult = await api.createScan({
        mode,
        cropId: mode === "CROP_PEST" ? cropId : undefined,
        trainingConsent,
      }, image, controller.signal);
      navigate(`/result/${encodeURIComponent(result.id)}`, { replace: true, state: { scan: result } });
    } catch (reason) {
      if (!(reason instanceof DOMException && reason.name === "AbortError")) {
        setError(reason instanceof Error ? reason.message : "Identification failed.");
        setStage("review");
      }
    }
  };

  const retake = () => {
    setImage(null);
    if (imageUrl) URL.revokeObjectURL(imageUrl);
    setImageUrl("");
    setError("");
    setStage("camera");
  };

  const hiddenInput = (
    <input ref={galleryRef} className="visually-hidden" type="file" accept="image/jpeg,image/png" capture="environment" onChange={chooseFile} aria-label="Choose an insect photo from your device" />
  );

  if (stage === "select") {
    return (
      <div className="page identify-select">
        <header className="identify-select__header"><span className="brand__mark"><Icon name="camera" /></span><h1>What are you scanning?</h1><p>Select a category{mode === "CROP_PEST" ? " and crop" : ""} before opening the camera.</p></header>
        <fieldset className="mode-selector"><legend className="visually-hidden">Identification category</legend>
          <label className={mode === "CROP_PEST" ? "is-selected" : ""}><input type="radio" name="mode" checked={mode === "CROP_PEST"} onChange={() => setMode("CROP_PEST")} /><Icon name="leaf" />Crop pest</label>
          <label className={mode === "GENERAL_INSECT" ? "is-selected" : ""}><input type="radio" name="mode" checked={mode === "GENERAL_INSECT"} onChange={() => setMode("GENERAL_INSECT")} /><Icon name="bug" />General insect</label>
        </fieldset>
        {mode === "CROP_PEST" ? error ? <ErrorState message={error} /> : crops === null ? <LoadingState label="Loading supported crops…" /> : crops.length === 0 ? <EmptyState title="No crops available" message="Identification will be available after a verified crop and pest set is published." /> : (
          <fieldset className="crop-selector"><legend>Select crop</legend>{crops.map((crop) => <label key={crop.id} className={cropId === crop.id ? "is-selected" : ""}><input type="radio" name="crop" value={crop.id} checked={cropId === crop.id} onChange={() => setCropId(crop.id)} />{crop.imageUrl ? <img src={crop.imageUrl} alt="" /> : <Icon name="leaf" />}<span>{crop.name}</span></label>)}</fieldset>
        ) : generalError ? <ErrorState message={generalError} onRetry={() => { setGeneralPests(null); setGeneralError(""); setGeneralReloadKey((value) => value + 1); }} /> : generalPests === null ? <LoadingState label="Loading supported insect groups…" /> : (
          <section className="general-mode-note" aria-labelledby="general-groups-heading">
            <Icon name="info" />
            <div>
              <strong id="general-groups-heading">{generalPests.length ? "Currently supported groups" : "General insect catalog in review"}</strong>
              {generalPests.length ? <><div className="general-mode-note__groups">{generalPests.map((pest) => <span key={pest.id}>{pest.commonName}</span>)}</div><p>Use a clear close-up of one insect. Anything outside these reviewed groups remains unknown.</p></> : <p>No general-insect model is promoted yet. You can still submit an unknown image for consented expert review.</p>}
            </div>
          </section>
        )}
        <button className="button" disabled={!selectionReady} onClick={() => { setError(""); setStage("camera"); }}><Icon name="camera" />Open camera</button>
        <button className="button button--outline" disabled={!selectionReady} onClick={() => galleryRef.current?.click()}><Icon name="gallery" />Choose from gallery</button>
        <label className="training-consent"><input type="checkbox" checked={trainingConsent} onChange={(event) => setTrainingConsent(event.target.checked)} /><span>Allow this image to improve future models after review <small>(optional)</small></span></label>
        {hiddenInput}
        <p className="scope-note"><Icon name="info" />SIDS identifies only reviewed supported classes from a controlled close-up image.</p>
      </div>
    );
  }

  if (stage === "review" || stage === "submitting") {
    return (
      <div className="review-page">
        <header className="camera-topbar camera-topbar--light"><button className="icon-button" onClick={retake} aria-label="Return to camera"><Icon name="back" /></button><strong>Review image</strong><span /></header>
        <div className="review-image">{imageUrl ? <img src={imageUrl} alt="Captured insect ready for review" /> : null}</div>
        {error ? <p className="camera-error" role="alert">{error}</p> : null}
        <div className="review-actions"><button className="button button--outline" disabled={stage === "submitting"} onClick={retake}>Retake</button><button className="button" disabled={stage === "submitting"} onClick={() => void identify()}>{stage === "submitting" ? "Identifying…" : "Identify"}</button></div>
      </div>
    );
  }

  return (
    <div className="camera-page">
      <header className="camera-topbar">
        <button className="icon-button" onClick={() => setStage("select")} aria-label="Close camera">×</button>
        {mode === "CROP_PEST" ? <label>Crop<select value={cropId} onChange={(event) => setCropId(event.target.value)} aria-label="Selected crop">{crops?.map((crop) => <option key={crop.id} value={crop.id}>{crop.name}</option>)}</select></label> : <strong>General insect</strong>}
        <span className="camera-topbar__crop">{mode === "CROP_PEST" ? selectedCrop?.name : "General insect"}</span>
      </header>
      <div className="camera-viewport">
        <video ref={videoRef} muted playsInline aria-label="Live camera preview" />
        {cameraState === "ready" ? <><div className="roi-guide" aria-hidden="true"><i /><i /><i /><i /></div><LiveValidationStatus state={validation} /><p className="camera-instruction">Place the insect inside the guide area</p></> : (
          <div className="camera-fallback" role="status">
            <Icon name={cameraState === "denied" ? "warning" : "camera"} />
            <h2>{cameraState === "starting" ? "Starting camera…" : cameraState === "denied" ? "Camera permission denied" : cameraState === "unavailable" ? "No camera available" : "Camera could not start"}</h2>
            <p>{cameraState === "denied" ? "Allow camera access in your browser settings, then try again." : "You can retry or choose a close-up image from your gallery."}</p>
            {cameraState !== "starting" ? <button className="button button--outline button--small" onClick={retryCamera}><Icon name="refresh" />Try camera again</button> : null}
          </div>
        )}
      </div>
      {error ? <p className="camera-error" role="alert">{error}</p> : null}
      <div className="camera-controls">
        <button className="camera-tool" onClick={() => galleryRef.current?.click()}><Icon name="gallery" /><span>Gallery</span></button>
        <button className="capture-button" disabled={cameraState !== "ready" || validation !== "READY"} onClick={() => void capture()} aria-label={validation === "READY" ? "Capture image" : "Capture disabled until image is ready"}><span /></button>
        <button className="camera-tool" onClick={switchCamera} disabled={cameraState !== "ready"}><Icon name="switch" /><span>Switch</span></button>
      </div>
      {hiddenInput}
    </div>
  );
}
