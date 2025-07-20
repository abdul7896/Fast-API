import locust

class UserBehavior(locust.HttpUser):
    @locust.task
    def test_users_endpoint(self):
        self.client.get("/users")