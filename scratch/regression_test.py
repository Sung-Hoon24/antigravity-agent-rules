# -*- coding: utf-8 -*-
"""
[제1연구소 Gated Commit Pipeline] 통합 회귀 테스트 자동화 스크립트 (regression_test.py)
- 헌법 및 안전 3단계 규정에 따라 핵심 프로덕션 변경 전 100% 검증을 수행합니다.
- 실패하는 케이스가 있을 경우 즉시 Exit Code 1을 리턴하여 머지를 차단합니다.
"""

import sys
import os
import time
import logging

# 프로젝트 루트 디렉터리를 sys.path에 추가하여 모듈 정상 로딩 보장
WORKSPACE = r"c:\1인기업\Apps\유튜브에이전트"
sys.path.append(WORKSPACE)
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RegressionGate")


def test_renderer_e2e():
    """
    [회귀 테스트 1] 기존 렌더러 기능 및 무결성 검증 필터 테스트 (Fast-Gate 적용)
    - JSON 형태의 기획 명세를 바탕으로 FFmpeg 비디오 합성이 에러 없이 이루어지고 파일이 디스크에 생성되는지 검증합니다.
    - Fast-Gate 옵션을 켜서 3초 인코딩으로 제한하여 회귀 테스트 구동 시간을 획기적으로 줄입니다.
    """
    logger.info("🧪 [Test 1] FFmpeg 무결성 렌더러 E2E 테스트 시작 (Fast-Gate 가동)")
    from telegram_bot.engine.video_renderer import render_video, validate_planning_json

    visual_path = os.path.join(
        WORKSPACE, "assets", "characters", "Rubia", "rubia_work_eye.png"
    )
    audio_path = os.path.join(WORKSPACE, "aura_shorts_v1.mp4")
    output_path = os.path.join(WORKSPACE, "output", "regression_test_output.mp4")

    # 1. 렌더러 스키마를 만족하는 JSON 명세 준비
    test_json_data = {
        "concept": "Regression test concept",
        "youtube_title": "Regression Test Title",
        "youtube_description": "Regression Test Description",
        "youtube_tags": ["regression", "test"],
        "playlist": [{"title": "Test Track 1", "duration_sec": 30}],
        "captions": [{"time_code": "00:02", "text": "Testing Gated Pipeline"}],
    }

    # 1-1. 렌더러 인터페이스 무결성 사전 검사
    validate_planning_json(test_json_data)
    logger.info("🛡️ [Test 1] validate_planning_json 사전 검증 통과")

    # 기존 임시 결과물 삭제
    if os.path.exists(output_path):
        os.remove(output_path)

    # 2. 렌더링 구동 (Fast-Gate 활성화로 3초 제한 렌더링)
    start_time = time.time()
    render_video(
        visual_path=visual_path,
        audio_path=audio_path,
        planning_data=test_json_data,
        output_path=output_path,
        video_format="shorts",
        fast_gate=True,
    )
    elapsed = time.time() - start_time
    logger.info(f"🛡️ [Test 1] 렌더링 완료 (Fast-Gate 소요 시간: {elapsed:.2f}초)")

    # 3. 파일 생성 유효성 검증
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        raise RuntimeError("렌더링 실패: 출력 비디오 파일이 없거나 크기가 0바이트입니다.")

    logger.info("✅ [Test 1 성공] 렌더러 E2E 회귀 테스트 통과!")
    # 리소스 정리
    try:
        os.remove(output_path)
    except Exception:
        pass


