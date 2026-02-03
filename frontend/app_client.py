import requests
from typing import List, Dict


class MedicalChatAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def send_message(
        self,
        message: str,
        history: List[Dict[str, str]],
    ) -> Dict:
        payload = {
            "message": message,
            "history": history,
        }

        response = requests.post(
            f"{self.base_url}/api/v1/chat/query",
            json=payload,
            timeout=60,
        )

        response.raise_for_status()
        return response.json()
