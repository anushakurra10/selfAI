import requests
from datetime import datetime
import os

def send_push(message: str):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"[{timestamp}] {message}"
    try:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": os.getenv("PUSHOVER_TOKEN"),
                "user": os.getenv("PUSHOVER_USER"),
                "message": message,
            }, timeout=6
        )
    except Exception as err:
        print("Don't crash UI if push fails",err);
        # Don't crash UI if push fails
        pass