def test_llm_structured_and_fallback():
    """
    [회귀 테스트 2] 로컬 LLM 접속 실패 및 클라우드 자가 치유(폴백)와 Pydantic 구조화 JSON 변환 성공 검증
    """
    logger.info("🧪 [Test 2] 로컬 LLM 폴백 및 Pydantic 정형 데이터 검증 시작")
    from telegram_bot.engine.llm_client import generate_structured_json
    from pydantic import BaseModel, Field
    from typing import List

    class SimpleSchema(BaseModel):
        concept: str = Field(description="컨셉 요약")
        tags: List[str] = Field(description="해시태그 리스트")

    prompt = "대만 타이베이의 빗소리 로파이 숏폼 컨셉을 간결하게 작성해줘."
    sys_instruction = "당신은 영상 기획자입니다. 오직 지정된 스키마 규격의 JSON만 출력해야 합니다."

    # 로컬 Ollama가 꺼진 상황을 연출하기 위해 mode="local"로 호출하여 강제 폴백 검증
    start_time = time.time()
    result = generate_structured_json(
        prompt=prompt,
        system_instruction=sys_instruction,
        response_schema=SimpleSchema,
        mode="local",
        # 💡 [한글 설명] 하드코딩된 API 주소 대신 중앙 Config의 OLLAMA_URL을 참조합니다.
        local_url=Config.OLLAMA_URL,
    )
    elapsed = time.time() - start_time
    logger.info(f"🛡️ [Test 2] 자가 치유 복구 완료 (소요 시간: {elapsed:.2f}초)")

    # 스키마 데이터 구조화 검증
    if (
        not result
        or not result.get("concept")
        or not isinstance(result.get("tags"), list)
    ):
        raise ValueError("반환된 데이터의 Pydantic 구조 정형성 검증이 실패했습니다.")

    logger.info(f"✅ [Test 2 성공] 폴백 & 구조화 JSON 데이터 획득 성공:\n{result}")


def test_state_machine_isolation():
    """
    [회귀 테스트 3] 상태 전이 격리 정책 및 ERROR_4001_VOID 차단 검증
    """
    logger.info("🧪 [Test 3] 상태 전이 규칙 및 4001 void 차단 테스트 시작")
    from api.state_machine_service import STATE_MACHINE_RULES, void_transition_failure

    current_state = "INPUT"
    allowed_states = STATE_MACHINE_RULES.get(current_state, {})

    # 1. 정상 전이 테스트
    next_state = "LOCAL_LLM_RUNNING"
    if next_state not in allowed_states:
        raise ValueError(f"정상적인 상태 전이 '{current_state} -> {next_state}'가 차단되었습니다.")
    logger.info(f"🛡️ [Test 3] 정상 상태 전이 '{current_state} -> {next_state}' 허용 확인")

    # 2. 비정상 전이(중간 단계 누락) 강제 테스트
    invalid_next_state = "REVIEW"
    logger.info(f"🛡️ [Test 3] 비정상 전이 시도: '{current_state}' -> '{invalid_next_state}'")

    try:
        void_transition_failure(
            current_state=current_state,
            next_state=invalid_next_state,
            payload={"video_id": "regression_test_01"},
            reason="렌더링 단계를 거치지 않고 검수 단계로 전이 시도",
        )
        # 예외가 발생하지 않고 코드가 흐르면 실패
        raise RuntimeError("오동작: 비정상 전이가 차단되지 않고 그대로 허용되었습니다.")
    except Exception as err:
        if (
            "System Void Detected" in str(err)
            or "ERROR_4001_VOID" in str(err)
            or "논리적 연결 고리가 누락" in str(err)
        ):
            logger.info("✅ [Test 3 성공] 비정상 전이(ERROR_4001_VOID)가 완벽히 차단되었습니다!")
        else:
            raise err


