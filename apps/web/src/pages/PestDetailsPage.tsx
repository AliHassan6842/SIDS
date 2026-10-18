import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { Pest } from "../api/contracts";
import { ErrorState, LoadingState } from "../components/AsyncState";
import { Icon } from "../components/Icon";
import { GuidanceItem } from "../components/GuidanceItem";
import { PageHeader } from "../components/PageHeader";

export function PestDetailsPage() {
  const { pestId = "" } = useParams();
  const [pest, setPest] = useState<Pest | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    api.pest(pestId, controller.signal).then(setPest).catch((reason: unknown) => {
      if (!(reason instanceof DOMException && reason.name === "AbortError")) setError(reason instanceof Error ? reason.message : "Pest information could not be loaded.");
    });
    return () => controller.abort();
  }, [pestId]);

  if (error) return <div className="page"><PageHeader title="Insect information" back /><ErrorState message={error} /></div>;
  if (!pest) return <div className="page"><PageHeader title="Insect information" back /><LoadingState /></div>;
  const guidance = pest.guidance;
  const generalGuidance = pest.generalGuidance;
  return (
    <div className="page">
      <PageHeader title="Insect information" back />
      <section className="pest-detail-hero">
        {pest.imageUrl ? <img src={pest.imageUrl} alt={`Close-up of ${pest.commonName}`} /> : <span><Icon name="bug" /></span>}
        <h1>{pest.commonName}</h1>
        {pest.scientificName ? <em>{pest.scientificName}</em> : null}
      </section>
      <div className="guidance-list">
        {pest.description ? <GuidanceItem title="What it is" content={pest.description} /> : null}
        {guidance?.damageDescription ? <GuidanceItem title="Possible crop damage" content={guidance.damageDescription} /> : null}
        {guidance?.prevention?.length ? <GuidanceItem title="Prevention" content={guidance.prevention} /> : null}
        {guidance?.basicManagement?.length ? <GuidanceItem title="Basic management" content={guidance.basicManagement} /> : null}
        {generalGuidance?.harmSummary ? <GuidanceItem title="Is it harmful?" content={generalGuidance.harmSummary} /> : null}
        {generalGuidance?.safeRemoval.length ? <GuidanceItem title="Safe removal" content={generalGuidance.safeRemoval} /> : null}
        {generalGuidance?.seekExpertHelpWhen.length ? <GuidanceItem title="Get expert help when" content={generalGuidance.seekExpertHelpWhen} /> : null}
      </div>
      {guidance?.sourceName ? <p className="source-note"><Icon name="leaf" />Source: {guidance.sourceUrl ? <a href={guidance.sourceUrl} target="_blank" rel="noreferrer">{guidance.sourceName}</a> : guidance.sourceName}</p> : generalGuidance?.sourceName ? <p className="source-note"><Icon name="info" />Source: {generalGuidance.sourceUrl ? <a href={generalGuidance.sourceUrl} target="_blank" rel="noreferrer">{generalGuidance.sourceName}</a> : generalGuidance.sourceName}</p> : null}
      <div className="safety-note"><Icon name="info" /><p>{pest.kind === "CROP_PEST" ? "Identification alone does not determine whether pesticide treatment is required. Consult a qualified local expert when needed." : "Avoid direct contact when identification is uncertain or the insect may bite, sting, or indicate an infestation."}</p></div>
      <Link className="button" to={`/identify?mode=${pest.kind}`}>Identify an insect</Link>
    </div>
  );
}
