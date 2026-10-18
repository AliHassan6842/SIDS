import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { ScanResult } from "../api/contracts";
import { EmptyState, ErrorState, LoadingState } from "../components/AsyncState";
import { PageHeader } from "../components/PageHeader";
import { ScanRow } from "../components/ScanRow";

export function HistoryPage() {
  const [scans, setScans] = useState<ScanResult[] | null>(null);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    api.scans(controller.signal).then(setScans).catch((reason: unknown) => {
      if (!(reason instanceof DOMException && reason.name === "AbortError")) setError(reason instanceof Error ? reason.message : "Scan history could not be loaded.");
    });
    return () => controller.abort();
  }, [reloadKey]);
  return (
    <div className="page">
      <PageHeader title="Scan history" />
      {error ? <ErrorState message={error} onRetry={() => { setError(""); setScans(null); setReloadKey((value) => value + 1); }} /> : scans === null ? <LoadingState /> : scans.length ? <div className="data-list data-list--large">{scans.map((scan) => <ScanRow key={scan.id} scan={scan} />)}</div> : <EmptyState title="No scan history" message="Completed, unknown, and rejected identifications will be saved here." action={<Link className="button button--small" to="/identify">Identify insect</Link>} />}
    </div>
  );
}
