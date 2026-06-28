# -*- coding: utf-8 -*-
"""
자연어 의도 분석기 (Intent Parser)
- 대표님의 한글 자연어 메시지를 분석하여 의도(Intent)와 파라미터(채널, 시간, 포맷)를 추출합니다.
- 1단계: Gemini Function Calling 기반 NLU (클라우드 모드)
- 2단계: 구조화된 JSON 응답 기반 로컬 LLM NLU (로컬 모드)
- 3단계: 정규식 및 키워드 매칭 폴백 (인터넷/API 장애 상황 대비용 안전장치)
"""

import re
import asyncio
from typing import Optional


# ─────────────────────────────────────────────
# 의도(Intent) 정의 및 상수
# ─────────────────────────────────────────────
INTENT_GREETING = "greeting"  # 인사
INTENT_CHANNEL_STATS = "channel_stats"  # 채널 현황 조회
INTENT_RECENT_VIDEOS = "recent_videos"  # 최근 영상 조회
INTENT_COMMENT_CHECK = "comment_check"  # 댓글 확인
INTENT_TEAM_STATUS = "team_status"  # 팀 상태
INTENT_HELP = "help"  # 도움말
INTENT_PLANNING = "planning"  # 기획 / 대본 작성
INTENT_PRODUCTION = "production"  # 영상 제작 / 무결성 검증
INTENT_SOUND_LAB = "sound_lab"  # 음원 템플릿 독립 생성
INTENT_PAYPAL_CONNECT = "paypal_connect"  # 페이팔 MCP 연결 브리핑
INTENT_UNKNOWN = "unknown"  # 인식 불가

# ─────────────────────────────────────────────
# 키워드 매칭 폴백용 패턴 정의
# ─────────────────────────────────────────────
INTENT_PATTERNS = [
    {
        "intent": INTENT_PRODUCTION,
        "keywords": [
            "제작",
            "영상제작",
            "영상 제작",
            "비디오제작",
            "렌더링",
            "빌드",
            "영상만들어",
            "영상 만들어",
            "비디오 만들어",
            "생성",
            "build",
            "render",
            "produce",
            "제작해줘",
            "업로드해줘",
            "비공개업로드",
            "업로드",
            "유튜브 업로드",
            "진행해",
            "진행시켜",
            "1안으로",
            "2안으로",
            "최종 완성",
            "합성해",
            "그대로 만들어",
            "그대로",
            "바로 만들어",
            "바로",
            "이어서",
            "이어서 만들어",
            "그걸로",
            "그걸로 해",
            "그걸로 진행",
            "그대로 진행",
        ],
        "description": "영상 제작 및 E2E 무결성 검증",
    },
    {
        "intent": INTENT_SOUND_LAB,
        "keywords": [
            "음악 템플릿",
            "음원 템플릿",
            "음원 생성",
            "사운드 템플릿",
            "오디오 생성",
            "gen_audio",
            "사운드랩",
            "음악 만들어",
            "음원 만들어",
        ],
        "description": "음원연구소 독립 템플릿 생성",
    },
    {
        "intent": INTENT_PAYPAL_CONNECT,
        "keywords": [
            "페이팔 mcp",
            "페이팔 연결",
            "paypal mcp",
            "결제 자동화 세팅",
            "페이팔mcp",
            "페이팔연결",
            "paypalmcp",
            "결제자동화세팅",
            "paypal mcp 연결",
            "paypal 연결",
            "페이팔 mcp 연결",
            "페이팔 mcp 연동",
        ],
        "description": "페이팔 MCP 연결 가이드 및 브리핑",
    },
    {
        "intent": INTENT_PLANNING,
        "keywords": [
            "기획",
            "대본",
            "쇼츠",
            "숏폼",
            "대사",
            "주제",
            "콘셉트",
            "시놉시스",
            "기획서",
            "기획안",
            "plan",
            "script",
            "shorts",
            "planning",
            "분석",
            "추천",
            "아이디어",
            "방향성",
            "레퍼런스",
            "롱폼",
            "longform",
            "가로형",
            "플레이리스트",
        ],
        "description": "숏폼 기획 및 대본 작성",
    },
    {
        "intent": INTENT_CHANNEL_STATS,
        "keywords": [
            "현황",
            "구독자",
            "조회수",
            "채널현황",
            "구독",
            "통계",
            "성과",
            "데이터",
            "stats",
            "subscribers",
        ],
        "description": "채널 현황 조회",
    },
    {
        "intent": INTENT_RECENT_VIDEOS,
        "keywords": [
            "최근",
            "최신",
            "업로드된",
            "기존 영상",
            "올린",
            "게시",
            "recent",
            "latest",
        ],
        "description": "최근 영상 조회",
    },
    {
        "intent": INTENT_COMMENT_CHECK,
        "keywords": [
            "댓글",
            "코멘트",
            "반응",
            "피드백",
            "comment",
            "feedback",
            "reply",
        ],
        "description": "댓글 확인",
    },
    {
        "intent": INTENT_TEAM_STATUS,
        "keywords": [
            "팀",
            "상태",
            "누구",
            "담당",
            "팀원",
            "team",
            "status",
            "who",
        ],
        "description": "팀 상태 확인",
    },
    {
        "intent": INTENT_HELP,
        "keywords": [
            # 기존 핵심 키워드
            "도움",
            "명령어",
            "뭐할수",
            "뭐할 수",
            "기능",
            "help",
            "메뉴",
            "사용법",
            "어떻게",
            "단축키",
            "단축어",
            "단축명령어",
            "단축키알려줘",
            "명령어보여줘",
            # 자연어 지시 뉘앙스 확장 (붙여쓰기/띄어쓰기 모두 커버)
            "명령어알려줘",
            "명령어 알려줘",
            "어떻게써",
            "어떻게 써",
            "뭐해",
            "뭘할수있어",
            "뭘 할 수 있어",
            "할수있는거",
            "할 수 있는 거",
            "안내",
            "가이드",
            "알려줘",
            "사용방법",
            "사용 방법",
            "스케줄",
            "예약",
            "자동업로드",
            "자동 업로드",
        ],
        "description": "도움말 및 단축키 안내",
    },
    {
        "intent": INTENT_GREETING,
        "keywords": [
            "안녕",
            "하이",
            "반가",
            "hello",
            "hi",
            "좋은아침",
            "좋은저녁",
            "수고",
            "고마워",
            "감사",
        ],
        "description": "인사",
    },
]

