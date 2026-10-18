import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { Pest, ScanResult } from "../api/contracts";
import { ErrorState, LoadingState } from "../components/AsyncState";
import { AuthenticatedScanImage } from "../components/AuthenticatedScanImage";
import { Icon } from "../components/Icon";
import { GuidanceItem } from "../components/GuidanceItem";
import { PageHeader } from "../components/PageHeader";
import { formatConfidence, humanizeCode } from "../lib/format";

interface ResultLocationState { scan?: ScanResult; }

export function ResultPage() {
  const { scanId = "" } = useParams();
  const location = useLocation();
  const initial = (location.state as ResultLocationState | null)?.scan;
  const [scan, setScan] = useState<ScanResult | null>(initial?.id === scanId ? initial : null);
  const [pest, setPest] = useState<Pest | null>(initial?.pest ?? null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (scan) return;
    const controller = new AbortController();
    api.scan(scanId, controller.signal).then((value) => {
      setScan(value);
      setPest(value.pest);
    }).catch((reason: unknown) => {
      if (!(reason instanceof DOMException && reason.name === "AbortError")) setError(reason instanceof Error ? reason.message : "Scan result could not be loaded.");
    });
    return () => controller.abort();
  }, [scan, scanId]);

  useEffect(() => {
    if (scan?.status !== "IDENTIFIED" || !scan.pest || scan.pest.guidance || scan.pest.generalGuidance) return;
    const controller = new AbortController();
    api.pest(scan.pest.id, controller.signal).then(setPest).catch(() => undefined);
    return () => controller.abort();
  }, [scan]);

  if (error) return <div className="page"><PageHeader title="Identification result" back /><ErrorState message={error} /></div>;
  if (!scan) return <div className="page"><PageHeader title="Identification result" back /><LoadingState label="Loading result…" /></div>;

  if (scan.status !== "IDENTIFIED" || !scan.pest) return <NonIdentifiedResult scan={scan} onChanged={setScan} />;
  const shownPest = pest ?? scan.pest;
  const guidance = shownPest.guidance;
  const generalGuidance = shownPest.generalGuidance;
  return (
    <div className="result-page">
      <PageHeader title="Identification result" back />
      <section className="result-heading">
        <h1>{shownPest.commonName}</h1>
        {shownPest.scientificName ? <em>{shownPest.scientificName}</em> : null}
        <span className="confidence">Confidence {formatConfidence(scan.confidence)}</span>
      </section>
      <ResultImage scan={scan} />
      <div className="guidance-list">
        {shownPest.description ? <GuidanceItem title="What it is" content={shownPest.description} /> : null}
        {shownPest.kind === "CROP_PEST" && guidance?.damageDescription ? <GuidanceItem title="Possible crop damage" content={guidance.damageDescription} /> : null}
        {guidance?.prevention?.length ? <GuidanceItem title="Prevention" content={guidance.prevention} /> : null}
        {guidance?.basicManagement?.length ? <GuidanceItem title="Basic management" content={guidance.basicManagement} /> : null}
        {generalGuidance?.harmSummary ? <GuidanceItem title="Is it harmful?" content={generalGuidance.harmSummary} /> : null}
        {generalGuidance?.safeRemoval.length ? <GuidanceItem title="Safe removal" content={generalGuidance.safeRemoval} /> : null}
        {generalGuidance?.seekExpertHelpWhen.length ? <GuidanceItem title="Get expert help when" content={generalGuidance.seekExpertHelpWhen} /> : null}
      </div>
      {guidance?.sourceName ? <p className="source-note"><Icon name="leaf" />Source: {guidance.sourceUrl ? <a href={guidance.sourceUrl} target="_blank" rel="noreferrer">{guidance.sourceName}</a> : guidance.sourceName}</p> : generalGuidance ? <p className="source-note"><Icon name="info" />Source: <a href={generalGuidance.sourceUrl} target="_blank" rel="noreferrer">{generalGuidance.sourceName}</a> · verified {generalGuidance.lastVerifiedAt}</p> : null}
      <div className="safety-note"><Icon name="info" /><p>{shownPest.kind === "CROP_PEST" ? "Identification alone does not determine whether pesticide treatment is required." : "Do not touch or handle an insect when identification is uncertain or a bite, sting, or infestation is possible."}</p></div>
      <ReviewContribution scan={scan} onChanged={setScan} />
    </div>
  );
}

