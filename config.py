# -*- coding: utf-8 -*-
"""
[제4연구소] LLM 설정 중앙 관리 모듈 (config.py)
- python-dotenv를 활용하여 루트 경로의 .env 파일을 로드하고, 로컬 LLM API URL을 집중 관리합니다.
"""

import os
from dotenv import load_dotenv

# 💡 [방어적 프로그래밍] 현재 파일이 위치한 루트 디렉터리의 .env 경로를 명시적으로 찾아서 로드합니다.
base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, ".env")

# 기존 환경변수를 오버라이드하여 최신 설정값을 즉시 갱신합니다.
load_dotenv(env_path, override=True)


class Config:
    """로컬 LLM 주소 및 활성화된 엔진 설정을 제공하는 중앙 설정 클래스"""

    LM_STUDIO_URL = os.getenv(
        "LM_STUDIO_URL", "http://127.0.0.1:1234/v1/chat/completions"
    )
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/v1/chat/completions")
    ACTIVE_ENGINE = os.getenv("ACTIVE_ENGINE", "lmstudio")

    @classmethod
    def get_active_url(cls) -> str:
        """
        [동적 라우팅 API]
        - ACTIVE_ENGINE 설정에 따라 최종적으로 호출할 로컬 LLM 주소를 반환합니다.
        - 만약 설정값이 올바르지 않다면 기본값으로 LM Studio URL을 반환하도록 방어적으로 대응합니다.
        """
        engine = (cls.ACTIVE_ENGINE or "lmstudio").lower().strip()
        if engine == "ollama":
            return cls.OLLAMA_URL
        return cls.LM_STUDIO_URL
