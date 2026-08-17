# SIDS AI Team Onboarding Guide

Welcome to the AI Subsystem for the SIDS (Smart Insect Detection System) project! 

Because Machine Learning models and datasets are extremely large (often gigabytes in size), we **do not** commit them to the Git repository. If we did, the repository would be too slow to clone and would violate GitHub's file size limits. 

Instead, we use a standard **MLOps Workflow**. When you clone this repository for the first time, follow the steps below to fetch the data and trained models locally.

---

## 1. Setup Your Virtual Environment
First, ensure you have your Python virtual environment activated and dependencies installed:
```bash
# Activate the virtual environment
source .venv/Scripts/activate  # On Windows

# Install the required packages
pip install -r requirements.txt
pip install gdown  # Used for downloading the model from Google Drive
```

## 2. Download the Datasets (Images)
Instead of downloading thousands of images from Git, we fetch them directly from their official sources to ensure everyone has a pristine copy.
```bash
# From the FinalYearProject root directory, run:
python -m ml.scripts.download.downloader
```
This script will automatically download the dataset (e.g., PlantVillage) and place the images into your local `ml/datasets/` folder.

## 3. Download the Trained AI Model
Our trained AI model (`best_model.pth`) is securely hosted on Google Drive. To download it and verify its cryptographic integrity against our Model Registry, run:
```bash
python -m ml.scripts.download.download_model
```
This script will:
1. Download the `best_model.pth` from Google Drive.
2. Place it in `ml/exports/classification_v1/`.
3. Read our local `sids-disease-classifier-0.1.0.json` manifest.
4. Calculate the SHA256 hash of the downloaded model to mathematically guarantee the file wasn't corrupted or tampered with.

## 4. You're Ready!
You now have the exact same datasets and trained models as the rest of the team! You can now run the FastAPI server or continue developing the AI pipeline.
