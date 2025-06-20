import os
import boto3
import joblib
from functools import lru_cache


USE_LOCAL = os.getenv("USE_LOCAL_MODELS", "false").lower() == "true"
LOCAL_MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
S3_BUCKET = "shrubb-ai-ml-models"
S3_PREFIX = "models"
S3_CACHE_DIR = "/tmp/prophet_models"
os.makedirs(S3_CACHE_DIR, exist_ok=True)

s3 = boto3.client("s3")


def get_local_model_path(ticker: str) -> str:
    return os.path.join(LOCAL_MODEL_DIR, f"{ticker}_prophet.pkl")

def get_cached_s3_model_path(ticker: str) -> str:
    return os.path.join(S3_CACHE_DIR, f"{ticker}_prophet.pkl")


def download_model_from_s3(ticker: str) -> str:
    local_path = get_cached_s3_model_path(ticker)
    if os.path.exists(local_path):
        return local_path

    key = f"{S3_PREFIX}/{ticker}_prophet.pkl"
    print(f"📦 Downloading model from s3://{S3_BUCKET}/{key}")
    s3.download_file(S3_BUCKET, key, local_path)
    return local_path


@lru_cache(maxsize=128)
def load_model(ticker: str):
    ticker = ticker.upper()
    if USE_LOCAL:
        path = get_local_model_path(ticker)
        print(f"📂 Loading model from local path: {path}")
    else:
        path = download_model_from_s3(ticker)
    return joblib.load(path)