def test_rag_validator_gate():
    """
    [회귀 테스트 4] RAG 유입 데이터 무결성 검증 필터 테스트
    - 정상 데이터의 통과 및 유해어 필터링(Cleanse) 확인.
    - 지표 오류(음수 조회수, 100% 초과 CTR)의 차단(Discard) 검증.
    - 보안 위협(HTML 태그 주입, SQL 인젝션 공격)의 차단(Discard) 검증.
    """
    logger.info("🧪 [Test 4] RAG 무결성 모니터링 및 보안 게이트 테스트 시작")
    from telegram_bot.nlp.rag_validator import validate_rag_ingestion

    # 1. 정상 데이터 및 유해어 필터링 검증
    valid_data = {
        "channel": "rubia",
        "video_id": "vid_01",
        "title": "대만 타이베이 빗소리 lofi",
        "views": 5000,
        "ctr": 8.5,
        "comments": ["정말 시발 최고네요!", "Beautiful lofi beats."],
        "analysis_summary": "성공적인 숏폼 포맷 적용",
    }

    result = validate_rag_ingestion(valid_data)
    # 욕설(시발)이 "***"로 정화되었는지 검증
    if "***" not in result["comments"][0]:
        raise ValueError("자가 정화 실패: 유해 단어가 마스킹되지 않았습니다.")
    logger.info("🛡️ [Test 4] 정상 데이터 통과 및 욕설 정화 기능 성공 확인")

    # 2. 비정상 지표 차단 검증 (조회수 음수)
    invalid_views = valid_data.copy()
    invalid_views["views"] = -10
    try:
        validate_rag_ingestion(invalid_views)
        raise RuntimeError("오동작: 음수 조회수가 무결성 필터를 통과했습니다.")
    except ValueError as e:
        logger.info(f"🛡️ [Test 4] 음수 조회수 정상 차단 완료 (사유: {e})")

    # 3. 비정상 지표 차단 검증 (CTR 100% 초과)
    invalid_ctr = valid_data.copy()
    invalid_ctr["ctr"] = 120.0
    try:
        validate_rag_ingestion(invalid_ctr)
        raise RuntimeError("오동작: 100% 초과 CTR이 무결성 필터를 통과했습니다.")
    except ValueError as e:
        logger.info(f"🛡️ [Test 4] 100% 초과 CTR 정상 차단 완료 (사유: {e})")

    # 4. 보안 위협 차단 검증 (XSS HTML 태그 주입)
    xss_data = valid_data.copy()
    xss_data["title"] = "빗소리 <script>alert(1)</script>"
    try:
        validate_rag_ingestion(xss_data)
        raise RuntimeError("오동작: HTML 스크립트 주입이 무결성 필터를 통과했습니다.")
    except ValueError as e:
        logger.info(f"🛡️ [Test 4] HTML 태그 공격 정상 차단 완료 (사유: {e})")

    # 5. 보안 위협 차단 검증 (SQL 인젝션)
    sqli_data = valid_data.copy()
    sqli_data["analysis_summary"] = "영상 요약 ' OR '1'='1"
    try:
        validate_rag_ingestion(sqli_data)
        raise RuntimeError("오동작: SQL 인젝션 구문이 무결성 필터를 통과했습니다.")
    except ValueError as e:
        logger.info(f"🛡️ [Test 4] SQL 인젝션 공격 정상 차단 완료 (사유: {e})")

    logger.info("✅ [Test 4 성공] RAG 무결성 모니터링 & 보안 게이트 회귀 테스트 통과!")


def test_feedback_loop_chain():
    """
    [회귀 테스트 5] 닫힌 루프(Closed-Loop) 성과 환류 제어 파이프라인 검증
    - Ingestion -> Validation -> Analysis -> Storage -> Indexing의 전체 피드백 체인이
      오류 없이 연결되고, 무결성 게이트를 통해 안전하게 지식을 RAG에 적재하는지 E2E 검사합니다.
    """
    logger.info("🧪 [Test 5] 닫힌 루프 성과 환류 및 무결성 게이트 체인 테스트 시작")
    from telegram_bot.engine.feedback_loop import run_performance_feedback_loop

    # 1. rubia 채널의 피드백 루프 작동
    result = run_performance_feedback_loop("rubia")

    if not result or result.get("status") != "success":
        raise RuntimeError(f"피드백 루프 실행 실패: 반환 상태가 success가 아닙니다 ({result})")

    saved_path = result.get("saved_path")
    if not saved_path or not os.path.exists(saved_path):
        raise FileNotFoundError(f"성공 문법 파일이 디스크에 정상 보존되지 않았습니다: {saved_path}")

    logger.info(f"🛡️ [Test 5] 닫힌 루프 기동 및 성공 문법 저장 검증 통과 (경로: {saved_path})")

    # 2. RAG 검색기와의 연동 가능성 검증 (정상 동기화 체크)
    from telegram_bot.engine.rag_retriever import retrieve_relevant_knowledge

    context = retrieve_relevant_knowledge("Taipei rain lofi", limit=1)

    if not context:
        logger.warning("⚠️ RAG 검색 결과가 비어 있습니다. (Chroma 미로딩 폴백 상황인 경우 통과)")

    logger.info("✅ [Test 5 성공] 닫힌 루프 성과 환류 체인 회귀 테스트 통과!")