# 채널명 인식을 위한 별칭 매핑
CHANNEL_ALIASES = {
    "루비아": "rubia",
    "rubia": "rubia",
    "로파이": "rubia",
    "lofi": "rubia",
    "아우라": "aura",
    "aura": "aura",
    "웰니스": "aura",
    "명상": "aura",
    "스마트": "smartage",
    "smart": "smartage",
    "시니어": "smartage",
    "스마트에이지": "smartage",
    "smartage": "smartage",
    "타이페이": "taipei",
    "taipei": "taipei",
    "대만": "taipei",
}

# 🖥️ 로컬 NLU 모니터링 및 무결성 검증을 위한 전역 통계 카운터 (제4연구소 가동 지침)
LOCAL_NLU_TOTAL_CALLS = 0
LOCAL_NLU_FAILED_CALLS = 0
LOCAL_NLU_WARNING_TRIGGERED = False

# google-genai 라이브러리 임포트 (클라우드 전용)
try:
    from google import genai
    from google.genai import types
except ImportError:
    pass


def route_intent(
    intent: str,
    channel: Optional[str] = None,
    video_length: int = 1,
    video_format: str = "shorts",
):
    """
    [Gemini Tool] 사용자의 대화 메시지를 분석하여 의도(intent), 대상 채널(channel), 제작할 비디오의 목표 재생 시간(video_length), 그리고 비디오 포맷(video_format)을 추출하여 시스템을 라우팅합니다.

    Args:
        intent: 사용자의 의도를 나타내는 문자열. 다음 값 중 하나여야 합니다:
            - 'channel_stats': 채널 통계 확인 (구독자 수, 조회수 등)
            - 'recent_videos': 채널에 업로드된 최신 영상 목록 조회
            - 'comment_check': 채널에 달린 댓글, 반응 피드백 확인
            - 'planning': 영상 기획안, 대본/스크립트 작성, 주제/콘셉트 제안 요청
            - 'production': 비디오/영상 제작, 유튜브 업로드, 렌더링, E2E 무결성 빌드 요청
            - 'sound_lab': 음원연구소 독립 템플릿 생성, 음악/음원 템플릿 만들어
            - 'paypal_connect': 페이팔 MCP 연결 가이드 및 결제 자동화 브리핑
            - 'team_status': AI 팀원의 상태 및 역할 확인
            - 'help': 도움말, 명령어 사용법, 단축키 안내 요청
            - 'greeting': 단순 인사, 수고/감사 인사
            - 'chat': 시스템 기능 외의 일반적인 잡담 및 자유 질문
        channel: 사용자가 지칭한 유튜브 채널의 구분자 (메시지나 문맥에 채널명이 명시되어 있는 경우에만 채널을 판별하고, 없으면 생략하거나 null로 지정):
            - 'rubia': 루비아, 로파이, lofi 채널 관련
            - 'aura': 아우라, aura, 웰니스, wellness, 명상, 치유 채널 관련
            - 'smartage': 스마트, 스마트에이지, 시니어, 테크 채널 관련
            - 'taipei': 타이페이, 대만 채널 관련
        video_length: 비디오 제작(production) 또는 기획(planning) 지시 시 비디오의 타겟 시간 (단위: 분, 정수형).
            - 메시지에 1분, 3분, 10분 등 명시적인 시간이 명기되면 해당 숫자를 분 단위 정수로 지정합니다 (예: "3분짜리 쇼츠" -> 3, "10분 영상" -> 10).
            - 명시되지 않은 일반적인 쇼츠의 경우 기본값은 1
        video_format: 제작하고자 하는 영상 포맷 ('shorts' 또는 'longform')
    """
    pass


