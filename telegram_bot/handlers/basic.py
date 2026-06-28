# -*- coding: utf-8 -*-
"""
기본 명령어 및 상태 처리 핸들러
- /start, /help, /status 명령어 및 일반 인사/팀 상태 응답을 담당합니다.
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.config import ALLOWED_USER_IDS, TEAM_EMOJI
from telegram_bot.utils.image_helper import get_agent_image_path
from telegram_bot.nlp.intent_parser import get_help_text
import random


# 권한 검증 데코레이터/헬퍼 함수
def check_permission(func):
    """대표님 본인만 봇을 사용할 수 있도록 보장하는 권한 검증용 데코레이터"""

    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        if not update.effective_user:
            return
        user_id = update.effective_user.id

        # ALLOWED_USER_IDS가 지정되어 있고, 사용자가 여기에 없으면 거부
        if ALLOWED_USER_IDS and user_id not in ALLOWED_USER_IDS:
            await update.message.reply_text(
                f"🔒 *접근이 제한되었습니다.*\n"
                f"대표님의 사용자 ID: `{user_id}`\n\n"
                f"접근 권한이 없습니다. 이 ID를 `.env` 또는 `config.py`의 `ALLOWED_USER_IDS`에 추가해주세요.",
                parse_mode="Markdown",
            )
            return
        return await func(update, context, *args, **kwargs)

    return wrapper


@check_permission
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start 명령어 핸들러: 대표님 환영 메시지와 루비아 이미지 전송"""
    username = update.effective_user.username or "대표님"
    img_path = get_agent_image_path("rubia", "greeting")

    caption = (
        f"👑 *안녕하세요, {username} 대표님!*\n"
        f"루비아 팀 유튜브 에이전트 봇이 정상적으로 온라인 상태로 진입했습니다.\n\n"
        f"자연어 명령어(예: '루비아 채널 현황 어때?', '스마트 최신 영상 보여줘')를 입력하시거나, "
        f"`/help` 또는 `도움말`을 입력하여 사용법을 확인해보세요."
    )

    try:
        if img_path:
            with open(img_path, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo, caption=caption, parse_mode="Markdown"
                )
        else:
            await update.message.reply_text(caption, parse_mode="Markdown")
    except Exception as e:
        print(f"Error in start_command: {e}")
        await update.message.reply_text(caption, parse_mode="Markdown")


@check_permission
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/help 명령어 및 도움말 의도 핸들러: 사용 가이드 안내"""
    # 가디아가 규칙을 꼼꼼하게 알려주는 연출
    img_path = get_agent_image_path("guardia", "working")
    help_text = get_help_text()

    try:
        if img_path:
            with open(img_path, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=f"🛡️ *가디아가 알려드리는 사용법:*\n\n{help_text}",
                    parse_mode="Markdown",
                )
        else:
            await update.message.reply_text(help_text, parse_mode="Markdown")
    except Exception as e:
        print(f"Error in help_command: {e}")
        await update.message.reply_text(help_text, parse_mode="Markdown")


@check_permission
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/status 명령어 및 팀 상태 의도 핸들러: 루비아 팀 조직 현황 브리핑"""
    # 루비아의 사무실 모드 혹은 리더십 커맨드 이미지 선택
    img_path = get_agent_image_path("rubia", "working")

    status_text = (
        "👑 *루비아 팀 전체 조직 및 시스템 상태 브리핑*\n\n"
        "현재 유튜브 에이전트 자동화 시스템은 안정적으로 가동 중입니다.\n\n"
        "👥 *팀 업무 분장 현황:*\n"
        "👑 *루비아 (Rubia / 총괄)* — 전체 채널 통제 및 비서 총괄\n"
        "💡 *라비아 (Ravia / 기획)* — 콘텐츠/썸네일 및 감성 콘셉트 도출\n"
        "📡 *인텔라 (Intella / 리서치)* — 최신 트렌드 정찰 및 유튜브 분석\n"
        "⚙️ *코디아 (Cordia / 기술)* — 자동화 엔진 구축 및 데이터 연동\n"
        "📊 *시그나 (Signa / 최적화)* — 채널 성과 데이터 분석 및 A/B 테스트\n"
        "🛡️ *가디아 (Guardia / 보안)* — 시스템 무결성, 보안 감사 및 규정 준수\n\n"
        "💡 _대표님, 지시할 준비가 모두 완료되었습니다!_"
    )

    try:
        if img_path:
            with open(img_path, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo, caption=status_text, parse_mode="Markdown"
                )
        else:
            await update.message.reply_text(status_text, parse_mode="Markdown")
    except Exception as e:
        print(f"Error in status_command: {e}")
        await update.message.reply_text(status_text, parse_mode="Markdown")


@check_permission
async def handle_greeting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """일반 인사 의도 처리: 랜덤 에이전트가 교대로 상냥하게 인사"""
    agents = ["rubia", "ravia", "intella", "cordia", "signa", "guardia", "stella"]
    selected_agent = random.choice(agents)
    emoji = TEAM_EMOJI.get(selected_agent, "💡")

    # 해당 에이전트의 greeting 이미지
    img_path = get_agent_image_path(selected_agent, "greeting")

    greetings = [
        f"{emoji} *안녕하세요, 대표님! {selected_agent.capitalize()}입니다.* 무엇을 도와드릴까요?",
        f"{emoji} *반갑습니다, 대표님!* 오늘 하루도 힘차게 시작해 보겠습니다. 필요하신 채널 작업을 지시해주세요!",
        f"{emoji} *대표님, 환영합니다!* 실시간으로 유튜브 채널 모니터링을 진행하고 있습니다. 궁금한 점이 있으시면 말씀해주세요.",
    ]
    greeting_text = random.choice(greetings)

    try:
        if img_path:
            with open(img_path, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo, caption=greeting_text, parse_mode="Markdown"
                )
        else:
            await update.message.reply_text(greeting_text, parse_mode="Markdown")
    except Exception as e:
        print(f"Error in handle_greeting: {e}")
        await update.message.reply_text(greeting_text, parse_mode="Markdown")
