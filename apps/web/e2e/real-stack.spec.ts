import { deflateSync } from "node:zlib";
import { expect, test } from "./test";

const realEnabled = process.env.SIDS_E2E_REAL === "1";
const apiBase = (process.env.SIDS_REAL_API_URL ?? "http://127.0.0.1:8080").replace(/\/$/, "");

const crcTable = Array.from({ length: 256 }, (_, value) => {
  let crc = value;
  for (let bit = 0; bit < 8; bit += 1) crc = (crc & 1) ? 0xedb88320 ^ (crc >>> 1) : crc >>> 1;
  return crc >>> 0;
});

function crc32(data: Buffer): number {
  let crc = 0xffffffff;
  for (const byte of data) crc = crcTable[(crc ^ byte) & 0xff]! ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}

function chunk(type: string, data: Buffer): Buffer {
  const typeData = Buffer.from(type, "ascii");
  const length = Buffer.alloc(4);
  length.writeUInt32BE(data.length);
  const checksum = Buffer.alloc(4);
  checksum.writeUInt32BE(crc32(Buffer.concat([typeData, data])));
  return Buffer.concat([length, typeData, data, checksum]);
}

function checkerboardPng(width = 512, height = 512): Buffer {
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8;
  ihdr[9] = 2;
  const rows: Buffer[] = [];
  for (let y = 0; y < height; y += 1) {
    const row = Buffer.alloc(1 + width * 3);
    for (let x = 0; x < width; x += 1) {
      const value = (Math.floor(x / 12) + Math.floor(y / 12)) % 2 === 0 ? 55 : 190;
      row[1 + x * 3] = value;
      row[2 + x * 3] = value;
      row[3 + x * 3] = value;
    }
    rows.push(row);
  }
  return Buffer.concat([
    Buffer.from("89504e470d0a1a0a", "hex"),
    chunk("IHDR", ihdr),
    chunk("IDAT", deflateSync(Buffer.concat(rows))),
    chunk("IEND", Buffer.alloc(0)),
  ]);
}

test("real Java database and private Python frame-validation smoke", async ({ request }) => {
  test.skip(!realEnabled, "Set SIDS_E2E_REAL=1 with the real stack running.");
  const email = `playwright-${Date.now()}@example.test`;
  const register = await request.post(`${apiBase}/api/v1/auth/register`, {
    data: { fullName: "Playwright Smoke", email, password: "playwright-smoke-password", language: "en" },
  });
  expect(register.status()).toBe(201);
  const auth = await register.json() as { token: string };
  const headers = { Authorization: `Bearer ${auth.token}` };

  const cropsResponse = await request.get(`${apiBase}/api/v1/crops`, { headers });
  expect(cropsResponse.status(), await cropsResponse.text()).toBe(200);
  const crops = await cropsResponse.json() as Array<{ slug: string; imageUrl: string | null }>;
  expect(crops.map((crop) => crop.slug).sort()).toEqual([
    "cotton",
    "rice",
    "tomato",
  ]);
  const pestsResponse = await request.get(`${apiBase}/api/v1/pests`, { headers });
  expect(pestsResponse.status(), await pestsResponse.text()).toBe(200);
  const pests = await pestsResponse.json() as Array<{ slug: string; imageUrl: string | null }>;
  expect(pests.map((pest) => pest.slug).sort()).toEqual([
    "american-bollworm",
    "cotton-jassid",
    "cotton-leaf-curl",
    "cotton-mealybug",
    "cotton-thrips",
    "cotton-whitefly",
    "pink-bollworm",
    "rice-leaf-roller",
    "rice-water-weevil",
    "spotted-bollworm",
    "tomato-bacterial-spot",
    "tomato-early-blight",
    "tomato-late-blight",
    "tomato-yellow-leaf-curl-virus",
  ]);
  expect(pests.every((pest) => pest.imageUrl?.startsWith("/catalog/pests/"))).toBeTruthy();

  const generalPestsResponse = await request.get(`${apiBase}/api/v1/pests?kind=GENERAL_INSECT`, { headers });
  expect(generalPestsResponse.ok()).toBeTruthy();
  const generalPests = await generalPestsResponse.json() as Array<{ slug: string }>;
  expect(generalPests.map((pest) => pest.slug).sort()).toEqual([
    "beetle",
    "grasshopper",
    "mosquito",
  ]);

  const riceCrop = crops.find(c => c.slug === 'rice')!;
  const cropPestsResponse = await request.get(`${apiBase}/api/v1/crops/${riceCrop.id}/pests`, { headers });
  expect(cropPestsResponse.status(), await cropPestsResponse.text()).toBe(200);
  const cropPests = await cropPestsResponse.json() as Array<{ slug: string }>;
  expect(cropPests.map((pest) => pest.slug).sort()).toEqual([
    "rice-leaf-roller",
    "rice-water-weevil",
  ]);

  const validation = await request.post(`${apiBase}/api/v1/vision/validate-frame`, {
    headers,
    multipart: {
      cropId: riceCrop.id,
      image: { name: "checkerboard.png", mimeType: "image/png", buffer: checkerboardPng() },
    },
  });
  expect(validation.status(), await validation.text()).toBe(200);
  const payload = await validation.json() as Record<string, unknown>;
  expect(payload).toEqual(expect.objectContaining({
    valid: expect.any(Boolean),
    insectCandidate: expect.any(Boolean),
    quality: expect.any(Object),
  }));

  const scanResponse = await request.post(`${apiBase}/api/v1/scans`, {
    headers,
    multipart: {
      cropId: riceCrop.id,
      image: { name: "checkerboard.png", mimeType: "image/png", buffer: checkerboardPng() },
    },
  });
  expect(scanResponse.status(), await scanResponse.text()).toBe(201);
  const scan = await scanResponse.json() as { id: string; status: string; imageUrl: string };
  expect(["IDENTIFIED", "UNKNOWN", "REJECTED_IMAGE"]).toContain(scan.status);

  const generalScanResponse = await request.post(`${apiBase}/api/v1/scans`, {
    headers,
    multipart: {
      mode: "GENERAL_INSECT",
      image: { name: "checkerboard.png", mimeType: "image/png", buffer: checkerboardPng() },
    },
  });
  expect(generalScanResponse.status(), await generalScanResponse.text()).toBe(201);
  const generalScan = await generalScanResponse.json() as { id: string; status: string; imageUrl: string };
  expect(["IDENTIFIED", "UNKNOWN", "REJECTED_IMAGE"]).toContain(generalScan.status);

  const privateImage = await request.get(`${apiBase}${scan.imageUrl}`, { headers });
  expect(privateImage.status()).toBe(200);
  expect(privateImage.headers()["content-type"]).toContain("image/jpeg");
  const anonymousImage = await request.get(`${apiBase}${scan.imageUrl}`);
  expect(anonymousImage.status()).toBe(403);

  const historyResponse = await request.get(`${apiBase}/api/v1/scans`, { headers });
  expect(historyResponse.ok()).toBeTruthy();
  const history = await historyResponse.json() as Array<{ id: string }>;
  expect(history.some((entry) => entry.id === scan.id)).toBeTruthy();
});