async def parse_intent(
    message: str, llm_mode: str = "cloud", local_url: Optional[str] = None
) -> dict:
    """
    대표님의 한글 자연어 메시지를 분석하여 의도, 대상 채널, 비디오 재생 시간 및 포맷을 추출합니다.
    """
    if not message or not message.strip():
        return {
            "intent": INTENT_UNKNOWN,
            "channel": None,
            "video_length": 1,
            "video_format": "shorts",
            "raw_message": message or "",
            "confidence": "low",
            "conflict_detected": False,
        }

    # 1) [Cloud Mode] Gemini Function Calling NLU
    if llm_mode == "cloud":
        try:
            from telegram_bot.config import GEMINI_API_KEY, YOUTUBE_API_KEY

            api_key = GEMINI_API_KEY or YOUTUBE_API_KEY
            if not api_key:
                raise ValueError("Gemini API 키가 구성되지 않았습니다.")

            client = genai.Client(api_key=api_key.split(",")[0].strip())

            sys_instruction = (
                "You are an NLU router for the Rubia Team YouTube automation system. "
                "Analyze the user's message and call the 'route_intent' function with appropriate arguments."
            )

            def call_gemini_fc():
                return client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=message,
                    config=types.GenerateContentConfig(
                        system_instruction=sys_instruction,
                        tools=[route_intent],
                        tool_config=types.ToolConfig(
                            function_calling_config=types.FunctionCallingConfig(
                                mode="ANY", allowed_function_names=["route_intent"]
                            )
                        ),
                    ),
                )

            response = await asyncio.to_thread(call_gemini_fc)

            detected_intent = INTENT_UNKNOWN
            detected_channel = None
            video_length = 1
            video_format = "shorts"

            if response.function_calls:
                call = response.function_calls[0]
                if call.name == "route_intent":
                    # call.args가 None일 경우 get() 호출 시 AttributeError 방지를 위한 안전 기본값 지정
                    args = call.args or {}
                    detected_intent = args.get("intent", INTENT_UNKNOWN)
                    detected_channel = args.get("channel", None)
                    video_length = args.get("video_length", 1)
                    video_format = args.get("video_format", "shorts")

            print(
                f"🧠 [LLM Function Calling NLU] Intent: '{detected_intent}', Channel: '{detected_channel}', Length: {video_length}, Format: '{video_format}' (Raw: '{message}')"
            )

            if detected_intent == "chat":
                detected_intent = INTENT_UNKNOWN

            # 🚨 [하드 락] LLM이 파라미터를 잘못 추출하는 버그(Hallucination) 방지
            fallback_data = parse_intent_fallback(message)
            has_explicit_duration = bool(re.search(r"\d+\s*(?:분|min|시간|hr)", message))
            has_explicit_format = any(
                kw in message.lower()
                for kw in [
                    "shorts",
                    "숏폼",
                    "세로",
                    "롱폼",
                    "longform",
                    "가로",
                    "플레이리스트",
                    "playlist",
                ]
            )

            if has_explicit_format:
                video_format = fallback_data["video_format"]
            if has_explicit_duration:
                video_length = fallback_data["video_length"]

            if int(video_length) >= 2:
                video_format = "longform"

            # 💵 [비용 최적화] Gemini NLU API 호출 비용 로깅
            try:
                from telegram_bot.config import (
                    COST_GEMINI_INPUT_1K,
                    COST_GEMINI_OUTPUT_1K,
                )
                from telegram_bot.utils.cost_logger import log_api_cost

                meta = getattr(response, "usage_metadata", None)
                input_tokens = meta.prompt_token_count if meta else 0
                output_tokens = meta.candidates_token_count if meta else 0
                cost = (input_tokens / 1000.0) * COST_GEMINI_INPUT_1K + (
                    output_tokens / 1000.0
                ) * COST_GEMINI_OUTPUT_1K
                log_api_cost(
                    "Gemini NLU (Cloud)",
                    cost,
                    f"Input: {input_tokens}t, Output: {output_tokens}t",
                )
            except Exception as cle:
                print(f"⚠️ [Cost Logging Fail] 비용 로깅 실패: {cle}")

            return {
                "intent": detected_intent,
                "channel": detected_channel,
                "video_length": int(video_length),
                "video_format": video_format,
                "raw_message": message,
                "confidence": "high",
                "conflict_detected": _detect_format_conflict(
                    message.strip().lower(), int(video_length)
                ),
            }

        except Exception as e:
            print(f"⚠️ [Gemini Function Calling Error]: {e}. 키워드 폴백을 작동합니다.")
            return parse_intent_fallback(message)

    # 2) [Local Mode] 로컬 LLM을 위한 구조화된 JSON 스키마 응답 생성
    else:
        global LOCAL_NLU_TOTAL_CALLS, LOCAL_NLU_FAILED_CALLS, LOCAL_NLU_WARNING_TRIGGERED
        LOCAL_NLU_TOTAL_CALLS += 1
        try:
            from telegram_bot.engine.llm_client import generate_text

            sys_instruction = (
                "당신은 사용자의 메시지를 분석하여 의도(intent), 유튜브 채널(channel), 비디오 타겟 시간(video_length), 그리고 비디오 포맷(video_format)을 분류하는 NLU 라우터입니다.\n"
                "반드시 아래 JSON 포맷으로만 응답해야 하며, 어떠한 부연 설명이나 마크다운 백틱(```json 등)도 쓰지 마세요.\n\n"
                "{\n"
                '  "intent": "string",\n'
                '  "channel": "string or null",\n'
                '  "video_length": 1,\n'
                '  "video_format": "shorts or longform"\n'
                "}\n\n"
                "사용 가능한 의도(intent):\n"
                "- 'channel_stats': 채널 통계 확인\n"
                "- 'recent_videos': 최근 영상 목록 확인\n"
                "- 'comment_check': 댓글 확인\n"
                "- 'planning': 쇼츠/기획안/대본 작성 요청\n"
                "- 'production': 비디오/영상 제작, 렌더링 요청\n"
                "- 'sound_lab': 음원연구소 독립 템플릿 생성\n"
                "- 'paypal_connect': 페이팔 MCP 연결 가이드 및 결제 자동화 브리핑\n"
                "- 'team_status': 팀원 상태 확인\n"
                "- 'help': 도움말/단축키 안내\n"
                "- 'greeting': 인사/감사\n"
                "- 'chat': 일반적인 잡담 및 자유 대화\n\n"
                "사용 가능한 채널(channel):\n"
                "- 'rubia': 루비아 로파이 관련\n"
                "- 'aura': 아우라 웰니스 관련\n"
                "- 'smartage': 스마트에이지/시니어 관련\n"
                "- 'taipei': 대만 로파이 관련\n"
                "- null: 채널이 언급되지 않았거나 불확실한 경우\n\n"
                "사용 가능한 video_length: 분 단위 정수 (기본값 1)\n"
                "사용 가능한 video_format: 'shorts' 또는 'longform'\n"
            )

            def call_local_llm():
                return generate_text(
                    message, sys_instruction, mode="local", local_url=local_url
                )

            response_text = await asyncio.to_thread(call_local_llm)

            import json

            # 혹시 마크다운 백틱이나 공백이 들어갔을 경우를 대비해 정규식으로 JSON만 추출
            json_match = re.search(r"\{.*\}", response_text.strip(), re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
            else:
                data = json.loads(response_text.strip())

            # 💡 [방어적 프로그래밍] 로컬 모델의 비정상 JSON 반환 및 규격 이탈 방지 검증
            if not isinstance(data, dict):
                raise ValueError("로컬 LLM 응답이 딕셔너리 포맷이 아닙니다.")

            detected_intent = data.get("intent", INTENT_UNKNOWN)
            detected_channel = data.get("channel", None)

            # 재생 시간 타입 강제 정수화 예외 처리
            try:
                video_length = int(data.get("video_length", 1))
            except (ValueError, TypeError):
                video_length = 1

            video_format = data.get("video_format", "shorts")

            # 로컬 모델 특유의 channel: "null" 문자열 리턴 버그 방어
            if detected_channel == "null" or detected_channel is None:
                detected_channel = None

            print(
                f"🖥️ [Local LLM NLU] Intent: '{detected_intent}', Channel: '{detected_channel}', Length: {video_length}, Format: '{video_format}' (Raw: '{message}')"
            )

            if detected_intent == "chat":
                detected_intent = INTENT_UNKNOWN

            # 🚨 [하드 락] LLM 파라미터 오추출 방지 (로컬 모드)
            fallback_data = parse_intent_fallback(message)
            has_explicit_duration = bool(re.search(r"\d+\s*(?:분|min|시간|hr)", message))
            has_explicit_format = any(
                kw in message.lower()
                for kw in [
                    "shorts",
                    "숏폼",
                    "세로",
                    "롱폼",
                    "longform",
                    "가로",
                    "플레이리스트",
                    "playlist",
                ]
            )

            if has_explicit_format:
                video_format = fallback_data["video_format"]
            if has_explicit_duration:
                video_length = fallback_data["video_length"]

            if int(video_length) >= 2:
                video_format = "longform"

            # 💵 [비용 최적화] 로컬 LLM NLU 사용 시 절감 비용(마이너스 비용) 로깅
            try:
                from telegram_bot.config import COST_LOCAL_LLM_SAVED_1K
                from telegram_bot.utils.cost_logger import log_api_cost

                # 로컬 메시지 토큰 대략적 산출 (메시지 길이 + 시스템 프로프스 1500자 = 약 1000토큰 가정)
                est_tokens = len(message) + 1000
                saved_cost = (est_tokens / 1000.0) * COST_LOCAL_LLM_SAVED_1K
                log_api_cost(
                    "Local LLM NLU (Local)",
                    -saved_cost,
                    f"Est Tokens: {est_tokens}t (Saved)",
                )
            except Exception as cle:
                print(f"⚠️ [Cost Logging Fail] 비용 로깅 실패: {cle}")

            # 한글 설명: 성공 시에도 누적 실패율 검증 진행
            if LOCAL_NLU_TOTAL_CALLS >= 5:
                fail_rate = LOCAL_NLU_FAILED_CALLS / LOCAL_NLU_TOTAL_CALLS
                if fail_rate >= 0.30:
                    LOCAL_NLU_WARNING_TRIGGERED = True
                    print(
                        f"🚨 [Local NLU Integrity Alert] 로컬 NLU 파싱 실패율이 {fail_rate*100:.1f}%로 임계치를 초과했습니다."
                    )
                else:
                    LOCAL_NLU_WARNING_TRIGGERED = False

            return {
                "intent": detected_intent,
                "channel": detected_channel,
                "video_length": int(video_length),
                "video_format": video_format,
                "raw_message": message,
                "confidence": "high",
                "conflict_detected": _detect_format_conflict(
                    message.strip().lower(), int(video_length)
                ),
            }

        except Exception as e:
            LOCAL_NLU_FAILED_CALLS += 1
            # 한글 설명: 호출 수가 최소 5회 이상이고, NLU 파싱 실패율이 30%를 초과하면 무결성 경보 작동
            if LOCAL_NLU_TOTAL_CALLS >= 5:
                fail_rate = LOCAL_NLU_FAILED_CALLS / LOCAL_NLU_TOTAL_CALLS
                if fail_rate >= 0.30:
                    LOCAL_NLU_WARNING_TRIGGERED = True
                    print(
                        f"🚨 [Local NLU Integrity Alert] 로컬 NLU 파싱 실패율이 {fail_rate*100:.1f}%로 임계치를 초과했습니다."
                    )
                else:
                    LOCAL_NLU_WARNING_TRIGGERED = False
            print(f"⚠️ [Local LLM NLU Error]: {e}. 키워드 폴백을 작동합니다.")
            return parse_intent_fallback(message)


def parse_intent_fallback(message: str) -> dict:
    """
    [안전 장치] LLM 연동 실패 시 작동할 최후의 키워드 매칭 폴백입니다.
    - 정규식을 활용해 dynamic하게 재생 시간을 파악하며, 3분 이상일 경우 자동으로 롱폼(longform) 포맷을 설정합니다.
    """
    if not message or not message.strip():
        return {
            "intent": INTENT_UNKNOWN,
            "channel": None,
            "video_length": 1,
            "video_format": "shorts",
            "raw_message": message or "",
            "confidence": "low",
            "conflict_detected": False,
        }

    text = message.strip().lower()
    detected_channel = _detect_channel(text)
    detected_intent = INTENT_UNKNOWN

    # 💡 [보완] 시간 및 포맷 감지 (정규식 기반 범용화)
    video_length = 1
    video_format = "shorts"

    # 💡 [시간/hour 단위 지원] "1시간", "2hr", "1 hour 30분" 등을 분 단위로 자동 변환합니다.
    # 기존에는 "분/min"만 인식하여 "1시간 롱폼" 같은 지시가 video_length=1(분)으로 처리되는 버그가 있었습니다.
    hour_match = re.search(r"(\d+)\s*(?:시간|hour|hours|hr)", text)
    min_match = re.search(r"(\d+)\s*(?:분|min)", text)
    if hour_match:
        video_length = int(hour_match.group(1)) * 60
    if min_match:
        # "1시간 30분" 같은 복합 표현 시 누적 합산
        video_length = (
            video_length + int(min_match.group(1))
            if hour_match
            else int(min_match.group(1))
        )

    # 포맷 판별: 롱폼 키워드가 있거나 재생 시간이 3분 이상인 경우 longform 적용
    longform_keywords = [
        "롱폼",
        "longform",
        "long-form",
        "long form",
        "플레이리스트",
        "playlist",
        "가로형",
        "가로",
        "긴영상",
        "긴 영상",
    ]
    if any(kw in text for kw in longform_keywords) or video_length >= 3:
        video_format = "longform"

    max_score = 0
    for pattern in INTENT_PATTERNS:
        score = 0
        for keyword in pattern["keywords"]:
            if keyword in text:
                score += 1
        if score > max_score:
            max_score = score
            detected_intent = pattern["intent"]

    if max_score >= 3:
        confidence = "high"
    elif max_score >= 1:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "intent": detected_intent,
        "channel": detected_channel,
        "video_length": video_length,
        "video_format": video_format,
        "raw_message": message.strip(),
        "confidence": confidence,
        "conflict_detected": _detect_format_conflict(text, video_length),
    }