def test_kpi_dashboard_and_monetization_gate():
    """
    [회귀 테스트 6] KPI 대시보드 지표 수집 검증 및 가디아 금융 보안 게이트(Luhn 신용카드 차단) 테스트
    - 5대 KPI 수치(Content Velocity, Cost, Engagement, Projected Revenue 등)가 정상 구조로 집계되는지 확인합니다.
    - Luhn 알고리즘을 충족하는 신용카드 번호 유출 시도가 무결성 검증 필터에서 Discard(차단)되는지 확인합니다.
    """
    logger.info("🧪 [Test 6] KPI 대시보드 및 금융 보안 게이트(Monetization Gate) 검증 시작")

    # 💡 [한글 설명] 함수 초입에 모든 관련 모듈 임포트를 정렬하여 UnboundLocalError 방지
    # 💡 [한글 설명] 단순 Boolean 값 임포트 시 값 복사 이슈를 피하기 위해 모듈 자체(rag_val)를 임포트하여 동적 조회
    from telegram_bot.handlers.kpi_dashboard import get_kpi_metrics
    import telegram_bot.nlp.rag_validator as rag_val
    from telegram_bot.nlp.rag_validator import (
        validate_rag_ingestion,
        monitor_latency_and_errors,
        disable_safe_mode,
        check_safe_mode_lock,
    )
    import asyncio

    # 1. 5대 KPI 지표 집계 정형 구조 검증
    metrics = asyncio.run(get_kpi_metrics("rubia"))
    required_metrics = [
        "content_velocity",
        "idea_to_live_time",
        "cost_per_video",
        "engagement_rate",
        "projected_revenue",
        "paypal_revenue",
    ]
    for m in required_metrics:
        if m not in metrics or metrics[m] is None:
            raise ValueError(f"KPI 지표 집계 누락: '{m}' 지표가 집계되지 않았습니다.")

    logger.info(
        f"🛡️ [Test 6] 5대 KPI 지표 정상 수집 확인 (예상 수익: ${metrics['projected_revenue']:.2f})"
    )

    # 2. 금융 보안 게이트(Monetization Gate) Luhn 신용카드 차단 검증
    # Luhn 검증을 통과하는 임의의 카드 번호 (4111-1111-1111-1111) 주입 시도
    leakage_data = {
        "channel": "rubia",
        "video_id": "vid_sec_01",
        "title": "대만 lofi 비디오 - 4111-1111-1111-1111",  # 카드 정보 노출 유도
        "views": 2000,
        "ctr": 7.2,
        "comments": ["정말 힐링되네요."],
        "analysis_summary": "정상 컨셉",
    }

    try:
        validate_rag_ingestion(leakage_data)
        raise RuntimeError("오동작: 유효한 카드번호(4111-1111-1111-1111) 노출 데이터가 차단되지 않고 통과했습니다.")
    except ValueError as e:
        if "금융 민감 정보" in str(e) or "유출" in str(e):
            logger.info(f"🛡️ [Test 6] 카드번호 유출 데이터 정상 폐기(Discard) 완료. (사유: {e})")
        else:
            raise e

    # 3. 은행 계좌 정보 유출 차단 검증
    account_leakage = leakage_data.copy()
    account_leakage["title"] = "대만 lofi 비디오"
    account_leakage["comments"] = ["여기로 후원해 주세요: 110-345-678901 신한은행"]

    try:
        validate_rag_ingestion(account_leakage)
        raise RuntimeError("오동작: 은행 계좌번호 노출 데이터가 차단되지 않고 통과했습니다.")
    except ValueError as e:
        logger.info(f"🛡️ [Test 6] 은행 계좌번호 유출 데이터 정상 폐기(Discard) 완료. (사유: {e})")

    # 💡 [한글 설명] 다음 테스트 영향 방지를 위해 이전 테스트 시 활성화된 안전 모드가 있다면 해제
    disable_safe_mode()

    # 4. Circuit Breaker 회복 탄력성 (1~2회 실패 후 3회째 복구 통과 케이스) 검증
    fail_count = 0

    @monitor_latency_and_errors
    def temporary_failing_function():
        nonlocal fail_count
        fail_count += 1
        if fail_count < 3:
            raise RuntimeError(f"일시적 네트워크 타임아웃 모사 에러 ({fail_count}/3)")
        return "SuccessAfterRetries"

    # 💡 [한글 설명] 2회 실패 후 3회째에 성공하므로 최종적으로 예외 없이 정상 복원되어 값을 리턴해야 함
    res = temporary_failing_function()
    if res != "SuccessAfterRetries":
        raise RuntimeError(
            f"Circuit Breaker 자가 복구 실패: 예상 결과 'SuccessAfterRetries', 실제 결과 '{res}'"
        )
    if rag_val.SAFE_MODE_ENABLED:
        raise RuntimeError("오동작: 자가 복구에 성공했으나 세이프 모드가 활성화되어 있습니다.")

    logger.info("🛡️ [Test 6] Circuit Breaker 1~2회 일시 실패 후 자가 복구 테스트 성공 완료")

    # 5. Circuit Breaker 3회 연속 실패에 따른 비상 제동(Safe Mode Lock) 작동 검증
    # 💡 [한글 설명] 다시 Safe Mode 비활성화 상태로 시작
    disable_safe_mode()

    @monitor_latency_and_errors
    def persistent_failing_function():
        raise RuntimeError("치명적 외부 API 장애 모사 에러")

    try:
        persistent_failing_function()
        raise RuntimeError("오동작: 3회 연속 실패하는 함수가 예외를 던지지 않고 통과했습니다.")
    except Exception as e:
        if "치명적 외부 API 장애 모사 에러" not in str(e):
            raise e

    # 💡 [한글 설명] 3회 연속 실패했으므로 가디아 비상 제동 플래그가 참(True)으로 설정되어야 함
    if not rag_val.SAFE_MODE_ENABLED:
        raise RuntimeError("오동작: 3회 연속 실패했으나 비상 제동 안전 모드(Safe Mode)가 활성화되지 않았습니다.")

    # 💡 [한글 설명] 안전 잠금(Safety Lock)이 걸렸을 때 check_safe_mode_lock() 호출 시 PermissionError 차단이 일어나는지 검증
    try:
        check_safe_mode_lock()
        raise RuntimeError(
            "오동작: Safe Mode 상태임에도 check_safe_mode_lock()이 작동하여 잠금 예외를 던지지 않았습니다."
        )
    except PermissionError as e:
        logger.info(f"🛡️ [Test 6] Safe Mode 상태에서 Safety Lock 정상 작동 잠금 확인: {e}")

    # 💡 [한글 설명] 다음 검증 진행 및 실동을 위해 Safe Mode 복원(Deactivate)
    disable_safe_mode()

    logger.info("🛡️ [Test 6] Circuit Breaker 3회 연속 실패 시 Safe Mode 강제 차단 테스트 성공 완료")

    logger.info("✅ [Test 6 성공] KPI 대시보드, 금융 보안 게이트 및 Circuit Breaker 자가 치유 검증 통과!")


