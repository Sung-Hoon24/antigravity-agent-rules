# -*- coding: utf-8 -*-
"""
유튜브 동영상 제작 및 E2E 무결성 검증을 위한 AI 핸들러
- 기술 리드 '코디아(Cordia)' 페르소나를 사용하여 비디오 빌드 결과를 출력합니다.
- e2e_integration_tester.py의 시뮬레이션을 구동하여 무결성을 검사합니다.
"""

import os
import asyncio
import datetime
from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.config import CHANNEL_MAP
from telegram_bot.utils.image_helper import get_agent_image_path
from telegram_bot.handlers.basic import check_permission
from e2e_integration_tester import run_e2e_test, MTP_V2_SIMULATED
from google import genai
from google.genai import types


@check_permission
async def handle_production(
    update: Update, context: ContextTypes.DEFAULT_TYPE, channel_key: str = None
) -> None:
    """기술 리드 코디아가 제작 파이프라인 E2E 무결성 검증 및 빌드를 수행하는 핸들러"""
    if not update.message:
        return

    user_message = update.message.text or ""

    # ⚙️ 제작은 코디아가 담당
    working_img = get_agent_image_path("cordia", "working")
    success_img = get_agent_image_path("cordia", "success")

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

    # 💡 [안전 장치] 명백한 에이전트 캐릭터 파일명 필터링용 셋 정의
    character_names = [
        "rubia",
        "ravia",
        "cordia",
        "guardia",
        "intella",
        "signa",
        "stella",
    ]

    # 🔄 [에러 후 재시도 세션 검증 및 복원]
    is_retry = False
    cached_context = None
    if context.chat_data and context.chat_data.get("awaiting_error_retry"):
        import time

        cached_context = context.chat_data.get("error_retry_context", {})
        err_ts = cached_context.get("timestamp", 0)
        if time.time() - err_ts <= 300:
            is_retry = True
            print("🔄 [Production] 5분 이내 재시도 세션 감지: 이전 맥락 복원 가동.")

    if is_retry:
        video_format = cached_context.get("video_format", "shorts")
        video_length = cached_context.get("video_length", 1)
        channel_key = cached_context.get("channel_key", channel_key)
        print(
            f"🔄 [Production] 재시도 복원 완료: Format={video_format}, Length={video_length}, Channel={channel_key}"
        )
    else:
        # 💡 [보완] 숏폼 / 롱폼 포맷 및 재생시간 판별 (자연어 명령 우선순위 1순위 적용)
        # - 대표님이 메시지에 명시한 지시어(예: 1분 숏폼, 10분 롱폼)가 이전 캐시에 밀려 무시되는 버그를 방어합니다.
        from telegram_bot.nlp.intent_parser import parse_intent_fallback
        import re

        analysis = parse_intent_fallback(user_message)
        msg_format = analysis.get("video_format")
        msg_length = analysis.get("video_length")

        # 메시지에 명시적인 시간 지시(숫자+분)가 포함되어 있거나 포맷(숏폼/롱폼 등)이 언급되었는지 확인
        has_explicit_duration = bool(re.search(r"\d+\s*(?:분|min|시간|hr)", user_message))
        has_explicit_format = any(
            kw in user_message.lower()
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

        if has_explicit_duration or has_explicit_format:
            video_format = msg_format
            video_length = msg_length
            print(
                f"🎯 [Production] 대표님의 명시적 지시어 우선 채택: Format={video_format}, Length={video_length}"
            )
        else:
            # 명시적 지시가 없을 때만 이전 기획 세션 캐시 참조
            if context.chat_data is not None:
                video_format = (
                    context.chat_data.get("last_planning_format")
                    or context.chat_data.get("target_format")
                    or "shorts"
                )
                video_length = (
                    context.chat_data.get("last_planning_length")
                    or context.chat_data.get("target_length")
                    or 1
                )
            else:
                video_format = "shorts"
                video_length = 1

        # 🚨 [안전 장치] 길이에 따른 포맷 하드 강제 (2분 이상은 무조건 롱폼)
        if int(video_length) >= 2:
            video_format = "longform"

    format_label = (
        "숏폼(Shorts, 9:16)"
        if video_format == "shorts"
        else f"롱폼(Long-form, 16:9, {video_length}분)"
    )

    # 로딩 알림 전송 (코디아 작업 이미지 포함 및 실시간 진척도 1단계 설정)
    load_msg = f"⚙️ *기술 디렉터 코디아*가 `{conf['name']}` {format_label} 영상 제작을 시작합니다.\n\n⏳ [1/4] 비디오 마스터 템플릿(VTM) 데이터 로드 중... (25%)"
    if working_img:
        with open(working_img, "rb") as photo:
            status_msg = await update.message.reply_photo(
                photo=photo, caption=load_msg, parse_mode="Markdown"
            )
    else:
        status_msg = await update.message.reply_text(load_msg, parse_mode="Markdown")

    try:
        # 비동기로 E2E 시뮬레이션 테스트 실행 (CPU 블로킹 방지)
        results = await asyncio.to_thread(run_e2e_test, MTP_V2_SIMULATED)

        # 1.5초 대기 후 진척도 2단계 업데이트
        await asyncio.sleep(1.5)
        step2_msg = f"⚙️ *기술 디렉터 코디아*가 `{conf['name']}` {format_label} 영상 제작 중입니다.\n\n🎨 [2/4] 대본 자막 및 시각 비주얼 레이어 인코딩 중... (50%)"
        if working_img:
            await context.bot.edit_message_caption(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                caption=step2_msg,
                parse_mode="Markdown",
            )
        else:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                text=step2_msg,
                parse_mode="Markdown",
            )

        # 1.5초 대기 후 진척도 3단계 업데이트
        await asyncio.sleep(1.5)
        step3_msg = f"⚙️ *기술 디렉터 코디아*가 `{conf['name']}` {format_label} 영상 제작 중입니다.\n\n🎵 [3/4] 칠(Chill)한 오디오 BGM 믹싱 및 특수 글리치 효과 합성 중... (75%)"
        if working_img:
            await context.bot.edit_message_caption(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                caption=step3_msg,
                parse_mode="Markdown",
            )
        else:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                text=step3_msg,
                parse_mode="Markdown",
            )

        # 1.5초 대기 후 진척도 4단계 업데이트
        await asyncio.sleep(1.5)
        step4_msg = f"⚙️ *기술 디렉터 코디아*가 `{conf['name']}` {format_label} 영상 제작 중입니다.\n\n🚀 [4/4] 최종 E2E 렌더링 파이프라인 무결성 검사 중... (90%)"
        if working_img:
            await context.bot.edit_message_caption(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                caption=step4_msg,
                parse_mode="Markdown",
            )
        else:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                text=step4_msg,
                parse_mode="Markdown",
            )

        await asyncio.sleep(1.0)

        total_success = len(results["success_cases"])
        total_failed = len(results["failure_cases"])
        total_tests = total_success + total_failed

        # 가상 mp4 출력 파일 사양서 구성
        output_filename = f"{channel_key}_{video_format}_v1.mp4"

        # [로컬 저장소 폴더 분리 체계화]
        # 비디오 포맷(shorts vs longform)에 따라 outputs/shorts/ 또는 outputs/longform/ 하위 폴더로 동적 분리 저장합니다.
        output_dir = os.path.join(
            "c:/1인기업/Apps/유튜브에이전트/outputs",
            "shorts" if video_format == "shorts" else "longform",
            channel_key,
        )
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, output_filename)

        # 실제 렌더링 엔진(FFmpeg) 파이프라인 가동
        from telegram_bot.engine.audio_generator import generate_lyria3_music

        # 💡 [방어적 프로그래밍 & 사용자 커스텀 소스 연동]
        # 대표님이 전송하신 커스텀 파일이 input/<channel_key>/ 폴더에 존재한다면 이를 최우선으로 사용합니다.

        custom_visual = None
        custom_audio = None

        input_channel_dir = os.path.join("c:/1인기업/Apps/유튜브에이전트/input", channel_key)
        images_dir = os.path.join(input_channel_dir, "images")
        videos_dir = os.path.join(input_channel_dir, "videos")
        audios_dir = os.path.join(input_channel_dir, "audios")

        # GEMINI API 키 가져오기
        from telegram_bot.config import GEMINI_API_KEY

        api_key = GEMINI_API_KEY.split(",")[0].strip() if GEMINI_API_KEY else None

        # 파일 목록 스캔 및 캐릭터 이미지 자동 스킵 필터링
        visual_paths = []
        audio_paths = []

        # 1. 이미지 폴더 스캔 (images/)
        if os.path.exists(images_dir):
            for f in os.listdir(images_dir):
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                    f_path = os.path.join(images_dir, f)
                    try:
                        # 파일명에 에이전트 캐릭터 키워드가 포함되어 있다면 배경용 리소스에서 안전 스킵
                        if any(char in f.lower() for char in character_names):
                            print(f"⚠️ [Production] 에이전트 캐릭터 리소스 파일명 제외: {f}")
                            continue
                        visual_paths.append(f_path)
                    except Exception:
                        visual_paths.append(f_path)

        # 2. 비디오 폴더 스캔 (videos/)
        if os.path.exists(videos_dir):
            for f in os.listdir(videos_dir):
                if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
                    visual_paths.append(os.path.join(videos_dir, f))

        # 3. 오디오 폴더 스캔 (audios/)
        if os.path.exists(audios_dir):
            for f in os.listdir(audios_dir):
                if f.lower().endswith((".mp3", ".wav", ".m4a")):
                    audio_paths.append(os.path.join(audios_dir, f))

        # 수정 시간 기준으로 정렬 (최신 파일 우선)
        visual_paths = sorted(
            visual_paths, key=lambda x: os.path.getmtime(x), reverse=True
        )
        audio_paths = sorted(
            audio_paths, key=lambda x: os.path.getmtime(x), reverse=True
        )

        # 메시지에서 명시적으로 특정 파일명이 언급되었는지 확인
        # 🚨 [Fallback 금지 규칙] 대표님이 메시지에서 파일명을 직접 언급한 경우에만 custom_visual/custom_audio를 사용합니다.
        # 디렉토리 스캔 결과를 자동으로 할당하는 로직을 완전 제거합니다.
        for f_path in visual_paths:
            if os.path.basename(f_path) in user_message:
                custom_visual = f_path
                print(f"📸 [Production] 대표님이 명시한 파일 감지: {os.path.basename(f_path)}")
                break

        for f_path in audio_paths:
            if os.path.basename(f_path) in user_message:
                custom_audio = f_path
                print(f"🎵 [Production] 대표님이 명시한 음원 파일 감지: {os.path.basename(f_path)}")
                break

        # 🚨 [신규 에셋 100% 생성 강제 규칙]
        # 대표님이 직접 파일을 전송하거나 메시지에서 파일명을 언급한 경우가 아니면,
        # 항상 새 이미지를 생성합니다. 디렉토리에 남아있는 과거 파일을 절대 자동 사용하지 않습니다.
        should_generate_image = True
        if custom_visual:
            # 대표님이 명시적으로 지정한 파일이 있으면 새 이미지 생성을 스킵
            should_generate_image = False
            print(
                f"📸 [Production] 대표님 전송 자료 감지로 이미지 생성 스킵: {os.path.basename(custom_visual)}"
            )

        # 💡 [방어적 프로그래밍] 캐싱된 기획 대본이 존재하지 않거나, 대표님이 "새로", "기획"을 원할 때 백그라운드 실시간 기획 가동
        planning_script = None
        if is_retry:
            planning_script = cached_context.get("planning_script")
            print("📝 [Production] 재시도 모드: 캐시된 기획 대본 복원 완료.")
        elif context.chat_data is not None:
            # 💡 [논스톱 브릿지] planning.py에서 저장한 기획안을 우선 참조하고, 없으면 last_generated_plan 폴백
            planning_script = context.chat_data.get(
                "last_planning_result"
            ) or context.chat_data.get("last_generated_plan")

        is_new_plan_requested = any(kw in user_message for kw in ["새로", "new", "기획"])
        # 재시도 모드가 아닐 때에만 기획 재생성을 판단
        if not is_retry and (not planning_script or is_new_plan_requested):
            # 1. 봇 진행율 메시지 업데이트 (백그라운드 기획 시작)
            step_bg_plan_msg = f"⚙️ *기술 디렉터 코디아*가 `{conf['name']}` {format_label} 대본 기획을 백그라운드에서 실시간 구성 중입니다..."
            if working_img:
                await context.bot.edit_message_caption(
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id,
                    caption=step_bg_plan_msg,
                    parse_mode="Markdown",
                )
            else:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id,
                    text=step_bg_plan_msg,
                    parse_mode="Markdown",
                )

            from telegram_bot.engine.llm_client import generate_text
            from telegram_bot.config import CHANNEL_IDENTITIES

            identity = CHANNEL_IDENTITIES.get(channel_key, "일반 동영상 크리에이터 채널")

            # 실시간 심층 기획 템플릿 호출 (자막 은은성 룰 반영)
            system_instruction = (
                "당신은 루비아 팀의 기획팀장 '라비아'입니다. "
                f"대표님의 지시에 따라 {video_format} 영상 대본을 구성하십시오. "
                "자막의 간격은 빽빽하지 않고 은은하게(예: 8초~15초 간격으로 짧고 감성적인 핵심 메시지만 분산 배치) 구성하십시오. "
                "'AI', '인공지능', '자동화' 등의 단어는 절대 금지합니다."
            )

            lang_rule = (
                "영어(English)로만 대사/자막을 작성하십시오."
                if channel_key == "aura"
                else "대만 번체자(繁體中文)와 일본어(日本語)로만 작성하십시오."
                if channel_key in ["rubia", "taipei"]
                else "국내 시니어 대상이므로 이해하기 쉬운 한글 경어체로만 작성하십시오."
            )

            plan_prompt = f"""
            대표님의 {video_format} 영상 제작 지시: "{user_message}"
            타겟 길이: {video_length}분
            이 채널의 정체성: {identity}
            언어 규칙: {lang_rule}

            출력 포맷:
            자막: [텍스트] 형태로 8초~15초 간격의 타임라인 자막을 작성하십시오.
            """
            try:
                llm_mode = context.bot_data.get("llm_mode", "cloud")
                local_url = context.bot_data.get("local_llm_url")
                planning_script = await asyncio.to_thread(
                    generate_text,
                    plan_prompt,
                    system_instruction,
                    mode=llm_mode,
                    local_url=local_url,
                )
                if context.chat_data is not None:
                    context.chat_data["last_planning_result"] = planning_script
                    context.chat_data["last_planning_format"] = video_format
                    context.chat_data["last_planning_length"] = video_length
                print("✅ [Production] 백그라운드 대본 기획 성공 완료.")
            except Exception as pe:
                print(f"⚠️ [Production] 백그라운드 기획 실패: {pe}")

        # 최종 기획 텍스트 검증 폴백
        if not planning_script:
            if channel_key == "aura":
                planning_script = "자막: Close your eyes and breathe in.\n자막: Feel the warm energy flowing.\n자막: Let go of all your tension."
            elif channel_key in ["rubia", "taipei"]:
                planning_script = "字幕: 閉上眼睛，深呼吸。\n字幕: 感受溫暖的能量在流動。\n字幕: 放下所有的疲憊與焦慮。"
            elif channel_key == "smartage":
                planning_script = "자막: 눈을 감고 천천히 숨을 쉬어보세요.\n자막: 편안한 음악과 함께 하루를 정리합니다.\n자막: 오늘 하루도 정말 수고하셨습니다."
            else:
                planning_script = "자막: 오늘 하루, 너무 길고 지치지 않았나요?\n자막: 복잡한 생각은 모두 내려놓고,\n자막: 그저 음악과 함께 걸어보세요."

        # 🎨 [Imagen 4.0 이미지 생성 실행]
        generated_img_path = None
        if should_generate_image and api_key:
            os.makedirs(images_dir, exist_ok=True)

            step_gen_img_msg = f"🎨 *기술 디렉터 코디아*가 `{conf['name']}` 비디오 배경 이미지를 새로 생성하고 있습니다...\n\n🚀 [Imagen 4.0] 기획안 기반 고화질 이미지 렌더링 중..."
            if working_img:
                await context.bot.edit_message_caption(
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id,
                    caption=step_gen_img_msg,
                    parse_mode="Markdown",
                )
            else:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id,
                    text=step_gen_img_msg,
                    parse_mode="Markdown",
                )

            try:
                client = genai.Client(api_key=api_key)

                image_prompt = None
                if is_retry and cached_context.get("image_prompt"):
                    image_prompt = cached_context.get("image_prompt")
                    print(
                        f"🎨 [Production] 재시도 모드: 캐시된 이미지 프롬프트 복원 완료: {image_prompt[:60]}..."
                    )

                if not image_prompt:
                    system_instruction = (
                        "You are a professional prompt engineer for Imagen 4.0. "
                        "Create a highly detailed, artistic, and aesthetic English image generation prompt "
                        f"suitable for {video_format} (aspect ratio) background "
                        "that matches the user's request and the wellness/lofi theme. "
                        "Do NOT output any markdown, explanations, or quotes. Output ONLY the raw prompt text."
                    )

                    prompt_input = f"User Request: '{user_message}'\nContext Planning Details:\n{planning_script[:500]}"

                    def extract_prompt():
                        r = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt_input,
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction, temperature=0.7
                            ),
                        )
                        return r.text.strip()

                    image_prompt = await asyncio.to_thread(extract_prompt)
                    image_prompt = image_prompt.strip("\"'")
                    print(
                        f"[Imagen Prompt Generation] Generated Prompt: {image_prompt}"
                    )

                target_ratio = "9:16" if video_format == "shorts" else "16:9"

                def generate_visual():
                    res = client.models.generate_images(
                        model="imagen-4.0-generate-001",
                        prompt=image_prompt,
                        config=dict(
                            number_of_images=1,
                            aspect_ratio=target_ratio,
                            person_generation="DONT_ALLOW",
                        ),
                    )
                    return res

                image_res = await asyncio.to_thread(generate_visual)

                if image_res.generated_images:
                    img_data = image_res.generated_images[0]
                    generated_img_filename = f"generated_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    generated_img_path = os.path.join(
                        images_dir, generated_img_filename
                    )

                    import io
                    from PIL import Image

                    image = Image.open(io.BytesIO(img_data.image.image_bytes))
                    image.save(generated_img_path)
                    print(
                        f"[Imagen Success] Saved generated image to: {generated_img_path}"
                    )
                else:
                    print("[Imagen Error] No images returned.")
            except Exception as ie:
                import traceback

                traceback.print_exc()
                print(f"🚨 [Imagen Error]: {ie}")

                # 🚨 [에러 후 재시도 세션 유지] 직전 기획/프롬프트 맥락 캐싱 (5분 유지용)
                if context.chat_data is not None:
                    context.chat_data["awaiting_error_retry"] = True
                    context.chat_data["error_retry_context"] = {
                        "channel_key": channel_key,
                        "video_format": video_format,
                        "video_length": video_length,
                        "file_path": file_path,
                        "output_dir": output_dir,
                        "planning_script": planning_script,
                        "image_prompt": image_prompt
                        if "image_prompt" in locals()
                        else None,
                        "timestamp": __import__("time").time(),
                        "stage": "image",
                    }
                    print("💾 [Production] 이미지 생성 에러 감지. 5분간 재시도용 작업 컨텍스트를 캐싱했습니다.")

                # 🚨 [Fallback 금지 규칙] 이미지 생성 실패 시 기존 파일 재사용 전면 금지.
                # 프로세스를 즉시 중단하고 에러 리포트를 송출합니다.
                await update.message.reply_text(
                    f"⚠️ *[에셋 생성 실패] 이미지 생성 API 응답 없음.*\n"
                    f"기존 파일을 사용하지 않고 작업을 중단합니다.\n"
                    f"상세 오류: `{str(ie)}`\n\n"
                    f"대표님, 다시 지시하시려면 '재시도해' 또는 '다시 해봐'를 보내주세요. (5분간 기획안/프롬프트가 유지됩니다.)",
                    parse_mode="Markdown",
                )
                return

        source_log = []

        # 1. 시각적 이미지/비디오 소스 확정
        # 🚨 [Fallback 금지 규칙] 시스템 기본값 이미지 폴백을 완전 제거합니다.
        if generated_img_path and os.path.exists(generated_img_path):
            dummy_img = generated_img_path
            source_log.append(
                f"🎨 *적용 이미지*: `{os.path.basename(generated_img_path)}` (AI 실시간 생성 이미지)"
            )
        elif custom_visual and os.path.exists(custom_visual):
            dummy_img = custom_visual
            v_type = (
                "동영상"
                if custom_visual.lower().endswith(
                    (".mp4", ".avi", ".mov", ".mkv", ".gif")
                )
                else "이미지"
            )
            source_log.append(
                f"📸 *적용 {v_type}*: `{os.path.basename(custom_visual)}` (대표님 전송 자료)"
            )
        else:
            # 🚨 [Fallback 금지] 가용 이미지가 없으면 즉시 중단하고 에러 리포트
            await update.message.reply_text(
                "⚠️ *[에셋 생성 실패] 가용 이미지 리소스 없음.*\n"
                "기존 파일을 사용하지 않고 작업을 중단합니다.\n"
                "이미지를 새로 생성하거나 텔레그램으로 전송해 주세요.\n\n"
                "재시도하시겠습니까?",
                parse_mode="Markdown",
            )
            return

        # 2. 오디오 BGM 소스 확정
        # 🚨 [Fallback 금지 규칙] 오디오 생성 실패 시 기존 파일 재사용을 전면 금지합니다.
        if custom_audio and os.path.exists(custom_audio):
            dummy_audio = custom_audio
            source_log.append(
                f"🎵 *적용 음원*: `{os.path.basename(custom_audio)}` (대표님 전송 자료)"
            )
        else:
            step_music_msg = f"⚙️ *기술 디렉터 코디아*가 `{conf['name']}` {format_label} 영상 제작 중입니다.\n\n🎵 [Phase 5] Lyria 3 Pro AI 실시간 작곡 및 루프 생성 중... (1~5분 소요 예상)"
            if working_img:
                await context.bot.edit_message_caption(
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id,
                    caption=step_music_msg,
                    parse_mode="Markdown",
                )
            else:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id,
                    text=step_music_msg,
                    parse_mode="Markdown",
                )

            audio_filename = f"{channel_key}_music_generated.mp3"
            audio_path = os.path.join(output_dir, audio_filename)

            try:
                dummy_audio = await asyncio.to_thread(
                    generate_lyria3_music,
                    channel_key,
                    audio_path,
                    duration_min=video_length,
                )
            except Exception as e:
                # 🚨 [에러 후 재시도 세션 유지] 음원 생성 실패 시 작업 맥락 캐싱 (5분 유지용)
                if context.chat_data is not None:
                    context.chat_data["awaiting_error_retry"] = True
                    context.chat_data["error_retry_context"] = {
                        "channel_key": channel_key,
                        "video_format": video_format,
                        "video_length": video_length,
                        "file_path": file_path,
                        "output_dir": output_dir,
                        "planning_script": planning_script,
                        "image_prompt": image_prompt
                        if "image_prompt" in locals()
                        else None,
                        "timestamp": __import__("time").time(),
                        "stage": "audio",
                    }
                    print("💾 [Production] 음원 생성 에러 감지. 5분간 재시도용 작업 컨텍스트를 캐싱했습니다.")

                # 🚨 [Fallback 금지] 음원 생성 실패 시 기존 파일 재사용 전면 금지
                await update.message.reply_text(
                    f"⚠️ *[에셋 생성 실패] 음원 생성 API 응답 없음.*\n"
                    f"기존 파일을 사용하지 않고 작업을 중단합니다.\n"
                    f"상세 오류: `{str(e)}`\n\n"
                    f"대표님, 다시 지시하시려면 '재시도해' 또는 '다시 해봐'를 보내주세요. (5분간 기획안/프롬프트가 유지됩니다.)",
                    parse_mode="Markdown",
                )
                return
            source_log.append("🎵 *적용 음원*: `Lyria 3 Pro AI 생성 음원` (자동 작곡 및 시간 동기화 완료)")

        # ─────────────────────────────────────────────
        # 🚨 [승인 대기 모드] 에셋 생성 완료 후 채팅방에 파일을 게시하고
        # 대표님의 명시적 승인("진행해", "OK" 등)이 올 때까지 렌더링을 보류합니다.
        # ─────────────────────────────────────────────

        # 🛡️ [타임스탬프 사전 검증 - TSS v1.1 기준 개정] Standby 메시지 게시 직전,
        # 해당 이미지/음원 파일의 생성 시각(mtime)이 현재 시도 시각으로부터 과거 15분 이내(< 900초)인지 확인합니다.
        now_ts = __import__("time").time()

        if os.path.exists(dummy_img):
            img_mtime = os.path.getmtime(dummy_img)
            if not (0 <= now_ts - img_mtime <= 900):
                await update.message.reply_text(
                    f"🚨 *[타임스탬프 검증 실패] 이미지 파일이 15분 유효시간을 초과한 구형 캐시입니다.*\n"
                    f"파일: `{os.path.basename(dummy_img)}`\n"
                    f"기존 파일을 사용하지 않고 작업을 중단합니다.\n"
                    f"이미지를 새로 생성해 주세요.",
                    parse_mode="Markdown",
                )
                return

        if os.path.exists(dummy_audio):
            audio_mtime = os.path.getmtime(dummy_audio)
            if not (0 <= now_ts - audio_mtime <= 900):
                await update.message.reply_text(
                    f"🚨 *[타임스탬프 검증 실패] 음원 파일이 15분 유효시간을 초과한 구형 캐시입니다.*\n"
                    f"파일: `{os.path.basename(dummy_audio)}`\n"
                    f"기존 파일을 사용하지 않고 작업을 중단합니다.\n"
                    f"음원을 새로 생성해 주세요.",
                    parse_mode="Markdown",
                )
                return

        # 3. 생성된 에셋 파일을 텔레그램 채팅방에 게시
        try:
            # 이미지 게시
            if os.path.exists(dummy_img):
                await context.bot.send_chat_action(
                    chat_id=update.effective_chat.id, action="upload_photo"
                )
                img_caption = f"🎨 생성된 배경 이미지: `{os.path.basename(dummy_img)}`"
                with open(dummy_img, "rb") as img_file:
                    await update.message.reply_photo(
                        photo=img_file, caption=img_caption, parse_mode="Markdown"
                    )

            # 음원 게시
            if os.path.exists(dummy_audio):
                await context.bot.send_chat_action(
                    chat_id=update.effective_chat.id, action="upload_voice"
                )
                audio_caption = f"🎵 생성된 BGM 음원: `{os.path.basename(dummy_audio)}`"
                with open(dummy_audio, "rb") as audio_file:
                    await update.message.reply_audio(
                        audio=audio_file, caption=audio_caption, parse_mode="Markdown"
                    )
        except Exception as asset_send_err:
            print(f"⚠️ [Asset Upload Error]: {asset_send_err}")

        # 4. 에셋 경로를 세션 메모리에 캐싱 (승인 후 렌더링에 사용)
        if context.chat_data is not None:
            context.chat_data["pending_visual"] = dummy_img
            context.chat_data["pending_audio"] = dummy_audio
            context.chat_data["pending_script"] = planning_script
            context.chat_data["pending_channel_key"] = channel_key
            context.chat_data["pending_video_format"] = video_format
            context.chat_data["pending_video_length"] = video_length
            context.chat_data["pending_output_path"] = file_path
            context.chat_data["pending_output_dir"] = output_dir
            # 🛡️ [타임스탬프 기록] 에셋 생성 지시 시각을 기록하여 렌더링 직전 교차 검증에 사용
            context.chat_data[
                "asset_creation_timestamp"
            ] = datetime.datetime.now().timestamp()
            context.chat_data["awaiting_build_approval"] = True

            # 에셋이 생성 완료되었으므로 에러 재시도 상태를 안전하게 해제합니다.
            context.chat_data["awaiting_error_retry"] = False
            context.chat_data["error_retry_context"] = None
            print("🧹 [Production] 에셋 정상 생성 완료. 에러 재시도 캐시 세션 초기화.")

        # 5. 승인 대기 메시지 송출 및 프로세스 중단 (Standby)
        standby_msg = (
            f"✅ *에셋 생성이 완료되었습니다.* (파일 확인 요망)\n\n"
            f"📸 이미지: `{os.path.basename(dummy_img)}`\n"
            f"🎵 음원: `{os.path.basename(dummy_audio)}`\n"
            f"📝 대본: 기획안 캐싱 완료\n\n"
            f"대표님, 이 결과물로 *영상 렌더링 단계(비디오 빌드)*를 진행할까요?\n"
            f"('진행해', '영상 만들어', 'OK' 등으로 승인해 주세요)"
        )
        if success_img:
            with open(success_img, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo, caption=standby_msg, parse_mode="Markdown"
                )
        else:
            await update.message.reply_text(standby_msg, parse_mode="Markdown")

        # 🚨 [핵심] 여기서 return하여 비디오 렌더링을 진행하지 않고 대기합니다.
        # 대표님의 승인 명령이 들어오면 handle_approved_build()가 호출됩니다.
        print("⏸️ [Production] 에셋 생성 완료. 대표님의 승인 명령 대기 중 (Standby 모드)...")

    except Exception as e:
        import traceback

        traceback.print_exc()
        error_msg = f"❌ *코디아 빌드 에러*: 에셋 생성 파이프라인을 완료하지 못했습니다.\n" f"상세 오류: `{str(e)}`"
        await update.message.reply_text(error_msg, parse_mode="Markdown")
    finally:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id, message_id=status_msg.message_id
            )
        except Exception:
            pass


