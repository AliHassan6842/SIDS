import os
import zipfile
import sys
import subprocess

try:
    import gdown
except ImportError:
    print("Error: 'gdown' is not installed. Installing it now...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown"])
    import gdown

# Google Drive File IDs
DATASET_COCO_ID = "1LMic0y-og1eV_Owi3mIhf8sDubmkgZzi"
BEST_PT_ID = "12oRbWkLy1sW_B8_dQ1oMVlp7D0rv4tNp"
BEST_MODEL_PTH_ID = "1FB19HciYe4cRbXu6z_lY4EpM-hWr4zMr"

# Define destination directories (relative to project root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
MODEL_REGISTRY_DIR = os.path.join(PROJECT_ROOT, "ml", "model-registry")
DATASETS_DIR = os.path.join(PROJECT_ROOT, "ml", "datasets")

os.makedirs(MODEL_REGISTRY_DIR, exist_ok=True)
os.makedirs(DATASETS_DIR, exist_ok=True)

def download_from_drive(file_id, dest_path):
    print(f"[*] Downloading to {dest_path}...")
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, dest_path, quiet=False)
    print(f"[+] Download complete: {dest_path}\n")

def main():
    print("=== SIDS AI Asset Downloader ===\n")
    
    # 1. Download Pest Detection Model (best.pt)
    best_pt_path = os.path.join(MODEL_REGISTRY_DIR, "best.pt")
    if not os.path.exists(best_pt_path):
        print("Fetching Pest Detection Model (YOLO)...")
        download_from_drive(BEST_PT_ID, best_pt_path)
    else:
        print(f"[✓] best.pt already exists at {best_pt_path}")

    # 2. Download Disease Classification Model (best_model.pth)
    best_model_path = os.path.join(MODEL_REGISTRY_DIR, "best_model.pth")
    if not os.path.exists(best_model_path):
        print("Fetching Disease Classification Model (PyTorch)...")
        download_from_drive(BEST_MODEL_PTH_ID, best_model_path)
    else:
        print(f"[✓] best_model.pth already exists at {best_model_path}")

    # 3. Download and Extract Datasets (datasets.zip)
    dataset_zip_path = os.path.join(DATASETS_DIR, "datasets.zip")
    if not os.path.exists(dataset_zip_path):
        print("Fetching Training Datasets...")
        download_from_drive(DATASET_COCO_ID, dataset_zip_path)
        
        # Extract the ZIP
        print(f"[*] Extracting {dataset_zip_path}...")
        with zipfile.ZipFile(dataset_zip_path, 'r') as zip_ref:
            zip_ref.extractall(DATASETS_DIR)
        print(f"[+] Extraction complete to {DATASETS_DIR}\n")
    else:
        print(f"[✓] datasets.zip already exists at {dataset_zip_path}")
        
    print("=== All Assets Successfully Synced! ===")

if __name__ == "__main__":
    main()
