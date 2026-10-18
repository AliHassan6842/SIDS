import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import type { Crop, Pest, PestKind } from "../api/contracts";
import { EmptyState, ErrorState, LoadingState } from "../components/AsyncState";
import { PageHeader } from "../components/PageHeader";
import { PestRow } from "../components/PestRow";

export function PestLibraryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [crops, setCrops] = useState<Crop[]>([]);
  const [selectedCrop, setSelectedCrop] = useState("");
  const [kind, setKind] = useState<PestKind>(() => searchParams.get("kind") === "GENERAL_INSECT" ? "GENERAL_INSECT" : "CROP_PEST");
  const [pests, setPests] = useState<Pest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    api.crops({ includeUnavailable: true }, controller.signal).then(setCrops).catch(() => setCrops([]));
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    api.pests({ kind, cropId: kind === "CROP_PEST" ? selectedCrop || undefined : undefined }, controller.signal)
      .then((items) => { setPests(items); setLoading(false); })
      .catch((reason: unknown) => {
        if (!(reason instanceof DOMException && reason.name === "AbortError")) {
          setError(reason instanceof Error ? reason.message : "Pests could not be loaded.");
          setLoading(false);
        }
      });
    return () => controller.abort();
  }, [kind, selectedCrop, reloadKey]);

  return (
    <div className="page">
      <PageHeader title="Insect library" />
      <div className="library-tabs" role="tablist" aria-label="Insect type">
        <button role="tab" aria-selected={kind === "CROP_PEST"} onClick={() => { setLoading(true); setError(""); setKind("CROP_PEST"); setSearchParams({}); }}>Crop pests</button>
        <button role="tab" aria-selected={kind === "GENERAL_INSECT"} onClick={() => { setLoading(true); setError(""); setKind("GENERAL_INSECT"); setSelectedCrop(""); setSearchParams({ kind: "GENERAL_INSECT" }); }}>General insects</button>
      </div>
      {kind === "CROP_PEST" && crops.length ? (
        <label className="select-field">Crop
          <select value={selectedCrop} onChange={(event) => { setLoading(true); setError(""); setSelectedCrop(event.target.value); }}>
            <option value="">All supported crops</option>
            {crops.map((crop) => <option key={crop.id} value={crop.id}>{crop.name}</option>)}
          </select>
        </label>
      ) : null}
      {loading ? <LoadingState label="Loading supported pests…" /> : error ? <ErrorState message={error} onRetry={() => { setLoading(true); setError(""); setReloadKey((value) => value + 1); }} /> : pests.length ? (
        <div className="data-list data-list--large">{pests.map((pest) => <PestRow key={pest.id} pest={pest} />)}</div>
      ) : <EmptyState title={kind === "GENERAL_INSECT" ? "General insect catalog in review" : "No supported pests"} message={kind === "GENERAL_INSECT" ? "Reviewed general-insect classes will appear here only after model and guidance approval." : selectedCrop ? "No verified pests are enabled for this crop." : "The verified pest catalog is empty."} />}
    </div>
  );
}
