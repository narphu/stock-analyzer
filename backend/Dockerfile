FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirement file and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of your backend code
COPY . .

# Expose port and run server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]