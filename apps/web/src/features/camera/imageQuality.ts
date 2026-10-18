import type { ValidationReason } from "../../api/contracts";

export const ROI = { x: 0.15, y: 0.2, width: 0.7, height: 0.55 } as const;

export interface FrameMetrics {
  brightness: number;
  sharpness: number;
}

export interface CapturedFrame {
  blob: Blob;
  metrics: FrameMetrics;
}

export const localQualityReason = ({ brightness, sharpness }: FrameMetrics): ValidationReason | null => {
  if (brightness < 45) return "TOO_DARK";
  if (brightness > 220) return "TOO_BRIGHT";
  if (sharpness < 5.5) return "TOO_BLURRY";
  return null;
};

const canvasBlob = (canvas: HTMLCanvasElement, quality: number): Promise<Blob> =>
  new Promise((resolve, reject) => {
    canvas.toBlob((blob) => (blob ? resolve(blob) : reject(new Error("Could not encode camera frame"))), "image/jpeg", quality);
  });

const calculateMetrics = (data: Uint8ClampedArray, width: number, height: number): FrameMetrics => {
  const step = 4;
  let brightnessSum = 0;
  let samples = 0;
  let sharpnessSum = 0;
  for (let y = 1; y < height - 1; y += step) {
    for (let x = 1; x < width - 1; x += step) {
      const index = (y * width + x) * 4;
      const left = index - 4;
      const right = index + 4;
      const up = index - width * 4;
      const down = index + width * 4;
      const gray = (data[index]! + data[index + 1]! + data[index + 2]!) / 3;
      const neighbor =
        (data[left]! + data[left + 1]! + data[left + 2]! +
          data[right]! + data[right + 1]! + data[right + 2]! +
          data[up]! + data[up + 1]! + data[up + 2]! +
          data[down]! + data[down + 1]! + data[down + 2]!) / 12;
      brightnessSum += gray;
      sharpnessSum += Math.abs(gray - neighbor);
      samples += 1;
    }
  }
  return {
    brightness: samples ? brightnessSum / samples : 0,
    sharpness: samples ? sharpnessSum / samples : 0,
  };
};

export async function captureVideoFrame(
  video: HTMLVideoElement,
  roiOnly: boolean,
  maxWidth = 1280,
  quality = 0.88,
): Promise<CapturedFrame> {
  if (!video.videoWidth || !video.videoHeight) throw new Error("Camera is not ready");
  const source = roiOnly
    ? {
        x: Math.round(video.videoWidth * ROI.x),
        y: Math.round(video.videoHeight * ROI.y),
        width: Math.round(video.videoWidth * ROI.width),
        height: Math.round(video.videoHeight * ROI.height),
      }
    : { x: 0, y: 0, width: video.videoWidth, height: video.videoHeight };
  const scale = Math.min(1, maxWidth / source.width);
  const canvas = document.createElement("canvas");
  canvas.width = Math.max(1, Math.round(source.width * scale));
  canvas.height = Math.max(1, Math.round(source.height * scale));
  const context = canvas.getContext("2d", { willReadFrequently: true });
  if (!context) throw new Error("Image processing is unavailable");
  context.drawImage(video, source.x, source.y, source.width, source.height, 0, 0, canvas.width, canvas.height);
  const pixels = context.getImageData(0, 0, canvas.width, canvas.height);
  return {
    blob: await canvasBlob(canvas, quality),
    metrics: calculateMetrics(pixels.data, canvas.width, canvas.height),
  };
}
