# -*- coding: utf-8 -*-
"""
[제1연구소 가디아 보안 모듈] RAG 데이터 무결성 검증 필터 (rag_validator.py)
- 외부 유튜브 API 또는 댓글 스크래핑을 통해 획득한 데이터가 RAG 저장소에 진입하기 전,
  데이터의 무결성과 보안 위협(SQL 인젝션, XSS HTML 태그, 깨진 유니코드, 비상식적 지표)을 검증하여
  불량 데이터를 원천 차단(Discard)합니다.
- [Ver 2.0 수익화 가동 보강] 결제 데이터(PayPal) 연동에 맞춘 신용카드 번호(Luhn 알고리즘) 및 계좌 정보 유출 차단(Monetization Gate) 장착.
- 24/7 실시간 API 지연(Latency > 15초), API Error, 무결성 검증 실패 시 0.1초 긴급 알림 전송기 내장.
"""

import re
import time
import logging
import urllib.request
import urllib.parse
import json
from functools import wraps

# 가디아 보안 로깅 설정
logger = logging.getLogger("GuardiaSecurityGate")

# 간단한 유해어 필터링 사전 (콘텐츠 정화용)
PROFANITY_WORDS = ["시발", "개새끼", "존나", "병신", "fuck", "shit", "asshole"]


def send_telegram_alert(message: str):
    """
    [가디아 24/7 긴급 알림]
    보안 위협, 금융 민감 정보 노출, 시스템 장애(지연, API 에러) 감지 즉시 대표님께 알림 전송
    """
    try:
        from telegram_bot.config import (
            TELEGRAM_BOT_TOKEN,
            TELEGRAM_rubia_smart_bot_TOKEN,
            TELEGRAM_Taipei_Lofi_New_Bot_TOKEN,
            ALLOWED_USER_IDS,
        )

        # 가용한 토큰 선택
        token = (
            TELEGRAM_BOT_TOKEN
            or TELEGRAM_rubia_smart_bot_TOKEN
            or TELEGRAM_Taipei_Lofi_New_Bot_TOKEN
        )
        if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            logger.warning(
                f"⚠️ [Telegram Alert Bypass] 유효한 봇 토큰이 없어 경보 발송을 건너뜁니다: {message}"
            )
            return

        # ALLOWED_USER_IDS가 비어있다면, 경보 발송 대상을 찾을 수 없음
        if not ALLOWED_USER_IDS:
            logger.warning(
                f"⚠️ [Telegram Alert Bypass] 수신할 ALLOWED_USER_IDS가 비어 있어 전송할 수 없습니다: {message}"
            )
            return

        for chat_id in ALLOWED_USER_IDS:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": f"🛡️ *[가디아 24/7 보안/무결성 긴급 경보]*\n\n{message}",
                "parse_mode": "Markdown",
            }
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=2.0):
                    pass
                logger.info(f"📡 [Telegram Alert Sent] 경보 송출 완료. ChatID: {chat_id}")
            except Exception as inner_err:
                logger.error(f"❌ [Telegram Alert Failed] 전송 실패: {inner_err}")
    except Exception as e:
        logger.error(f"❌ [Telegram Alert Critical Error] 알림 시스템 크래시: {e}")


