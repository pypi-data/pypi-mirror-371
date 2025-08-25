import requests
from pathlib import Path

class EmbeddingResponse:
    def __init__(self, embedding):
        self.embedding = embedding

class Ambade:
    def __init__(self, api_key=None, base_url="https://embed-test-1.onrender.com"):
        self.api_key = api_key
        self.base_url = base_url

    def embed(self, model: str, input_data: str):
        if Path(input_data).is_file():
            with open(input_data, "rb") as f:
                files = {"file": (Path(input_data).name, f)}
                data = {"model": model}
                resp = requests.post(f"{self.base_url}/embed", data=data, files=files)
        else:
            data = {"model": model, "input_text": input_data}
            resp = requests.post(f"{self.base_url}/embed", data=data)

        resp.raise_for_status()
        return EmbeddingResponse(resp.json()["embedding"])
