import requests
import re
from datetime import datetime

def handle_exception(self, e):
        print("Error in chat function:", e)
        
        # If we don't have contact recorded yet, ask the UI to open the form
        if not self.details_recorded:
            self.error_contact = True

        if isinstance(e, requests.exceptions.Timeout):
            return "⏱️ Server timeout. Please try again later."

        if isinstance(e, requests.exceptions.ConnectionError):
            return "🔌 I’m having trouble connecting. Please try again later."

        try:
            error_message = e.args[0]
            match = re.search(r"'X-RateLimit-Reset': '(\d+)'", error_message)
            if match:
                reset_ts = int(match.group(1)) / 1000
                reset_time = datetime.fromtimestamp(reset_ts).strftime("%Y-%m-%d %H:%M:%S")
                return (
                    f"🚫 I’m on a break. Please be back after {reset_time}."
                )
        except Exception:
            pass

        return "⚠️ Something went wrong. Please try again later."