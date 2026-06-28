# -*- coding: utf-8 -*-
"""
유튜브 동영상(숏폼 및 롱폼) 기획 및 대본 작성을 위한 AI 핸들러
- google-generativeai 라이브러리를 통해 Gemini API를 호출합니다.
- 기획팀장 '라비아(Ravia)' 페르소나를 사용하여 특화된 프롬프트를 처리합니다.
"""

import asyncio
import google.generativeai as genai
from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.config import (
    GEMINI_API_KEY,
    YOUTUBE_API_KEY,
    CHANNEL_MAP,
    CHANNEL_IDENTITIES,
)
from telegram_bot.utils.image_helper import get_agent_image_path
from telegram_bot.handlers.basic import check_permission

# ─────────────────────────────────────────────
# 🧠 Gemini API 클라이언트 설정
# ─────────────────────────────────────────────
api_key = GEMINI_API_KEY or YOUTUBE_API_KEY
if api_key:
    genai.configure(api_key=api_key)


@check_permission
async def handle_planning(
    update: Update, context: ContextTypes.DEFAULT_TYPE, channel_key: str = None
) -> None:
    """기획팀장 라비아가 Gemini API를 이용해 동영상(숏폼/롱폼) 기획 및 대본을 작성하는 핸들러"""
    if not update.message:
        return

    user_message = update.message.text

    # 💡 기획은 라비아가 담당
    working_img = get_agent_image_path("ravia", "working")
    success_img = get_agent_image_path("ravia", "success")

    # 채널 기본값 매핑
    bot_profile_key = context.bot_data.get("bot_profile")
    from telegram_bot.config import BOT_PROFILES

    if not channel_key:
        if bot_profile_key and bot_profile_key in BOT_PROFILES:
            channel_key = BOT_PROFILES[bot_profile_key]["default_channel"]
        else:
            channel_key = "rubia"

    # 채널 프로필 권한 체크
    from telegram_bot.handlers.channel_stats import (
        _check_bot_permission_and_get_channels,
    )

    target_channels, _, is_error = await _check_bot_permission_and_get_channels(
        update, context, channel_key
    )
    if is_error:
        return

    conf = CHANNEL_MAP.get(channel_key)
    identity = CHANNEL_IDENTITIES.get(channel_key, "일반 동영상 크리에이터 채널")

    # 💡 [보완] 대상 비디오 포맷(shorts/longform) 및 시간(video_length) 파악
    # context.chat_data에 캐싱된 정보가 없다면 intent_parser를 통해 직접 판별
    video_format = "shorts"
    video_length = 1

    if context.chat_data is not None:
        video_format = context.chat_data.get("target_format", "shorts")
        video_length = context.chat_data.get("target_length", 1)
    else:
        # 폴백 판별
        from telegram_bot.nlp.intent_parser import parse_intent_fallback

        analysis = parse_intent_fallback(user_message)
        video_format = analysis.get("video_format", "shorts")
        video_length = analysis.get("video_length", 1)

    # 세션 데이터 동기화
    if context.chat_data is not None:
        context.chat_data["last_planning_format"] = video_format
        context.chat_data["last_planning_length"] = video_length

    format_label = (
        "숏폼(Shorts, 9:16)"
        if video_format == "shorts"
        else f"롱폼(Long-form, 16:9, {video_length}분)"
    )

    # 로딩 알림 전송 (라비아 작업 이미지 포함)
    load_msg = f"💡 *기획팀장 라비아*가 `{conf['name']}` 채널의 정체성에 맞춘 {format_label} 기획서를 구성하고 있습니다. 잠시만 기다려주세요..."
    if working_img:
        with open(working_img, "rb") as photo:
            status_msg = await update.message.reply_photo(
                photo=photo, caption=load_msg, parse_mode="Markdown"
            )
    else:
        status_msg = await update.message.reply_text(load_msg, parse_mode="Markdown")

    try:
        llm_mode = context.bot_data.get("llm_mode", "cloud")
        local_url = context.bot_data.get("local_llm_url")

        # 💡 [RAG 지식 검색기 연동 - Multi-path & Incremental Sync 기반]
        rag_context = ""
        try:
            from telegram_bot.engine.rag_retriever import retrieve_relevant_knowledge

            # 대표님의 자연어 메시지를 쿼리로 삼아 로컬 지식 RAG DB를 비동기식으로 조회
            rag_context = await asyncio.to_thread(
                retrieve_relevant_knowledge, user_message
            )
        except Exception as rag_err:
            print(f"⚠️ [RAG Retrieve Error] planning 핸들러 내 지식 검색 실패: {rag_err}")

        # 채널별 영상물 및 메타데이터 전용 언어 규칙 설정
        language_rule = ""
        if channel_key == "aura":
            language_rule = "- **언어 규정 (영문 전용)**: 작성되는 영상 제목(Title), 설명란(Description), 해시태그 및 대본의 대사/자막(Script) 본문 내용은 **오직 영어(English)**로만 작성되어야 합니다. 한국어, 대만어, 일본어는 절대 단 한 단어도 포함하지 마십시오.\n"
        elif channel_key in ["rubia", "taipei"]:
            language_rule = "- **언어 규정 (대만어 및 일본어 전용)**: 작성되는 영상 제목(Title), 설명란(Description), 해시태그 및 대본의 대사/자막(Script) 본문 내용은 **대만 번체자(繁體中文)와 일본어(日本語)**만을 사용하여 작성되어야 합니다. 한국어의 사용은 완전히 제외하십시오.\n"
        elif channel_key == "smartage":
            language_rule = "- **언어 규정 (한국어 전용)**: 작성되는 영상 제목(Title), 설명란(Description), 해시태그 및 대본의 대사/자막(Script) 본문 내용은 **오직 한국어(Korean)**로만 작성되어야 합니다. 국내 시니어 타겟이므로 이해하기 쉬운 친절한 한글 경어체로 작성하십시오.\n"
        else:
            language_rule = "- **언어 규정**: 영상물 텍스트 및 대본은 채널의 타겟 국가 정체성 언어에 맞춰 작성하되, 국내 채널인 경우에는 한국어를 사용하고, 해외 채널인 경우에는 한국어를 철저히 배제해 주십시오.\n"

        # RAG 지식 주입 여부 결정 및 마크다운 포맷 바인딩
        rag_injection = ""
        if rag_context:
            rag_injection = f"\n\n[로컬 지식 참고(Obsidian & AI Connect)]:\n{rag_context}\n"

        language_hard_lock = (
            "🚨 **[최고 우선순위 언어 강제 규칙 (Language Hard-Lock)]** 🚨\n"
            "1. 현재 제공된 [로컬 지식 참고] 데이터나 사용자의 지시어가 '한국어'로 작성되어 있더라도, 이는 기획의 '내용과 세계관'을 파악하기 위한 용도일 뿐입니다.\n"
            "2. 해외 타겟 채널(글로벌 로파이, 웰니스 등)의 경우, 최종 생성되는 **영상 대본(자막), 제목, 설명란, 태그에는 단 한 글자의 한국어도 포함되어서는 안 됩니다.**\n"
            "3. 중간에 한국어가 섞이는 혼용 출력을 엄격히 금지하며, 반드시 **100% 완벽한 영문(또는 설정된 타겟 국가 언어)**으로만 번역 및 작성하여 출력하십시오.\n\n"
        )

        # 💡 [방어적 프로그래밍] 감성 채널의 몰입도를 유지하기 위해 기계적/기술적 메타데이터(포맷, AI 툴 명칭 등)가 설명란 및 기획서 전반에 출력되는 현상을 차단합니다.
        global_metadata_ban = (
            "🚫 **[전역 메타데이터 및 AI 출처 차단 규칙]**\n"
            "1. 적용 범위: 영상 제목, 설명란, 해시태그, 대본(자막), 영상 기획 의도를 포함한 **당신이 출력하는 모든 텍스트**.\n"
            "2. 영상의 기술적 포맷(예: Long-form, 16:9 Landscape, Shorts, 해상도 등)을 기계적으로 명시하는 것을 절대 금지합니다.\n"
            "3. AI 툴 이름(Lyria 3 Pro, Imagen 4.0 등), 자동화 시스템(Automated Production Flow V2.0), AI 작곡, AI 생성 등의 **제작 방식과 관련된 모든 단어의 사용을 전 구역에서 원천 차단**합니다.\n"
            "4. 설명란에 들어가는 `[Video Info]` 블록은 Format, Audio, System 같은 딱딱한 구조나 위 금지어들을 완전히 삭제하고, 오직 **'전체 재생 시간', '이미지의 분위기', '음원의 분위기'**만을 부드럽고 감성적인 문장으로 요약하여 작성하십시오. (다른 내용과 중복되면 제외)\n"
            "5. 오직 시청자가 온전히 음악과 분위기에 몰입할 수 있도록, 순수하고 감성적인 문구와 채널의 세계관만을 작성하십시오.\n\n"
        )

        self_verification = (
            "\n\n🔍 **[최종 출력 전 2차 자체 검증 (Self-Verification) 필수 수행]**\n"
            "대본과 기획안 작성을 완료한 후, 즉시 화면에 출력하지 말고 내부적으로 아래의 2차 검증을 반드시 거치십시오.\n"
            "1. 검증 대상: 제안하는 영상 제목, 설명란, 해시태그, 영상 대본(자막/멘트) 전체\n"
            "2. 검증 기준: 해외 채널 타겟임에도 불구하고 위 대상 영역에 '한국어'가 단 한 글자라도 섞여 들어갔는지 스캔하십시오. (단, 대표님께 드리는 앞뒤 안내 멘트는 한국어 유지)\n"
            "3. 교정 조치: 만약 자막이나 본문에 한국어가 섞인 것이 발견되었다면, 해당 부분을 100% 완벽한 타겟 국가 언어(영어 등)로 즉시 번역 및 교정하십시오.\n"
            "4. 최종 출력: 이 2차 검증과 교정이 모두 끝난, 언어 규정을 100% 통과한 무결점 결과물만 최종적으로 출력하십시오."
        )

        system_instruction = (
            f"[현재 엔진 모드: {llm_mode}]\n"
            "당신은 루비아(Rubia) 팀의 기획팀장 '라비아(Ravia)'입니다.\n"
            f"{language_hard_lock}"
            f"{global_metadata_ban}"
            "대표님께 기획 결과를 보고하고 안내하는 멘트(브리핑)는 똑똑하고 생기발랄한 한국어로 작성하되, "
            "**실제 제안하는 유튜브 영상 제목, 설명란, 태그, 그리고 영상 대본(자막/멘트) 본문**은 반드시 아래 [언어 규정]을 100% 준수하여 해당 외국어로만 생성하십시오.\n\n"
            f"{language_rule}\n"
            "- **⚠️ 절대 금지어 지침**: 기획서 전체 내용에서 **'AI', '인공지능', '자동화', 'Automation', 'Artificial' 등의 단어는 절대 사용할 수 없습니다.** 기술/시스템 관련 서술이 필요하다면 '스마트 시스템', '디지털 라이프', '사운드 믹싱', '지능형 도구' 등의 대체 용어로 우회하여 표현하십시오.\n"
            "- **📺 자막 기획 원칙**: 영상과 음악의 온전한 감상을 방해하지 않도록 **자막의 간격은 빽빽하지 않고 은은하게(예: 8초~15초 간격으로 짧고 감성적인 핵심 메시지만 분산 배치)** 대본을 설계하십시오.\n"
            "- **💡 [지식 활용 원칙]**: 제공된 로컬 지식 중 과거의 낡은 정보나 사용자의 현재 지시와 상충하는 내용이 있다면 과감히 배제하십시오. 로컬 지식은 채널의 핵심 세계관과 고유한 문체를 유지하는 '참고용'으로만 활용하며, 항상 최신 트렌드와 사용자의 직접 지시를 최우선으로 반영하여 기획하십시오."
            f"{rag_injection}"
            f"{self_verification}"
        )

        # 💡 [롱폼 포맷 제약 해제 지시] 롱폼일 때 숏폼(1분) 제약을 풀고 충분한 분량을 확보하도록 지시
        if video_format == "longform":
            format_instruction = (
                f"\n\n💡 **[포맷 지시 - 롱폼(Long-form)]**: 본 기획안은 16:9 가로형 규격의 롱폼 영상(Long-form, {video_length}분)입니다. "
                "1분 이내의 시간 제약이 없으므로, 티저나 쇼츠 형태로 압축하지 마십시오. "
                f"사용자가 요청한 {video_length}분을 온전히 채울 수 있도록 충분한 서사와 넉넉한 대본 분량을 확보하여 깊이 있게 기획하십시오."
            )
        else:
            format_instruction = (
                f"\n\n💡 **[포맷 지시 - 숏폼(Shorts)]**: 본 기획안은 9:16 세로형 규격의 유튜브 쇼츠({video_length}분 이내)입니다. "
                "짧고 강렬한 임팩트에 집중하여 기획하십시오."
            )
        system_instruction += format_instruction

        # 비디오 포맷에 따른 지시 프롬프트 분기
        if video_format == "longform":
            prompt = f"""
            대표님으로부터 유튜브 {video_length}분 롱폼(Long-form, 16:9 가로형) 영상 기획 지시를 받았습니다: "{user_message}"

            이 채널의 이름은 "{conf['name']}" 이며, 채널의 기획 정체성은 다음과 같습니다:
            [{identity}]

            보고서 구성 내용:
            1. 🎯 [기획 콘셉트] - 이번 {video_length}분 영상의 타겟 시청층 및 가로형 레이아웃 연출 방향성
            2. 💡 [영상 제목 및 썸네일 추천] - 클릭율을 유도할 3가지 매혹적인 제목과 16:9 썸네일 구도 제안
            3. 🎵 [플레이리스트 및 음원 트랙 구성]
               - 총 {video_length}분의 흐름에 맞춘 음악(Lo-fi 또는 Meditative Ambient) 트랙 구성 및 분할 구성안
               - 예: {video_length}분이 5분 이상인 경우 최소 3분짜리 음원을 여러 개 합치는 구성 방식을 제안 (3분 x N개 구성)
            4. 🎬 [{video_length}분 자막 대본]
               - 타임라인별 자막(자막: 텍스트)을 구체적인 시간 단위(초/분)로 기입하여 롱폼 비디오 인코딩에 연동될 수 있도록 기입
               - 대사와 시각 묘사(화면 연출)를 상세히 포함
            5. 💫 [시각 효과 및 오디오 연출 가이드] - 배경 이미지/동영상 연출 기획 및 특수효과 제안
            6. 📝 [유튜브 최종 업로드 메타데이터]
               - 유튜브에 실제로 업로드될 최종 확정 **제목(Title), 설명란(Description), 해시태그(Hashtags)** 작성
               - 설명란 하단에 전체 재생 시간, 이미지/음원 분위기를 담은 감성적인 `[Video Info]` 블록 포함
            """
        else:
            prompt = f"""
            대표님으로부터 유튜브 쇼츠(Shorts, 9:16 세로형, {video_length}분 이내) 기획 지시를 받았습니다: "{user_message}"

            이 채널의 이름은 "{conf['name']}" 이며, 채널의 기획 정체성은 다음과 같습니다:
            [{identity}]

            보고서 구성 내용:
            1. 🎯 [기획 콘셉트] - 이번 쇼츠 영상의 핵심 타겟층 및 연출 의도 설명
            2. 💡 [영상 제목 및 썸네일 추천] - 클릭율을 높일 3가지 기발한 제목과 9:16 쇼츠 커버 디자인 제안
            3. 🎬 [쇼츠 대본]
               - 0~5초: 강력한 후킹(Hooking) 연출 및 멘트
               - 5초 ~ 끝: 본론 및 자막 멘트 (자막: 텍스트 형태로 작성하여 자막 파서 연동)
               - 아웃트로: 시청자 유도(CTA) 및 댓글 참여 유도 멘트
            4. 🎵 [BGM 및 시각 효과 제안] - 추천 사운드 무드 및 코디아(Cordia)에게 전달할 화면 전환 특수효과 제안
            5. 📝 [유튜브 최종 업로드 메타데이터]
               - 유튜브에 실제로 업로드될 최종 확정 **제목(Title), 설명란(Description), 해시태그(Hashtags)** 작성
               - 설명란 하단에 전체 재생 시간, 이미지/음원 분위기를 담은 감성적인 `[Video Info]` 블록 포함
            """

        # 2. 통합 하이브리드 엔진 호출 (스레드 분리)
        def generate_planning():
            from telegram_bot.engine.llm_client import generate_text

            return generate_text(
                prompt, system_instruction, mode=llm_mode, local_url=local_url
            )

        response_text = await asyncio.to_thread(generate_planning)

        # ─────────────────────────────────────────────
        # 🧼 [방어적 프로그래밍] 2차 정적 하드 필터링 (Cleansing / Hard Filtering)
        # ─────────────────────────────────────────────
        import re

        # 1. 불필요한 메타데이터 블록 감지 시 제거 (새롭게 정의된 감성적인 [Video Info]는 보존합니다)
        # 줄바꿈(\n\n), 다른 대괄호 블록, 또는 텍스트 끝을 기준으로 매칭하여 삭제합니다.
        response_text = re.sub(
            r"(?i)\[Metadata\][\s\S]*?(?=\n\s*\n|\n\s*\[|$)", "", response_text
        )

        # 2. 금지어 리스트 순회하며 강제 공백화 (AI 툴 이름, 자동화 및 규격 정보 제거)
        forbidden_words = [
            "Lyria 3 Pro",
            "Lyria",
            "Imagen 4.0",
            "Imagen",
            "Automated Production Flow",
            "AI 작곡",
            "AI 생성",
            "AI Generated",
            "Long-form",
            "16:9 Landscape Video",
            "Automated",
            "Flow V2.0",
            "System:",
            "Audio:",
            "Format:",
        ]
        for word in forbidden_words:
            if word in response_text:
                response_text = response_text.replace(word, "")

        # 3. 삭제 후 발생하는 어색한 다중 줄바꿈 및 불필요한 공백 깔끔하게 정돈
        response_text = re.sub(r"\n{3,}", "\n\n", response_text)
        response_text = response_text.strip()

        # 💡 [방어적 프로그래밍] 이후 제작(Production) 단계로 기획 대본이 정상 인계될 수 있도록
        # 텔레그램 대화방 세션 메모리에 기획 결과를 임시 캐싱합니다.
        if context.chat_data is not None:
            context.chat_data["last_planning_result"] = response_text
            # 💡 [논스톱 브릿지] production.py가 참조할 수 있도록 별도 키로도 중복 저장
            context.chat_data["last_generated_plan"] = response_text

        # 요가 명상 관련 콘텐츠 기획 시, 요가 이미지가 있다면 특별 노출하여 생동감 향상!
        specific_img = None
        if any(keyword in user_message for keyword in ["요가", "명상", "스트레칭", "웰니스"]):
            specific_img = get_agent_image_path("ravia", "yoga")

        final_img = specific_img or success_img

        # 1. Ravia 캐릭터 이미지와 함께 완료 알림 전송 (캡션 1,024자 안전 한도 준수)
        intro_caption = f"💡 *라비아의 {format_label} 기획안 보고서*\n\n대표님, 요청하신 기획안 수립이 완료되었습니다! 아래 리포트를 브리핑해 드립니다."
        if final_img:
            with open(final_img, "rb") as photo:
                try:
                    await update.message.reply_photo(
                        photo=photo, caption=intro_caption, parse_mode="Markdown"
                    )
                except Exception as pe:
                    print(
                        f"⚠️ [Caption Markdown Parse Error]: {pe}. Retrying with plain text."
                    )
                    await update.message.reply_photo(
                        photo=photo,
                        caption=intro_caption.replace("*", ""),
                        parse_mode=None,
                    )
        else:
            try:
                await update.message.reply_text(intro_caption, parse_mode="Markdown")
            except Exception as pe:
                print(
                    f"⚠️ [Intro Text Markdown Parse Error]: {pe}. Retrying with plain text."
                )
                await update.message.reply_text(
                    intro_caption.replace("*", ""), parse_mode=None
                )

        # 2. 기획안 본문은 일반 텍스트(3,800자 단위 안전 분할)로 이어서 전송
        MAX_MSG_LEN = 3800
        if len(response_text) > MAX_MSG_LEN:
            for i in range(0, len(response_text), MAX_MSG_LEN):
                part = response_text[i : i + MAX_MSG_LEN]
                try:
                    await update.message.reply_text(part, parse_mode="Markdown")
                except Exception as pe:
                    print(
                        f"⚠️ [Content Split Markdown Parse Error]: {pe}. Retrying with plain text."
                    )
                    await update.message.reply_text(part, parse_mode=None)
        else:
            try:
                await update.message.reply_text(response_text, parse_mode="Markdown")
            except Exception as pe:
                print(
                    f"⚠️ [Content Markdown Parse Error]: {pe}. Retrying with plain text."
                )
                await update.message.reply_text(response_text, parse_mode=None)

    except Exception as e:
        import traceback

        traceback.print_exc()
        error_msg = (
            f"❌ *라비아 기획 실패*: AI 기획을 완료하지 못했습니다.\n"
            f"상세 오류: `{str(e)}`\n\n"
            f"💡 _힌트: .env 파일에 올바른 API 키가 들어가 있는지 확인해 주세요._"
        )
        await update.message.reply_text(error_msg, parse_mode="Markdown")
    finally:
        # 로딩 메시지 삭제
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id, message_id=status_msg.message_id
            )
        except Exception:
            pass
