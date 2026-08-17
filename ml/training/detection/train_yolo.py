import argparse
import logging
from typing import Any

from ultralytics import YOLO

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train YOLO for Pest Detection")
    parser.add_argument("--data", type=str, required=True, help="Path to the dataset config file (YAML)")
    parser.add_argument("--model", type=str, default="yolo11n.pt", help="Model to start training from (e.g., yolo11n.pt)")
    parser.add_argument("--epochs", type=int, default=100, help="Number of epochs to train for")
    parser.add_argument("--batch", type=int, default=16, help="Batch size for training")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size as integer")
    parser.add_argument("--device", type=str, default="", help="Device to run on, i.e. cuda, cpu, mps")
    parser.add_argument("--project", type=str, default="runs/detect", help="Save to project/name")
    parser.add_argument("--name", type=str, default="train", help="Save to project/name")
    parser.add_argument("--resume", action="store_true", help="Resume training from last checkpoint")
    return parser.parse_args()


def train(
    data_path: str,
    model_name: str = "yolo11n.pt",
    epochs: int = 100,
    batch: int = 16,
    imgsz: int = 640,
    device: str = "",
    project: str = "runs/detect",
    name: str = "train",
    resume: bool = False
) -> Any:
    """
    Train a YOLO model.
    """
    if resume:
        logger.info(f"Resuming training from {model_name}")
        model = YOLO(model_name)
    else:
        logger.info(f"Starting new training with {model_name}")
        model = YOLO(model_name)

    logger.info(f"Training parameters: data={data_path}, epochs={epochs}, batch={batch}, imgsz={imgsz}, device={device}")
    
    results = model.train(
        data=data_path,
        epochs=epochs,
        batch=batch,
        imgsz=imgsz,
        device=device,
        project=project,
        name=name,
        resume=resume
    )
    
    logger.info("Training complete.")
    logger.info(f"Results: {results}")
    return results


def main() -> None:
    args = parse_args()
    train(
        data_path=args.data,
        model_name=args.model,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=args.device,
        project=args.project,
        name=args.name,
        resume=args.resume
    )


if __name__ == "__main__":
    main()
