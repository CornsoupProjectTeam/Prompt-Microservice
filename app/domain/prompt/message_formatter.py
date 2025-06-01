# domain/message_formatter.py

def format_response(memberId, message):
    return {
        "memberId": memberId,
        "message": message,
        "status": "responded"
    }
