import { Link } from "react-router-dom";
import type { Pest } from "../api/contracts";
import { Icon } from "./Icon";

export function PestRow({ pest }: { pest: Pest }) {
  return (
    <Link className="data-row" to={`/pests/${encodeURIComponent(pest.id)}`}>
      <span className="data-row__media">
        {pest.imageUrl ? <img src={pest.imageUrl} alt="" loading="lazy" /> : <Icon name="bug" />}
      </span>
      <span className="data-row__copy">
        <strong>{pest.commonName}</strong>
        {pest.scientificName ? <em>{pest.scientificName}</em> : <span>Reviewed insect group</span>}
      </span>
      <Icon className="data-row__chevron" name="chevron" />
    </Link>
  );
}
