"""Fetch a frozen, license-filtered iNaturalist general-insect v2 source pool."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path

from PIL import Image


API = "https://api.inaturalist.org/v1/observations"
USER_AGENT = "SIDS-FYP-reproducible-dataset-fetch/1.0"
ALLOWED = {"cc0", "cc-by", "cc-by-sa"}
TAXA = {
    "beetle": {"taxon_id": 47208, "taxon_name": "Coleoptera", "role": "known", "target": 180},
    "grasshopper": {"taxon_id": 67688, "taxon_name": "Caelifera", "role": "known", "target": 180},
    "mosquito": {"taxon_id": 52134, "taxon_name": "Culicidae", "role": "known", "target": 180},
    "odonata": {"taxon_id": 47792, "taxon_name": "Odonata", "role": "unsupported-insect", "target": 60},
    "mantodea": {"taxon_id": 48112, "taxon_name": "Mantodea", "role": "unsupported-insect", "target": 60},
    "hemiptera": {"taxon_id": 47744, "taxon_name": "Hemiptera", "role": "unsupported-insect", "target": 60},
}


def get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def download(candidate: dict, output_root: Path) -> dict:
    request = urllib.request.Request(candidate["download_url"], headers={"User-Agent": USER_AGENT})
    error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read(8 * 1024 * 1024 + 1)
                final_url = response.geturl()
            if len(data) > 8 * 1024 * 1024:
                raise ValueError("photo exceeds 8 MiB")
            with Image.open(BytesIO(data)) as image:
                image.verify()
            with Image.open(BytesIO(data)) as image:
                width, height = image.size
                image_format = image.format
            if width < 224 or height < 224:
                raise ValueError(f"photo too small: {width}x{height}")
            suffix = ".jpg" if image_format in {"JPEG", "MPO"} else ".png"
            relative = Path(candidate["role"]) / candidate["class_slug"] / f"inat_{candidate['observation_id']}_{candidate['photo_id']}{suffix}"
            destination = output_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            return {
                **candidate,
                "status": "VERIFIED",
                "local_path": str(destination),
                "relative_path": relative.as_posix(),
                "http_final_url": final_url,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "width": width,
                "height": height,
            }
        except Exception as exc:  # network and decode failures are recorded per item
            error = f"{type(exc).__name__}: {exc}"
            time.sleep(0.5 * (attempt + 1))
    return {**candidate, "status": "FAILED", "error": error}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    output = workspace / "ml/data/fetched/inaturalist-general-v2"
    manifest_path = output / "FETCH_MANIFEST.json"
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    (output / "api-pages").mkdir(parents=True)
    candidates = []
    for slug, taxon in TAXA.items():
        observations = []
        for page in range(1, 4):
            parameters = {
                "taxon_id": taxon["taxon_id"],
                "quality_grade": "research",
                "photos": "true",
                "photo_license": "cc0,cc-by,cc-by-sa",
                "per_page": 200,
                "page": page,
                "order_by": "id",
                "order": "desc",
            }
            url = API + "?" + urllib.parse.urlencode(parameters)
            document = get_json(url)
            snapshot = output / "api-pages" / f"{slug}-page-{page}.json"
            snapshot.write_text(json.dumps(document, separators=(",", ":")), encoding="utf-8")
            observations.extend(document["results"])
            time.sleep(1.0)
        photographer_counts: Counter[int] = Counter()
        selected = []
        for observation in observations:
            user = observation.get("user") or {}
            photographer_id = user.get("id")
            if photographer_id is None or photographer_counts[photographer_id] >= 4:
                continue
            qualifying = []
            for observation_photo in observation.get("observation_photos", []):
                photo = observation_photo.get("photo") or {}
                license_code = (photo.get("license_code") or "").lower()
                if license_code in ALLOWED and photo.get("url"):
                    qualifying.append(photo)
            if not qualifying:
                continue
            photo = qualifying[0]
            url = photo.get("medium_url") or photo["url"].replace("square.", "medium.")
            selected.append(
                {
                    "dataset": "inaturalist-research-grade-v1-api",
                    "role": taxon["role"],
                    "class_slug": slug,
                    "query_taxon_id": taxon["taxon_id"],
                    "query_taxon_name": taxon["taxon_name"],
                    "observation_id": observation["id"],
                    "observation_url": observation.get("uri") or f"https://www.inaturalist.org/observations/{observation['id']}",
                    "observed_taxon_id": (observation.get("taxon") or {}).get("id"),
                    "observed_taxon_name": (observation.get("taxon") or {}).get("name"),
                    "quality_grade": observation.get("quality_grade"),
                    "photographer_id": photographer_id,
                    "photographer_login": user.get("login"),
                    "photo_id": photo["id"],
                    "photo_license": photo["license_code"].upper(),
                    "photo_attribution": photo.get("attribution"),
                    "photo_original_dimensions": photo.get("original_dimensions"),
                    "download_url": url,
                    "api_query_url": url if False else API + "?" + urllib.parse.urlencode({"id": observation["id"]}),
                }
            )
            photographer_counts[photographer_id] += 1
            if len(selected) >= taxon["target"] + 30:
                break
        candidates.extend(selected)
        print(json.dumps({"class": slug, "api_observations": len(observations), "download_candidates": len(selected)}), flush=True)

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(download, candidate, output / "images"): candidate for candidate in candidates}
        for index, future in enumerate(as_completed(futures), start=1):
            results.append(future.result())
            if index % 100 == 0:
                print(json.dumps({"downloads_completed": index, "total": len(futures)}), flush=True)
    verified_by_slug: dict[str, list[dict]] = defaultdict(list)
    failures = []
    for result in results:
        if result["status"] == "VERIFIED":
            verified_by_slug[result["class_slug"]].append(result)
        else:
            failures.append(result)
    retained = []
    for slug, taxon in TAXA.items():
        rows = sorted(verified_by_slug[slug], key=lambda row: row["observation_id"])
        retained.extend(rows[: taxon["target"]])
    retained_paths = {row["local_path"] for row in retained}
    for rows in verified_by_slug.values():
        for row in rows:
            if row["local_path"] not in retained_paths:
                Path(row["local_path"]).unlink()
    manifest = {
        "schema_version": 1,
        "fetched_at": "2026-08-26",
        "api": API,
        "api_filter": {
            "quality_grade": "research",
            "photos": True,
            "photo_license": ["CC0", "CC-BY", "CC-BY-SA"],
            "one_photo_per_observation": True,
            "maximum_photos_per_photographer_per_class": 4,
        },
        "taxa": TAXA,
        "verified_counts": dict(sorted(Counter(row["class_slug"] for row in retained).items())),
        "verified_bytes": sum(row["bytes"] for row in retained),
        "records": sorted(retained, key=lambda row: (row["class_slug"], row["observation_id"])),
        "failures": failures,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verified_counts": manifest["verified_counts"], "verified_bytes": manifest["verified_bytes"], "failures": len(failures)}, indent=2))
    shortfalls = {slug: taxon["target"] - manifest["verified_counts"].get(slug, 0) for slug, taxon in TAXA.items()}
    if any(value > 0 for value in shortfalls.values()):
        raise SystemExit(f"Fetch shortfalls: {shortfalls}")


if __name__ == "__main__":
    main()
