# -*- coding: utf-8 -*-
"""
텔레그램 봇 메인 실행 파일 (Entry Point)
- python-telegram-bot v20+ 비동기 API 기준 설계
- 자연어 파서(nlp/intent_parser) 및 핸들러들을 연동하여 실행합니다.
- 복수 봇 토큰이 감지될 경우, 단일 이벤트 루프에서 병렬 기동하는 아키텍처를 적용했습니다.
"""

import sys
import os
import asyncio

# 프로젝트 루트 경로 추가 (모듈 로딩 방어)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from telegram_bot.config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_Taipei_Lofi_New_Bot_TOKEN,
    TELEGRAM_rubia_smart_bot_TOKEN,
    TELEGRAM_Youtube_Total_Music_Taipei_Lofi_New_Bot_TOKEN,
)

# 💡 [방어적 프로그래밍] telegram_bot.config와의 이름 충돌을 방지하기 위해 루트 config.py를 명시적으로 절대경로 로드합니다.
import importlib.util

_root_config_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.py"
)
_spec = importlib.util.spec_from_file_location("root_config", _root_config_path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
Config = _module.Config
from telegram_bot.nlp.intent_parser import (
    parse_intent,
    INTENT_GREETING,
    INTENT_CHANNEL_STATS,
    INTENT_RECENT_VIDEOS,
    INTENT_COMMENT_CHECK,
    INTENT_TEAM_STATUS,
    INTENT_HELP,
    INTENT_PLANNING,
    INTENT_PRODUCTION,
    INTENT_SOUND_LAB,
    INTENT_PAYPAL_CONNECT,
)
from telegram_bot.handlers.basic import (
    start_command,
    help_command,
    status_command,
    handle_greeting,
)


async def kill_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """긴급 상황 발생 시 로컬 봇 프로세스를 강제 종료합니다."""
    await update.message.reply_text(
        "🚨 긴급 정지 명령 수신. 로컬 봇 프로세스를 즉시 강제 종료합니다...", parse_mode="Markdown"
    )
    print("🚨 텔레그램 /kill 명령에 의해 프로세스를 강제 종료합니다.")
    os._exit(0)


async def llm_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """LLM 모드를 클라우드(Gemini)와 로컬(LM Studio/Ollama) 간에 스위칭합니다."""
    if not context.args:
        current_mode = context.bot_data.get("llm_mode", "cloud")
        local_url = context.bot_data.get("local_llm_url", "기본값 (.env 참조)")
        await update.message.reply_text(
            f"🧠 *현재 LLM 엔진 모드:* `{current_mode}`\n"
            f"🔗 *로컬 연결 주소:* `{local_url}`\n\n"
            "📋 *명령어 예시:*\n"
            "`/llm cloud` (구글 제미나이 사용)\n"
            "`/llm lmstudio` (LM Studio - 포트 1234)\n"
            "`/llm ollama` (Ollama - 포트 11434)",
            parse_mode="Markdown",
        )
        return

    mode = context.args[0].lower()
    if mode == "cloud":
        context.bot_data["llm_mode"] = "cloud"
        await update.message.reply_text(
            "☁️ *Gemini (클라우드)* 모드로 엔진 전환 완료!", parse_mode="Markdown"
        )
    elif mode in ["local", "lmstudio"]:
        context.bot_data["llm_mode"] = "local"
        # 💡 [한글 설명] 하드코딩된 API 주소 대신 중앙 Config의 LM_STUDIO_URL을 참조합니다.
        context.bot_data["local_llm_url"] = Config.LM_STUDIO_URL
        await update.message.reply_text(
            "🖥️ *LM Studio (포트 1234)* 모드로 엔진 전환 완료!", parse_mode="Markdown"
        )
    elif mode == "ollama":
        context.bot_data["llm_mode"] = "local"
        # 💡 [한글 설명] 하드코딩된 API 주소 대신 중앙 Config의 OLLAMA_URL을 참조합니다.
        context.bot_data["local_llm_url"] = Config.OLLAMA_URL
        await update.message.reply_text(
            "🦙 *Ollama (포트 11434)* 모드로 엔진 전환 완료!", parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "올바르지 않은 모드입니다. `cloud`, `lmstudio`, `ollama` 중 하나를 입력하세요.",
            parse_mode="Markdown",
        )


async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """하이브리드 추론 라우팅 모드를 전환합니다."""
    import telegram_bot.config as config

    if not context.args:
        mode_str = (
            "지능형 자동 전환 (Auto)"
            if config.HYBRID_ROUTING_MODE == "auto"
            else (
                "수동 로컬 강제 (Manual-Local)"
                if config.HYBRID_ROUTING_MODE == "manual_local"
                else "수동 클라우드 강제 (Manual-Cloud)"
            )
        )
        await update.message.reply_text(
            f"🧠 *현재 하이브리드 라우팅 모드:* `{mode_str}`\n\n"
            "📋 *명령어 사용법:*\n"
            "`/mode auto` : 지능형 자동 전환 (경량 로컬, 복합 클라우드)\n"
            "`/mode manual_local` : 로컬 LLM 강제 처리 (비용 제로화)\n"
            "`/mode manual_cloud` : 클라우드 LLM 강제 처리 (고성능 추론)",
            parse_mode="Markdown",
        )
        return

    mode = context.args[0].lower().strip()
    if mode == "auto":
        config.HYBRID_ROUTING_MODE = "auto"
        await update.message.reply_text(
            "🤖 *하이브리드 자동 라우팅(Auto)* 모드로 전환 완료!", parse_mode="Markdown"
        )
    elif mode == "manual_local":
        config.HYBRID_ROUTING_MODE = "manual_local"
        await update.message.reply_text(
            "🖥️ *수동 로컬 LLM 강제(manual_local)* 모드로 전환 완료!", parse_mode="Markdown"
        )
    elif mode == "manual_cloud":
        config.HYBRID_ROUTING_MODE = "manual_cloud"
        await update.message.reply_text(
            "☁️ *수동 클라우드 LLM 강제(manual_cloud)* 모드로 전환 완료!", parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "올바르지 않은 모드입니다. `auto`, `manual_local`, `manual_cloud` 중 하나를 입력하세요.",
            parse_mode="Markdown",
        )


async def index_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """옵시디언 및 로컬 지식 RAG DB를 증분 동기화(스캔 및 임베딩 인덱싱)합니다."""
    if not update.message:
        return

    status_msg = await update.message.reply_text(
        "🔄 *옵시디언 및 로컬 지식을 동기화합니다...*", parse_mode="Markdown"
    )

    try:
        from telegram_bot.engine.rag_retriever import index_vault_to_chroma

        # 1초 미만 증분 동기화 백그라운드 스레드 기동
        result = await asyncio.to_thread(index_vault_to_chroma)

        status = result.get("status")

        if status in ["blocked_limit", "blocked_api"]:
            title = "🚨 *[시스템 긴급 정지]*"
            reason = f"• **원인(Reason)**: {result.get('reason')}"
            solution = f"• **해결 방법(Solution)**: {result.get('solution')}"

            await status_msg.edit_text(
                f"{title}\n\n" f"{reason}\n" f"{solution}", parse_mode="Markdown"
            )
        elif status == "success":
            await status_msg.edit_text(
                f"✅ *RAG 지식 동기화 성공*\n\n" f"{result.get('report_message')}",
                parse_mode="Markdown",
            )
        else:
            await status_msg.edit_text(
                f"❌ *동기화 중 오류 발생*: `{result.get('report_message', '알 수 없는 오류')}`",
                parse_mode="Markdown",
            )

    except Exception as e:
        await status_msg.edit_text(
            f"🚨 *동기화 파이프라인 크래시*: `{str(e)}`", parse_mode="Markdown"
        )


from telegram_bot.handlers.channel_stats import (
    handle_channel_stats,
    handle_comment_check,
)
from telegram_bot.handlers.production import (
    handle_production,
    handle_approved_build,
    handle_callback_query,
    handle_paypal_connect,
)
from telegram_bot.handlers.planning import handle_planning
from telegram_bot.handlers.kpi_dashboard import (
    handle_kpi_command,
    kpi_scheduler_loop,
    handle_sound_lab,
)


async def gen_audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """단축 명령어: 즉시 음원 템플릿(Sound Lab) 기획 파이프라인을 가동합니다."""
    # 프로필에서 채널 추출하거나 기본값 사용
    bot_profile_key = context.bot_data.get("bot_profile")
    channel = "rubia"
    from telegram_bot.config import BOT_PROFILES

    if bot_profile_key and bot_profile_key in BOT_PROFILES:
        channel = BOT_PROFILES[bot_profile_key]["default_channel"]

    await handle_sound_lab(update, context, channel_key=channel)


# ─────────────────────────────────────────────
# 📡 통합 자연어 라우터 핸들러
# ─────────────────────────────────────────────


async def natural_language_router(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """모든 일반 텍스트 메시지를 차단 및 분석하여 올바른 핸들러로 매핑합니다."""
    if not update.message or not update.message.text:
        return

    text = update.message.text

    # 🚨 [세션 락(Session Lock) 메커니즘]
    # 5단계 파이프라인이 구동 중일 때는 대표님의 무작위 채팅이 상태값을 침범하여 파이프라인을 훼손하지 않도록 접근을 제한합니다.
    current_state = (
        context.chat_data.get("current_state") if context.chat_data else None
    )
    pipeline_busy_states = [
        "STATE_ASSET_PROCESSING",
        "STATE_PLANNING_PROCESSING",
        "STATE_BUILD_PROCESSING",
        "STATE_SOUND_LAB_PROCESSING",
    ]

    # 예외 명령어: '취소', '정지', '그만', 'cancel' 등은 락을 해제하고 즉시 종료할 수 있도록 통과시킵니다.
    if current_state in pipeline_busy_states and not any(
        kw in text for kw in ["취소", "정지", "그만", "cancel"]
    ):
        await update.message.reply_text(
            "⏳ *[제4연구소 보안 관제]*\n"
            "현재 에셋 제작 또는 렌더링 파이프라인이 안전 모드 하에 가동 중입니다.\n"
            "진행 중인 작업의 무결성 보호를 위해 대화창이 일시 잠금되었습니다.\n"
            "작업이 완료될 때까지 잠시 대기해 주십시오. (세션 취소를 원하시면 `취소`를 입력해 주세요.)",
            parse_mode="Markdown",
        )
        return

    # 🚨 1. 업로드 명령어 인터셉트 (최우선 처리)
    if "업로드" in text or "올려" in text:
        pending_upload = (
            context.chat_data.get("pending_upload_video") if context.chat_data else None
        )
        if pending_upload and os.path.exists(pending_upload):
            await update.message.reply_text("🚀 방금 완성된 영상을 유튜브 채널에 업로드를 시작합니다...")
            try:
                from telegram_bot.utils.youtube_uploader import upload_video_to_youtube
                from telegram_bot.config import CHANNEL_MAP

                channel_key = context.chat_data.get(
                    "pending_upload_channel_key", "rubia"
                )
                planning_script = context.chat_data.get("pending_upload_script", "")
                video_format = context.chat_data.get(
                    "pending_upload_video_format", "shorts"
                )
                conf = CHANNEL_MAP.get(channel_key)

                if conf:
                    token_file = conf.get("token_file", f"token_{channel_key}.json")

                    def run_upload():
                        return upload_video_to_youtube(
                            token_file,
                            pending_upload,
                            planning_script,
                            channel_key,
                            video_format=video_format,
                        )

                    video_id, video_url = await asyncio.to_thread(run_upload)

                    await update.message.reply_text(
                        f"🚀 *유튜브 업로드 성공!*\n"
                        f"• **채널**: `{conf['name']}`\n"
                        f"• **비디오 링크**: [유튜브에서 보기]({video_url})",
                        parse_mode="Markdown",
                    )
                else:
                    await update.message.reply_text("❌ 채널 매핑 정보를 찾을 수 없습니다.")
            except Exception as ue:
                import traceback

                traceback.print_exc()
                await update.message.reply_text(
                    f"🚨 *유튜브 업로드 실패*: `{str(ue)}`", parse_mode="Markdown"
                )
            finally:
                if context.chat_data:
                    context.chat_data["pending_upload_video"] = None
            return
        else:
            await update.message.reply_text("⚠️ 현재 기억하고 있는 완성된 영상이 없습니다. 새 영상을 기획할까요?")
            return

    # 🚨 최근 영상 조회 인터셉트
    if "최근 영상" in text or "최근영상" in text:
        from telegram_bot.handlers.channel_stats import handle_recent_videos

        await handle_recent_videos(update, context)
        return

    # 🚨 2. 자막 커스텀 스타일 설정 변경 감지 및 캐싱 (Few-Shot NLU 적용)
    style_keywords = [
        "색",
        "크기",
        "위",
        "아래",
        "올려",
        "내려",
        "폰트",
        "글꼴",
        "글자",
        "마진",
        "옐로우",
        "화이트",
        "레드",
        "블랙",
        "골드",
        "그린",
        "블루",
        "핑크",
        "옐로",
        "노란",
    ]
    if "자막" in text and ("초기화" in text or "리셋" in text):
        if context.chat_data is not None:
            context.chat_data["custom_style"] = {}
        await update.message.reply_text(
            "🧹 *자막 커스텀 스타일 설정이 기본값으로 초기화되었습니다.*", parse_mode="Markdown"
        )
        return

    if "자막" in text and any(kw in text for kw in style_keywords):
        from telegram_bot.engine.llm_client import generate_text
        import json

        # 시스템 프롬프트 (Few-Shot 예시 추가)
        sys_instruction = (
            "당신은 유튜브 숏폼/롱폼 자동화 봇의 '자막 스타일 분석 NLU 에이전트'입니다.\n"
            "사용자의 자연어 지시와 [현재 설정 상태]를 비교 분석하여, 최종적으로 변경되어야 할 속성만 아래 JSON 형식으로 추출하세요.\n"
            "절대 마크다운(```json)이나 부연 설명을 달지 말고 오직 순수 JSON만 출력하세요.\n\n"
            "{\n"
            '  "font_size": integer or null,\n'
            '  "margin_v": integer or null,\n'
            '  "primary_color": "string or null",\n'
            '  "font_name": "string or null"\n'
            "}\n\n"
            "[맥락 이해 규칙]\n"
            '1. 상대적 지시("더 크게", "조금 위로")가 오면, [현재 설정 상태]의 값을 기준으로 계산하여 새로운 정수값을 도출하세요.\n'
            "2. 색상은 영어명칭(예: yellow, red, black, white)으로 변환하세요.\n\n"
            "[Few-Shot 예시]\n"
            '현재: {"font_size": 80, "margin_v": 350} / 사용자: "글자 좀만 더 키워주고 노란색으로 해"\n'
            '출력: {"font_size": 90, "margin_v": null, "primary_color": "yellow", "font_name": null}\n\n'
            '현재: {"margin_v": 350} / 사용자: "자막이 너무 위에 있어. 많이 내려줘"\n'
            '출력: {"font_size": null, "margin_v": 200, "primary_color": null, "font_name": null}\n'
        )

        # 현재 세션에 저장된 자막 상태를 가져옵니다
        current_state = (
            context.chat_data.get("custom_style", {}) if context.chat_data else {}
        )
        prompt_payload = f"[현재 설정 상태]: {current_state}\n[사용자 지시]: {text}"

        try:
            llm_mode = context.bot_data.get("llm_mode", "cloud")
            local_url = context.bot_data.get("local_llm_url")

            if llm_mode == "cloud":
                from telegram_bot.config import GEMINI_API_KEY, YOUTUBE_API_KEY

                api_key = GEMINI_API_KEY or YOUTUBE_API_KEY
                if api_key:
                    from google import genai
                    from google.genai import types

                    client = genai.Client(api_key=api_key.split(",")[0].strip())

                    def call_gemini():
                        r = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt_payload,
                            config=types.GenerateContentConfig(
                                system_instruction=sys_instruction, temperature=0.0
                            ),
                        )
                        return r.text.strip()

                    response_text = await asyncio.to_thread(call_gemini)
                else:
                    response_text = await asyncio.to_thread(
                        generate_text,
                        prompt_payload,
                        sys_instruction,
                        mode="local",
                        local_url=local_url,
                    )
            else:
                response_text = await asyncio.to_thread(
                    generate_text,
                    prompt_payload,
                    sys_instruction,
                    mode="local",
                    local_url=local_url,
                )

            # JSON 추출 파싱
            import re

            json_match = re.search(r"\{.*\}", response_text.strip(), re.DOTALL)
            if json_match:
                parsed_style = json.loads(json_match.group(0))
            else:
                parsed_style = json.loads(response_text.strip())

            if context.chat_data is None:
                context.chat_data = {}

            if "custom_style" not in context.chat_data:
                context.chat_data["custom_style"] = {}

            updated_fields = []
            for key, val in parsed_style.items():
                if val is not None:
                    context.chat_data["custom_style"][key] = val
                    updated_fields.append(f"{key}: {val}")

            if updated_fields:
                print(f"💾 [Style Cache Updated] {context.chat_data['custom_style']}")
                style_desc = []
                style_info = context.chat_data["custom_style"]
                if "font_size" in style_info:
                    style_desc.append(f"• 📏 *크기*: `{style_info['font_size']}`")
                if "margin_v" in style_info:
                    style_desc.append(f"• 📍 *위치(마진)*: `{style_info['margin_v']}`")
                if "primary_color" in style_info:
                    style_desc.append(f"• 🎨 *색상*: `{style_info['primary_color']}`")
                if "font_name" in style_info:
                    style_desc.append(f"• 🔤 *폰트*: `{style_info['font_name']}`")

                style_desc_str = "\n".join(style_desc)
                await update.message.reply_text(
                    f"✍️ *자막 스타일 캐시가 성공적으로 업데이트되었습니다!*\n"
                    f"이후 제작 승인되는 비디오 렌더링 시 아래 스타일이 적용됩니다:\n\n"
                    f"{style_desc_str}\n\n"
                    f"💡 _초기화를 원하시면 '자막 스타일 초기화'라고 말해 주세요._",
                    parse_mode="Markdown",
                )
                return
        except Exception as style_err:
            print(f"⚠️ [Subtitle Style Parsing Error]: {style_err}")

    # 🚨 [승인 대기 모드 우선 처리] 기획 승인 대기 또는 에셋 승인 대기 상황에 따른 스마트 이중 라우팅 수행
    # 이 체크는 일반 의도 파싱보다 선행되어 진행됩니다.
    approval_keywords = [
        "진행해",
        "진행시켜",
        "영상 만들어",
        "영상만들어",
        "비디오 빌드",
        "비디오빌드",
        "렌더링",
        "렌더링해",
        "합성해",
        "합성해줘",
        "ok",
        "OK",
        "네",
        "오케이",
        "승인",
        "승인해",
        "좋아",
        "만들어줘",
        "제작해",
        "제작해줘",
        "최종 완성",
        "확정",
        "실행",
        "고",
        "진행",
    ]
    # 💡 [방어적 프로그래밍] '1번 프리셋으로 진행해'처럼 프리셋 설정 키워드가 들어간 경우는 승인 명령에서 제외합니다.
    has_preset_keyword = any(
        p_kw in text for p_kw in ["1번", "2번", "3번", "4번", "일번", "이번", "삼번", "사번"]
    )

    if any(kw in text for kw in approval_keywords) and not has_preset_keyword:
        current_state = (
            context.chat_data.get("current_state") if context.chat_data else None
        )

        # [라우팅 분기 1] 기획 완료 후 승인 -> 에셋 생성(handle_production)으로 전환
        if current_state == "STATE_PLANNING_DONE":
            print("🔌 [라우터 교정] 기획 승인 확인 -> 에셋 생성(handle_production)으로 배관 전환")
            if context.chat_data is not None:
                context.chat_data["current_state"] = "STATE_ASSET_PROCESSING"
            return await handle_production(update, context)

        # [라우팅 분기 2] 에셋 대기 완료 후 최종 승인 -> FFmpeg 빌드(handle_approved_build)로 전환
        has_pending = context.chat_data and context.chat_data.get(
            "awaiting_build_approval"
        )
        if current_state == "STATE_ASSET_STANDBY" or has_pending:
            # 💡 [자막 간편 프리셋 번호 파싱 및 자막 스타일 캐시 맵핑]
            if "1번" in text:
                if context.chat_data is None:
                    context.chat_data = {}
                if "custom_style" not in context.chat_data:
                    context.chat_data["custom_style"] = {}
                context.chat_data["custom_style"].update(
                    {
                        "font_name": "Malgun Gothic",
                        "font_size": 80,
                        "margin_v": 350,
                        "primary_color": "white",
                        "border_style": 1,
                        "shadow": 1,
                    }
                )
                print("🔢 [Preset Action] 1번 클래식 시네마 프리셋이 자막 스타일 캐시에 적용되었습니다.")
            elif "2번" in text:
                if context.chat_data is None:
                    context.chat_data = {}
                if "custom_style" not in context.chat_data:
                    context.chat_data["custom_style"] = {}
                context.chat_data["custom_style"].update(
                    {
                        "font_name": "Malgun Gothic",
                        "font_size": 80,
                        "margin_v": 350,
                        "primary_color": "#FFEC94",  # 파스텔 노랑
                        "border_style": 3,  # 반투명 음영 박스
                        "shadow": 0,
                    }
                )
                print("🔢 [Preset Action] 2번 아늑한 다락방 프리셋이 자막 스타일 캐시에 적용되었습니다.")
            elif "3번" in text:
                if context.chat_data is None:
                    context.chat_data = {}
                if "custom_style" not in context.chat_data:
                    context.chat_data["custom_style"] = {}
                context.chat_data["custom_style"].update(
                    {
                        "font_name": "Batang",  # 명조체
                        "font_size": 80,
                        "margin_v": 350,
                        "primary_color": "white",
                        "border_style": 1,
                        "shadow": 3,  # 소프트 그림자
                    }
                )
                print("🔢 [Preset Action] 3번 숲속의 고요 프리셋이 자막 스타일 캐시에 적용되었습니다.")

            # 💡 [방어적 프로그래밍 - 봇 재부팅 후 세션 복원]
            if not has_pending:
                import time
                import glob

                channel_key = "rubia"

                # outputs/shorts 및 outputs/longform 둘 다 스캔
                recent_imgs = []
                recent_audios = []

                search_paths = [
                    f"c:/1인기업/Apps/유튜브에이전트/outputs/shorts/{channel_key}",
                    f"c:/1인기업/Apps/유튜브에이전트/outputs/longform/{channel_key}",
                    f"c:/1인기업/Apps/유튜브에이전트/output/{channel_key}",
                    f"c:/1인기업/Apps/유튜브에이전트/input/{channel_key}/images",
                ]

                for path in search_paths:
                    if os.path.exists(path):
                        recent_imgs.extend(glob.glob(f"{path}/*.png"))
                        recent_audios.extend(glob.glob(f"{path}/*.mp3"))

                recent_imgs = sorted(recent_imgs, key=os.path.getmtime, reverse=True)
                recent_audios = sorted(
                    recent_audios, key=os.path.getmtime, reverse=True
                )

                if recent_imgs and recent_audios:
                    img_age = time.time() - os.path.getmtime(recent_imgs[0])
                    audio_age = time.time() - os.path.getmtime(recent_audios[0])
                    # 둘 다 15분(900초) 이내에 생성된 자산인 경우 세션 복원
                    if img_age <= 900 and audio_age <= 900:
                        print(
                            "💾 [Router] 봇 재시작으로 유실된 승인 세션 감지. 15분 이내 최신 에셋을 확인하여 세션을 복원합니다."
                        )
                        try:
                            restored_output_dir = os.path.dirname(recent_imgs[0])
                            restored_format = "shorts"
                            if "longform" in restored_output_dir.lower():
                                restored_format = "longform"

                            context.chat_data["awaiting_build_approval"] = True
                            context.chat_data["current_state"] = "STATE_ASSET_STANDBY"
                            context.chat_data["pending_visual"] = recent_imgs[0]
                            context.chat_data["pending_audio"] = recent_audios[0]
                            context.chat_data["pending_channel_key"] = channel_key
                            context.chat_data["pending_video_format"] = restored_format
                            context.chat_data["pending_video_length"] = 1
                            context.chat_data["pending_output_path"] = os.path.join(
                                restored_output_dir,
                                f"{channel_key}_{restored_format}_v1.mp4",
                            )
                            context.chat_data[
                                "pending_output_dir"
                            ] = restored_output_dir
                            context.chat_data[
                                "asset_creation_timestamp"
                            ] = os.path.getmtime(recent_imgs[0])
                        except Exception as restore_err:
                            print(
                                f"⚠️ [Session Restore Error] 세션 강제 주입 실패: {restore_err}"
                            )

            # 승인 대기 상태 검증 (복원되었거나 기존에 있었던 경우 실행)
            if context.chat_data and context.chat_data.get("awaiting_build_approval"):
                await handle_approved_build(update, context)
                return

    # 🚨 [에러 후 재시도 세션 유지 처리]
    # 에셋 생성 에러가 발생한 지 5분 이내이고, 대표님이 재시도 명령을 내린 경우
    if context.chat_data and context.chat_data.get("awaiting_error_retry"):
        import time

        err_context = context.chat_data.get("error_retry_context", {})
        err_ts = err_context.get("timestamp", 0)
        # 5분(300초) 이내의 요청인지 확인
        if time.time() - err_ts <= 300:
            retry_keywords = [
                "재시도해",
                "다시 해봐",
                "다시시도",
                "다시해봐",
                "재시도",
                "retry",
                "Retry",
                "다시 해",
                "다시해",
            ]
            if any(kw in text for kw in retry_keywords):
                print("🔄 [Router] 5분 이내 대표님 재시도 명령 감지. 캐시된 세션으로 재호출 시작.")
                channel_key = err_context.get("channel_key", "rubia")
                await handle_production(update, context, channel_key=channel_key)
                return
        else:
            # 5분이 지나면 재시도 세션을 안전하게 파기
            context.chat_data["awaiting_error_retry"] = False
            context.chat_data["error_retry_context"] = None
            print("🧹 [Router] 재시도 유효 시간 5분 초과. 컨텍스트 세션 파기.")

    # 봇의 상태에서 LLM 모드 및 로컬 URL 로드
    llm_mode = context.bot_data.get("llm_mode", "cloud")
    local_url = context.bot_data.get("local_llm_url")

    # 💡 [진행 상태 알림] 텔레그램 채팅창에 엔진 가동 상태 출력
    status_msg = None
    try:
        status_msg = await update.message.reply_text(
            "☁️ [LLM Client] 구글 Gemini 클라우드 엔진 가동 중...", parse_mode="Markdown"
        )
    except Exception as e:
        print(f"⚠️ 상태 메시지 전송 실패: {e}")

    # 1. 100% LLM (Gemini Function Calling) 기반 의도/채널 파싱
    analysis = await parse_intent(text, llm_mode=llm_mode, local_url=local_url)

    # 💡 [진행 상태 알림] 분석이 완료되면 상태 메시지 자동 삭제
    if status_msg:
        try:
            await status_msg.delete()
        except Exception:
            pass

    intent = analysis["intent"]
    channel = analysis["channel"]

    # 💡 [방어적 프로그래밍] 사용자가 메시지에 명시적으로 채널 관련 키워드를 언급했는지 확인
    # 언급하지 않았다면, LLM의 채널 판별을 무시하고 현재 봇 프로필의 디폴트 채널을 강제 적용합니다.
    bot_profile_key = context.bot_data.get("bot_profile")
    from telegram_bot.config import BOT_PROFILES, CHANNEL_MAP

    if bot_profile_key and bot_profile_key in BOT_PROFILES:
        profile = BOT_PROFILES[bot_profile_key]
        profile["allowed_channels"]

        # 메시지 텍스트에서 명시적 채널 키워드 감지 시도
        has_explicit_channel_keyword = False
        all_aliases = []
        for ch_key in CHANNEL_MAP:
            all_aliases.extend(CHANNEL_MAP[ch_key].get("aliases", []))

        for alias in all_aliases:
            if alias in text.lower():
                has_explicit_channel_keyword = True
                break

        # 명시적인 채널 키워드가 텍스트에 없는 경우, 현재 봇의 기본 채널로 강제 적용
        if not has_explicit_channel_keyword:
            channel = profile["default_channel"]

    # 디버그 로그
    print(
        f"[NLP Log] Raw Text: '{text}' -> Intent: '{intent}', Final Channel: '{channel}'"
    )

    # 2. 의도에 따라 라우팅
    if intent == INTENT_CHANNEL_STATS:
        await handle_channel_stats(update, context, channel_key=channel)
    elif intent == INTENT_RECENT_VIDEOS:
        await handle_recent_videos(update, context, channel_key=channel)
    elif intent == INTENT_COMMENT_CHECK:
        await handle_comment_check(update, context, channel_key=channel)
    elif intent == INTENT_PLANNING:
        # 🚨 [모순 지시어 감지] 숏폼 키워드 + 2분 이상 분량 등 충돌 시 기획 차단 및 안내
        if analysis.get("conflict_detected"):
            clarification_msg = (
                "💡 **포맷 충돌 감지 알림**\n\n"
                "대표님, 유튜브 정책상 **쇼츠(Shorts)는 1분 미만**이어야 합니다.\n"
                "요청하신 분량을 살려 **[롱폼(가로형)]**으로 기획할까요? "
                "아니면 1분 이내의 **[쇼츠(세로형)]**로 압축해서 기획할까요?\n\n"
                "_(답변 예시: '롱폼으로 해줘' 또는 '쇼츠로 진행해')_"
            )
            await update.message.reply_text(clarification_msg, parse_mode="Markdown")
            return
        # 💡 [버그 수정] intent_parser가 도출한 video_format, video_length를 세션에 저장
        # planning.py가 이 값을 읽어 숏폼/롱폼을 정확히 분기합니다.
        if context.chat_data is not None:
            context.chat_data["target_format"] = analysis.get("video_format", "shorts")
            context.chat_data["target_length"] = analysis.get("video_length", 1)
        await handle_planning(update, context, channel_key=channel)
    elif intent == INTENT_PRODUCTION:
        # 💡 [동일 적용] 제작 핸들러에도 포맷/길이 파라미터 전달
        if context.chat_data is not None:
            context.chat_data["target_format"] = analysis.get("video_format", "shorts")
            context.chat_data["target_length"] = analysis.get("video_length", 1)
        await handle_production(update, context, channel_key=channel)
    elif intent == INTENT_SOUND_LAB:
        # [독립 라우팅 분기] 음원 템플릿 독립 생성 (영상 조립 배제)
        await handle_sound_lab(update, context, channel_key=channel)
    elif intent == INTENT_PAYPAL_CONNECT:
        # [독립 라우팅 분기] 페이팔 MCP 연결 브리핑 가이드 호출
        await handle_paypal_connect(update, context)
    elif intent == INTENT_TEAM_STATUS:
        await status_command(update, context)
    elif intent == INTENT_HELP:
        await help_command(update, context)
    elif intent == INTENT_GREETING:
        await handle_greeting(update, context)
    else:
        # 감지되지 않은 의도(INTENT_UNKNOWN 등)나 일반 대화는 루비아 비서실장이 직접 응답합니다.
        from telegram_bot.handlers.chat import handle_chat

        await handle_chat(update, context)


# ─────────────────────────────────────────────
# 🛡️ 에러 핸들러
# ─────────────────────────────────────────────


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """봇 실행 도중 예기치 못한 예외가 발생했을 때 로그를 남기고 비정상 종료를 방지합니다."""
    print(f"⚠️ [Telegram Bot Error]: {context.error}")


# ─────────────────────────────────────────────
# 🚀 봇 인스턴스 초기화 함수
# ─────────────────────────────────────────────


async def build_and_start_bot(
    profile_key: str | None, token: str, display_name: str
) -> object:
    """개별 봇 인스턴스를 빌드하고 폴링을 개시합니다."""
    # 1. 애플리케이션 빌드 (네트워크 타임아웃 30초로 넉넉하게 연장)
    application = (
        ApplicationBuilder()
        .token(token)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .build()
    )

    # 2. 프로필 저장 (핸들러에서 조회용)
    application.bot_data["bot_profile"] = profile_key

    # 3. 핸들러 등록
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("kill", kill_command))
    application.add_handler(CommandHandler("llm", llm_command))
    application.add_handler(CommandHandler("mode", mode_command))
    application.add_handler(CommandHandler("index", index_command))
    application.add_handler(CommandHandler("kpi", handle_kpi_command))
    application.add_handler(CommandHandler("gen_audio", gen_audio_command))

    # 일반 메시지 (자연어 및 미지정 텍스트) 라우터
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, natural_language_router)
    )

    # ⚙️ API 에러 팝업 의사결정용 콜백 쿼리 핸들러 등록
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    # ⚙️ 양방향 파일 수신 핸들러 등록 (대표님이 보낸 문서, 사진, 오디오, 비디오)
    from telegram_bot.handlers.file_receiver import handle_file_upload

    application.add_handler(
        MessageHandler(
            (filters.Document.ALL | filters.PHOTO | filters.AUDIO | filters.VIDEO)
            & ~filters.COMMAND,
            handle_file_upload,
        )
    )

    # 글로벌 에러 핸들러
    application.add_error_handler(error_handler)

    # 4. 초기화 및 시작
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    print(f"✅ {display_name} 가동 완료 및 폴링 대기 중...")
    return application


