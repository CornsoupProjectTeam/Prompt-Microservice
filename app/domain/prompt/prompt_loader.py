# domain/prompt/prompt_loader.py

import json
from pathlib import Path

class PromptLoader:
    _support_prompts_cache = None
    _direct_prompts_cache = None
    _pers_prompt_cache = None

    BASE_DIR = Path(__file__).resolve().parent

    @staticmethod
    def load_support_prompts() -> dict:
        if PromptLoader._support_prompts_cache is None:
            file_path = PromptLoader.BASE_DIR / "support_prompts.json"
            with open(file_path, "r", encoding="utf-8") as f:
                PromptLoader._support_prompts_cache = json.load(f)
        return PromptLoader._support_prompts_cache

    @staticmethod
    def load_direct_prompts() -> dict:
        if PromptLoader._direct_prompts_cache is None:
            file_path = PromptLoader.BASE_DIR / "direct_question_prompts.json"
            with open(file_path, "r", encoding="utf-8") as f:
                PromptLoader._direct_prompts_cache = json.load(f)
        return PromptLoader._direct_prompts_cache

    @staticmethod
    def load_pers_prompts() -> dict:
        if PromptLoader._pers_prompt_cache is None:
            file_path = PromptLoader.BASE_DIR / "pers_prompt.json"
            with open(file_path, "r", encoding="utf-8") as f:
                PromptLoader._pers_prompt_cache = json.load(f)
        return PromptLoader._pers_prompt_cache
