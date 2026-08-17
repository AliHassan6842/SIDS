import argparse

from downloader import download_dataset

# Dataset Configurations
DATASETS = {
    "ip102": {
        "name": "IP102",
        "description": "A Large-Scale Benchmark Dataset for Insect Pest Recognition",
        "url": None, # Requires manual acceptance/login from standard repositories
        "status": "MANUAL_ACQUISITION_REQUIRED",
        "instructions": "IP102 requires manual download from its official repository due to license acceptance. Download the ZIP file and place it in ml/datasets/ip102/",
    },
    "paddy_doctor": {
        "name": "Paddy Doctor",
        "description": "Paddy Disease Classification Dataset",
        "url": None, # Kaggle dataset, needs API or manual
        "status": "MANUAL_ACQUISITION_REQUIRED",
        "instructions": "Paddy Doctor is hosted on Kaggle. Use `kaggle competitions download -c paddy-disease-classification` and place in ml/datasets/paddy_doctor/",
    },
    "plantdoc": {
        "name": "PlantDoc",
        "description": "A Dataset for Visual Plant Disease Detection",
        "url": None,
        "status": "MANUAL_ACQUISITION_REQUIRED",
        "instructions": "PlantDoc requires manual acquisition from GitHub/Roboflow. Extract to ml/datasets/plantdoc/",
    },
    "plantvillage": {
        "name": "PlantVillage",
        "description": "Plant disease classification dataset",
        "url": None,
        "status": "MANUAL_ACQUISITION_REQUIRED",
        "instructions": "PlantVillage is hosted on Kaggle. Use `kaggle datasets download -d emmarex/plantdisease` and place in ml/datasets/plantvillage/"
    },
    "bollwm": {
        "name": "BOLLWM",
        "description": "Bollworm Dataset",
        "url": None,
        "status": "MANUAL_ACQUISITION_REQUIRED",
        "instructions": "BOLLWM is private or requires manual access. Extract to ml/datasets/bollwm/"
    }
}

def get_dataset(dataset_id: str, dest_dir: str):
    if dataset_id not in DATASETS:
        print(f"Unknown dataset: {dataset_id}")
        return
        
    config = DATASETS[dataset_id]
    if config["status"] == "MANUAL_ACQUISITION_REQUIRED":
        print(f"[{config['name']}] MANUAL ACQUISITION REQUIRED")
        print(config["instructions"])
        return
        
    if config["status"] == "AUTO_DOWNLOADABLE":
        print(f"Starting automatic download for {config['name']}...")
        download_dataset(
            url=config["url"],
            dest_dir=dest_dir,
            expected_sha256=config.get("sha256")
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download configured datasets.")
    parser.add_argument("--dataset", required=True, choices=list(DATASETS.keys()), help="Dataset ID to download")
    parser.add_argument("--dest", default="ml/datasets/", help="Destination directory")
    args = parser.parse_args()
    
    get_dataset(args.dataset, args.dest)
