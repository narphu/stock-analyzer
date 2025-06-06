FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install fastapi uvicorn scikit-learn pandas
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]