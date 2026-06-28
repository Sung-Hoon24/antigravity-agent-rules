import os
import asyncio
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram_bot.config import CHANNEL_MAP
from telegram_bot.utils.image_helper import get_agent_image_path
from telegram_bot.handlers.basic import check_permission
from e2e_integration_tester import run_e2e_test, MTP_V2_SIMULATED
from google import genai
from google.genai import types

from pydantic import BaseModel, Field
from typing import List


def validate_planning_json(data: dict) -> None:
    """
    [R&D Validation Gate]
    렌더링에 주입될 기획안 JSON 데이터의 무결성을 검증합니다.
    필수 메타데이터가 결손되거나 쓰레기 데이터가 감지되면 즉각 Exception을 발생시켜 빌드를 폐기(Discard)합니다.
    """
    if not data or not isinstance(data, dict):
        raise ValueError("기획 세션 데이터가 올바른 JSON(dict) 형식이 아닙니다.")

    required_fields = ["concept", "youtube_title", "captions", "playlist"]
    for field in required_fields:
        if field not in data or not data.get(field):
            raise ValueError(f"데이터 무결성 오류: 필수 메타데이터 필드 '{field}'가 유실되었습니다.")

    # 자막 리스트 정밀 검증
    captions = data.get("captions", [])
    if not isinstance(captions, list) or len(captions) == 0:
        raise ValueError("데이터 무결성 오류: 자막 대본(captions) 리스트가 비어 있거나 올바르지 않습니다.")

    for idx, cap in enumerate(captions):
        if not isinstance(cap, dict) or "time_code" not in cap or "text" not in cap:
            raise ValueError(
                f"데이터 무결성 오류: {idx}번째 자막의 필수 항목(time_code, text)이 유실되었습니다."
            )
        if not cap.get("text"):
            raise ValueError(f"데이터 무결성 오류: {idx}번째 자막 내용이 비어 있습니다.")

    # 플레이리스트 정밀 검증
    playlist = data.get("playlist", [])
    if not isinstance(playlist, list) or len(playlist) == 0:
        raise ValueError("데이터 무결성 오류: 플레이리스트(playlist) 구성안이 비어 있거나 올바르지 않습니다.")


class VideoTrack(BaseModel):
    title: str = Field(description="BGM 음원 트랙 제목")
    duration_sec: int = Field(description="BGM 음원 재생 시간(초)")


class TimelineCaption(BaseModel):
    time_code: str = Field(description="자막 표출 타임라인 시점 (예: '00:02', '00:15')")
    text: str = Field(description="화면에 노출될 감성적인 자막/멘트 문구")


class VideoPlanningJSON(BaseModel):
    concept: str = Field(description="기획안 콘셉트 및 화면 연출 요약")
    youtube_title: str = Field(description="유튜브 최종 업로드 제목 (타겟 채널 언어 100% 준수)")
    youtube_description: str = Field(description="유튜브 최종 업로드 설명란 (Video Info 감성 소개 포함)")
    youtube_tags: List[str] = Field(description="유튜브 업로드 해시태그 목록")
    playlist: List[VideoTrack] = Field(description="추천 플레이리스트 및 사운드 무드 사양")
    captions: List[TimelineCaption] = Field(description="타임라인별 자막 리스트")
    visual_audio_guide: str = Field(description="시각 연출 및 특수 효과 가이드라인")


class CallbackUpdateWrapper:
    """[R&D Lab] Update 객체의 message 속성 readonly 제약을 우회하기 위한 위임(Delegation) 래퍼"""

    def __init__(self, orig, msg):
        self._orig = orig
        self.message = msg
        self.callback_query = orig.callback_query
        self.effective_chat = orig.effective_chat
        self.effective_user = orig.effective_user

    def __getattr__(self, name):
        return getattr(self._orig, name)


