# application/session_manager.py

from typing import Dict
from domain.prompt.pers_chat_service import PersChatService

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, PersChatService] = {}

    def get_or_create_session(self, memberId: str):
        if memberId not in self.sessions:
            self.sessions[memberId] = PersChatService(memberId)
        return self.sessions[memberId]

    def remove_session(self, memberId: str):
        if memberId in self.sessions:
            del self.sessions[memberId]
