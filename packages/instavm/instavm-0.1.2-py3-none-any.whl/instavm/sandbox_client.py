import requests
class InstaVM:
    def __init__(self, api_key=None, base_url="http://api.instavm.io"):
        self.base_url = base_url
        self.api_key = api_key
        self.session_id = None

        if self.api_key:
            self.start_session()

    def start_session(self):
        if not self.api_key:
            raise ValueError("API key not set. Please provide an API key or create one first.")
        url = f"{self.base_url}/session"
        data = {"api_key": self.api_key}
        response = requests.post(url, json=data)
        response.raise_for_status()
        self.session_id = response.json().get("session_id")
        return self.session_id

    def execute(self, command):
        if not self.session_id:
            raise ValueError("Session ID not set. Please start a session first.")
        url = f"{self.base_url}/execute"
        data = {
            "command": command,
            "api_key": self.api_key,
            "session_id": self.session_id,
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def get_usage(self):
        if not self.session_id:
            raise ValueError("Session ID not set. Please start a session first.")
        url = f"{self.base_url}/usage/{self.session_id}"
        response = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"})
        response.raise_for_status()
        return response.json()

    def upload_file(self, file_path):
        if not self.session_id:
            raise ValueError("Session ID not set. Please start a session first.")

        url = f"{self.base_url}/upload/"
        with open(file_path, 'rb') as file:
            files = {'file': file}
            data = {
                "api_key": self.api_key,
                "session_id": self.session_id,
            }
            response = requests.post(url, data=data, files=files)

        response.raise_for_status()
        return response.json()