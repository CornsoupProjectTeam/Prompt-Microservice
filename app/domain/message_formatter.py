def format_response(user_id, session_id, message):
    return {
        "user_id": user_id,
        "session_id": session_id,
        "message": message,
        "status": "responded"
    }