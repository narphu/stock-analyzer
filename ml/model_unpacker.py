# sagemaker_model_unpacker.py
# Extracts model.tar.gz from SageMaker output and uploads individual models by type to S3

import boto3
import os
import tarfile
import tempfile
import json

BUCKET = "shrubb-ai-ml-models"
JOB_NAME = os.getenv("SM_JOB_NAME")  # e.g., stock-analyzer-20240623
SOURCE_KEY = f"models/{JOB_NAME}/output/model.tar.gz"
DEST_PREFIX = "models/"  # Base path in S3

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
            local_path = os.path.join(extract_dir, file)

            # Upload models by filename convention
            if file.endswith((".pkl", ".h5")) and "_" in file:
                try:
                    ticker, model_ext = file.rsplit("_", 1)
                    model_name = model_ext.replace(".pkl", "").replace(".h5", "")
                    dest_key = f"{DEST_PREFIX}{model_name}/{ticker}.{model_ext.split('.')[-1]}"
                    print(f"⬆️ Uploading {file} to s3://{BUCKET}/{dest_key}")
                    s3.upload_file(local_path, BUCKET, dest_key)
                except Exception as e:
                    print(f"⚠️ Skipping {file}: {e}")

            # Also upload any accuracy.json files found
            elif file == "accuracy.json":
                s3_key = f"{DEST_PREFIX}/{model_name}/accuracy.json"
                print(f"📤 Uploading per-ticker accuracy for {model_name} to s3://{BUCKET}/{s3_key}")
                s3.upload_file(file, BUCKET, s3_key)

        print("✅ Done extracting and uploading model files.")

if __name__ == "__main__":
    extract_and_upload()