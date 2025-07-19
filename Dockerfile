FROM python:3.9-slim

WORKDIR /app

# Install dependencies (including python-dotenv for .env support)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code (including .env for local dev, but ensure it's .dockerignore'd in prod)
COPY . .

# Run the API (use .env if present, else rely on runtime env vars)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]