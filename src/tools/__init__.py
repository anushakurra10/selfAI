from .user_details import record_user_details_json
from .unknown_ques import  record_unknown_question_json

# Expose a unified TOOLS list for OpenAI
TOOLS = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
]

__all__ = [
     "record_user_details_json",
     "record_unknown_question_json"
]