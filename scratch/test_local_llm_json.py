# -*- coding: utf-8 -*-
"""
로컬 LLM JSON 구조화 변환 엔진 및 폴백, 상태 전이 시뮬레이션 테스트 스크립트
"""

import sys
import os
import json
import logging

# 프로젝트 루트 디렉터리를 sys.path에 추가하여 telegram_bot 및 api 모듈 로드 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

from pydantic import BaseModel, Field
from typing import List

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestLocalLLM")


# 테스트용 구조화 스키마 모델 정의
class TestTrack(BaseModel):
    title: str = Field(description="음악 트랙 제목")
    duration: int = Field(description="트랙 길이 (초)")


class TestPlanning(BaseModel):
    concept: str = Field(description="영상 기획 컨셉 요약")
    playlist: List[TestTrack] = Field(description="플레이리스트 구성안")
    tags: List[str] = Field(description="해시태그 리스트")


def run_tests():
    # ─────────────────────────────────────────────
    # 🧪 테스트 1: 로컬 LLM JSON 구조화 및 폴백 엔진 검증
    # ─────────────────────────────────────────────
    logger.info("🧪 [테스트 1] generate_structured_json 실행 (로컬 모드 시도)")

    from telegram_bot.engine.llm_client import generate_structured_json

    prompt = "대만의 타이페이 밤거리를 배경으로 하는 감성적인 로파이 비디오 기획해줘. 음악 트랙은 2개로 해줘."
    system_instruction = "당신은 영상 기획자입니다. 요청된 포맷의 JSON 데이터만 출력해야 합니다."

    # 로컬 LLM(Ollama 등)이 켜져 있지 않아도 자동으로 Gemini API로 폴백되는지 검증하기 위해 mode="local"로 호출
    # 로컬에 Ollama가 없더라도 Exception이 발생하고, log.error에 [JSON_PARSE_FAILED]가 찍힌 후 Gemini로 복구되어야 합니다.
    try:
        result = generate_structured_json(
            prompt=prompt,
            system_instruction=system_instruction,
            response_schema=TestPlanning,
            mode="local",
            # 💡 [한글 설명] 하드코딩된 API 주소 대신 중앙 Config의 OLLAMA_URL을 참조합니다.
            local_url=Config.OLLAMA_URL,
        )
        logger.info(
            f"✅ [테스트 1 성공] 구조화 JSON 데이터 반환 완료:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
        )
    except Exception as e:
        logger.error(f"❌ [테스트 1 실패] 최종 구조화 데이터 획득 실패: {e}")

    # ─────────────────────────────────────────────
    # 🧪 테스트 2: State Machine 규칙 및 VOID Transition 차단 시뮬레이션
    # ─────────────────────────────────────────────
    logger.info("\n🧪 [테스트 2] Funnel State Machine 전이 시뮬레이션 테스트")

    from api.state_machine_service import STATE_MACHINE_RULES, void_transition_failure

    # 2-1. 정상적인 전이 시나리오 시뮬레이션 (Auto-Pipeline 5단계)
    # INPUT ➔ LOCAL_LLM_RUNNING ➔ JSON_PARSE_SUCCESS ➔ RENDERING
    current_state = "INPUT"
    allowed = STATE_MACHINE_RULES.get(current_state, {})

    logger.info(f"현재 상태: {current_state} | 허용된 다음 상태: {list(allowed.keys())}")

    # 로컬 LLM 작동 상태로 전이 시도
    next_state = "LOCAL_LLM_RUNNING"
    if next_state in allowed:
        logger.info(
            f"✅ [정상] '{current_state}'에서 '{next_state}'로의 전이가 허용됩니다. ({allowed[next_state]})"
        )
    else:
        logger.error(f"❌ [에러] '{current_state}'에서 '{next_state}'로 전이할 수 없습니다.")

    # 2-2. 비정상 전이 차단 및 ERROR_4001_VOID 예외 발생 검증
    # INPUT에서 바로 REVIEW로 건너뛰는 것은 불가능함 (중간 렌더링 누락 차단)
    invalid_next_state = "REVIEW"
    logger.info(f"⚠️ [비정상 전이 시도] '{current_state}' -> '{invalid_next_state}' 강제 테스트")
    try:
        if invalid_next_state not in allowed:
            void_transition_failure(
                current_state=current_state,
                next_state=invalid_next_state,
                payload={"video_id": "test_001"},
                reason="렌더링(RENDERING) 단계를 거치지 않고 검수(REVIEW) 단계로 직접 전이할 수 없습니다.",
            )
        else:
            logger.error("❌ [오동작] 비정상 전이가 필터링되지 않고 허용되었습니다.")
    except Exception as void_err:
        logger.info(f"✅ [정상 차단 완료] void_transition_failure 작동 성공. 예외 메시지:\n{void_err}")


if __name__ == "__main__":
    run_tests()