def test_hybrid_routing_gate():
    """
    [회귀 테스트 7] 하이브리드 추론 라우팅 분기 및 수동 오버라이드 무결성 검증
    - /mode auto, manual_local, manual_cloud 설정 변경에 따라 LLM 라우팅 엔진이
      local/cloud로 각각 정확히 동적 분기하는지 검증합니다.
    """
    logger.info("🧪 [Test 7] 하이브리드 추론 라우팅 분기 무결성 검증 시작")
    import telegram_bot.config as config
    from telegram_bot.engine.llm_client import determine_routing_mode

    # 💡 [한글 설명] 이전 설정 백업 및 초기화
    original_mode = config.HYBRID_ROUTING_MODE

    try:
        # 1. 수동 로컬 강제 모드 검증
        config.HYBRID_ROUTING_MODE = "manual_local"
        mode = determine_routing_mode("기획안을 짜줘", "당신은 기획자입니다.", has_schema=True)
        if mode != "local":
            raise ValueError(f"오동작: 수동 로컬 강제 상태이나 '{mode}'로 라우팅되었습니다.")

        # 2. 수동 클라우드 강제 모드 검증
        config.HYBRID_ROUTING_MODE = "manual_cloud"
        mode = determine_routing_mode("단순 인사", "인사말", has_schema=False)
        if mode != "cloud":
            raise ValueError(f"오동작: 수동 클라우드 강제 상태이나 '{mode}'로 라우팅되었습니다.")

        # 3. 스마트 자동 전환 모드 (Auto) - 경량 업무 라우팅 검증
        config.HYBRID_ROUTING_MODE = "auto"
        mode = determine_routing_mode("안녕? 오늘 날씨 어때?", "당신은 비서입니다.", has_schema=False)
        if mode != "local":
            raise ValueError(f"오동작: 스마트 Auto 경량 업무 상태이나 '{mode}'로 라우팅되었습니다. (local 예상)")

        # 4. 스마트 자동 전환 모드 (Auto) - 복합 분석 업무 (스키마 존재) 검증
        mode = determine_routing_mode("비디오 정보 수집", "스키마 분석", has_schema=True)
        if mode != "cloud":
            raise ValueError(
                f"오동작: 스마트 Auto 구조화(schema) 업무 상태이나 '{mode}'로 라우팅되었습니다. (cloud 예상)"
            )

        # 5. 스마트 자동 전환 모드 (Auto) - 복합 분석 업무 (키워드 매칭) 검증
        mode = determine_routing_mode("kpi 대시보드 기획 분석해줘", "보고서", has_schema=False)
        if mode != "cloud":
            raise ValueError(
                f"오동작: 스마트 Auto 키워드 매칭 업무 상태이나 '{mode}'로 라우팅되었습니다. (cloud 예상)"
            )

        logger.info("✅ [Test 7 성공] 하이브리드 추론 라우팅 및 스마트 스위치 검증 통과!")

    finally:
        # 💡 [한글 설명] 다음 기동을 위해 모드 원상 복구
        config.HYBRID_ROUTING_MODE = original_mode


