import { Link } from "react-router-dom";
import type { ScanResult } from "../api/contracts";
import { formatDate, humanizeCode } from "../lib/format";
import { AuthenticatedScanImage } from "./AuthenticatedScanImage";
import { Icon } from "./Icon";

const titleFor = (scan: ScanResult): string => {
  if (scan.status === "IDENTIFIED" && scan.pest) return scan.pest.commonName;
  if (scan.status === "UNKNOWN") return "Unsupported or uncertain insect";
  if (scan.status === "REJECTED_IMAGE") return "Image not suitable";
  return "Identification failed";
};

export function ScanRow({ scan }: { scan: ScanResult }) {
  return (
    <Link className="data-row" to={`/result/${encodeURIComponent(scan.id)}`}>
      <span className="data-row__media">
        {scan.imageUrl ? <AuthenticatedScanImage scanId={scan.id} alt="" loading="lazy" fallback={<Icon name="camera" />} /> : <Icon name="camera" />}
      </span>
      <span className="data-row__copy">
        <strong>{titleFor(scan)}</strong>
        <span>{scan.pest?.scientificName || humanizeCode(scan.reason)}</span>
        <small>{formatDate(scan.createdAt)}</small>
      </span>
      <Icon className="data-row__chevron" name="chevron" />
    </Link>
  );
}
