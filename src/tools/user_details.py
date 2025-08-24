record_user_details_json = {
    "name": "record_user_details",
    "description": "Record an interested user's contact information.",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "User's email address"},
            "phone": {"type": "string", "description": "User's phone number"},
            "notes": {"type": "string", "description": "Additional context"}
        },
        "required": ["email", "phone"],
        "additionalProperties": False
    }
}