def _detect_channel(text: str) -> str | None:
    """메시지 문맥에서 매칭되는 채널 구분자를 감지합니다."""
    for alias, channel_key in CHANNEL_ALIASES.items():
        if alias in text:
            return channel_key
    return None


def _detect_format_conflict(text: str, video_length: int) -> bool:
    """
    숏폼과 롱폼 키워드가 동시에 존재하거나, 쇼츠 + 2분 이상 등 모순 지시를 감지합니다.
    예: "3분짜리 쇼츠 만들어" → 쇼츠(1분 미만) + 3분 = 충돌
    """
    shorts_keywords = ["쇼츠", "숏폼", "세로", "shorts"]
    longform_keywords = [
        "롱폼",
        "longform",
        "long-form",
        "long form",
        "플레이리스트",
        "playlist",
        "가로형",
        "가로",
        "긴영상",
        "긴 영상",
    ]

    has_shorts = any(kw in text for kw in shorts_keywords)
    has_longform = any(kw in text for kw in longform_keywords) or video_length >= 2

    return has_shorts and has_longform


def get_help_text() -> str:
    """사용 가능한 단축 명령어 및 가이드를 생성합니다."""
    lines = [
        "📋 *사용 가능한 단축 명령어 (자연어도 OK!)*\n",
        "🔹 *채널 현황* — 채널 구독자/조회수 확인",
        '   예: "루비아 채널 현황 알려줘"',
        '   예: "아우라 조회수 얼마야?"\n',
        "🔹 *최근 영상* — 최신 업로드 영상 확인",
        '   예: "최근 영상 보여줘"\n',
        "🔹 *동영상 기획* — 💡라비아의 AI 기획서 (숏폼/롱폼 자동 판별)",
        '   예: "요가 스트레칭 3분 쇼츠 기획해줘"',
        '   예: "대만 로파이 12분 롱폼 플레이리스트 기획해줘"\n',
        "🔹 *영상 제작* — ⚙️코디아의 비디오 렌더링 및 E2E 무결성 빌드",
        '   예: "대만 로파이 1분 영상 제작해줘"',
        '   예: "아우라 5분 롱폼 비디오 제작해줘"\n',
        "🧠 *LLM 엔진 전환 단축키*",
        "   `/llm cloud` : 구글 제미나이(클라우드)로 전환",
        "   `/llm lmstudio` : 로컬 LM Studio로 전환",
        "   `/llm ollama` : 로컬 Ollama로 전환",
        "   `/llm` : 현재 활성화된 엔진 상태 확인\n",
        "⏰ *정기 자동 업로드 (윈도우 작업 스케줄러)*",
        "   매일 정해진 시간에 자동으로 영상을 제작하고 업로드할 수 있습니다.\n",
        "   *설정 방법:*",
        "   1️⃣ Win + R → `taskschd.msc` 입력 → 작업 스케줄러 실행",
        "   2️⃣ 오른쪽 패널 → '기본 작업 만들기' 클릭",
        "   3️⃣ 이름: `루비아 자동업로드` (원하는 이름)",
        "   4️⃣ 트리거: '매일' 선택 → 원하는 시각 설정 (예: 오전 9:00)",
        "   5️⃣ 동작: '프로그램 시작' 선택",
        "      프로그램: `python`",
        "      인수: `telegram_bot/bot.py --auto-upload`",
        "      시작 위치: 프로젝트 루트 폴더 경로\n",
        "   *참고 사항:*",
        "   • PC가 켜져 있어야 예약 작업이 실행됩니다",
        "   • '작업 조건' 탭에서 '절전 모드 해제' 옵션 체크 권장",
        "   • 여러 채널을 다른 시각에 예약하면 채널별 자동 운영 가능\n",
        "🎨 *자막 스타일 커스텀 (채팅 지시)*",
        "채팅창에 원하는 자막 디자인을 말하면 봇이 알아서 설정해 둡니다.",
        '• 사용 예시: "자막 파스텔 노란색으로 해줘", "자막 크기 90으로 키워", "자막 위로 올려줘", "자막 폰트 명조체로 바꿔"',
        '• 🔄 초기화: "자막 스타일 초기화" 라고 입력하면 기본값으로 돌아갑니다.\n',
        "🔢 *자막 간편 프리셋 (렌더링 승인 시)*",
        "에셋 생성 완료 후 렌더링을 지시할 때 번호를 함께 말씀하시면 세팅된 디자인이 적용됩니다.",
        "• 1번: 클래식 시네마 (화이트 + 얇은 테두리, 기본값)",
        "• 2번: 아늑한 다락방 (파스텔 노랑 + 반투명 음영 박스)",
        "• 3번: 숲속의 고요 (우아한 명조체 + 소프트 그림자)",
        '• 사용 예시: "2번으로 진행해", "3번 영상 만들어줘"\n',
        "💡 _이 외의 모든 말은 비서실장 루비아와 자유롭게 대화하실 수 있습니다!_",
    ]
    return "\n".join(lines)
