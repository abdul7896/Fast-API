FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole app folder into /app/app
COPY app app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
