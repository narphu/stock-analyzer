# sagemaker_model_unpacker.py
# This script extracts individual .pkl model files from a SageMaker training job output (.tar.gz)
# and uploads them to a flat S3 structure so the FastAPI backend can load them directly

import boto3
import os
import tarfile
import tempfile

BUCKET = "shrubb-ai-ml-models"
JOB_NAME = os.getenv("SM_JOB_NAME")  # Or pass directly
SOURCE_KEY = f"models/{JOB_NAME}/output/model.tar.gz"
DEST_PREFIX = "models/"  # final destination for .pkl files

s3 = boto3.client("s3")

def extract_and_upload():
    with tempfile.TemporaryDirectory() as tmp:
        tar_path = os.path.join(tmp, "model.tar.gz")
        extract_dir = os.path.join(tmp, "extracted")
        os.makedirs(extract_dir, exist_ok=True)

        print(f"⬇️ Downloading s3://{BUCKET}/{SOURCE_KEY}")
        s3.download_file(BUCKET, SOURCE_KEY, tar_path)

        print("📦 Extracting model.tar.gz")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=extract_dir)

        for file in os.listdir(extract_dir):
            if file.endswith("_prophet.pkl"):
                local_path = os.path.join(extract_dir, file)
                s3_path = f"{DEST_PREFIX}{file}"

                print(f"⬆️ Uploading {file} to s3://{BUCKET}/{s3_path}")
                s3.upload_file(local_path, BUCKET, s3_path)

        print("✅ Done extracting and uploading Prophet model files.")

if __name__ == "__main__":
    extract_and_upload()