def is_valid_luhn(card_number: str) -> bool:
    """Luhn 알고리즘을 활용한 신용카드 번호 유효성 검증"""
    card_number = re.sub(r"\D", "", card_number)
    if len(card_number) < 13 or len(card_number) > 19:
        return False
    digits = [int(d) for d in card_number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        double_d = d * 2
        checksum += double_d if double_d < 10 else double_d - 9
    return checksum % 10 == 0


def detect_financial_exposure(text: str) -> bool:
    """금융 민감 정보(카드 번호, 은행 계좌 형태 등) 노출 탐지"""
    # 1. 13~19자리 연속된 숫자 또는 하이픈으로 구분된 카드 번호 패턴 탐지
    card_patterns = [r"\b(?:\d[ -]*?){13,19}\b"]
    for pattern in card_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            cleaned = re.sub(r"\D", "", match)
            if is_valid_luhn(cleaned):
                logger.warning(
                    f"🚨 [Monetization Gate] 신용카드 정보 검출 (Luhn 검증 통과): {match[:4]}-****-****-{match[-4:] if len(match) > 4 else ''}"
                )
                return True

    # 2. 계좌 번호 또는 주민등록번호 유사 패턴 탐지 (기본 필터)
    account_patterns = [
        r"\b\d{3,6}-\d{2,6}-\d{3,6}\b",  # 일반 계좌 형태
    ]
    for pattern in account_patterns:
        if re.search(pattern, text):
            logger.warning(f"🚨 [Monetization Gate] 은행 계좌 형식 노출 검출: {pattern}")
            return True

    return False


def monitor_latency_and_errors(func):
    """
    [가디아 24/7 성능/오류 데코레이터 - Circuit Breaker 탑재 (Ver 2.1)]
    - 함수 실행 시간(Latency)과 예외(API Error)를 감시합니다.
    - 외부 API 오류 또는 일시적 네트워크 장애 발생 시 즉각 안전 모드(Safe Mode)로 진입하지 않고,
      최대 3회 재시도(지수 백오프 1초 -> 2초 -> 4초 대기)를 수행합니다.
    - 3회 연속 실패(3 consecutive failures)가 확정되었을 때만 enable_safe_mode를 기동하여 Safe Mode Lock을 걸고 예외를 raise합니다.
    - 15초 이상 지연되거나 최종 에러가 발생하는 경우 실시간으로 대표님께 긴급 텔레그램 알림을 발송합니다.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        max_retries = 3
        backoffs = [1.0, 2.0, 4.0]

        # 💡 [한글 설명] 재시도 루프를 돌아 일시적 장애(Transient Error) 시 자가 치유를 도모함
        for attempt in range(1, max_retries + 1):
            try:
                # 💡 [한글 설명] 안전 모드로 강제 잠금된 상태라면 추가 실행 및 재시도를 즉각 중단함
                check_safe_mode_lock()

                res = func(*args, **kwargs)

                # 💡 [한글 설명] 정상 실행 완료 후 소요 시간(Latency)이 15초를 초과한 경우 대표님께 알림
                latency = time.time() - start_time
                if latency > 15.0:
                    logger.warning(
                        f"⚠️ [Guardia Latency Warning] 함수 {func.__name__} 실행 지연 감지: {latency:.2f}초"
                    )
                    send_telegram_alert(
                        f"⚠️ *[시스템 실행 지연 감지]*\n"
                        f"• **함수명**: `{func.__name__}`\n"
                        f"• **소요시간**: `{latency:.2f}초` (기준값 15.0초 초과)\n"
                        f"• **상태**: 정상 처리되었으나, 병목 현상 점검을 권장합니다."
                    )
                return res
            except Exception as e:
                # 💡 [한글 설명] 이미 안전 모드로 인한 잠금(PermissionError) 상태라면 재시도 없이 예외를 전파함
                if isinstance(e, PermissionError) and "[Safety Lock]" in str(e):
                    raise e

                logger.warning(
                    f"⚠️ [Guardia Retry Warning] 함수 {func.__name__} 실행 실패 ({attempt}/{max_retries}차 시도): {e}"
                )

                # 💡 [한글 설명] 3회 연속 실패가 확정되었을 때만 안전 모드를 활성화하고 텔레그램 긴급 알림을 보냄
                if attempt == max_retries:
                    latency = time.time() - start_time
                    logger.error(
                        f"❌ [Guardia Circuit Breaker Triggered] 함수 {func.__name__} 3회 연속 실패: {e}"
                    )

                    enable_safe_mode(f"외부 API 3회 연속 실패 ({func.__name__}): {e}")

                    send_telegram_alert(
                        f"🚨 *[시스템 치명적 오류 감지 - Circuit Breaker 작동]*\n"
                        f"• **함수명**: `{func.__name__}`\n"
                        f"• **에러메시지**: `{str(e)}` (3회 연속 실패)\n"
                        f"• **소요시간**: `{latency:.2f}초`\n"
                        f"• **상태**: 안전 모드로 즉시 전환하여 파이프라인 가동을 중단합니다."
                    )
                    raise e

                # 💡 [한글 설명] 지수 백오프 대기 적용 (1초 -> 2초 -> 4초)
                sleep_time = backoffs[attempt - 1]
                logger.info(
                    f"⏳ [Backoff] {sleep_time}초 대기 후 {attempt + 1}차 재시도를 진행합니다."
                )
                time.sleep(sleep_time)

    return wrapper


def validate_rag_ingestion(data: dict) -> dict:
    """
    [RAG Ingestion 무결성 게이트 + Monetization Gate]
    수집된 원시 데이터의 무결성을 검증하고, 금융 유출이나 오염 데이터를 감지하면 즉시 ValueError를 던져 Discard합니다.
    """
    # 💡 [한글 설명] 데이터 존재 여부 및 타입 검사
    if not data:
        logger.error("🚨 [GUARDIA SECURITY WARNING] Discard: 빈 데이터가 RAG 유입 지점에 전달되었습니다.")
        raise ValueError("무결성 오류: RAG 유입 데이터가 비어 있습니다.")

    if not isinstance(data, dict):
        logger.error(
            "🚨 [GUARDIA SECURITY WARNING] Discard: 올바르지 않은 데이터 형식(dict가 아님)이 감지되었습니다."
        )
        raise ValueError("무결성 오류: RAG 유입 데이터가 딕셔너리 형식이 아닙니다.")

    # 1. 필수 필드 검증 (유튜브 성과 환류 스펙 만족 여부)
    required_fields = ["channel", "video_id", "views", "ctr"]
    for field in required_fields:
        if field not in data or data.get(field) is None:
            logger.error(
                f"🚨 [GUARDIA SECURITY WARNING] Discard: 필수 필드 '{field}'가 유실된 불완전 데이터가 감지되었습니다."
            )
            raise ValueError(f"무결성 오류: 필수 필드 '{field}'가 유실되었습니다.")

    # 2. 지표(Metrics) 무결성 검증 (비상식적인 수치 범위 탐지)
    try:
        views = int(data["views"])
        ctr = float(data["ctr"])
    except (ValueError, TypeError) as num_err:
        logger.error(f"🚨 [GUARDIA SECURITY WARNING] Discard: 수치 데이터 형 변환 실패: {num_err}")
        raise ValueError("무결성 오류: 조회수 또는 CTR의 수치 형 변환에 실패했습니다.")

    # 조회수가 음수인 경우 차단
    if views < 0:
        logger.error(f"🚨 [GUARDIA SECURITY WARNING] Discard: 음수 조회수 감지 ({views})")
        raise ValueError(f"무결성 오류: 조회수({views})는 음수가 될 수 없습니다.")

    # CTR이 음수이거나 100%를 초과하는 비상식적인 수치인 경우 차단
    if ctr < 0.0 or ctr > 100.0:
        logger.error(f"🚨 [GUARDIA SECURITY WARNING] Discard: 비정상 CTR 범위 감지 ({ctr}%)")
        raise ValueError(f"무결성 오류: CTR({ctr}%) 범위는 0%에서 100% 사이여야 합니다.")

    # 3. 텍스트 보안 및 오염 검증 (HTML 태그, SQL 인젝션, 깨진 유니코드, 금융 민감 정보)
    text_fields = ["title", "analysis_summary"]
    comments = data.get("comments", [])

    # 댓글 목록 형식 검증
    if not isinstance(comments, list):
        logger.error("🚨 [GUARDIA SECURITY WARNING] Discard: comments 필드가 리스트 형식이 아닙니다.")
        raise ValueError("무결성 오류: comments 필드는 리스트 형식이어야 합니다.")

    all_texts_to_check = []

    # 검사할 모든 텍스트 병합
    for tf in text_fields:
        if tf in data and data[tf]:
            all_texts_to_check.append((tf, str(data[tf])))

    for idx, comment in enumerate(comments):
        all_texts_to_check.append((f"comments[{idx}]", str(comment)))

    for field_name, text in all_texts_to_check:
        # [Ver 2.0 Monetization Gate] 금융 민감 정보 노출 필터링
        if detect_financial_exposure(text):
            msg = f"금융 민감 정보 유출 위험 감지: '{field_name}' 필드에서 카드번호 또는 계좌 번호가 검출되어 처리가 차단(Discard)되었습니다."
            logger.error(f"🚨 [GUARDIA MONETIZATION WARNING] Discard: {msg}")
            # 비상 제동 장치 (Safe Mode) 자동 작동
            enable_safe_mode(f"금융 정보 유출 시도 차단 ({field_name})")
            raise ValueError(msg)

        # 3-1. 깨진 유니코드 및 Null 바이트 검사 (C-style 공격 차단)
        if "\x00" in text or "\x1a" in text:
            logger.error(
                f"🚨 [GUARDIA SECURITY WARNING] Discard: '{field_name}' 필드에서 C-style Null 바이트 또는 제어 문자가 탐지되었습니다."
            )
            raise ValueError(
                f"보안 위험 감지: '{field_name}' 필드에 깨진 유니코드 및 제어 문자가 포함되어 있습니다."
            )

        # 3-2. HTML 태그 탐지 (XSS 스크립트 주입 공격 방어)
        if re.search(r"<[^>]+>", text):
            logger.error(
                f"🚨 [GUARDIA SECURITY WARNING] Discard: '{field_name}' 필드에서 HTML 태그 또는 스크립트 오염이 탐지되었습니다. 입력값: {text[:100]}"
            )
            raise ValueError(
                f"보안 위험 감지: '{field_name}' 필드에 HTML 태그가 포함되어 있어 유입이 차단되었습니다."
            )

        # 3-3. SQL 인젝션 공격 쿼리 패턴 검출
        sql_injection_patterns = [
            r"(?i)\b(union\s+select|select\s+.+\s+from|insert\s+into|delete\s+from|drop\s+table|alter\s+table)\b",
            r"(?i)'.+\b(or|and)\b.+\s*=\s*.+",
            r"--",
            r"\/\*",
        ]
        for pattern in sql_injection_patterns:
            if re.search(pattern, text):
                logger.error(
                    f"🚨 [GUARDIA SECURITY WARNING] Discard: '{field_name}' 필드에서 SQL 인젝션 공격 의심 패턴이 탐지되었습니다. 패턴: {pattern}"
                )
                raise ValueError(
                    f"보안 위험 감지: '{field_name}' 필드에 SQL 인젝션 의심 구문이 발견되었습니다."
                )

        # 3-4. 유해어/욕설 검사 및 경고 (데이터 정화)
        for bad_word in PROFANITY_WORDS:
            if bad_word in text.lower():
                logger.warning(
                    f"⚠️ [GUARDIA CONTENT CLEANSE] '{field_name}' 필드에서 욕설/유해어 '{bad_word}'가 감지되었습니다. 정제 처리를 시행합니다."
                )
                # 유해어는 완전 차단(Discard)하지 않고 기획 참고용 지표임을 고려하여 검열처리(***)로 자체 정화
                cleaned_text = re.sub(
                    re.escape(bad_word), "***", text, flags=re.IGNORECASE
                )
                if field_name.startswith("comments["):
                    idx = int(field_name.split("[")[1].split("]")[0])
                    comments[idx] = cleaned_text
                else:
                    data[field_name] = cleaned_text

    # 무결성 검증을 마친 정제된 데이터 리턴
    data["comments"] = comments
    logger.info("🛡️ [RAG Ingestion Pass] 데이터 무결성 게이트 최종 통과 완료.")
    return data


# 🚨 [비상 제동 시스템 (Safe Mode)]
SAFE_MODE_ENABLED = False


def enable_safe_mode(reason: str):
    """시스템 비상 제동 장치를 즉시 작동시키고, 대표님께 텔레그램 긴급 알림을 발송합니다."""
    global SAFE_MODE_ENABLED
    if not SAFE_MODE_ENABLED:
        SAFE_MODE_ENABLED = True
        logger.error(f"🚨 [SAFE MODE ACTIVATED] 시스템 비상 제동 작동! 사유: {reason}")
        send_telegram_alert(
            f"🚨 *[시스템 비상 제동 장치 작동 (Safe Mode)]*\n"
            f"• **제동 사유**: `{reason}`\n"
            f"• **조치**: 추가적인 금융 유출 및 리스크 예방을 위해 기획, 결제, 렌더링 파이프라인의 가동을 전면 일시 차단(Safety Lock)했습니다."
        )


def disable_safe_mode():
    """시스템 안전 모드를 해제하고 정상 기동 모드로 복구합니다."""
    global SAFE_MODE_ENABLED
    if SAFE_MODE_ENABLED:
        SAFE_MODE_ENABLED = False
        logger.info("🟢 [SAFE MODE DEACTIVATED] 시스템이 정상 모드로 안전하게 복구되었습니다.")
        send_telegram_alert("🟢 *[시스템 복구 완료]*\n\n모든 안전 점검이 완료되어 시스템이 정상 가동 모드로 복원되었습니다.")


def check_safe_mode_lock():
    """안전 모드 활성화 여부를 조회하여 활성 시 예외를 던져 파이프라인을 비상 차단합니다."""
    global SAFE_MODE_ENABLED
    if SAFE_MODE_ENABLED:
        raise PermissionError(
            "🚨 [Safety Lock] 시스템이 가디아의 비상 제동 안전 모드(Safe Mode)에 의해 잠겨 있습니다. 관리자의 복구 지시가 필요합니다."
        )
