import os
import json
import hashlib
import sys
try:
    import gdown
except ImportError:
    print("Error: 'gdown' is not installed. Please run: pip install gdown")
    sys.exit(1)

# --- CONFIGURATION ---
# TODO for the Admin: Upload `best_model.pth` to Google Drive, right click -> Get Link, 
# and extract the file ID from the URL (the random string of characters).
GOOGLE_DRIVE_FILE_ID = "1FB19HciYe4cRbXu6z_lY4EpM-hWr4zMr"
MODEL_EXPORT_DIR = "ml/exports/classification_v1"
MANIFEST_PATH = "ml/model-registry/manifests/sids-disease-classifier-0.1.0.json"
MODEL_FILENAME = "best_model.pth"

def calculate_sha256(filepath):
    """Calculates the SHA256 hash of a file to guarantee it wasn't corrupted."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read in chunks for memory efficiency
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_against_manifest(filepath, manifest_path, target_filename):
    if not os.path.exists(manifest_path):
        print(f"[-] Manifest {manifest_path} not found! Cannot verify integrity.")
        return False
        
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
        
    expected_hash = None
    for artifact in manifest.get("artifacts", []):
        if artifact.get("file_name") == target_filename:
            expected_hash = artifact.get("sha256")
            break
            
    if not expected_hash:
        print(f"[-] Could not find '{target_filename}' in manifest!")
        return False
        
    print(f"[*] Calculating SHA256 hash of downloaded model... (This may take a few seconds)")
    actual_hash = calculate_sha256(filepath)
    
    if actual_hash.lower() == expected_hash.lower():
        print(f"[+] SUCCESS: Integrity Verified! Hash matches manifest: {actual_hash}")
        return True
    else:
        print(f"[-] ERROR: Hash mismatch!")
        print(f"    Expected: {expected_hash}")
        print(f"    Got:      {actual_hash}")
        return False

def main():
    if GOOGLE_DRIVE_FILE_ID == "YOUR_GOOGLE_DRIVE_FILE_ID_HERE":
        print("[-] Error: GOOGLE_DRIVE_FILE_ID is not configured in this script.")
        print("    Please upload the model to Google Drive and paste the File ID into ml/scripts/download/download_model.py")
        sys.exit(1)

    os.makedirs(MODEL_EXPORT_DIR, exist_ok=True)
    destination_path = os.path.join(MODEL_EXPORT_DIR, MODEL_FILENAME)
    
    if os.path.exists(destination_path):
        print(f"[*] Model already exists at {destination_path}. Verifying integrity...")
        if verify_against_manifest(destination_path, MANIFEST_PATH, MODEL_FILENAME):
            print("[+] Model is already downloaded and verified. Exiting.")
            sys.exit(0)
        else:
            print("[*] Existing model failed verification. Re-downloading...")
            os.remove(destination_path)

    print(f"[*] Downloading {MODEL_FILENAME} from Google Drive...")
    # gdown URL format for a file ID
    gdrive_url = f"https://drive.google.com/uc?id={GOOGLE_DRIVE_FILE_ID}"
    gdown.download(gdrive_url, destination_path, quiet=False)

    if not os.path.exists(destination_path):
        print("[-] Error: Download failed.")
        sys.exit(1)

    verify_against_manifest(destination_path, MANIFEST_PATH, MODEL_FILENAME)

if __name__ == "__main__":
    main()
