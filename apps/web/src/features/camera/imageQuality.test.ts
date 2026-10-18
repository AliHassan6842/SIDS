import { describe, expect, it } from "vitest";
import { localQualityReason } from "./imageQuality";

describe("localQualityReason", () => {
  it("rejects underexposed frames", () => {
    expect(localQualityReason({ brightness: 30, sharpness: 20 })).toBe("TOO_DARK");
  });

  it("rejects overexposed frames", () => {
    expect(localQualityReason({ brightness: 230, sharpness: 20 })).toBe("TOO_BRIGHT");
  });

  it("rejects blurry frames", () => {
    expect(localQualityReason({ brightness: 120, sharpness: 2 })).toBe("TOO_BLURRY");
  });

  it("allows a locally suitable frame to reach server validation", () => {
    expect(localQualityReason({ brightness: 120, sharpness: 12 })).toBeNull();
  });
});
