# -*- coding: utf-8 -*-
"""
로컬 지식(RAG) 로더 모듈
- 이전 프로젝트(루나과제) 폴더의 스크립트와 가이드라인을 읽어 LLM 프롬프트에 주입합니다.
"""

import os

# 대표님이 지정한 로컬 지식 절대 경로
KNOWLEDGE_DIR = r"C:\1인기업\Apps\0312라이브_자동화 루나과제\로컬지식"


def load_local_knowledge(channel_key: str = None) -> str:
    """로컬 지식 폴더에서 파이프라인 및 가이드 문서를 읽어 RAG 컨텍스트로 반환합니다."""
    knowledge_text = "\n\n=== [로컬 지식 기반 훈련 데이터 (참고용)] ===\n"
    knowledge_text += "아래는 기존에 성공적으로 작동했던 영상 제작 파이프라인 파이썬 코드 및 설정입니다. 기획 시 이 방식과 느낌을 적극 참고하여 우리만의 채널 고유의 스타일을 유지하세요.\n\n"

    # 핵심 파이프라인 스크립트 로드
    files_to_read = ["produce_rubia_lofi_v2.py", "produce_aura_masterpiece_v1.py"]

    loaded_count = 0
    for filename in files_to_read:
        filepath = os.path.join(KNOWLEDGE_DIR, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    # 너무 길면 토큰 제한을 넘을 수 있으므로 핵심만 추출 (앞부분 3000자)
                    truncated = (
                        content[:3000] + "\n...[이하 생략]..."
                        if len(content) > 3000
                        else content
                    )
                    knowledge_text += f"\n--- 파일명: {filename} ---\n{truncated}\n"
                    loaded_count += 1
            except Exception:
                pass

    if loaded_count == 0:
        return ""  # 로드된 지식이 없으면 빈 문자열 반환

    return knowledge_text