# ─────────────────────────────────────────────
# 🚀 메인 비동기 실행 루프
# ─────────────────────────────────────────────


async def run_bots_async(bot_filter: str = None) -> None:
    apps = []

    # 1. 각 토큰 확인 후 개별/복수 실행 개시
    # 로파이 대만 채널 전용 봇 (@Taipei_Lofi_New_Bot)
    if (
        (bot_filter is None or bot_filter == "rofi")
        and TELEGRAM_Taipei_Lofi_New_Bot_TOKEN
        and TELEGRAM_Taipei_Lofi_New_Bot_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN_HERE"
    ):
        app = await build_and_start_bot(
            "rofi",
            TELEGRAM_Taipei_Lofi_New_Bot_TOKEN,
            "로파이 대만 봇 (@Taipei_Lofi_New_Bot)",
        )
        apps.append(app)

    # Aura 및 스마트에이지 채널 전용 봇 (@rubia_smart_bot)
    if (
        (bot_filter is None or bot_filter == "aura")
        and TELEGRAM_rubia_smart_bot_TOKEN
        and TELEGRAM_rubia_smart_bot_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN_HERE"
    ):
        app = await build_and_start_bot(
            "aura", TELEGRAM_rubia_smart_bot_TOKEN, "Aura & 스마트에이지 봇 (@rubia_smart_bot)"
        )
        apps.append(app)

    # Youtube 분석가 채널 전용 봇 (@Taipei_Lofi_New_Bot_Analyst)
    # 대안 3에 따라, 기본 구동(bot_filter is None) 시에는 analyst 봇을 기동하지 않고
    # 오직 명시적으로 'analyst' 필터가 인자로 주어졌을 때만 기동합니다.
    if (
        bot_filter == "analyst"
        and TELEGRAM_Youtube_Total_Music_Taipei_Lofi_New_Bot_TOKEN
        and TELEGRAM_Youtube_Total_Music_Taipei_Lofi_New_Bot_TOKEN
        != "YOUR_TELEGRAM_BOT_TOKEN_HERE"
    ):
        app = await build_and_start_bot(
            "analyst",
            TELEGRAM_Youtube_Total_Music_Taipei_Lofi_New_Bot_TOKEN,
            "유튜브 분석가 봇 (@Taipei_Lofi_New_Bot_Analyst)",
        )
        apps.append(app)

    # 기본 단일 통합 봇 (이전 세팅 폴백)
    if (
        not apps
        and TELEGRAM_BOT_TOKEN
        and TELEGRAM_BOT_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN_HERE"
    ):
        app = await build_and_start_bot(None, TELEGRAM_BOT_TOKEN, "통합 관리 채널 봇")
        apps.append(app)

    # 등록된 봇이 없을 경우 경고 메시지 출력 후 종료
    if not apps:
        print("=" * 60)
        print("🚨 오류: 설정된 텔레그램 봇 토큰이 없습니다!")
        print("  - 프로젝트 루트의 `.env` 파일에 아래 토큰을 하나 이상 기입해주세요:")
        print("    TELEGRAM_ROFI_BOT_TOKEN=...  (로파이 대만용)")
        print("    TELEGRAM_AURA_BOT_TOKEN=...  (아우라/스마트용)")
        print("    또는 TELEGRAM_BOT_TOKEN=...  (통합 채널용)")
        print("=" * 60)
        return

    print(f"\n📡 총 {len(apps)}개의 에이전트 봇이 단일 프로세스에서 동시에 구동 중입니다.")
    print("대표님의 원격 명령을 실시간 대기하고 있습니다... (Ctrl + C 누르면 안전 종료)")

    # ⏰ KPI 매일 아침 09:00 정기 브리핑 스케줄러 태스크 구동
    asyncio.create_task(kpi_scheduler_loop(apps[0]))

    # 2. 프로세스 활성 상태 유지
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit, asyncio.CancelledError):
        print("\n🛑 종료 요청을 수신했습니다. 봇 안전 종료를 개시합니다...")
    finally:
        # 안전한 종료 처리
        for app in apps:
            profile = app.bot_data.get("bot_profile") or "통합"
            print(f"🔌 [{profile}] 봇 폴링 중지 및 세션 정리 중...")
            try:
                await app.updater.stop()
                await app.stop()
                await app.shutdown()
            except Exception as e:
                print(f"⚠️ [{profile}] 봇 정리 중 오류: {e}")
        print("✅ 모든 에이전트 봇이 정상적으로 비활성화되었습니다.")


def main():
    """메인 진입점: 비동기 루프 기동"""
    bot_filter = None
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower().strip()
        if arg in ["rofi", "aura", "analyst"]:
            bot_filter = arg

    try:
        asyncio.run(run_bots_async(bot_filter))
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    main()
