FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc build-essential curl gnupg \
    libxml2-dev libxslt1-dev libcurl4-openssl-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Prophet and other Python libs
# Add requirements and install them
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Add training script
COPY train_model.py /opt/ml/code/train_model.py

# SageMaker expects this entrypoint
ENV SAGEMAKER_PROGRAM=train_model.py
