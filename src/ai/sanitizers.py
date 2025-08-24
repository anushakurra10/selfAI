import re

BLOCKED_PHRASES = {
    "If you’re open to connecting further, feel free to share your email or phone number, and I’ll reach out to you.🙂",
}

def clean_reply(text: str) -> str:
    if not text:
        return text
    for p in BLOCKED_PHRASES:
        if p in text:
            text = text.replace(p, "")
    # Hide internal tool names from user-visible text
    text = re.sub(r"record_user_details|record_unknown_question", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s{2,}", " ", text).strip()
