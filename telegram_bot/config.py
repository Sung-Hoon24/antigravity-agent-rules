# -*- coding: utf-8 -*-
"""
텔레그램 봇 설정 파일
- 봇 토큰, 허용 사용자, 채널 매핑 등 핵심 설정을 관리합니다.
- 민감 정보는 .env 파일에서 불러옵니다.
"""

import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
# 프로젝트 루트의 .env를 찾아서 불러옴
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# ─────────────────────────────────────────────
# 🔑 텔레그램 봇 토큰 (BotFather에서 발급)
# ─────────────────────────────────────────────
# 단일 봇 운용 시 기본 토큰
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# 멀티 봇 운용 시 개별 토큰 (대표님 요청 사항)
TELEGRAM_Taipei_Lofi_New_Bot_TOKEN = os.getenv("TELEGRAM_Taipei_Lofi_New_Bot_TOKEN", "")
TELEGRAM_rubia_smart_bot_TOKEN = os.getenv("TELEGRAM_rubia_smart_bot_TOKEN", "")
TELEGRAM_Youtube_Total_Music_Taipei_Lofi_New_Bot_TOKEN = os.getenv(
    "TELEGRAM_Youtube_Total_Music_Taipei_Lofi_New_Bot_TOKEN", ""
)

# 🤖 3대 멀티 봇 프로필 정의
# ─────────────────────────────────────────────
BOT_PROFILES = {
    "rofi": {
        "token": TELEGRAM_Taipei_Lofi_New_Bot_TOKEN,
        "allowed_channels": ["rubia", "taipei"],
        "default_channel": "rubia",
        "username": "@Taipei_Lofi_New_Bot",
        "name": "그린스터디채널 봇 👑",
    },
    "aura": {
        "token": TELEGRAM_rubia_smart_bot_TOKEN,
        "allowed_channels": ["aura", "smartage"],
        "default_channel": "aura",
        "username": "@rubia_smart_bot",
        "name": "AURA & 스마트에이지 채널 봇 📡",
    },
    "analyst": {
        "token": TELEGRAM_Youtube_Total_Music_Taipei_Lofi_New_Bot_TOKEN,
        "allowed_channels": ["rubia", "taipei", "aura", "smartage"],
        "default_channel": "rubia",
        "username": "@Taipei_Lofi_New_Bot_Analyst",  # 중복 방지를 위한 디폴트 유저네임
        "name": "Youtube 분석가 봇 📊",
    },
}

# ─────────────────────────────────────────────
# 🛡️ 허용된 사용자 ID (대표님만 명령 가능)
# BotFather 봇에서 /start 후 chat_id를 확인하여 여기에 입력
# 빈 리스트일 경우 → 최초 실행 시 자동으로 ID를 알려주는 모드로 동작
# ─────────────────────────────────────────────
ALLOWED_USER_IDS = []  # 예: [123456789]
_env_ids = os.getenv("TELEGRAM_ALLOWED_IDS", "")
if _env_ids:
    try:
        ALLOWED_USER_IDS = [
            int(uid.strip()) for uid in _env_ids.split(",") if uid.strip()
        ]
    except ValueError:
        print("⚠️ TELEGRAM_ALLOWED_IDS 형식 오류 — 숫자를 쉼표로 구분해주세요.")

# ─────────────────────────────────────────────
# 📺 YouTube 채널 매핑 (토큰-채널 매칭 감사 기준)
# ─────────────────────────────────────────────
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# 🧠 Gemini API 키 및 채널 정체성 정보
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

CHANNEL_IDENTITIES = {
    "rubia": "A cozy lofi background music space featuring a rainy greenhouse and plant-filled library, tailored for deep focus, coding, reading, and creative work.",
    "taipei": "Immersive lofi visual and sound assets set in a tranquil greenhouse with gentle rain, designed to enhance focus, productivity, and relaxation.",
    "aura": "A peaceful sanctuary featuring nature sounds and Solfeggio healing frequencies (528Hz, 432Hz) for deep rest, sleep, meditation, and yoga. Pure organic soundscapes for ultimate serenity.",
    "smartage": "Digital tool and smart device guides for global seniors.",
}

# 채널명 → 채널 ID 매핑
# 실제 채널 ID는 YouTube Studio에서 확인 가능
CHANNEL_MAP = {
    "rubia": {
        "name": "Rubia Lofi - Daily Chill Beats & BGM",
        "channel_id": "UCgfReXSDhiDTe0JJgbyHGIw",  # Rubia Lofi 실제 채널 ID
        "token_file": "token_rubia.json",
        "aliases": ["rubia", "rubialofi", "lofi", "bgm", "focus"],
    },
    "aura": {
        "name": "Aura Serenity Wellness",
        "channel_id": "UC8jlSVeaw_wisJim9E_XHSQ",  # Aura Serenity Wellness 실제 채널 ID
        "token_file": "token_aura.json",
        "aliases": ["aura", "wellness", "meditation", "healing", "solfeggio"],
    },
    "smartage": {
        "name": "SmartAgeTech",
        "channel_id": "UCV9yGd2MS-RMcH30owlbB1w",  # SmartAgeTech 실제 채널 ID
        "token_file": "token_smartagetech.json",
        "aliases": ["smart", "smartage", "tech", "senior", "guide"],
    },
    "taipei": {
        "name": "Green Study Series (그린스터디)",
        "channel_id": "UCgfReXSDhiDTe0JJgbyHGIw",  # Rubia Lofi와 동일 채널 ID
        "token_file": "token_taipei.json",
        "aliases": ["greenstudy", "green", "study", "focus", "bgm", "coding"],
    },
}

# ─────────────────────────────────────────────
# 🤖 봇 기본 설정
# ─────────────────────────────────────────────
BOT_NAME = "RubiaTeamBot"

# 루비아 팀 담당자 이모지 매핑
TEAM_EMOJI = {
    "rubia": "👑",
    "ravia": "💡",
    "intella": "📡",
    "cordia": "⚙️",
    "signa": "📊",
    "guardia": "🛡️",
    "stella": "⭐",
}

# 🤖 하이브리드 추론 라우팅 모드 설정 (Ver 2.2)
# - "auto": 지능형 자동 전환 (경량 업무는 로컬, 복합 업무는 클라우드)
# - "manual_local": 로컬 LLM 강제 처리 (비용 제로화)
# - "manual_cloud": 클라우드 LLM 강제 처리 (고성능 추론)
HYBRID_ROUTING_MODE = "auto"

# ─────────────────────────────────────────────
# 💵 유료 API 및 로컬 LLM 비용 관리 단가 설정 (USD)
# ─────────────────────────────────────────────
COST_IMAGEN_IMAGE = 0.03  # Imagen 이미지 1장당 생성 요금
COST_LYRIA_SECOND = 0.005  # Lyria 오디오 1초당 요금 (30초=$0.15, 1분=$0.30)
COST_GEMINI_INPUT_1K = 0.000075  # Gemini 1.5 Flash 입력 토큰 1,000개당
COST_GEMINI_OUTPUT_1K = 0.0003  # Gemini 1.5 Flash 출력 토큰 1,000개당
COST_LOCAL_LLM_SAVED_1K = 0.00015  # 로컬 LLM 구동 시 절감되는 가상 비용 (1,000 토큰당)