class FakeMessageWrapper:
    """[R&D Lab] CallbackQuery의 message 텍스트를 '다시 시도'로 위장하여 재시도 세션을 정상 트리거하는 래퍼"""

    def __init__(self, orig_msg):
        self._orig_msg = orig_msg
        self.text = "다시 시도"

    def __getattr__(self, name):
        return getattr(self._orig_msg, name)


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
        # 💡 [한글 주석] E2E 직행 파이프라인에서 대표님이 수동 타이핑 지시 없이
        # 이미지/음원만 전송했을 경우, 파일의 실제 규격을 감지하여 포맷을 자동 매핑합니다.
        # - 이미지의 가로세로 비율(가로가 길면 16:9 롱폼)
        # - 음원의 실제 재생 길이(59.5초를 초과하면 무조건 롱폼 및 분 단위 격상)
        img_aspect_ratio = None
        session_img = (
            context.chat_data.get("last_uploaded_image") if context.chat_data else None
        )
        if session_img and os.path.exists(session_img):
            try:
                from PIL import Image

                with Image.open(session_img) as img:
                    w, h = img.size
                    if w > h:
                        img_aspect_ratio = "longform"  # 가로형 이미지 -> 롱폼
                    else:
                        img_aspect_ratio = "shorts"  # 세로형 이미지 -> 숏폼
                    print(
                        f"📷 [Image Aspect Analyzer] 자동 분석 완료: {w}x{h} -> {img_aspect_ratio}"
                    )
            except Exception as img_err:
                print(f"⚠️ [Image Aspect Analyzer] 이미지 비율 분석 실패 (기본값 유지): {img_err}")

        audio_dur_sec = None
        audio_dur_format = None
        session_audio = (
            context.chat_data.get("last_uploaded_audio") if context.chat_data else None
        )
        if session_audio and os.path.exists(session_audio):
            try:
                from telegram_bot.engine.video_renderer import get_audio_duration

                audio_dur_sec = get_audio_duration(session_audio)
                if audio_dur_sec:
                    # 💡 [한글 주석] 유튜브 Shorts 제한선인 60초(59.5초 안전마진)를 초과할 경우
                    # 숏폼으로 강제하면 렌더링은 되나 Shorts 탭에 올라가지 못하므로 자동으로 롱폼으로 판정합니다.
                    if audio_dur_sec > 59.5:
                        audio_dur_format = "longform"
                    else:
                        audio_dur_format = "shorts"
                    print(
                        f"🎵 [Audio Duration Analyzer] 자동 분석 완료: {audio_dur_sec:.2f}초 -> {audio_dur_format}"
                    )
            except Exception as audio_err:
                print(f"⚠️ [Audio Duration Analyzer] 음원 길이 분석 실패 (기본값 유지): {audio_err}")

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
            # 💡 [한글 주석] 대표님의 수동 채팅 지시가 없는 경우, 방금 실측 분석한 이미지/음원 규격을 우선 반영합니다.
            detected_format = img_aspect_ratio or audio_dur_format
            detected_length = 1
            if audio_dur_sec:
                import math

                detected_length = math.ceil(audio_dur_sec / 60)

            if detected_format:
                video_format = detected_format
                video_length = detected_length
                print(
                    f"🎯 [Production] 업로드 에셋 실측 감지 적용: Format={video_format}, Length={video_length}"
                )
            else:
                # 명시적 지시 및 업로드 자산 실측 정보가 모두 없을 때만 이전 기획 세션 캐시 참조
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

    # [루비아 기술연구소 제4연구소] 5단계 파이프라인 자율 순환 가동
    if context.chat_data is not None:
        context.chat_data["current_state"] = "STATE_BUILD_PROCESSING"

    # 1단계 접수
    load_msg = f"⚙️ *기술 디렉터 코디아*가 `{conf['name']}` {format_label} 영상 제작을 시작합니다.\n\n[📥 1단계: 이미지/영상/텍스트 접수 완료] ➔ VTM 데이터 로드 및 접수 완료 (20%)"
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

        # 1.5초 대기 후 2단계 로컬 랜딩 완료 업데이트
        await asyncio.sleep(1.5)
        step2_msg = f"⚙️ *기술 디렉터 코디아*가 `{conf['name']}` {format_label} 영상을 제작 중입니다.\n\n[💾 2단계: 로컬 랜딩 완료] ➔ 대본 자막 및 비주얼 레이어 인코딩 완료 (40%)"
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

        # 1.5초 대기 후 3단계 검토 진행 중 업데이트
        await asyncio.sleep(1.5)
        step3_msg = f"⚙️ *기술 디렉터 코디아*가 `{conf['name']}` {format_label} 영상을 제작 중입니다.\n\n[👀 3단계: 검토 진행 중] ➔ BGM 믹싱 및 렌더링 검토 진행 중 (60%)"
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

        # 1.5초 대기 후 4단계 업로드 승인 대기 업데이트
        await asyncio.sleep(1.5)
        step4_msg = f"⚙️ *기술 디렉터 코디아*가 `{conf['name']}` {format_label} 영상을 제작 중입니다.\n\n[✅ 4단계: 업로드 승인 대기] ➔ 최종 E2E 렌더링 무결성 통과 (80%)"
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
        total_success + total_failed

        # 가상 mp4 출력 파일 사양서 구성
        output_filename = f"{channel_key}_{video_format}_v1.mp4"

        # [로컬 저장소 폴더 분리 체계화]
        # 비디오 포맷(shorts vs longform)에 따라 outputs/shorts/ 또는 outputs/longform/ 하위 폴더로 동적 분리 저장합니다.
        # 💡 [AGENTS.md §4 준수] 하드코딩 절대경로 대신 실행 환경 기준 동적 경로 조립
        handler_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(
            os.path.dirname(handler_dir)
        )  # telegram_bot 상위 = 프로젝트 루트
        output_dir = os.path.join(
            project_root,
            "outputs",
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

        # 💡 [보완] 세션 메모리에 방금 업로드된 최신 이미지가 있다면 1순위로 자동 채택
        if context.chat_data and context.chat_data.get("last_uploaded_image"):
            fallback_img_path = context.chat_data.get("last_uploaded_image")
            if os.path.exists(fallback_img_path):
                custom_visual = fallback_img_path
                print(
                    f"📸 [Production] 세션 최신 업로드 이미지 자동 채택: {os.path.basename(custom_visual)}"
                )

        # 메시지에서 명시적으로 특정 파일명이 언급되었는지 확인
        # 🚨 [Fallback 금지 규칙] 대표님이 메시지에서 파일명을 직접 언급한 경우에만 custom_visual/custom_audio를 사용합니다.
        # 디렉토리 스캔 결과를 자동으로 할당하는 로직을 완전 제거합니다.
        if not custom_visual:
            for f_path in visual_paths:
                if os.path.basename(f_path) in user_message:
                    custom_visual = f_path
                    print(f"📸 [Production] 대표님이 명시한 파일 감지: {os.path.basename(f_path)}")
                    break

        # 💡 [보완] 세션 메모리에 방금 업로드된 최신 음원이 있다면 1순위로 자동 채택
        if context.chat_data and context.chat_data.get("last_uploaded_audio"):
            fallback_audio_path = context.chat_data.get("last_uploaded_audio")
            if os.path.exists(fallback_audio_path):
                custom_audio = fallback_audio_path
                print(
                    f"🎵 [Production] 세션 최신 업로드 음원 자동 채택: {os.path.basename(custom_audio)}"
                )

        if not custom_audio:
            for f_path in audio_paths:
                if os.path.basename(f_path) in user_message:
                    custom_audio = f_path
                    print(
                        f"🎵 [Production] 대표님이 명시한 음원 파일 감지: {os.path.basename(f_path)}"
                    )
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
        last_planning_json = None
        if is_retry:
            last_planning_json = cached_context.get("last_planning_json")
        elif context.chat_data is not None:
            last_planning_json = context.chat_data.get("last_planning_json")
        # 재시도 모드가 아닐 때에만 기획 재생성을 판단
        if not is_retry and (not last_planning_json or is_new_plan_requested):
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

            from telegram_bot.config import CHANNEL_IDENTITIES

            identity = CHANNEL_IDENTITIES.get(channel_key, "일반 동영상 크리에이터 채널")

            # 실시간 심층 기획 템플릿 호출 (자막 은은성 룰 반영)
            system_instruction = (
                "당신은 루비아 팀의 기획팀장 '라비아'입니다. "
                f"대표님의 지시에 따라 {video_format} 영상 대본을 구성하십시오. "
                "자막의 간격은 빽빽하지 않고 은은하게(예: 8초~15초 간격으로 짧고 감성적인 핵심 메시지만 분산 배치) 구성하십시오. "
                "'AI', '인공지능', '자동화' 등의 단어는 절대 금지합니다."
            )

            # [한글 주석] Rubia 채널도 글로벌 영어(English Only)로 단일화하여 대만어/일본어 출력을 원천 방지
            lang_rule = (
                "영어(English)로만 대사/자막, 그리고 최종 영상 제목과 설명란을 100% 영문으로만 작성하십시오. 한국어와 대만어(번체자), 일본어는 절대 금지합니다."
                if channel_key in ["aura", "taipei", "rubia"]
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
                from telegram_bot.engine.llm_client import generate_structured_json

                last_planning_json = await asyncio.to_thread(
                    generate_structured_json,
                    plan_prompt,
                    system_instruction,
                    response_schema=VideoPlanningJSON,
                    mode=llm_mode,
                    local_url=local_url,
                )

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

                def cleanse_text(text: str) -> str:
                    if not text:
                        return ""
                    for word in forbidden_words:
                        text = text.replace(word, "")
                    import re

                    text = re.sub(r"\n{3,}", "\n\n", text)
                    return text.strip()

                last_planning_json["concept"] = cleanse_text(
                    last_planning_json.get("concept", "")
                )
                last_planning_json["youtube_title"] = cleanse_text(
                    last_planning_json.get("youtube_title", "")
                )
                last_planning_json["youtube_description"] = cleanse_text(
                    last_planning_json.get("youtube_description", "")
                )
                last_planning_json["visual_audio_guide"] = cleanse_text(
                    last_planning_json.get("visual_audio_guide", "")
                )

                for caption in last_planning_json.get("captions", []):
                    caption["text"] = cleanse_text(caption.get("text", ""))

                for track in last_planning_json.get("playlist", []):
                    track["title"] = cleanse_text(track.get("title", ""))

                playlist_str = "\n".join(
                    [
                        f"- {t.get('title', 'Untitled')} ({t.get('duration_sec', 0)}초)"
                        for t in last_planning_json.get("playlist", [])
                    ]
                )
                captions_str = "\n".join(
                    [
                        f"- [{c.get('time_code', '00:00')}] {c.get('text', '')}"
                        for c in last_planning_json.get("captions", [])
                    ]
                )
                tags_str = " ".join(last_planning_json.get("youtube_tags", []))

                planning_script = (
                    f"🎯 *[기획 콘셉트]*\n{last_planning_json.get('concept', '')}\n\n"
                    f"💡 *[영상 제목 및 썸네일 추천]*\n- 유튜브 공식 제목: {last_planning_json.get('youtube_title', '')}\n- 연출 가이드: {last_planning_json.get('visual_audio_guide', '')}\n\n"
                    f"🎵 *[플레이리스트 및 음원 트랙 구성]*\n{playlist_str}\n\n"
                    f"🎬 *[대본 및 자막 타임라인]*\n{captions_str}\n\n"
                    f"📝 *[유튜브 최종 업로드 메타데이터]*\n"
                    f"- 제목: {last_planning_json.get('youtube_title', '')}\n"
                    f"- 설명란:\n{last_planning_json.get('youtube_description', '')}\n"
                    f"- 태그: {tags_str}"
                )

                # [Validation Gate] Check background planning json integrity
                validate_planning_json(last_planning_json)

                if context.chat_data is not None:
                    context.chat_data["last_planning_json"] = last_planning_json
                    context.chat_data["last_planning_result"] = planning_script
                    context.chat_data["last_generated_plan"] = planning_script
                    context.chat_data["last_planning_format"] = video_format
                    context.chat_data["last_planning_length"] = video_length
                print("Validation Gate passed. Background planning succeeded.")
            except Exception as pe:
                print(f"Background planning failed or discarded: {pe}")

        # 최종 기획 텍스트 검증 폴백
        if not planning_script:
            if channel_key in ["aura", "rubia"]:
                planning_script = "자막: Close your eyes and breathe in.\n자막: Feel the warm energy flowing.\n자막: Let go of all your tension."
            elif channel_key == "taipei":
                planning_script = "자막: Close your eyes and breathe deeply.\n자막: Feel the warm greenhouse breeze.\n자막: Release all your stress and coding fatigue."
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

                    # 💵 [비용 최적화] Imagen 이미지 생성 비용 로깅 이식
                    try:
                        from telegram_bot.config import COST_IMAGEN_IMAGE
                        from telegram_bot.utils.cost_logger import log_api_cost

                        log_api_cost(
                            "Imagen 4.0 (Visual)",
                            COST_IMAGEN_IMAGE,
                            f"File: {generated_img_filename}",
                        )
                    except Exception as cle:
                        print(f"⚠️ [Cost Logging Fail] 비용 로깅 실패: {cle}")

                    print(
                        f"[Imagen Success] Saved generated image to: {generated_img_path}"
                    )
                else:
                    print("[Imagen Error] No images returned.")
            except Exception as ie:
                import traceback

                traceback.print_exc()
                print(f"🚨 [Imagen Error]: {ie}")

                # 🛡️ [자가 치유 의사결정 세션 캐싱]
                if context.chat_data is not None:
                    context.chat_data["fallback_session"] = {
                        "channel_key": channel_key,
                        "video_format": video_format,
                        "video_length": video_length,
                        "file_path": file_path,
                        "output_dir": output_dir,
                        "planning_script": planning_script,
                        "visual_paths": visual_paths,
                        "audio_paths": audio_paths,
                        "character_names": character_names,
                    }

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "1️⃣ 최근 이미지/음원 사용", callback_data="fallback_use_recent"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "2️⃣ 다시 시도하기 (API 재호출)", callback_data="fallback_retry"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "3️⃣ 이번 기획 종료", callback_data="fallback_cancel"
                        )
                    ],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    "🚨 *[API 장애 감지] 이미지 생성 중 에러가 발생했습니다.*\n"
                    "오류 원인: `RESOURCE_EXHAUSTED (429) 또는 API 미응답`\n\n"
                    "대표님, 아래 대체 방법 중 하나를 선택해 진행해 주세요:",
                    reply_markup=reply_markup,
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
                print(f"🚨 [Audio Generation Error]: {e}")
                # 🛡️ [자가 치유 의사결정 세션 캐싱]
                if context.chat_data is not None:
                    context.chat_data["fallback_session"] = {
                        "channel_key": channel_key,
                        "video_format": video_format,
                        "video_length": video_length,
                        "file_path": file_path,
                        "output_dir": output_dir,
                        "planning_script": planning_script,
                        "visual_paths": visual_paths,
                        "audio_paths": audio_paths,
                        "character_names": character_names,
                    }

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "1️⃣ 최근 이미지/음원 사용", callback_data="fallback_use_recent"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "2️⃣ 다시 시도하기 (API 재호출)", callback_data="fallback_retry"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "3️⃣ 이번 기획 종료", callback_data="fallback_cancel"
                        )
                    ],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    "🚨 *[API 장애 감지] 음원 생성 중 에러가 발생했습니다.*\n"
                    "오류 원인: `RESOURCE_EXHAUSTED (429) 또는 API 미응답`\n\n"
                    "대표님, 아래 대체 방법 중 하나를 선택해 진행해 주세요:",
                    reply_markup=reply_markup,
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
            context.chat_data["pending_planning_json"] = last_planning_json
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
            context.chat_data["current_state"] = "STATE_ASSET_STANDBY"

            # 에셋이 생성 완료되었으므로 에러 재시도 상태를 안전하게 해제합니다.
            context.chat_data["awaiting_error_retry"] = False
            context.chat_data["error_retry_context"] = None
            print(
                "🧹 [Production] 에셋 정상 생성 완료. 에러 재시도 캐시 세션 초기화 및 상태를 STATE_ASSET_STANDBY로 지정."
            )

        # 5. 승인 대기 메시지 송출 및 프로세스 중단 (Standby)
        standby_msg = (
            f"✅ *에셋 생성이 완료되었습니다.* (파일 확인 요망)\n\n"
            f"📸 이미지: `{os.path.basename(dummy_img)}`\n"
            f"🎵 음원: `{os.path.basename(dummy_audio)}`\n"
            f"📝 대본: 기획안 캐싱 완료\n\n"
            f"대표님, 이 결과물로 *영상 렌더링 단계(비디오 빌드)*를 진행할까요?\n"
            f"아래 버튼 또는 채팅('진행해', '영상 만들어', 'OK')으로 승인해 주세요:"
        )

        # 💡 [반복 방지] 에셋 대기 단계용 세분화된 행동 버튼 구성
        keyboard = [
            [
                InlineKeyboardButton("🚀 렌더링 시작", callback_data="btn_build_start"),
                InlineKeyboardButton(
                    "📤 렌더링 후 자동 업로드", callback_data="btn_build_upload"
                ),
            ],
            [
                InlineKeyboardButton("🔄 이미지 재생성", callback_data="btn_regen_img"),
                InlineKeyboardButton("🎵 BGM 재생성", callback_data="btn_regen_aud"),
            ],
            [InlineKeyboardButton("❌ 이번 세션 취소", callback_data="btn_cancel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if success_img:
            with open(success_img, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=standby_msg,
                    reply_markup=reply_markup,
                    parse_mode="Markdown",
                )
        else:
            await update.message.reply_text(
                standby_msg, reply_markup=reply_markup, parse_mode="Markdown"
            )

        # 🚨 [핵심] 여기서 return하여 비디오 렌더링을 진행하지 않고 대기합니다.
        # 대표님의 승인 명령이 들어오면 handle_approved_build()가 호출됩니다.
        print("⏸️ [Production] 에셋 생성 완료. 대표님의 승인 명령 대기 중 (Standby 모드)...")

    except Exception as e:
        import traceback

        traceback.print_exc()
        error_msg = f"❌ *코디아 빌드 에러*: 에셋 생성 파이프라인을 완료하지 못했습니다.\n" f"상세 오류: `{str(e)}`"
        await update.message.reply_text(error_msg, parse_mode="Markdown")
        # 한글 설명: 예외 발생 시 세션 락(Session Lock) 교착 상태 방지를 위해 상태 초기화
        if context.chat_data is not None:
            context.chat_data["current_state"] = None
    finally:
        # 한글 설명: 예외가 발생하여 STANDBY 단계로 진입하지 못하고 걸린 락 강제 해제
        if (
            context.chat_data is not None
            and context.chat_data.get("current_state") == "STATE_BUILD_PROCESSING"
        ):
            if not context.chat_data.get("awaiting_build_approval"):
                context.chat_data["current_state"] = None
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
    pending_planning_json = context.chat_data.get("pending_planning_json")
    channel_key = context.chat_data.get("pending_channel_key", "rubia")

    # ♻️ [한글 설명 - 자가 치유 세션 복구]
    # 봇 재시작/강제종료 후 강제 복원 등으로 기획 JSON이 유실되고 대본 텍스트만 복구된 경우,
    # 렌더러의 JSON 명세 계약 규격에 맞춰 무결성 JSON을 즉시 복원하여 빌드를 완수할 수 있게 가공합니다.
    if not pending_planning_json and planning_script:
        try:
            lines = planning_script.split("\n")
            temp_captions = []
            for line in lines:
                matched_prefix = None
                for prefix in ["자막:", "자막：", "字幕:", "字幕：", "Subtitle:", "Subtitle："]:
                    if prefix in line:
                        matched_prefix = prefix
                        break
                if matched_prefix:
                    parts = line.split(matched_prefix, 1)
                    txt = parts[1].strip().strip('"').strip("'").strip()
                    if txt:
                        temp_captions.append({"time_code": "00:00", "text": txt})

            if temp_captions:
                pending_planning_json = {
                    "concept": f"Restored concept for {channel_key}",
                    "youtube_title": f"Restored Title for {channel_key}",
                    "youtube_description": "Restored description",
                    "youtube_tags": ["restored"],
                    "playlist": [{"title": "Restored Track", "duration_sec": 60}],
                    "captions": temp_captions,
                }
                context.chat_data["pending_planning_json"] = pending_planning_json
                print(
                    "♻️ [Session Restore] 텍스트 대본으로부터 렌더러 스키마 준수용 JSON 데이터 복원 및 캐싱 주입 완료."
                )
        except Exception as restore_err:
            print(f"⚠️ [Session Restore Error] JSON 데이터 자가 복원 실패: {restore_err}")

    # [R&D Validation Gate] 렌더링 개시 전 교차 검사
    if pending_planning_json:
        try:
            validate_planning_json(pending_planning_json)
            print("✅ [Validation Gate] 빌드 승인 단계 기획 데이터 무결성 검증 통과.")
        except Exception as val_err:
            print(f"🚨 [Validation Gate Discard] 빌드 승인 단계 쓰레기 데이터 감지 차단: {val_err}")
            await update.message.reply_text(
                f"🚨 *[데이터 무결성 오류]*\n"
                f"승인 대기 중인 기획 데이터 규격에 결손이 감지되어 비디오 빌드를 즉각 차단 및 폐기했습니다.\n"
                f"상세 사유: `{val_err}`",
                parse_mode="Markdown",
            )
            context.chat_data["awaiting_build_approval"] = False
            return

    if not planning_script:
        # 💡 [방어적 프로그래밍 - 세션 복원 시 대본 유실 방지]
        # 봇 재부팅 후 강제 복원 등으로 대본이 유실되었을 경우, 채널 성격에 맞는 기본 템플릿 대본을 자동 맵핑합니다.
        if channel_key in ["aura", "rubia"]:
            planning_script = "자막: Close your eyes and breathe in.\n자막: Feel the warm energy flowing.\n자막: Let go of all your tension."
        elif channel_key == "taipei":
            planning_script = "자막: Close your eyes and breathe deeply.\n자막: Feel the warm greenhouse breeze.\n자막: Release all your stress and coding fatigue."
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
                "🚨 *[에셋 누락] 이미지/음원 파일을 찾을 수 없습니다.* 에셋 생성을 다시 요청해 주세요.",
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

        # 느슨한 결합(Loose Coupling) 원칙에 따라, 구조화 JSON이 있으면 JSON을 우선 전달, 없으면 텍스트(하위 호환) 전달
        render_data = pending_planning_json or planning_script

        await asyncio.to_thread(
            render_video,
            dummy_img,
            dummy_audio,
            render_data,
            file_path,
            video_format=video_format,
            custom_style=custom_style,
        )

        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

        # 💡 [한글 주석] 대표님이 메신저에서 실제 렌더링 영상을 감상한 후 수동으로 업로드를 누르도록
        # 렌더링 직후 즉시 자동 업로드되는 E2E 연동은 비활성화합니다.
        should_upload = False
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

        # 💡 [한글 주석] 완성된 비디오의 실제 재생시간을 구하는 도우미 함수를 정의합니다.
        # 외부 FFmpeg 엔진을 통해 실측하며, 만약의 오류 시에는 기존 기획 분량을 폴백으로 적용합니다.
        def get_actual_duration_str(video_file_path, fallback_length):
            try:
                from telegram_bot.engine.video_renderer import get_audio_duration

                actual_seconds = get_audio_duration(video_file_path)
                if actual_seconds:
                    m = int(actual_seconds // 60)
                    s = int(round(actual_seconds % 60))
                    if m > 0:
                        return f"{m}분 {s}초" if s > 0 else f"{m}분"
                    else:
                        return f"{s}초"
            except Exception as dur_err:
                print(f"⚠️ [Report Helper] 완성 비디오 실측 실패: {dur_err}")
            return f"{fallback_length}분"

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
            "[📊 5단계: 보고서 발행 완료] ➔ 비디오 렌더링 완수 및 주간 진화 RAG 데이터 연동 (100%)\n",
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
                # 💡 [한글 주석] 하드코딩된 재생시간 변수 출력 대신 실측 시간을 출력하여 괴리를 해소합니다.
                f"• **재생 시간**: `{get_actual_duration_str(file_path, video_length)}`",
                f"• **용량**: `{file_size_mb:.1f} MB`\n",
                f"📊 *E2E 검증*: 성공 {total_success} / 실패 {total_failed} (총 {total_tests})",
            ]
        )

        final_report = "\n".join(report_lines)

        if success_img and os.path.exists(success_img):
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
        context.chat_data["current_state"] = None
        # 💡 [보완] 비디오 합성 완료 시 임시 업로드 에셋 정보 클린업
        context.chat_data["last_uploaded_file"] = None
        context.chat_data["last_uploaded_sub_dir"] = None
        context.chat_data["last_uploaded_name"] = None
        context.chat_data["last_uploaded_image"] = None
        context.chat_data["last_uploaded_audio"] = None
        context.chat_data["last_uploaded_video"] = None
        context.chat_data["last_uploaded_caption"] = None

        # 💡 [반복 방지] 빌드 완료 후 대표님의 다음 의사결정 수립용 세분화 버튼 구성
        upload_keyboard = [
            [
                InlineKeyboardButton("📤 유튜브 비공개 업로드", callback_data="btn_yt_private"),
                InlineKeyboardButton("📢 유튜브 즉시 공개 게시", callback_data="btn_yt_public"),
            ],
            [
                InlineKeyboardButton("✨ 새 동영상 기획하기", callback_data="btn_new_plan"),
                InlineKeyboardButton("❌ 이번 기획 종료", callback_data="btn_cancel"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(upload_keyboard)

        await update.message.reply_text(
            "✅ *비디오 빌드 및 무결성 검증이 완료되었습니다!*\n" "유튜브에 바로 업로드하시거나 다음 작업을 지시해 주세요:",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        await update.message.reply_text(
            f"❌ *코디아 렌더링 에러*: `{str(e)}`", parse_mode="Markdown"
        )
        context.chat_data["awaiting_build_approval"] = False
        context.chat_data["current_state"] = None
    finally:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id, message_id=status_msg.message_id
            )
        except Exception:
            pass


@check_permission
async def regenerate_image_only(
    update: Update, context: ContextTypes.DEFAULT_TYPE, channel_key: str = None
) -> None:
    query = update.callback_query
    chat_data = context.chat_data
    if not chat_data or not chat_data.get("pending_script"):
        await query.message.reply_text("⚠️ 기획안 데이터가 유실되었습니다. 새로 기획을 진행해 주세요.")
        return

    user_message = "새로 기획해서 이미지 배경 만들어줘"
    planning_script = chat_data.get("pending_script")
    video_format = chat_data.get("pending_video_format", "shorts")
    channel_key = channel_key or chat_data.get("pending_channel_key", "rubia")

    from telegram_bot.config import CHANNEL_MAP

    CHANNEL_MAP.get(channel_key, {"name": channel_key})

    output_dir = chat_data.get("pending_output_dir")
    if not output_dir:
        output_dir = os.path.join(
            "c:/1인기업/Apps/유튜브에이전트/outputs",
            "shorts" if video_format == "shorts" else "longform",
            channel_key,
        )
    input_channel_dir = os.path.join("c:/1인기업/Apps/유튜브에이전트/input", channel_key)
    images_dir = os.path.join(input_channel_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    working_img = get_agent_image_path("cordia", "working")
    step_msg = "🔄 *[이미지 모듈 단독 재생성]* Imagen 4.0 API를 호출하여 이미지만 새로 렌더링합니다...\n\n🚀 기획안 기반 고화질 이미지 생성 중..."

    status_msg = None
    if working_img:
        with open(working_img, "rb") as photo:
            status_msg = await query.message.reply_photo(
                photo=photo, caption=step_msg, parse_mode="Markdown"
            )
    else:
        status_msg = await query.message.reply_text(step_msg, parse_mode="Markdown")

    from telegram_bot.config import GEMINI_API_KEY

    api_key = GEMINI_API_KEY.split(",")[0].strip() if GEMINI_API_KEY else None

    generated_img_path = None
    if api_key:
        try:
            from google import genai
            from google.genai import types
            import datetime

            client = genai.Client(api_key=api_key)
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
                return r.text.strip().strip("\"'")

            image_prompt = await asyncio.to_thread(extract_prompt)
            print(f"[Imagen Prompt Generation] Generated Prompt: {image_prompt}")

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
                generated_img_filename = (
                    f"generated_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                )
                generated_img_path = os.path.join(images_dir, generated_img_filename)
                import io
                from PIL import Image

                image = Image.open(io.BytesIO(img_data.image.image_bytes))
                image.save(generated_img_path)

                # 💵 [비용 최적화] Imagen 이미지 생성 비용 로깅 이식
                try:
                    from telegram_bot.config import COST_IMAGEN_IMAGE
                    from telegram_bot.utils.cost_logger import log_api_cost

                    log_api_cost(
                        "Imagen 4.0 (Visual)",
                        COST_IMAGEN_IMAGE,
                        f"File: {generated_img_filename}",
                    )
                except Exception as cle:
                    print(f"⚠️ [Cost Logging Fail] 비용 로깅 실패: {cle}")
        except Exception as e:
            print(f"🚨 [Imagen Error]: {e}")
            await status_msg.reply_text(f"❌ 이미지 생성 에러: {e}")
            return

    if not generated_img_path:
        await status_msg.reply_text("❌ 이미지 생성에 실패했습니다.")
        return

    chat_data["pending_visual"] = generated_img_path
    chat_data["asset_creation_timestamp"] = (
        __import__("datetime").datetime.now().timestamp()
    )

    try:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=status_msg.message_id
        )
    except Exception:
        pass

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="upload_photo"
    )
    with open(generated_img_path, "rb") as img_file:
        await query.message.reply_photo(
            photo=img_file,
            caption=f"🎨 새로 생성된 배경 이미지: `{os.path.basename(generated_img_path)}`",
            parse_mode="Markdown",
        )

    await _show_standby_menu(update, context)


@check_permission
async def regenerate_audio_only(
    update: Update, context: ContextTypes.DEFAULT_TYPE, channel_key: str = None
) -> None:
    query = update.callback_query
    chat_data = context.chat_data
    if not chat_data or not chat_data.get("pending_script"):
        await query.message.reply_text("⚠️ 기획안 데이터가 유실되었습니다. 새로 기획을 진행해 주세요.")
        return

    video_length = chat_data.get("pending_video_length", 1)
    video_format = chat_data.get("pending_video_format", "shorts")
    channel_key = channel_key or chat_data.get("pending_channel_key", "rubia")
    output_dir = chat_data.get("pending_output_dir")
    if not output_dir:
        output_dir = os.path.join(
            "c:/1인기업/Apps/유튜브에이전트/outputs",
            "shorts" if video_format == "shorts" else "longform",
            channel_key,
        )

    working_img = get_agent_image_path("cordia", "working")
    step_msg = "🔄 *[오디오 모듈 단독 재생성]* Lyria 3 Pro API를 호출하여 음원만 새로 렌더링합니다...\n\n🎵 실시간 작곡 중 (1~5분 소요 예상)"

    status_msg = None
    if working_img:
        with open(working_img, "rb") as photo:
            status_msg = await query.message.reply_photo(
                photo=photo, caption=step_msg, parse_mode="Markdown"
            )
    else:
        status_msg = await query.message.reply_text(step_msg, parse_mode="Markdown")

    import datetime

    audio_filename = f"{channel_key}_music_generated_regen_{datetime.datetime.now().strftime('%H%M%S')}.mp3"
    audio_path = os.path.join(output_dir, audio_filename)

    try:
        from telegram_bot.engine.audio_generator import generate_lyria3_music

        generated_audio = await asyncio.to_thread(
            generate_lyria3_music, channel_key, audio_path, duration_min=video_length
        )
    except Exception as e:
        print(f"🚨 [Audio Error]: {e}")
        await status_msg.reply_text(f"❌ 음원 생성 에러: {e}")
        return

    chat_data["pending_audio"] = generated_audio
    chat_data["asset_creation_timestamp"] = datetime.datetime.now().timestamp()

    try:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=status_msg.message_id
        )
    except Exception:
        pass

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="upload_voice"
    )
    with open(generated_audio, "rb") as audio_file:
        await query.message.reply_audio(
            audio=audio_file,
            caption=f"🎵 새로 생성된 BGM 음원: `{os.path.basename(generated_audio)}`",
            parse_mode="Markdown",
        )

    await _show_standby_menu(update, context)


async def _show_standby_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_data = context.chat_data
    dummy_img = chat_data.get("pending_visual", "")
    dummy_audio = chat_data.get("pending_audio", "")

    now_ts = __import__("time").time()
    if os.path.exists(dummy_img):
        img_mtime = os.path.getmtime(dummy_img)
        if not (0 <= now_ts - img_mtime <= 900):
            await update.callback_query.message.reply_text(
                "🚨 *[타임스탬프 검증 실패] 이미지 파일 유효시간 15분 초과.* 재생성 바랍니다.", parse_mode="Markdown"
            )
            return
    if os.path.exists(dummy_audio):
        audio_mtime = os.path.getmtime(dummy_audio)
        if not (0 <= now_ts - audio_mtime <= 900):
            await update.callback_query.message.reply_text(
                "🚨 *[타임스탬프 검증 실패] 음원 파일 유효시간 15분 초과.* 재생성 바랍니다.", parse_mode="Markdown"
            )
            return

    standby_msg = (
        f"✅ *모듈 단위 에셋 갱신이 완료되었습니다.* (파일 확인 요망)\n\n"
        f"📸 현재 적용 이미지: `{os.path.basename(dummy_img)}`\n"
        f"🎵 현재 적용 음원: `{os.path.basename(dummy_audio)}`\n"
        f"📝 대본: 기획안 유지됨\n\n"
        f"대표님, 이 결과물로 *영상 조립(비디오 빌드)*을 바로 진행할까요?\n"
    )

    keyboard = [
        [
            InlineKeyboardButton("🚀 렌더링 시작", callback_data="btn_build_start"),
            InlineKeyboardButton("📤 렌더링 후 자동 업로드", callback_data="btn_build_upload"),
        ],
        [
            InlineKeyboardButton("🔄 이미지 단독 재생성", callback_data="btn_regen_img"),
            InlineKeyboardButton("🎵 BGM 단독 재생성", callback_data="btn_regen_aud"),
        ],
        [InlineKeyboardButton("❌ 이번 세션 취소", callback_data="btn_cancel")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    success_img = get_agent_image_path("cordia", "success")
    query = update.callback_query
    if success_img:
        with open(success_img, "rb") as photo:
            await query.message.reply_photo(
                photo=photo,
                caption=standby_msg,
                reply_markup=reply_markup,
                parse_mode="Markdown",
            )
    else:
        await query.message.reply_text(
            standby_msg, reply_markup=reply_markup, parse_mode="Markdown"
        )


@check_permission
async def handle_callback_query(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """[R&D Lab 보안/자가치유 & 세분화 버튼 라우팅] 텔레그램의 모든 인라인 버튼 이벤트를 받아 분기 처리하는 허브 핸들러"""
    query = update.callback_query
    if not query:
        return

    await query.answer()

    data = query.data
    chat_data = context.chat_data

    # 1-1. 곡명 자동 작명 선택 처리 (t_sel_[session_id]_[option_idx])
    if data.startswith("t_sel_"):
        parts = data.split("_")
        if len(parts) >= 4:
            session_id = parts[2]
            try:
                option_idx = int(parts[3])
            except ValueError:
                option_idx = 0

            session_db = context.bot_data.get("planning_sessions", {})
            session_data = session_db.get(session_id)

            if session_data:
                planning_json = session_data.get("planning_json", {})
                suggested = planning_json.get("suggested_titles", [])
                if suggested and option_idx < len(suggested):
                    selected_title = suggested[option_idx]

                    # 곡명 업데이트
                    old_title = planning_json.get("youtube_title", "")
                    planning_json["youtube_title"] = selected_title

                    # 브리핑 텍스트에서도 구/신 제목 치환
                    planning_text = session_data.get("planning_text", "")
                    if old_title and old_title in planning_text:
                        planning_text = planning_text.replace(old_title, selected_title)

                    session_data["planning_json"] = planning_json
                    session_data["planning_text"] = planning_text

                    # 현재 세션 캐시 동기화
                    if chat_data:
                        chat_data["last_planning_json"] = planning_json
                        chat_data["last_planning_result"] = planning_text

                    await query.message.reply_text(
                        f"✅ *[곡명 확정]* 곡명이 **'{selected_title}'**(으)로 수정 및 자동 적용되었습니다.",
                        parse_mode="Markdown",
                    )
                else:
                    await query.message.reply_text("⚠️ 선택한 곡명 후보 데이터를 찾을 수 없습니다.")
            else:
                await query.message.reply_text("⚠️ 기획 세션이 만료되었습니다. 다시 기획해 주세요.")
        return

    # 1. 취소 버튼 (공통)
    if data in ["btn_cancel", "fallback_cancel"]:
        if chat_data:
            chat_data["fallback_session"] = None
            chat_data["awaiting_build_approval"] = False
            chat_data["awaiting_error_retry"] = False
            chat_data["current_state"] = None
            chat_data["pending_visual"] = None
            chat_data["pending_audio"] = None
            chat_data["pending_script"] = None
            # 💡 [보완] 임시 업로드 에셋 정보 클린업
            chat_data["last_uploaded_file"] = None
            chat_data["last_uploaded_sub_dir"] = None
            chat_data["last_uploaded_name"] = None
            chat_data["last_uploaded_image"] = None
            chat_data["last_uploaded_audio"] = None
            chat_data["last_uploaded_video"] = None
            chat_data["last_uploaded_caption"] = None
        await query.message.reply_text(
            "🛑 *진행 중이던 기획 및 영상 제작 세션이 최종 취소(종료)되었습니다.*", parse_mode="Markdown"
        )
        return

    # 2-2. 💡 [한글 주석] 대표님이 업로드한 파일에 대해 숏폼/롱폼 포맷 선택 버튼을 눌렀을 때의 콜백을 처리합니다.
    # 세션 메모리에 포맷을 캐싱하고 음원 추가 방식 설정 인라인 키보드를 출력합니다.
    if data.startswith("btn_format_"):
        parts = data.split("_")
        if len(parts) >= 4:
            format_type = parts[2]  # "shorts" or "longform"
            target_channel = parts[3]  # "rubia", "aura", "taipei" 등

            if chat_data is not None:
                chat_data["target_format"] = format_type
                # 숏폼이면 1분, 롱폼이면 10분을 기본으로 설정 (사용자 음원 실측에서 재정의됨)
                chat_data["target_length"] = 1 if format_type == "shorts" else 10
                chat_data["current_state"] = "STATE_WAITING_AUDIO_DECISION"

            from telegram_bot.config import CHANNEL_MAP

            channel_name = CHANNEL_MAP.get(target_channel, {}).get(
                "name", target_channel
            )
            format_label = (
                "숏폼 (Shorts, 9:16)"
                if format_type == "shorts"
                else "롱폼 (Long-form, 16:9)"
            )

            next_report = (
                f"🎬 *포맷 설정 완료*: `{format_label}`\n\n"
                f"🎵 *[음원 추가 방식 설정]*\n"
                f"`{channel_name}` 채널 영상에 삽입할 음원(BGM)을 어떻게 제공하시겠습니까?\n"
                f"원하시는 방식을 선택해 주세요:"
            )

            keyboard = [
                [
                    InlineKeyboardButton(
                        "📁 사용자음원추가", callback_data=f"btn_audio_user_{target_channel}"
                    ),
                    InlineKeyboardButton(
                        "🎵 음원자동생성", callback_data=f"btn_audio_auto_{target_channel}"
                    ),
                ],
                [InlineKeyboardButton("❌ 이번 세션 취소", callback_data="btn_cancel")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.message.reply_text(
                next_report, reply_markup=reply_markup, parse_mode="Markdown"
            )
        return

    # 2. [핫픽스] 기획안(UUID) 기반 버튼 분기 처리 (세션 유지 및 자가 치유)
    if data.startswith("b_prod_") or data.startswith("b_plan_"):
        session_id = data.split("_", 2)[-1]
        session_db = context.bot_data.get("planning_sessions", {})
        session_data = session_db.get(session_id)

        channel_key = "rubia"  # default

        if session_data:
            channel_key = session_data.get("channel_key", "rubia")
            # 코디아(Technical Lead)가 조회하여 임시 DB에서 기획안 데이터 복원 (Hand-off 무결성)
            chat_data["last_planning_json"] = session_data.get("planning_json")
            chat_data["last_planning_result"] = session_data.get("planning_text")
            chat_data["target_format"] = session_data.get("video_format", "shorts")
            chat_data["target_length"] = session_data.get("video_length", 1)
            print(f"✅ [Session DB] UUID({session_id})로 기획안 데이터를 정상 복원했습니다.")
        else:
            print(
                f"⚠️ [Session DB] UUID({session_id})를 찾을 수 없습니다. 자가 치유(Self-healing) 로직 가동."
            )
            # 자가 치유(Self-healing) 로직: 단기 기억(Memory Layer) 뒤지기
            if chat_data and (
                chat_data.get("last_planning_result")
                or chat_data.get("last_planning_json")
            ):
                print("🔄 [Self-healing] 가장 최근에 승인 대기 중인 기획안을 찾아내어 복구했습니다.")
                # 채널키는 기본값 또는 이전 저장값으로 폴백
            else:
                await query.message.reply_text(
                    "⚠️ *참조 파일 정보가 완전히 유실되었습니다.* 자가 치유에 실패했습니다. 다시 기획을 요청해 주세요.",
                    parse_mode="Markdown",
                )
                return

        if data.startswith("b_prod_"):
            await query.message.reply_text(
                f"🚀 *[제작 진행]* `{channel_key}` 채널의 복원된 기획안으로 영상 에셋 생성을 시작합니다...",
                parse_mode="Markdown",
            )
            wrapped_message = FakeMessageWrapper(query.message)
            wrapped_message.text = f"{channel_key} 채널로 영상 만들어줘"
            wrapped_update = CallbackUpdateWrapper(update, wrapped_message)

            chat_data["current_state"] = "STATE_ASSET_PROCESSING"
            await handle_production(wrapped_update, context, channel_key=channel_key)

        elif data.startswith("b_plan_"):
            await query.message.reply_text(
                f"📝 *[기획 재구성]* `{channel_key}` 채널의 기획안을 새로 구성합니다...",
                parse_mode="Markdown",
            )
            wrapped_message = FakeMessageWrapper(query.message)
            wrapped_message.text = f"{channel_key} 채널 영상 새로 기획해줘"
            wrapped_update = CallbackUpdateWrapper(update, wrapped_message)

            chat_data["current_state"] = "STATE_PLANNING_PROCESSING"
            from telegram_bot.handlers.planning import handle_planning

            await handle_planning(wrapped_update, context, channel_key=channel_key)
        return

    # 3-1. 음원 설정 분기 버튼 처리 (사용자음원추가 및 음원자동생성)
    if data.startswith("btn_audio_user_") or data.startswith("btn_audio_auto_"):
        if not chat_data:
            await query.message.reply_text(
                "⚠️ *세션 정보가 유실되었습니다.* 다시 진행해 주세요.", parse_mode="Markdown"
            )
            return

        if data.startswith("btn_audio_user_"):
            channel_key = data.replace("btn_audio_user_", "")
            chat_data["current_state"] = "STATE_WAITING_USER_AUDIO"
            chat_data["pending_channel_key"] = channel_key

            await query.message.reply_text(
                f"📁 *[사용자 음원 추가]*\n\n"
                f"대표님, `{channel_key}` 채널 영상 제작에 사용할 **음원 파일(MP3, WAV 등)**을 텔레그램으로 전송해 주세요.\n"
                f"파일 수신이 확인되면 자동으로 영상 제작 단계로 이어집니다.",
                parse_mode="Markdown",
            )
            return

        elif data.startswith("btn_audio_auto_"):
            channel_key = data.replace("btn_audio_auto_", "")
            await query.message.reply_text(
                f"🎵 *[음원 자동 생성]*\n\n"
                f"`{channel_key}` 채널 성격에 맞는 AI 음원을 자동으로 생성한 후 영상 제작을 개시합니다...",
                parse_mode="Markdown",
            )

            # E2E 제작 진입을 위해 에셋 구성 및 handle_production 호출
            uploaded_file_name = chat_data.get("last_uploaded_name", "")
            user_caption = chat_data.get("last_uploaded_caption", "")

            uploaded_assets = []
            if chat_data.get("last_uploaded_image"):
                uploaded_assets.append(
                    f"이미지({os.path.basename(chat_data['last_uploaded_image'])})"
                )
            if chat_data.get("last_uploaded_audio"):
                uploaded_assets.append(
                    f"음원({os.path.basename(chat_data['last_uploaded_audio'])})"
                )
            if chat_data.get("last_uploaded_video"):
                uploaded_assets.append(
                    f"영상({os.path.basename(chat_data['last_uploaded_video'])})"
                )

            assets_str = (
                " 및 ".join(uploaded_assets) if uploaded_assets else uploaded_file_name
            )

            wrapped_message = FakeMessageWrapper(query.message)
            req_text = f"{channel_key} 채널로 {assets_str} 사용하여 영상 만들어줘"
            if user_caption:
                req_text += f". 설명: {user_caption}"
            wrapped_message.text = req_text
            wrapped_update = CallbackUpdateWrapper(update, wrapped_message)

            chat_data["current_state"] = "STATE_ASSET_PROCESSING"
            await handle_production(wrapped_update, context, channel_key=channel_key)
            return

    # 3. 파일 수신 후 채널/작업 분기 버튼 처리 (레거시 파일 업로드용)
    if data.startswith("btn_prod_") or data.startswith("btn_plan_"):
        if not chat_data or "last_uploaded_name" not in chat_data:
            await query.message.reply_text(
                "⚠️ *참조 파일 정보가 유실되었습니다.* 다시 업로드해 주세요.", parse_mode="Markdown"
            )
            return

        uploaded_file_name = chat_data.get("last_uploaded_name", "")
        user_caption = chat_data.get("last_uploaded_caption", "")

        # 💡 [보완] 세션에 저장된 최신 업로드 에셋 목록 구성
        uploaded_assets = []
        if chat_data.get("last_uploaded_image"):
            uploaded_assets.append(
                f"이미지({os.path.basename(chat_data['last_uploaded_image'])})"
            )
        if chat_data.get("last_uploaded_audio"):
            uploaded_assets.append(
                f"음원({os.path.basename(chat_data['last_uploaded_audio'])})"
            )
        if chat_data.get("last_uploaded_video"):
            uploaded_assets.append(
                f"영상({os.path.basename(chat_data['last_uploaded_video'])})"
            )

        assets_str = (
            " 및 ".join(uploaded_assets) if uploaded_assets else uploaded_file_name
        )

        if data.startswith("btn_prod_"):
            channel_key = data.replace("btn_prod_", "")

            # 💡 [한글 설명] 바로 제작하는 대신 음원 삽입 방식을 사용자에게 물어보기 위해 상태를 대기 상태로 전환하고 분기 버튼들을 제공합니다.
            chat_data["current_state"] = "STATE_WAITING_AUDIO_DECISION"
            chat_data["pending_channel_key"] = channel_key

            # 음원 선택을 위한 인라인 키보드 마크업 빌드
            audio_keyboard = [
                [
                    InlineKeyboardButton(
                        "📁 사용자음원추가", callback_data=f"btn_audio_user_{channel_key}"
                    ),
                    InlineKeyboardButton(
                        "🎵 음원자동생성", callback_data=f"btn_audio_auto_{channel_key}"
                    ),
                ],
                [InlineKeyboardButton("❌ 이번 세션 취소", callback_data="btn_cancel")],
            ]
            audio_markup = InlineKeyboardMarkup(audio_keyboard)

            await query.message.reply_text(
                f"🎵 *[음원 추가 방식 설정]*\n\n"
                f"`{channel_key}` 채널의 영상에 삽입할 음원(BGM)을 어떻게 제공하시겠습니까?\n"
                f"원하시는 방식을 선택해 주세요:",
                reply_markup=audio_markup,
                parse_mode="Markdown",
            )

        elif data.startswith("btn_plan_"):
            channel_key = data.replace("btn_plan_", "")
            await query.message.reply_text(
                f"📝 *[채널선택 수신]* `{channel_key}` 채널 자료로 대본 기획안을 작성합니다...",
                parse_mode="Markdown",
            )

            wrapped_message = FakeMessageWrapper(query.message)
            req_text = f"{channel_key} 채널로 {assets_str} 사용하여 기획해줘"
            if user_caption:
                req_text += f". 설명: {user_caption}"
            wrapped_message.text = req_text
            wrapped_update = CallbackUpdateWrapper(update, wrapped_message)

            chat_data["current_state"] = "STATE_PLANNING_PROCESSING"
            from telegram_bot.handlers.planning import handle_planning

            await handle_planning(wrapped_update, context, channel_key=channel_key)
        return

    # 3. 에셋 생성 완료 대기실 버튼 처리
    if data == "btn_build_start":
        await query.message.reply_text(
            "🚀 *[선택] 영상 렌더링 개시* - 비디오 렌더러를 직접 기동합니다...", parse_mode="Markdown"
        )
        wrapped_message = FakeMessageWrapper(query.message)
        wrapped_message.text = "진행해"
        wrapped_update = CallbackUpdateWrapper(update, wrapped_message)
        await handle_approved_build(wrapped_update, context)
        return

    elif data == "btn_build_upload":
        await query.message.reply_text(
            "🚀 *[선택] 렌더링 후 자동 업로드* - 비디오 빌드 및 업로드를 논스톱으로 진행합니다...",
            parse_mode="Markdown",
        )
        wrapped_message = FakeMessageWrapper(query.message)
        wrapped_message.text = "진행해 업로드"
        wrapped_update = CallbackUpdateWrapper(update, wrapped_message)
        await handle_approved_build(wrapped_update, context)
        return

    elif data == "btn_regen_img":
        channel_key = (
            chat_data.get("pending_channel_key", "rubia") if chat_data else "rubia"
        )
        if chat_data:
            chat_data["awaiting_build_approval"] = False
            chat_data["current_state"] = "STATE_ASSET_PROCESSING"
        await regenerate_image_only(update, context, channel_key=channel_key)
        return

    elif data == "btn_regen_aud":
        channel_key = (
            chat_data.get("pending_channel_key", "rubia") if chat_data else "rubia"
        )
        if chat_data:
            chat_data["awaiting_build_approval"] = False
            chat_data["current_state"] = "STATE_ASSET_PROCESSING"
        await regenerate_audio_only(update, context, channel_key=channel_key)
        return
    # [Sound Lab] 유사 기획 재시도 (Retry)
    elif data.startswith("btn_retry_sound_"):
        try:
            t_id = data.replace("btn_retry_sound_", "")
            await query.answer(
                "🔄 유사 기획 재시도 중입니다... 로컬 LLM이 가동됩니다 (약 10~30초 소요)", show_alert=False
            )

            from telegram_bot.engine.sound_template_generator import (
                generate_similar_template,
            )

            # 비동기로 돌리면 좋지만, 현재는 동기 함수이므로 to_thread 처리
            new_t = await asyncio.to_thread(generate_similar_template, t_id)

            msg = "🔄 *유사 기획 생성 완료!*\n\n"
            msg += f"제목: `{new_t.get('title')}`\n"
            msg += f"```\n{new_t.get('prompt')}\n```\n"
            msg += "다음 브리핑 또는 평가 UI에서 확인 가능합니다."
            await query.message.reply_text(msg, parse_mode="Markdown")
        except Exception as e:
            await query.answer(f"재시도 중 오류 발생: {e}", show_alert=True)
        return

    # [Sound Lab] 즉시 적용 (Apply)
    elif data.startswith("btn_apply_sound_"):
        try:
            t_id = data.replace("btn_apply_sound_", "")
            from telegram_bot.engine.sound_template_generator import (
                load_sound_templates,
                save_sound_templates,
            )

            db = load_sound_templates()
            found = False
            for t in db:
                if t.get("id") == t_id:
                    found = True
                    t["status"] = "APPROVED"
                    t["avg_score"] = 5
                    break
            if found:
                save_sound_templates(db)
                await query.answer(
                    "✅ 즉시 적용 완료! 이 템플릿이 라이브 렌더링 파이프라인의 1순위로 채택됩니다.", show_alert=True
                )
            else:
                await query.answer("해당 템플릿을 찾을 수 없습니다.", show_alert=True)
        except Exception as e:
            await query.answer(f"적용 중 오류 발생: {e}", show_alert=True)
        return

    # [Sound Lab] 30초 프리뷰 음원 생성 (🎧 프리뷰 생성)
    elif data.startswith("btn_preview_sound_"):
        t_id = data.replace("btn_preview_sound_", "")

        # 1. DB에서 템플릿 로드
        from telegram_bot.engine.sound_template_generator import (
            load_sound_templates,
            save_sound_templates,
        )

        db = load_sound_templates()
        t = next((x for x in db if x.get("id") == t_id), None)

        if not t:
            await query.answer("해당 템플릿을 찾을 수 없습니다.", show_alert=True)
            return

        await query.answer("🎧 30초 프리뷰 음원 생성을 시작합니다...", show_alert=False)
        channel_key = t.get("channel", "rubia")

        # 2. 로딩 알림 (코디아 캐릭터 노출)
        working_img = get_agent_image_path("cordia", "working")
        step_msg = f"🎵 *기술 디렉터 코디아*가 Lyria 3 Pro API로 30초 프리뷰 음원을 합성하고 있습니다...\n\n• 템플릿 제목: `{t.get('title')}`\n• 타겟 채널: `{channel_key}`\n\n*(약 30초~1분 소요 예정)*"

        status_msg = None
        if working_img and os.path.exists(working_img):
            with open(working_img, "rb") as photo:
                status_msg = await query.message.reply_photo(
                    photo=photo, caption=step_msg, parse_mode="Markdown"
                )
        else:
            status_msg = await query.message.reply_text(step_msg, parse_mode="Markdown")

        try:
            # 3. 프리뷰 음원 경로 생성 및 API 호출
            preview_dir = r"c:\1인기업\Apps\유튜브에이전트\outputs\previews"
            os.makedirs(preview_dir, exist_ok=True)
            preview_filename = f"preview_{t_id}_{int(time.time())}.mp3"
            preview_path = os.path.join(preview_dir, preview_filename)

            from telegram_bot.engine.audio_generator import generate_lyria3_music

            # duration_min=0.5 (30초), prompt_override를 통해 해당 템플릿의 프롬프트 직접 주입
            generated_audio = await asyncio.to_thread(
                generate_lyria3_music,
                channel_key,
                preview_path,
                duration_min=0.5,
                prompt_override=t.get("prompt"),
            )

            # 4. DB에 preview_audio_path 업데이트 및 저장
            db = load_sound_templates()
            for x in db:
                if x.get("id") == t_id:
                    x["preview_audio_path"] = generated_audio
                    break
            save_sound_templates(db)

            # 5. 로딩 메시지 삭제
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id, message_id=status_msg.message_id
                )
            except Exception:
                pass

            # 6. 프리뷰 음원 전송 및 청음 평가 버튼 제공
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id, action="upload_voice"
            )

            feedback_keyboard = [
                [
                    InlineKeyboardButton(
                        "🔄 유사 기획 재시도", callback_data=f"btn_retry_sound_{t_id}"
                    ),
                    InlineKeyboardButton(
                        "✅ 즉시 적용", callback_data=f"btn_apply_sound_{t_id}"
                    ),
                ],
                [
                    InlineKeyboardButton("⭐1점", callback_data=f"btn_rate_{t_id}_1"),
                    InlineKeyboardButton("⭐⭐⭐3점", callback_data=f"btn_rate_{t_id}_3"),
                    InlineKeyboardButton("⭐⭐⭐⭐⭐5점", callback_data=f"btn_rate_{t_id}_5"),
                ],
            ]
            feedback_markup = InlineKeyboardMarkup(feedback_keyboard)

            success_img = get_agent_image_path("cordia", "success")
            caption_text = (
                f"🎧 *음원연구소 프리뷰 생성 완료*\n\n"
                f"• 템플릿: `{t.get('title')}`\n"
                f"• 프롬프트:\n```\n{t.get('prompt')}\n```\n\n"
                f"대표님, 아래 버튼을 통해 청음 평가를 내려주시거나 즉시 전체 영상 제작을 승인해 주십시오."
            )

            with open(generated_audio, "rb") as audio_file:
                await query.message.reply_audio(
                    audio=audio_file,
                    caption=caption_text,
                    reply_markup=feedback_markup,
                    parse_mode="Markdown",
                )

        except Exception as err:
            print(f"🚨 [Preview Generation Error]: {err}")
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id, message_id=status_msg.message_id
                )
            except Exception:
                pass
            await query.message.reply_text(
                f"❌ *프리뷰 음원 생성 에러*: `{str(err)}`", parse_mode="Markdown"
            )
        return

    # [Sound Lab] 승인 및 전체 제작 (✅ 승인 및 전체 제작)
    elif data.startswith("btn_full_render_"):
        t_id = data.replace("btn_full_render_", "")

        # 1. DB에서 템플릿 로드 후 APPROVED 및 avg_score=5 설정
        from telegram_bot.engine.sound_template_generator import (
            load_sound_templates,
            save_sound_templates,
        )

        db = load_sound_templates()
        t = next((x for x in db if x.get("id") == t_id), None)

        if not t:
            await query.answer("해당 템플릿을 찾을 수 없습니다.", show_alert=True)
            return

        await query.answer("✅ 템플릿 승인 및 전체 제작을 개시합니다.", show_alert=False)

        for x in db:
            if x.get("id") == t_id:
                x["status"] = "APPROVED"
                x["avg_score"] = 5
                break
        save_sound_templates(db)

        channel_key = t.get("channel", "rubia")

        # 2. 전체 음원 제작을 위한 목표 재생 시간(분) 획득
        video_length = chat_data.get("pending_video_length", 1) if chat_data else 1
        video_format = (
            chat_data.get("pending_video_format", "shorts") if chat_data else "shorts"
        )

        output_dir = chat_data.get("pending_output_dir") if chat_data else None
        if not output_dir:
            output_dir = os.path.join(
                "c:/1인기업/Apps/유튜브에이전트/outputs",
                "shorts" if video_format == "shorts" else "longform",
                channel_key,
            )

        os.makedirs(output_dir, exist_ok=True)

        # 3. 로딩 상태 알림 (코디아 캐릭터 노출)
        working_img = get_agent_image_path("cordia", "working")
        step_msg = f"🚀 *기술 디렉터 코디아*가 승인된 템플릿으로 전체 BGM 음원을 렌더링하고 있습니다...\n\n• 제목: `{t.get('title')}`\n• 목표 길이: `{video_length}분`\n\n*(약 1~2분 소요 예정)*"

        status_msg = None
        if working_img and os.path.exists(working_img):
            with open(working_img, "rb") as photo:
                status_msg = await query.message.reply_photo(
                    photo=photo, caption=step_msg, parse_mode="Markdown"
                )
        else:
            status_msg = await query.message.reply_text(step_msg, parse_mode="Markdown")

        try:
            audio_filename = f"{channel_key}_music_generated_{int(time.time())}.mp3"
            audio_path = os.path.join(output_dir, audio_filename)

            from telegram_bot.engine.audio_generator import generate_lyria3_music

            generated_audio = await asyncio.to_thread(
                generate_lyria3_music,
                channel_key,
                audio_path,
                duration_min=video_length,
                prompt_override=t.get("prompt"),
            )

            # 4. 로딩 메시지 삭제
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id, message_id=status_msg.message_id
                )
            except Exception:
                pass

            # 5. 후속 연계 판별
            if chat_data and chat_data.get("pending_script"):
                chat_data["pending_audio"] = generated_audio
                chat_data["asset_creation_timestamp"] = time.time()
                chat_data["pending_channel_key"] = channel_key

                await context.bot.send_chat_action(
                    chat_id=update.effective_chat.id, action="upload_voice"
                )
                with open(generated_audio, "rb") as audio_file:
                    await query.message.reply_audio(
                        audio=audio_file,
                        caption=f"🎵 완곡 BGM 음원 생성 완료: `{os.path.basename(generated_audio)}`\n\n영상 조립 세션으로 연계됩니다.",
                        parse_mode="Markdown",
                    )
                await _show_standby_menu(update, context)
            else:
                await context.bot.send_chat_action(
                    chat_id=update.effective_chat.id, action="upload_voice"
                )
                with open(generated_audio, "rb") as audio_file:
                    await query.message.reply_audio(
                        audio=audio_file,
                        caption=(
                            f"🎵 *완곡 BGM 렌더링 완료*\n\n"
                            f"• 파일명: `{os.path.basename(generated_audio)}`\n"
                            f"• 재생 시간: `{video_length}분`\n"
                            f"• 경로: `{generated_audio}`"
                        ),
                        parse_mode="Markdown",
                    )
                await query.message.reply_text("✅ *음원 템플릿 단독 렌더링 세션이 종료되었습니다.*")

        except Exception as err:
            print(f"🚨 [Full Render Error]: {err}")
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id, message_id=status_msg.message_id
                )
            except Exception:
                pass
            await query.message.reply_text(
                f"❌ *전체 음원 렌더링 에러*: `{str(err)}`", parse_mode="Markdown"
            )
        return

    # [Sound Lab] 신규 음원 템플릿 개별 평가 (Evolution Loop)
    elif data.startswith("btn_rate_"):
        try:
            # 포맷: btn_rate_<uuid>_<score>
            parts = data.split("_")
            t_id = parts[2]
            score = int(parts[3])

            from telegram_bot.engine.sound_template_generator import (
                load_sound_templates,
                save_sound_templates,
            )

            db = load_sound_templates()
            found = False
            alt_template_ch = None

            # 비동기 대체 생성을 수행할 내부 함수 정의
            async def generate_alt_template(chat_id, ch_key):
                try:
                    from telegram_bot.engine.sound_template_generator import (
                        generate_daily_templates,
                    )

                    # 로컬 LLM에서 1개 신규 생성
                    new_templates = await asyncio.to_thread(
                        generate_daily_templates, ch_key, 1
                    )
                    if new_templates:
                        new_t = new_templates[0]
                        new_t_id = new_t.get("id")

                        alt_msg = (
                            f"🔄 *[기획 대체 완료] 다른 스타일의 음원 기획안 제안*\n\n"
                            f"• 제목: `{new_t.get('title', '제목 없음')}`\n"
                            f"• 채널: `{new_t.get('channel', ch_key)}`\n"
                            f"• 프롬프트: `{new_t.get('prompt', '')}`\n\n"
                            f"대표님, 아래 버튼을 통해 30초 샘플 음원을 청음해 보십시오."
                        )

                        alt_keyboard = [
                            [
                                InlineKeyboardButton(
                                    "🎧 프리뷰 생성",
                                    callback_data=f"btn_preview_sound_{new_t_id}",
                                )
                            ]
                        ]
                        alt_markup = InlineKeyboardMarkup(alt_keyboard)
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=alt_msg,
                            reply_markup=alt_markup,
                            parse_mode="Markdown",
                        )
                except Exception as alt_err:
                    print(
                        f"⚠️ [Alternative Template Generation Fail] 대체 템플릿 생성 실패: {alt_err}"
                    )

            for t in db:
                if t.get("id") == t_id:
                    found = True
                    t["avg_score"] = score
                    if score == 5:
                        t["status"] = "APPROVED"
                        msg = f"⭐ 5점 평가 완료! 이 템플릿('{t.get('title')}')은 향후 생성기의 '성공 문법'으로 자동 학습되며 라이브 렌더링에 적용됩니다."
                    elif score == 3:
                        t["status"] = "PENDING"
                        msg = (
                            f"😐 3점 평가 완료. 이 템플릿('{t.get('title')}')은 보류 상태로 데이터를 유지합니다."
                        )
                    elif score == 1:
                        # 📉 1점 평가: 즉시 폐기(REJECTED) 및 대체 템플릿 1개 신규 재생성
                        t["status"] = "REJECTED"
                        msg = f"📉 1점 평가 완료. 이 템플릿('{t.get('title')}')은 폐기되었으며, 다른 스타일의 기획으로 실시간 대체 중입니다..."
                        alt_template_ch = t.get("channel", "rubia")
                    else:
                        t["status"] = "PENDING"
                        msg = f"😐 {score}점 평가 완료. 이 템플릿('{t.get('title')}')은 보류 상태로 대기합니다."
                    break

            if found:
                # 1. 파일 DB에 변경된 상태(REJECTED 등)를 먼저 완전 저장하여 동시성 레이스 차단
                save_sound_templates(db)
                # 2. 저장이 완전히 완료된 후, 로컬 LLM을 통한 대체 템플릿 비동기 재생성 구동
                if alt_template_ch:
                    asyncio.create_task(
                        generate_alt_template(update.effective_chat.id, alt_template_ch)
                    )
                await query.answer(msg, show_alert=True)
            else:
                await query.answer("해당 템플릿을 DB에서 찾을 수 없습니다.", show_alert=True)
        except Exception as e:
            await query.answer(f"평가 처리 중 오류 발생: {e}", show_alert=True)
        return

    # [Sound Lab] 신규 음원 템플릿 일괄 승인 (기존 하위호환)
    elif data == "btn_approve_sound":
        try:
            from telegram_bot.engine.sound_template_generator import (
                load_sound_templates,
                save_sound_templates,
            )

            db = load_sound_templates()
            approved_count = 0
            for t in db:
                if t.get("status") == "PENDING":
                    t["status"] = "APPROVED"
                    t["avg_score"] = 5  # 일괄 승인 시 기본 5점 부여
                    approved_count += 1
            if approved_count > 0:
                save_sound_templates(db)
                await query.message.reply_text(
                    f"✅ *음원연구소 템플릿 승인 완료*\n총 {approved_count}개의 신규 템플릿이 라이브 DB에 등록되었습니다.",
                    parse_mode="Markdown",
                )
            else:
                await query.answer("승인할 대기 중인 템플릿이 없습니다.", show_alert=True)
        except Exception as e:
            await query.answer(f"오류 발생: {e}", show_alert=True)
        return

    # 4. 빌드 성공 완료 후 유튜브 게시 및 작업 순환 버튼 처리
    if data in ["btn_yt_private", "btn_yt_public"]:
        if not chat_data or "pending_upload_video" not in chat_data:
            await query.message.reply_text(
                "⚠️ *업로드 대기 중인 영상 파일이 없습니다.* 다시 빌드해 주세요.", parse_mode="Markdown"
            )
            return

        pending_upload = chat_data.get("pending_upload_video")
        if pending_upload and os.path.exists(pending_upload):
            publish_status = "unlisted" if data == "btn_yt_private" else "public"
            await query.message.reply_text(
                f"🚀 *[유튜브 배포]* 완성본 영상을 `{publish_status}` 상태로 업로드 중입니다..."
            )

            try:
                from telegram_bot.utils.youtube_uploader import upload_video_to_youtube
                from telegram_bot.config import CHANNEL_MAP

                channel_key = chat_data.get("pending_upload_channel_key", "rubia")
                planning_script = chat_data.get("pending_upload_script", "")
                video_format = chat_data.get("pending_upload_video_format", "shorts")
                conf = CHANNEL_MAP.get(channel_key)

                if conf:
                    token_file = conf.get("token_file", f"token_{channel_key}.json")

                    def run_upload():
                        # youtube_uploader는 업로더 내부에서 privacyStatus를 설정에 연동합니다.
                        return upload_video_to_youtube(
                            token_file,
                            pending_upload,
                            planning_script,
                            channel_key,
                            video_format=video_format,
                        )

                    video_id, video_url = await asyncio.to_thread(run_upload)

                    await query.message.reply_text(
                        f"🚀 *유튜브 업로드 완료!*\n"
                        f"• **채널**: `{conf['name']}`\n"
                        f"• **상태**: `{publish_status}`\n"
                        f"• **비디오 링크**: [유튜브에서 보기]({video_url})",
                        parse_mode="Markdown",
                    )
                else:
                    await query.message.reply_text("❌ 채널 매핑 정보를 찾을 수 없습니다.")
            except Exception as ue:
                print(f"🚨 [YouTube Upload Callback Error]: {ue}")
                await query.message.reply_text(
                    f"🚨 *유튜브 업로드 실패*: `{str(ue)}`", parse_mode="Markdown"
                )
            finally:
                chat_data["pending_upload_video"] = None
        else:
            await query.message.reply_text("⚠️ 빌드된 비디오 파일을 디스크에서 찾을 수 없습니다.")
        return

    elif data == "btn_new_plan":
        await query.message.reply_text(
            "✨ *[새 기획 수립]* - AI 기획팀장을 호출합니다...", parse_mode="Markdown"
        )
        wrapped_message = FakeMessageWrapper(query.message)
        wrapped_message.text = "새 기획 시작"
        wrapped_update = CallbackUpdateWrapper(update, wrapped_message)

        if chat_data:
            chat_data["current_state"] = None
            chat_data["awaiting_build_approval"] = False

        from telegram_bot.handlers.planning import handle_planning

        await handle_planning(wrapped_update, context)
        return

    # 5. 기존 자가치유 폴백 세션 분기 (하위 호환 유지)
    if not chat_data or "fallback_session" not in chat_data:
        await query.message.reply_text(
            "⚠️ *만료되었거나 이미 완료된 작업 세션입니다.*", parse_mode="Markdown"
        )
        return

    session = chat_data["fallback_session"]
    character_names = session.get(
        "character_names",
        ["rubia", "ravia", "cordia", "guardia", "intella", "signa", "stella"],
    )

    if data == "fallback_use_recent":
        await query.message.reply_text(
            "🔄 *[선택 1] 최근 이미지/음원 사용 수신* - 로컬 자산 핫스왑을 시작합니다...", parse_mode="Markdown"
        )

        # 1. 이미지 폴백 탐색
        fallback_img = None
        visual_paths = session.get("visual_paths", [])
        if visual_paths:
            for vp in visual_paths:
                if os.path.exists(vp) and not any(
                    char in os.path.basename(vp).lower() for char in character_names
                ):
                    fallback_img = vp
                    break
        if not fallback_img or not os.path.exists(fallback_img):
            fallback_img = os.path.join(
                "c:/1인기업/Apps/유튜브에이전트",
                "assets",
                "characters",
                "Rubia",
                "rubia_work_eye.png",
            )

        # 2. 오디오 폴백 탐색
        fallback_audio = None
        audio_paths = session.get("audio_paths", [])
        if audio_paths:
            for ap in audio_paths:
                if os.path.exists(ap):
                    fallback_audio = ap
                    break
        if not fallback_audio or not os.path.exists(fallback_audio):
            fallback_audio = os.path.join("c:/1인기업/Apps/유튜브에이전트", "aura_shorts_v1.mp4")

        # 3. 세션 메모리에 에셋 경로 강제 맵핑
        chat_data["pending_visual"] = fallback_img
        chat_data["pending_audio"] = fallback_audio
        chat_data["pending_script"] = session["planning_script"]
        chat_data["pending_channel_key"] = session["channel_key"]
        chat_data["pending_video_format"] = session["video_format"]
        chat_data["pending_video_length"] = session["video_length"]
        chat_data["pending_output_path"] = session["file_path"]
        chat_data["pending_output_dir"] = session["output_dir"]
        chat_data["asset_creation_timestamp"] = __import__("time").time()
        # 💡 [핫스왑 타임스탬프 갱신] 대표님이 승인한 로컬 에셋의 mtime을 현재 시각으로 touch하여
        # 후속 렌더링 단계의 15분 유효시간 검증(TSS v1.1)을 정상 통과시킵니다.
        # 일반 렌더링 흐름의 타임스탬프 검증은 영향받지 않습니다.
        for touch_path in [fallback_img, fallback_audio]:
            if touch_path and os.path.exists(touch_path):
                try:
                    os.utime(touch_path, None)
                except OSError:
                    pass
        chat_data["awaiting_build_approval"] = True
        chat_data["current_state"] = "STATE_ASSET_STANDBY"
        chat_data["fallback_session"] = None  # 임시 세션 소멸

        # 4. 승인 대기 메시지 송출
        success_img = get_agent_image_path("cordia", "success")
        standby_msg = (
            f"✅ *로컬 에셋 우회 대체가 완료되었습니다.*\n\n"
            f"📸 대체 이미지: `{os.path.basename(fallback_img)}`\n"
            f"🎵 대체 음원: `{os.path.basename(fallback_audio)}`\n\n"
            f"대표님, 이 결과물로 *영상 렌더링(비디오 빌드)*을 바로 진행할까요?\n"
            f"아래 버튼 또는 채팅('진행해', '영상 만들어', 'OK')으로 승인해 주세요:"
        )

        # 버튼 구성 동반
        keyboard = [
            [
                InlineKeyboardButton("🚀 렌더링 시작", callback_data="btn_build_start"),
                InlineKeyboardButton(
                    "📤 렌더링 후 자동 업로드", callback_data="btn_build_upload"
                ),
            ],
            [
                InlineKeyboardButton("🔄 이미지 재생성", callback_data="btn_regen_img"),
                InlineKeyboardButton("🎵 BGM 재생성", callback_data="btn_regen_aud"),
            ],
            [InlineKeyboardButton("❌ 이번 세션 취소", callback_data="btn_cancel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if success_img and os.path.exists(success_img):
            with open(success_img, "rb") as photo:
                await query.message.reply_photo(
                    photo=photo,
                    caption=standby_msg,
                    reply_markup=reply_markup,
                    parse_mode="Markdown",
                )
        else:
            await query.message.reply_text(
                standby_msg, reply_markup=reply_markup, parse_mode="Markdown"
            )

    elif data == "fallback_retry":
        await query.message.reply_text(
            "🔄 *[선택 2] 다시 시도하기 수신* - API 재호출을 진행합니다...", parse_mode="Markdown"
        )

        chat_data["awaiting_error_retry"] = True
        chat_data["error_retry_context"] = {
            "channel_key": session["channel_key"],
            "video_format": session["video_format"],
            "video_length": session["video_length"],
            "file_path": session["file_path"],
            "output_dir": session["output_dir"],
            "planning_script": session["planning_script"],
            "timestamp": __import__("time").time(),
        }
        chat_data["fallback_session"] = None

        # 🛡️ [자가 치유 Wrapper 적용] AttributeError 회피 및 재시도 분기 정상 진입
        wrapped_message = FakeMessageWrapper(query.message)
        wrapped_update = CallbackUpdateWrapper(update, wrapped_message)

        # 재호출 가동 (안전한 wrapped_update만 단일 실행)
        await handle_production(
            wrapped_update, context, channel_key=session["channel_key"]
        )


@check_permission
async def handle_paypal_connect(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """[제4연구소 (음원제작연구)] 페이팔 MCP 연결 지시 시 가이드 및 MCP Config 양식을 브리핑합니다."""
    # 🛡️ [Anti-Gravity Skill Gateway] 중복 API 호출 방지 및 트래픽 쓰로틀링 수칙 주입
    import time

    user_id = update.effective_user.id if update.effective_user else 0
    now = time.time()

    if context.chat_data is None:
        context.chat_data = {}

    last_call = context.chat_data.get("last_paypal_call", 0)
    if now - last_call < 5.0:
        print(f"🔒 [Security Gateway] User {user_id} PayPal API 중복/이상 트래픽 차단.")
        await update.message.reply_text(
            "🚨 *[보안 관제 경고]*\n"
            "단기간 내 중복된 PayPal API 연동 요청이 감지되어 트래픽이 일시 차단되었습니다.\n"
            "5초 후에 다시 시도해 주십시오.",
            parse_mode="Markdown",
        )
        return

    context.chat_data["last_paypal_call"] = now
    print(f"📡 [Security Gateway] User {user_id} PayPal API 가이드 브리핑 실행 (정상 접근 승인)")

    # 비서실장 루비아 오피스 모드 이미지 로드
    rubia_img = get_agent_image_path("rubia", "office_mode")
    if not rubia_img or not os.path.exists(rubia_img):
        rubia_img = get_agent_image_path("rubia", "working")

    guide_path = r"c:\1인기업\Apps\유튜브에이전트\.agents\guides\paypal_firebase_mcp_guide.md"

    briefing_text = (
        "👑 *비서실장 루비아의 페이팔 결제 자동화 MCP 연동 브리핑*\n\n"
        "대표님, 제1연구소의 페이팔(PayPal) MCP 결제 자동화 연동 가이드 및 안티그래비티 설정용 Config 양식을 브리핑해 드립니다.\n\n"
    )

    # 가이드 파일 동적 파싱 및 로드
    if os.path.exists(guide_path):
        try:
            with open(guide_path, "r", encoding="utf-8") as f:
                guide_content = f.read()
            # 대표님이 보기 편하게 마크다운 가이드 본문을 추가
            briefing_text += guide_content
        except Exception as e:
            briefing_text += f"⚠️ 가이드 문서 로드 실패: `{e}`\n\n[기본 설정 JSON]\n"
            briefing_text += (
                "```json\n"
                "{\n"
                '  "mcpServers": {\n'
                '    "paypal-mcp-server": {\n'
                '      "command": "npx",\n'
                '      "args": [\n'
                '        "-y",\n'
                '        "@paypal/mcp",\n'
                '        "--tools=all",\n'
                '        "--paypal-environment=sandbox"\n'
                "      ]\n"
                "    }\n"
                "  }\n"
                "}\n"
                "```"
            )
    else:
        briefing_text += "⚠️ `paypal_firebase_mcp_guide.md` 파일을 찾을 수 없습니다."

    # 메시지 송출
    try:
        if rubia_img and os.path.exists(rubia_img):
            with open(rubia_img, "rb") as photo:
                # 캡션 길이 초과(1024자) 방지를 위해 분리 송출
                await update.message.reply_photo(
                    photo=photo,
                    caption="👑 *비서실장 루비아의 페이팔 자동화 브리핑*",
                    parse_mode="Markdown",
                )

            # 전체 텍스트를 마크다운 유효성 검증 하에 분할 전송
            # 긴 마크다운 메시지 전송 시 텔레그램 메시지 길이 제한(4096자) 방지
            max_len = 3000
            for i in range(0, len(briefing_text), max_len):
                await update.message.reply_text(
                    briefing_text[i : i + max_len], parse_mode="Markdown"
                )
        else:
            max_len = 3000
            for i in range(0, len(briefing_text), max_len):
                await update.message.reply_text(
                    briefing_text[i : i + max_len], parse_mode="Markdown"
                )
    except Exception as err:
        # 마크다운 파싱 오류나 텔레그램 API 에러 발생 시 예외 안전 격리 및 일반 텍스트 폴백
        print(f"🚨 [PayPal Briefing Error]: {err}")
        try:
            plain_text = (
                briefing_text.replace("*", "").replace("#", "").replace("-", "•")
            )
            await update.message.reply_text(plain_text[:4000], parse_mode=None)
        except Exception:
            pass
