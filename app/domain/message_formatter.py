def format_response(memberId, session_id, message):
    return {
        "memberId": memberId,
        "session_id": session_id,
        "message": message,
        "status": "responded"
    }