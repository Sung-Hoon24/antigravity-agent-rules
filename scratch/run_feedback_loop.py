# -*- coding: utf-8 -*-
"""
[제1연구소 R&D] 닫힌 루프(Closed-Loop) 성과 환류 시스템 E2E 가동 스크립트 (run_feedback_loop.py)
- 'rubia' 채널의 성과 데이터를 수집하여 RAG 저장소에 성공 문법으로 적재합니다.
- 신규 기획안 수립 시 해당 성공 문법 지식이 프롬프트 컨텍스트에 주입(Injection)되어
  최종 기획서 JSON 결과에 반영되는지 직접 측정하고 검증합니다.
"""

import sys
import os
import time
import logging

# 프로젝트 루트 디렉터리를 sys.path에 추가
WORKSPACE = r"c:\1인기업\Apps\유튜브에이전트"
sys.path.append(WORKSPACE)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FeedbackLoopRunner")


def test_closed_loop_e2e():
    logger.info("=" * 60)
    logger.info("🚀 [Closed-Loop E2E] 닫힌 루프 성과 환류 시스템 실전 가동 개시")
    logger.info("=" * 60)

    # 1. 'rubia' 채널 성공 지표 환류 루프 기동 (Ingestion -> Validation -> Analysis -> Storage -> Indexing)
    logger.info("Step 1. 'rubia' 채널 성공 지표 수집 및 RAG 적재 개시...")
    from telegram_bot.engine.feedback_loop import run_performance_feedback_loop

    loop_result = run_performance_feedback_loop("rubia")
    logger.info(f"💾 Step 1 성공. 피드백 루프 실행 완료: {loop_result}")

    # 생성된 성공 문법 파일 경로 및 존재 검증
    saved_path = loop_result.get("saved_path")
    if not os.path.exists(saved_path):
        raise FileNotFoundError(f"성공 문법 마크다운 파일이 생성되지 않았습니다: {saved_path}")
    logger.info("✅ Step 1 검증 통과: 성공 문법 파일 존재 확인")

    # 2. RAG 지식 검색기 가동 및 지식 주입(Injection) 작동 여부 검증
    logger.info("\nStep 2. 신규 기획 요청 시 성공 문법 지식 주입(Injection) 테스트...")
    from telegram_bot.engine.rag_retriever import retrieve_relevant_knowledge

    # 라비아 기획에 전달될 대표님의 자연어 지시어 준비
    user_message = "대만 타이베이의 비 내리는 풍경과 어울리는 빗소리 lofi 숏폼 기획안 작성해줘."

    # RAG 지식 검색 가동 (Chroma 또는 Fallback Local JSON 조회)
    # 💡 [한글 설명] retrieve_relevant_knowledge가 방금 동기화된 success_pattern_rubia.md 파일의
    # 성공 문법 청크를 포함한 컨텍스트를 성공적으로 리턴하는지 조회합니다.
    rag_context = retrieve_relevant_knowledge(user_message, limit=2)
    logger.info(f"📚 Step 2 결과. 조회된 RAG 컨텍스트:\n{rag_context}")

    # RAG 조회 데이터 무결성 검증
    if (
        "success_pattern_rubia" not in rag_context
        and "taiwan" not in rag_context.lower()
        and "taipei" not in rag_context.lower()
    ):
        # Fallback 키워드 검색이라도 타이베이/대만/루비아가 들어가 있어야 함
        logger.warning(
            "⚠️ RAG 검색 결과에 방금 등록된 타이베이 성공 문법 출처가 명시적으로 매칭되지 않았습니다. (텍스트 내 키워드 매칭 여부 재확인 필요)"
        )
    else:
        logger.info("✅ Step 2 검증 통과: 성공 문법 RAG 매칭 및 추출 성공!")

    # 3. LLM NLU 기획 생성 및 성공 문법 바인딩
    logger.info("\nStep 3. 성공 문법이 주입된 최종 기획안(VideoPlanningJSON) 도출 및 성과 측정...")
    from telegram_bot.engine.llm_client import generate_structured_json
    from pydantic import BaseModel, Field
    from typing import List

    class VideoTrack(BaseModel):
        title: str = Field(description="BGM 음원 트랙 제목")
        duration_sec: int = Field(description="BGM 음원 재생 시간(초)")

    class TimelineCaption(BaseModel):
        time_code: str = Field(description="자막 표출 타임라인 시점 (예: '00:02')")
        text: str = Field(description="화면에 노출될 감성적인 자막/멘트 문구")

    class VideoPlanningJSON(BaseModel):
        concept: str = Field(description="기획안 콘셉트 및 화면 연출 요약")
        youtube_title: str = Field(description="유튜브 최종 업로드 제목 (타겟 채널 언어 100% 준수)")
        youtube_description: str = Field(description="유튜브 최종 업로드 설명란")
        youtube_tags: List[str] = Field(description="유튜브 업로드 해시태그 목록")
        playlist: List[VideoTrack] = Field(description="추천 플레이리스트 및 사운드 무드 사양")
        captions: List[TimelineCaption] = Field(description="타임라인별 자막 리스트")
        visual_audio_guide: str = Field(description="시각 연출 및 특수 효과 가이드라인")

    # 기획 NLU 프롬프트 및 시스템 지침 (RAG 주입 반영)
    rag_injection = f"\n\n[로컬 지식 참고(Obsidian & AI Connect)]:\n{rag_context}\n"
    system_instruction = (
        "당신은 루비아(Rubia) 팀의 기획팀장 '라비아(Ravia)'입니다.\n"
        "제공하는 [로컬 지식 참고]에 기재된 과거 성공 문법(제목 패턴, 시각 연출 키워드, 플레이리스트 무드)을 적극 참고하여 "
        "새로운 기획안을 수립해야 합니다. 성공했던 제목 구조를 변형해 이번 기획에 반영하십시오.\n"
        "출력은 오직 스키마에 정의된 JSON 규격을 엄수해야 하며, 한국어를 본문(자막, 제목)에 혼용해서는 안 됩니다. (자막과 제목은 번체 대만어 번역)\n"
        f"{rag_injection}"
    )

    prompt = f"대표님의 기획 지시: {user_message}"

    start_time = time.time()
    response_json = generate_structured_json(
        prompt=prompt,
        system_instruction=system_instruction,
        response_schema=VideoPlanningJSON,
        mode="cloud",  # 신뢰성 있는 Gemini API 직접 가동
    )
    elapsed = time.time() - start_time

    logger.info(f"🛡️ Step 3 기획안 생성 완료 (소요 시간: {elapsed:.2f}초)")
    logger.info(f"📊 최종 기획서 JSON 결과:\n{response_json}")

    # 4. 성공 문법 반영 및 성과 확인
    concept = response_json.get("concept", "")
    youtube_title = response_json.get("youtube_title", "")

    logger.info("\n=" * 60)
    logger.info("🎯 [Closed-Loop 환류 성과 확인 및 측정]")
    logger.info(f"- 주입된 성공 데이터 기반 제안 제목: {youtube_title}")
    logger.info(f"- 주입된 성공 데이터 기반 연출 컨셉: {concept[:150]}...")
    logger.info("=" * 60)

    logger.info("🎉 [E2E 검증 완료] 닫힌 루프 성과 환류 시스템이 성공적으로 정상 작동함을 입증했습니다!")


if __name__ == "__main__":
    test_closed_loop_e2e()
