# tests/test_performance.py
from locust import HttpUser, task

class FastAPIUser(HttpUser):
    wait_time = lambda self: 0.1

    @task
    def get_users(self):
        self.client.get("/users")

    @task(3)
    def create_user(self):
        self.client.post("/user", json={"email": "test@example.com", "name": "Test User"}, headers={"X-API-Key": "primaGUeeghoMV3wooeJnnmTmSoo6mfMZmjVBPqC3z7T7ydJrmP2Rpelsr4lMXJIZ1dtSWHcqoXli0xjONlrDDZx6CEh0NnP55tZ7SxwoaXAoOPNz8LqnCgzpE4tx5L1uStiwNU7wEeDuhoW2ohXEveg2qjHkPTgMkKvFbbebRWLNGzY1EGaRL2Y1wRnljcZXqbwYeKIib0lJTU7VsIQYnUMms4HgQMx3A8TlSZrDt4CNoEJ0cucoLBZX0s36JHl8dpe0NskukIdq4lUQCgrIHZ77aac4IBccgBOWyVWN61yLJK7TqnmEewHmfon5UEcqiqNHchAm997rkeXWk843r0raMEkU1VmNuXlbwgOVtiwjr1v5WEjuwpOBq9uPQowREmeqRk0NTrTFQFPDuXOY5P3iZfZdcW2h9jH6iW9H7SfZE0A52JBmyY97CybG0vtKEWKetZqTEbFQfWL559rfYIVfrKAIjZXT1yGg8LfeFX3XBhkDIydRoJkXYnQInGx
