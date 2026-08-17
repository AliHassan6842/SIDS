import logging

from train_yolo import train

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main() -> None:
    logger.info("Setting up smoke train test...")
    # Use coco8.yaml which ultralytics will auto-download
    # It contains a tiny dataset perfect for testing.
    data_path = "coco8.yaml"
    
    logger.info(f"Running 1 epoch on {data_path} to verify training pipeline...")
    
    results = train(
        data_path=data_path,
        model_name="yolo11n.pt", 
        epochs=1,
        batch=2,
        imgsz=320,
        device="cpu", # Force CPU for smoke test to ensure it runs everywhere
        project="runs/smoke_test",
        name="smoke_run",
        resume=False
    )
    
    logger.info("Smoke test completed successfully!")
    logger.info(f"Metrics (mAP50-95): {results.box.map}")
    logger.info(f"Metrics (mAP50): {results.box.map50}")

if __name__ == "__main__":
    main()
