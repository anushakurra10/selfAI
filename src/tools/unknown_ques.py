record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Record any question that couldn't be answered.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "Unanswered question"}
        },
        "required": ["question"],
        "additionalProperties": False
    }
}