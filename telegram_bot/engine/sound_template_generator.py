# -*- coding: utf-8 -*-
"""
음원연구소 (Sound Lab) 템플릿 생성기
- 로컬 LLM(Ollama)과 RAG 지식을 결합하여 독창적인 사운드 프롬프트를 자동 생성합니다.
- 외부 API 호출 비용 없이 100개 이상의 시즌별 템플릿을 생성하여 DB에 누적합니다.
"""

import os
import json
import logging
from datetime import datetime

# 로컬 패키지 임포트
try:
    from telegram_bot.engine.sound_lab_knowledge import get_rag_context
    from telegram_bot.engine.llm_client import generate_text
except ImportError:
    import sys

    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    )
    from telegram_bot.engine.sound_lab_knowledge import get_rag_context
    from telegram_bot.engine.llm_client import generate_text

logger = logging.getLogger("SoundTemplateGenerator")

DB_PATH = r"c:\1인기업\Apps\유튜브에이전트\database\sound_templates.json"


def load_sound_templates():
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_sound_templates(templates):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(templates, f, indent=4, ensure_ascii=False)


def generate_daily_templates(channel_key: str, count: int = 3):
    """
    일일 점진적 축적 방식:
    로컬 LLM을 호출하여 한 번에 3~5개 정도의 소량 템플릿을 생성하고 DB에 추가합니다.
    이 함수는 아침 브리핑 전에 호출됩니다.
    """
    rag_context = get_rag_context(channel_key)

    system_instruction = (
        "당신은 루비아 기술연구소 부설 '음원연구소(Sound Lab)'의 수석 기획자 '라비아'입니다.\n"
        "제공된 지식 베이스(RAG)를 바탕으로, 최고 수준의 AI 음악 생성기(Lyria 3 Pro 등)에 주입할 '오디오 프롬프트 템플릿'을 기획하십시오.\n"
        f"반드시 {count}개의 독창적인 템플릿을 배열(Array) 형태의 순수 JSON으로만 출력해야 합니다. 마크다운 기호(```json 등)는 쓰지 마세요.\n\n"
        "[출력 JSON 스키마]\n"
        "[\n"
        "  {\n"
        '    "title": "템플릿의 매력적인 제목 (예: 새벽 3시의 타이베이 골목)",\n'
        '    "channel": "rubia 또는 aura 등 타겟 채널",\n'
        '    "prompt": "영어로 작성된 완벽한 오디오 생성 프롬프트 (BPM, 악기, 분위기 포함)"\n'
        "  }\n"
        "]"
    )

    # 5점 만점인 성공 사례(Success Cases) 동적 주입
    db = load_sound_templates()
    success_cases = [
        t for t in db if t.get("avg_score", 0) == 5 and t.get("status") == "APPROVED"
    ]
    success_text = ""
    if success_cases:
        success_text = "--- 🌟 성공 사례 (반드시 이 스타일과 특징을 학습 및 벤치마킹할 것) ---\n"
        for t in success_cases[-3:]:  # 최근 3개만 주입
            success_text += f"제목: {t.get('title')}\n프롬프트: {t.get('prompt')}\n\n"
        success_text += "--------------------------------------------------------\n\n"

    prompt = (
        f"현재 채널 타겟: {channel_key}\n"
        f"생성 개수: {count}개\n\n"
        f"--- 🧠 지식 베이스 (RAG) ---\n{rag_context}\n------------------\n\n"
        f"{success_text}"
        "위 지식과 성공 사례를 응용하여 가장 효과적이고 진화된 오디오 프롬프트 템플릿 JSON 배열을 생성해 주세요."
    )

    logger.info(
        f"🎵 [Sound Lab] 로컬 LLM(Ollama)을 통한 템플릿 {count}개 생성 돌입 (채널: {channel_key})"
    )

    try:
        # 무조건 로컬 모드 강제 호출 (비용 0원 보장)
        response_text = generate_text(prompt, system_instruction, mode="local")

        # JSON 파싱 정제
        text_clean = response_text.strip()
        if text_clean.startswith("```json"):
            text_clean = text_clean[7:]
        if text_clean.startswith("```"):
            text_clean = text_clean[3:]
        if text_clean.endswith("```"):
            text_clean = text_clean[:-3]
        text_clean = text_clean.strip()

        new_templates = json.loads(text_clean)

        # 💵 [비용 최적화] 로컬 LLM 템플릿 생성 사용 시 절감 비용(마이너스 비용) 로깅
        try:
            from telegram_bot.config import COST_LOCAL_LLM_SAVED_1K
            from telegram_bot.utils.cost_logger import log_api_cost

            est_tokens = len(prompt) + len(system_instruction) + 1000
            saved_cost = (est_tokens / 1000.0) * COST_LOCAL_LLM_SAVED_1K
            log_api_cost(
                "Local LLM Template Generation (Local)",
                -saved_cost,
                f"Est Tokens: {est_tokens}t (Saved)",
            )
        except Exception as cle:
            logger.warning(f"⚠️ [Cost Logging Fail] 비용 로깅 실패: {cle}")

        import uuid

        # 메타데이터 추가
        for t in new_templates:
            t["id"] = str(uuid.uuid4())[:8]  # 8자리 고유 ID (텔레그램 인라인 버튼 한계 고려)
            t["created_at"] = datetime.now().isoformat()
            t["status"] = "PENDING"
            t["avg_score"] = 0
            t["usage_count"] = 0

        # 기존 DB 병합 (상단에서 불러온 db 재사용)
        db = load_sound_templates()
        db.extend(new_templates)
        save_sound_templates(db)

        logger.info(f"✅ [Sound Lab] 템플릿 {len(new_templates)}개 로컬 생성 성공 및 DB 저장 완료.")
        return new_templates

    except Exception as e:
        logger.error(f"🚨 [Sound Lab] 로컬 템플릿 생성 실패: {e}")
        return []


