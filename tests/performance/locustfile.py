from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 2.5) # Users wait between 1 and 2.5 seconds between tasks

    host = "http://localhost:8000" # Default host for the FastAPI backend

    _access_token = None

    def on_start(self):
        """ on_start is called once per user when the user starts running """
        self.login()

    def login(self):
        response = self.client.post("/token", data={"username": "testuser", "password": "testpassword"})
        if response.status_code == 200:
            self._access_token = response.json()["access_token"]
            self.client.headers = {"Authorization": f"Bearer {self._access_token}"}
            print(f"Logged in successfully, token: {self._access_token}")
        else:
            print(f"Login failed: {response.text}")
            self._access_token = None

    @task(3) # This task will be executed 3 times more often than other tasks
    def discover_item(self):
        if self._access_token:
            # Example URL to discover - replace with a real URL for testing
            test_url = "https://www.example.com/silver-item" 
            self.client.post(f"/discover/?url={test_url}", name="/discover/[url]")
        else:
            print("Cannot perform discovery, not logged in.")
            self.login() # Try to log in again if token is missing

    @task(1)
    def get_root(self):
        self.client.get("/")

    # Add more tasks to simulate other API calls
    # @task(1)
    # def geocode_address(self):
    #     if self._access_token:
    #         self.client.post("/logistics/geocode/", json={"address": "123 Main St"}, name="/logistics/geocode/")

    # @task(1)
    # def calculate_roi(self):
    #     if self._access_token:
    #         self.client.post("/valuation/calculate_roi/", json={"weight_grams": 100, "purity": 0.925, "purchase_price": 50}, name="/valuation/calculate_roi/")
