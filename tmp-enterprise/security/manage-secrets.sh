#!/bin/bash

# Script to manage Kubernetes secrets

echo "Creating secrets for AWS credentials..."
kubectl create secret generic aws-credentials \
  --from-literal=aws-access-key-id=YOUR_ACCESS_KEY_ID \
  --from-literal=aws-secret-access-key=YOUR_SECRET_ACCESS_KEY \
  --namespace=prima-api \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Creating secrets for API keys..."
kubectl create secret generic api-keys \
  --from-literal=api-key=primaGUeeghoMV3wooeJnnmTmSoo6mfMZmjVBPqC3z7T7ydJrmP2Rpelsr4lMXJIZ1dtSWHcqoXli0xjONlrDDZx6CEh0NnP55tZ7SxwoaXAoOPNz8LqnCgzpE4tx5L1uStiwNU7wEeDuhoW2ohXEveg2qjHkPTgMkKvFbbebRWLNGzY1EGaRL2Y1wRnljcZXqbwYeKIib0lJTU7VsIQYnUMms4HgQMx3A8TlSZrDt4CNoEJ0cucoLBZX0s36JHl8dpe0NskukIdq4lUQCgrIHZ77aac4IBccgBOWyVWN61yLJK7TqnmEewHmfon5UEcqiqNHchAm997rkeXWk843r0raMEkU1VmNuXlbwgOVtiwjr1v5WEjuwpOBq9uPQowREmeqRk0NTrTFQFPDuXOY5P3iZfZdcW2h9jH6iW9H7SfZE0A52JBmyY97CybG0vtKEWKetZqTEbFQfWL559rfYIVfrKAIjZXT1yGg8LfeFX3XBhkDIydRoJkXYnQInGx \
  --namespace=prima-api \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Secrets created successfully."