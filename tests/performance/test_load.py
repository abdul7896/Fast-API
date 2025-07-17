from locust import HttpUser, task, between
import random
import string

def random_email():
    return f"{''.join(random.choices(string.ascii_lowercase, k=8))}@example.com"

class LoadTest(HttpUser):
    # Set your FastAPI app URL here
    host = "http://localhost:8000"  # Make sure your app is running at this port

    wait_time = between(0.1, 0.5)

    @task
    def create_user(self):
        self.client.post("/user", json={
            "email": random_email(),
            "name": "Performance User"
        })

    @task(3)
    def get_users(self):
        self.client.get("/users")
