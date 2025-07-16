FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ ./

ENV AWS_REGION=us-east-1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