function ResultImage({ scan }: { scan: ScanResult }) {
  const box = scan.bbox;
  return (
    <div className="result-image">
      {scan.imageUrl ? <AuthenticatedScanImage scanId={scan.id} alt="Captured insect" fallback={<span><Icon name="camera" /></span>} /> : <span><Icon name="camera" /></span>}
      {box ? <i className="bounding-box" aria-label="Detected insect location" style={{ left: `${box.x * 100}%`, top: `${box.y * 100}%`, width: `${box.width * 100}%`, height: `${box.height * 100}%` }} /> : null}
    </div>
  );
}

function NonIdentifiedResult({ scan, onChanged }: { scan: ScanResult; onChanged: (scan: ScanResult) => void }) {
  const content = scan.status === "UNKNOWN"
    ? { title: "Insect not identified", message: "The image did not confidently match a supported pest. SIDS does not guess unsupported insects.", icon: "search" as const }
    : scan.status === "REJECTED_IMAGE"
      ? { title: "Image not suitable", message: `The image was rejected: ${humanizeCode(scan.reason)}. Retake a clear close-up with the insect inside the guide.`, icon: "camera" as const }
      : { title: "Identification failed", message: "The scan could not be completed. Try again when the service is available.", icon: "warning" as const };
  return (
    <div className="page result-state">
      <PageHeader title="Identification result" back />
      <span className="result-state__icon"><Icon name={content.icon} /></span>
      <h1>{content.title}</h1>
      <p>{content.message}</p>
      {scan.status === "UNKNOWN" ? <ReviewContribution scan={scan} onChanged={onChanged} /> : null}
      <div className="result-state__actions"><Link className="button" to="/identify">Try another image</Link><Link className="button button--outline" to="/pests">View supported pests</Link></div>
    </div>
  );
}

function ReviewContribution({ scan, onChanged }: { scan: ScanResult; onChanged: (scan: ScanResult) => void }) {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [actionError, setActionError] = useState("");
  const reviewSubmitted = scan.reviewStatus !== "NOT_SUBMITTED";

  const setConsent = async (trainingConsent: boolean) => {
    setBusy(true);
    setActionError("");
    setMessage("");
    try {
      const response = await api.updateTrainingConsent(scan.id, trainingConsent);
      onChanged({
        ...scan,
        trainingConsent: response.trainingConsent,
        consentedAt: response.consentedAt,
        reviewStatus: response.reviewStatus,
      });
      setMessage(trainingConsent ? "Consent saved. You can now submit this scan for review." : "Consent withdrawn. This image will not be used for future training.");
    } catch (reason) {
      setActionError(reason instanceof Error ? reason.message : "Training consent could not be updated.");
    } finally {
      setBusy(false);
    }
  };

  const submit = async () => {
    setBusy(true);
    setActionError("");
    setMessage("");
    try {
      const response = await api.submitForReview(scan.id, scan.pest?.slug);
      onChanged({ ...scan, reviewStatus: response.status });
      setMessage("Submitted for expert review. It will not enter training unless a reviewer approves it.");
    } catch (reason) {
      setActionError(reason instanceof Error ? reason.message : "This scan could not be submitted for review.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="review-contribution" aria-labelledby={`review-contribution-${scan.id}`}>
      <h2 id={`review-contribution-${scan.id}`}>Help improve future models</h2>
      <p>Your image is never added directly. It must be consented, reviewed, versioned, and pass model evaluation.</p>
      <label>
        <input type="checkbox" checked={scan.trainingConsent} disabled={busy} onChange={(event) => void setConsent(event.target.checked)} />
        <span>Allow this image to be considered after expert review</span>
      </label>
      {reviewSubmitted ? <strong className="review-contribution__status">Review status: {humanizeCode(scan.reviewStatus)}</strong> : (
        <button className="button button--small" disabled={busy || !scan.trainingConsent} onClick={() => void submit()}>{busy ? "Saving…" : "Submit for expert review"}</button>
      )}
      {message ? <p className="review-contribution__message" role="status">{message}</p> : null}
      {actionError ? <p className="camera-error" role="alert">{actionError}</p> : null}
    </section>
  );
}