def generate_similar_template(target_id: str):
    """
    특정 템플릿의 프롬프트를 기반으로 미세 조정(BPM, 악기 등)된 1개의 새로운 템플릿을 생성합니다.
    """
    db = load_sound_templates()
    target_t = next((t for t in db if t.get("id") == target_id), None)
    if not target_t:
        raise ValueError(f"템플릿 ID {target_id}를 찾을 수 없습니다.")

    system_instruction = (
        "당신은 루비아 기술연구소 부설 '음원연구소(Sound Lab)'의 수석 기획자 '라비아'입니다.\n"
        "제공된 기존 프롬프트를 바탕으로, 전체적인 분위기와 느낌은 유지하되 BPM, 리듬, 또는 백그라운드 악기 등을 '미세 조정(Fine-tune)'하여 1개의 새로운 프롬프트를 생성하십시오.\n"
        "반드시 단 1개의 객체를 포함하는 배열(Array) 형태의 순수 JSON으로만 출력해야 합니다. 마크다운 기호(```json 등)는 쓰지 마세요.\n\n"
        "[출력 JSON 스키마]\n"
        "[\n"
        "  {\n"
        '    "title": "템플릿의 매력적인 제목 (예: 새벽 3시의 타이베이 골목 - 변주)",\n'
        '    "channel": "원래 채널 유지",\n'
        '    "prompt": "영어로 작성된 완벽한 오디오 생성 프롬프트 (미세 조정됨)"\n'
        "  }\n"
        "]"
    )

    prompt = (
        f"--- 🎯 타겟 프롬프트 ---\n"
        f"제목: {target_t.get('title')}\n"
        f"프롬프트: {target_t.get('prompt')}\n"
        f"------------------\n\n"
        "위 프롬프트를 기반으로 유사하지만 확실히 변주된 1개의 새로운 프롬프트를 생성해 주세요."
    )

    try:
        response_text = generate_text(prompt, system_instruction, mode="local")

        # JSON 파싱 정제
        text_clean = response_text.strip()
        if text_clean.startswith("```json"):
            text_clean = text_clean[7:]
        if text_clean.startswith("```"):
            text_clean = text_clean[3:]
        if text_clean.endswith("```"):
            text_clean = text_clean[:-3]
        text_clean = text_clean.strip()

        new_templates = json.loads(text_clean)

        # 💵 [비용 최적화] 로컬 LLM 유사 템플릿 생성 사용 시 절감 비용(마이너스 비용) 로깅
        try:
            from telegram_bot.config import COST_LOCAL_LLM_SAVED_1K
            from telegram_bot.utils.cost_logger import log_api_cost

            est_tokens = len(prompt) + len(system_instruction) + 500
            saved_cost = (est_tokens / 1000.0) * COST_LOCAL_LLM_SAVED_1K
            log_api_cost(
                "Local LLM Similar Template Generation (Local)",
                -saved_cost,
                f"Est Tokens: {est_tokens}t (Saved)",
            )
        except Exception as cle:
            logger.warning(f"⚠️ [Cost Logging Fail] 비용 로깅 실패: {cle}")

        import uuid

        for t in new_templates:
            t["id"] = str(uuid.uuid4())[:8]
            t["created_at"] = datetime.now().isoformat()
            t["status"] = "PENDING"
            t["avg_score"] = 0
            t["usage_count"] = 0

        db.extend(new_templates)
        save_sound_templates(db)
        return new_templates[0]

    except Exception as e:
        logger.error(f"🚨 [Sound Lab] 유사 템플릿 생성 실패: {e}")
        raise e


if __name__ == "__main__":
    # 단독 테스트용
    print(generate_daily_templates("rubia", 2))