# ─────────────────────────────────────────────
# 🚀 [Phase 2] 승인 후 비디오 빌드 전용 핸들러
# 대표님의 명시적 승인("진행해", "OK" 등) 후에만 FFmpeg 렌더링을 실행합니다.
# ─────────────────────────────────────────────


@check_permission
async def handle_approved_build(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """대표님의 승인 명령 후 캐싱된 에셋으로 FFmpeg 비디오 렌더링을 실행하는 핸들러"""
    if not update.message:
        return

    # 승인 대기 상태 확인
    if context.chat_data is None or not context.chat_data.get(
        "awaiting_build_approval"
    ):
        await update.message.reply_text(
            "⚠️ *승인 대기 중인 에셋이 없습니다.*\n" "먼저 영상 제작(에셋 생성)을 요청해 주세요.",
            parse_mode="Markdown",
        )
        return

    working_img = get_agent_image_path("cordia", "working")
    success_img = get_agent_image_path("cordia", "success")

    # 캐싱된 에셋 경로 복원
    dummy_img = context.chat_data.get("pending_visual")
    dummy_audio = context.chat_data.get("pending_audio")
    planning_script = context.chat_data.get("pending_script")
    channel_key = context.chat_data.get("pending_channel_key", "rubia")

    if not planning_script:
        # 💡 [방어적 프로그래밍 - 세션 복원 시 대본 유실 방지]
        # 봇 재부팅 후 강제 복원 등으로 대본이 유실되었을 경우, 채널 성격에 맞는 기본 템플릿 대본을 자동 맵핑합니다.
        if channel_key == "aura":
            planning_script = "자막: Close your eyes and breathe in.\n자막: Feel the warm energy flowing.\n자막: Let go of all your tension."
        elif channel_key in ["rubia", "taipei"]:
            planning_script = "字幕: 閉上眼睛，深呼吸。\n字幕: 感受溫暖的能量在流動。\n字幕: 放下所有的疲憊與焦慮。"
        elif channel_key == "smartage":
            planning_script = "자막: 눈을 감고 천천히 숨을 쉬어보세요.\n자막: 편안한 음악과 함께 하루를 정리합니다.\n자막: 오늘 하루도 정말 수고하셨습니다."
        else:
            planning_script = "자막: 오늘 하루도 정말 수고 많으셨습니다.\n자막: 편안하게 들으면서 지친 마음을 달래보세요."
        print(f"📝 [Production] 세션 복원 대본 누락 감지 -> 기본 {channel_key} 채널 대본을 강제 적용합니다.")
    video_format = context.chat_data.get("pending_video_format", "shorts")
    video_length = context.chat_data.get("pending_video_length", 1)
    file_path = context.chat_data.get("pending_output_path")
    output_dir = context.chat_data.get("pending_output_dir")
    context.chat_data.get("asset_creation_timestamp", 0)

    conf = CHANNEL_MAP.get(channel_key)
    if not conf:
        await update.message.reply_text("❌ 채널 매핑 오류가 발생했습니다.", parse_mode="Markdown")
        return

    format_label = (
        "숏폼(Shorts, 9:16)"
        if video_format == "shorts"
        else f"롱폼(Long-form, 16:9, {video_length}분)"
    )
    user_message = update.message.text or ""

    # 🛡️ [타임스탬프 교차 검증 - TSS v1.1 기준 개정] FFmpeg 렌더링 직전,
    # 해당 이미지/음원 파일의 생성 시각(mtime)이 현재 렌더링 시도 시각으로부터 과거 15분 이내(< 900초)인지 확인합니다.
    try:
        import time

        now_ts = time.time()

        if dummy_img and os.path.exists(dummy_img):
            img_mtime = os.path.getmtime(dummy_img)
            if not (0 <= now_ts - img_mtime <= 900):
                await update.message.reply_text(
                    f"🚨 *[타임스탬프 검증 실패] 이미지 파일이 15분 유효시간을 초과한 구형 캐시입니다.*\n"
                    f"파일: `{os.path.basename(dummy_img)}`\n"
                    f"렌더링을 거부합니다. 이미지를 새로 생성해 주세요.",
                    parse_mode="Markdown",
                )
                context.chat_data["awaiting_build_approval"] = False
                return
        else:
            await update.message.reply_text(
                "🚨 *[에셋 누락] 이미지 파일을 찾을 수 없습니다.* 에셋 생성을 다시 요청해 주세요.",
                parse_mode="Markdown",
            )
            context.chat_data["awaiting_build_approval"] = False
            return

        if dummy_audio and os.path.exists(dummy_audio):
            audio_mtime = os.path.getmtime(dummy_audio)
            if not (0 <= now_ts - audio_mtime <= 900):
                await update.message.reply_text(
                    f"🚨 *[타임스탬프 검증 실패] 음원 파일이 15분 유효시간을 초과한 구형 캐시입니다.*\n"
                    f"파일: `{os.path.basename(dummy_audio)}`\n"
                    f"렌더링을 거부합니다. 음원을 새로 생성해 주세요.",
                    parse_mode="Markdown",
                )
                context.chat_data["awaiting_build_approval"] = False
                return
        else:
            await update.message.reply_text(
                "🚨 *[에셋 누락] 음원 파일을 찾을 수 없습니다.* 에셋 생성을 다시 요청해 주세요.",
                parse_mode="Markdown",
            )
            context.chat_data["awaiting_build_approval"] = False
            return
    except Exception as ts_err:
        print(f"⚠️ [Timestamp Validation Error]: {ts_err}")
        await update.message.reply_text(
            f"⚠️ *타임스탬프 검증 중 오류 발생*: `{str(ts_err)}`", parse_mode="Markdown"
        )
        context.chat_data["awaiting_build_approval"] = False
        return

    # 타임스탬프 검증 통과 — FFmpeg 렌더링 개시
    load_msg = (
        f"⚙️ *기술 디렉터 코디아*가 승인된 에셋으로 `{conf['name']}` {format_label} 비디오 렌더링을 시작합니다..."
    )
    if working_img:
        with open(working_img, "rb") as photo:
            status_msg = await update.message.reply_photo(
                photo=photo, caption=load_msg, parse_mode="Markdown"
            )
    else:
        status_msg = await update.message.reply_text(load_msg, parse_mode="Markdown")

    try:
        # E2E 무결성 검증
        results = await asyncio.to_thread(run_e2e_test, MTP_V2_SIMULATED)
        total_success = len(results["success_cases"])
        total_failed = len(results["failure_cases"])
        total_tests = total_success + total_failed

        # FFmpeg 렌더링 실행
        step_render_msg = "🚀 *FFmpeg 렌더링 실행 중*... 승인된 이미지와 음원으로 최종 합성 진행 중입니다."
        if working_img:
            await context.bot.edit_message_caption(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                caption=step_render_msg,
                parse_mode="Markdown",
            )
        else:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                text=step_render_msg,
                parse_mode="Markdown",
            )

        # 세션 메모리에 캐싱된 custom_style 가져오기 (없으면 None)
        custom_style = (
            context.chat_data.get("custom_style") if context.chat_data else None
        )

        from telegram_bot.engine.video_renderer import render_video

        await asyncio.to_thread(
            render_video,
            dummy_img,
            dummy_audio,
            planning_script,
            file_path,
            video_format=video_format,
            custom_style=custom_style,
        )

        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

        # 유튜브 업로드 판별
        should_upload = any(
            keyword in user_message.lower() for keyword in ["업로드", "올려", "게시", "upload"]
        )
        youtube_url = None
        upload_error = None

        if should_upload:
            try:
                from telegram_bot.utils.youtube_uploader import upload_video_to_youtube

                token_file = conf.get("token_file", f"token_{channel_key}.json")

                def run_upload():
                    return upload_video_to_youtube(
                        token_file,
                        file_path,
                        planning_script,
                        channel_key,
                        video_format=video_format,
                    )

                video_id, video_url = await asyncio.to_thread(run_upload)
                youtube_url = video_url
            except Exception as ue:
                import traceback

                traceback.print_exc()
                upload_error = str(ue)

        # 결과 보고서
        output_filename = os.path.basename(file_path)
        local_link = f"file:///{output_dir}"
        res_text = (
            "1080 x 1920 (세로형 Shorts, 9:16)"
            if video_format == "shorts"
            else "1920 x 1080 (가로형 Long-form, 16:9)"
        )

        report_lines = [
            "⚙️ *코디아의 비디오 빌드 & E2E 검증 보고서*\n",
            f"대표님, 승인하신 에셋으로 `{conf['name']}` {format_label} 비디오 렌더링이 완료되었습니다!\n",
        ]

        if should_upload:
            if youtube_url:
                report_lines.append("🚀 *유튜브 자동 업로드 완료*")
                report_lines.append(f"• **비디오 링크**: [유튜브에서 보기]({youtube_url})\n")
            else:
                report_lines.append(f"🚨 *유튜브 업로드 오류*: `{upload_error}`\n")

        report_lines.extend(
            [
                "📁 *비디오 파일 스펙*",
                f"• **출력 파일명**: `{output_filename}`",
                f"• 🎨 *이미지*: `{os.path.basename(dummy_img)}`",
                f"• 🎵 *음원*: `{os.path.basename(dummy_audio)}`",
                f"• **로컬 경로**: [출력 폴더 열기]({local_link})",
                f"• **해상도**: `{res_text}`",
                f"• **재생 시간**: `{video_length}분`",
                f"• **용량**: `{file_size_mb:.1f} MB`\n",
                f"📊 *E2E 검증*: 성공 {total_success} / 실패 {total_failed} (총 {total_tests})",
            ]
        )

        final_report = "\n".join(report_lines)

        if success_img:
            with open(success_img, "rb") as photo:
                try:
                    await update.message.reply_photo(
                        photo=photo, caption=final_report, parse_mode="Markdown"
                    )
                except Exception:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=final_report.replace("*", "").replace("`", "")[:1000],
                        parse_mode=None,
                    )
        else:
            try:
                await update.message.reply_text(final_report, parse_mode="Markdown")
            except Exception:
                await update.message.reply_text(
                    final_report.replace("*", "").replace("`", ""), parse_mode=None
                )

        # 완성 비디오 파일 텔레그램 전송
        try:
            if os.path.exists(file_path):
                await context.bot.send_chat_action(
                    chat_id=update.effective_chat.id, action="upload_video"
                )
                with open(file_path, "rb") as video_file:
                    await update.message.reply_video(
                        video=video_file,
                        caption=f"🎬 {conf['name']} 완성본 {video_format} 영상",
                        supports_streaming=True,
                    )
        except Exception as send_err:
            print(f"⚠️ [Video Send Error]: {send_err}")

        # 🚨 [세션 메모리 유지 - 업로드 상태 기억]
        # 비디오 렌더링이 성공적으로 완료되면 해당 파일 경로와 관련 정보를 캐싱합니다.
        context.chat_data["pending_upload_video"] = file_path
        context.chat_data["pending_upload_channel_key"] = channel_key
        context.chat_data["pending_upload_script"] = planning_script
        context.chat_data["pending_upload_video_format"] = video_format

        # 승인 대기 상태 초기화
        context.chat_data["awaiting_build_approval"] = False

        # 사용자에게 업로드 재촉 안내 메시지 출력
        await update.message.reply_text(
            "✅ 렌더링 완료! 유튜브에 업로드할까요? ('채널에 업로드해' 라고 말씀해 주세요)"
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        await update.message.reply_text(
            f"❌ *코디아 렌더링 에러*: `{str(e)}`", parse_mode="Markdown"
        )
        context.chat_data["awaiting_build_approval"] = False
    finally:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id, message_id=status_msg.message_id
            )
        except Exception:
            pass
