from .email import send_email
from .push import send_push


# === Tool Functions ===
def record_user_details(email, phone, notes=""):
    send_push(f"Recording user: Email: {email} | Phone: {phone} | Notes: {notes}")
    send_email(f"Recording user: Email: {email} | Phone: {phone} | Notes: {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    send_push(f"Unanswered question recorded: {question}")
    send_email(f"Unanswered question recorded: {question}")
    return {"recorded": "ok"}