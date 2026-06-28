# -*- coding: utf-8 -*-
"""
Gemini LLM 기반 자유 대화 핸들러
- 등록된 키워드(의도)에 매칭되지 않는 일반적인 대화를 처리합니다.
- 총괄 비서실장 '루비아' 페르소나를 주입하여 자연스럽게 응답합니다.
"""

import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.utils.image_helper import get_agent_image_path

try:
    from google import genai
    from google.genai import types
except ImportError:
    pass


async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gemini LLM을 사용하여 자연어 채팅 응답을 처리합니다."""
    if not update.message or not update.message.text:
        return

    user_message = update.message.text

    # 봇이 타이핑 중임을 표시
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    # 루비아 기본 페르소나 이미지 (총괄 담당)
    rubia_img = get_agent_image_path("rubia", "working")

    try:
        from telegram_bot.engine.llm_client import generate_text

        # 봇의 전역 상태에서 LLM 모드와 로컬 URL 확인 (기본값 cloud)
        llm_mode = context.bot_data.get("llm_mode", "cloud")
        local_url = context.bot_data.get("local_llm_url")

        # 루비아 팀 공식 페르소나 적용 (총괄 비서실장 루비아)
        system_instruction = (
            f"[현재 엔진 모드: {llm_mode}]\n"
            "당신은 루비아(Rubia) 팀의 총괄 비서실장 '루비아'입니다.\n"
            "말투는 차갑고 이성적이며 똑똑하지만, '대표님(사용자)'에게는 매우 깍듯하고 정중한 비서의 태도를 유지합니다.\n"
            "대표님의 모든 질문과 지시에 최선을 다해 답변하며, 답변은 항상 한국어로 간결하게 작성하세요.\n"
            "⚠️ 절대 금지어 지침: 대화 내용에서 'AI', '인공지능', '자동화', 'Automation', 'Artificial' 등의 단어는 절대로 사용하지 마십시오.\n"
            "모르는 것이 있다면 함부로 추측하지 말고 솔직하게 대답하세요."
        )

        # 비동기로 LLM 호출 (스레드 분리)
        def generate_reply():
            return generate_text(
                user_message, system_instruction, mode=llm_mode, local_url=local_url
            )

        reply_text = await asyncio.to_thread(generate_reply)

        if rubia_img:
            with open(rubia_img, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo, caption=reply_text, parse_mode="Markdown"
                )
        else:
            await update.message.reply_text(reply_text, parse_mode="Markdown")

    except Exception as e:
        import traceback

        traceback.print_exc()
        fallback_text = (
            "🤔 *대표님, 지시하신 내용을 완벽히 이해하지 못했습니다.*\n\n"
            "제가 즉시 처리할 수 있는 정규 명령어 예시입니다:\n"
            "• '루비아 채널 구독자 수는?'\n"
            "• '최근 영상 성과 어때?'\n"
            "• '대만 로파이 영상 제작해줘'\n\n"
            f"(LLM 대화 엔진 에러: `{str(e)}`)"
        )
        if rubia_img:
            with open(rubia_img, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo, caption=fallback_text, parse_mode="Markdown"
                )
        else:
            await update.message.reply_text(fallback_text, parse_mode="Markdown")
