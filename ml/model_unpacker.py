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
DEST_PREFIX = "models"  # Base path in S3

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
        
        for model_name in os.listdir(extract_dir):
            model_dir = os.path.join(extract_dir, model_name)
            if not os.path.isdir(model_dir):
                continue
        
            print(f"📁 Processing model: {model_name}")


            for file in os.listdir(model_dir):
                local_path = os.path.join(model_dir, file)

                # Upload models by filename convention
                if file.endswith((".pkl", ".keras")):
                    try:
                        s3_key = f"{DEST_PREFIX}/{model_name}/{file}"
                        print(f"⬆️ Uploading {file} to s3://{BUCKET}/{s3_key}")
                        s3.upload_file(local_path, BUCKET, s3_key)
                    except Exception as e:
                        print(f"⚠️ Skipping {file}: {e}")

                # Also upload any accuracy.json files found
                elif file == "accuracy.json":
                    s3_key = f"{DEST_PREFIX}/{model_name}/accuracy.json"
                    print(f"📤 Uploading per-ticker accuracy for {model_name} to s3://{BUCKET}/{s3_key}")
                    s3.upload_file(local_path, BUCKET, s3_key)

        print("✅ Done extracting and uploading model files.")

if __name__ == "__main__":
    extract_and_upload()