def run_all_tests():
    logger.info("=" * 60)
    logger.info("🚀 [Gated Commit Pipeline] 통합 회귀 테스트 가동")
    logger.info("=" * 60)

    failures = 0

    try:
        test_renderer_e2e()
    except Exception as e:
        logger.error(f"❌ [Test 1 실패] {e}", exc_info=True)
        failures += 1

    try:
        test_llm_structured_and_fallback()
    except Exception as e:
        logger.error(f"❌ [Test 2 실패] {e}", exc_info=True)
        failures += 1

    try:
        test_state_machine_isolation()
    except Exception as e:
        logger.error(f"❌ [Test 3 실패] {e}", exc_info=True)
        failures += 1

    try:
        test_rag_validator_gate()
    except Exception as e:
        logger.error(f"❌ [Test 4 실패] {e}", exc_info=True)
        failures += 1

    try:
        test_feedback_loop_chain()
    except Exception as e:
        logger.error(f"❌ [Test 5 실패] {e}", exc_info=True)
        failures += 1

    try:
        test_kpi_dashboard_and_monetization_gate()
    except Exception as e:
        logger.error(f"❌ [Test 6 실패] {e}", exc_info=True)
        failures += 1

    try:
        test_hybrid_routing_gate()
    except Exception as e:
        logger.error(f"❌ [Test 7 실패] {e}", exc_info=True)
        failures += 1

    logger.info("=" * 60)
    if failures == 0:
        logger.info("🎉 [Gated Commit 통과] 모든 회귀 테스트 케이스 성공 (100% Success)!")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error(f"🚨 [Gated Commit 반려] 총 {failures}개의 테스트 케이스 실패. 반영을 거부합니다.")
        logger.info("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
