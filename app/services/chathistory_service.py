import os
import json

class ChatHistoryService:
    def __init__(self, archive_file: str = None):
        # 기본 경로 설정
        if archive_file is None:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
            archive_file = os.path.join(base_path, "chat_archive.json")

        self.archive_file = archive_file

        # 파일 초기화 (덮어쓰기)
        with open(self.archive_file, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    def save(self, user_input: str, bot_response: str):
        with open(self.archive_file, "r+", encoding="utf-8") as f:
            archive = json.load(f)
            archive.append({
                "user": user_input,
                "bot": bot_response
            })
            f.seek(0)
            json.dump(archive, f, ensure_ascii=False, indent=2)
            f.truncate()
