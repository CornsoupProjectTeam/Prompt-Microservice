#application/session_manager.py
from typing import Dict
from application.prompt_service import PersChatService



class SessionManager:
    """
    member_id 기준으로 PersChatService 인스턴스를 관리하는 세션 관리자.
    """
    def __init__(self):
        self.sessions: Dict[str, PersChatService] = {}

    def get_or_create_session(self, member_id: str):
        if member_id not in self.sessions:
            self.sessions[member_id] = PersChatService()
        return self.sessions[member_id]

    def remove_session(self, member_id: str):
        if member_id in self.sessions:
            del self.sessions[member_id]

 
