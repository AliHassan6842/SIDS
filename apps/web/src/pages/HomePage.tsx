import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { Crop, Pest, ScanResult } from "../api/contracts";
import { EmptyState, ErrorState, LoadingState } from "../components/AsyncState";
import { Icon } from "../components/Icon";
import { PestRow } from "../components/PestRow";
import { ScanRow } from "../components/ScanRow";

interface HomeData { scans: ScanResult[]; crops: Crop[]; cropPests: Pest[]; generalPests: Pest[]; }

export function HomePage() {
  const [data, setData] = useState<HomeData | null>(null);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    Promise.all([
      api.scans(controller.signal),
      api.crops({ includeUnavailable: true }, controller.signal),
      api.pests({ kind: "CROP_PEST" }, controller.signal),
      api.pests({ kind: "GENERAL_INSECT" }, controller.signal),
    ])
      .then(([scans, crops, cropPests, generalPests]) => setData({ scans, crops, cropPests, generalPests }))
      .catch((reason: unknown) => {
        if (!(reason instanceof DOMException && reason.name === "AbortError")) setError(reason instanceof Error ? reason.message : "Home data could not be loaded.");
      });
    return () => controller.abort();
  }, [reloadKey]);

  return (
    <div className="page page--home">
      <div className="brand">
        <span className="brand__mark"><Icon name="leaf" /></span>
        <span><strong>SIDS</strong><small>Smart Insect Detection</small></span>
      </div>
      <section className="home-hero">
        <h1>Identify an insect</h1>
        <p>Scan supported crop pests or submit a general insect for reviewed identification.</p>
        <div className="home-hero__actions">
          <Link className="button" to="/identify?mode=CROP_PEST"><Icon name="camera" />Crop pest <Icon name="chevron" /></Link>
        </div>
      </section>

      {error ? <ErrorState message={error} onRetry={() => { setError(""); setData(null); setReloadKey((value) => value + 1); }} /> : !data ? <LoadingState label="Loading your SIDS home…" /> : (
        <>
          <section className="content-section">
            <div className="section-heading"><h2>Recent scans</h2><Link to="/history">View all <Icon name="chevron" /></Link></div>
            {data.scans.length ? <div className="data-list">{data.scans.slice(0, 3).map((scan) => <ScanRow key={scan.id} scan={scan} />)}</div> : <EmptyState title="No scans yet" message="Your completed identifications will appear here." />}
          </section>
          <section className="content-section">
            <div className="section-heading"><h2>Supported pests</h2><Link to="/pests">View all <Icon name="chevron" /></Link></div>
            {data.cropPests.length ? <div className="data-list">{data.cropPests.slice(0, 3).map((pest) => <PestRow key={pest.id} pest={pest} />)}</div> : <EmptyState title="No supported pests published" message="The verified pest catalog is not available yet." />}
          </section>
          <section className="content-section">
            <div className="section-heading"><h2>General insect groups</h2><Link to="/pests?kind=GENERAL_INSECT">View library <Icon name="chevron" /></Link></div>
            {data.generalPests.length ? <div className="data-list">{data.generalPests.slice(0, 3).map((pest) => <PestRow key={pest.id} pest={pest} />)}</div> : <EmptyState title="General catalog in review" message="Promoted insect groups will appear here after model and guidance approval." />}
          </section>
          <section className="content-section supported-crops">
            <h2>Crop coverage</h2>
            {data.crops.length ? <div className="crop-cards">{data.crops.map((crop) => <article className="crop-card" key={crop.id}>{crop.imageUrl ? <img src={crop.imageUrl} alt="" loading="lazy" /> : <span><Icon name="leaf" /></span>}<div><strong>{crop.name}</strong><small>{crop.identificationSupported ? "Identification available" : "Dataset preparation"}</small></div></article>)}</div> : <p className="muted">No crops are currently enabled.</p>}
          </section>
        </>
      )}
    </div>
  );
}
