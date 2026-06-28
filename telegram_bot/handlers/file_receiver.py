# -*- coding: utf-8 -*-
"""
양방향 파일 수신 핸들러
- 대표님이 텔레그램을 통해 전송한 파일(문서, 사진, 오디오, 비디오)을 실시간 감지합니다.
- 감지된 파일은 로컬 컴퓨터의 C:\\1인기업\\Apps\\유튜브에이전트\\input 폴더에 자동 다운로드됩니다.
"""

import os
import datetime
import traceback

# 💡 [한글 설명] 텔레그램 봇에서 버튼 상호작용(InlineKeyboard)을 정상적으로 렌더링하기 위해 필수적인 클래스들을 임포트합니다.
# 임포트 유실 시 대표님이 파일 송출 후 버튼이 출력되지 않거나 봇 프로세스가 중단되는 크래시가 발생할 수 있습니다.
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram_bot.utils.image_helper import get_agent_image_path


async def handle_file_upload(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """대표님이 보낸 파일을 감지하고 로컬 컴퓨터의 input 폴더로 저장하는 비동기 핸들러"""
    if not update.message:
        return

    # 💡 [방어적 프로그래밍] 보낸 유저가 봇(Bot) 본인이거나 다른 봇일 경우 파일 수신을 원천 차단
    # - 봇이 성공/진행율 보고용으로 보낸 캐릭터 이미지를 대표님의 신규 업로드 파일로 오인 다운로드하는 버그를 해결합니다.
    if update.message.from_user and update.message.from_user.is_bot:
        return

    # ⚙️ 파일 처리는 기술 리드 코디아가 전담
    get_agent_image_path("cordia", "working")
    success_img = get_agent_image_path("cordia", "success")

    # 봇의 프로필 상태 가져오기
    bot_profile_key = context.bot_data.get("bot_profile")

    # 봇 프로필에 매칭되는 기본 채널 설정
    from telegram_bot.config import BOT_PROFILES

    channel_key = "general"  # 기본 폴백 디렉토리
    if bot_profile_key and bot_profile_key in BOT_PROFILES:
        channel_key = BOT_PROFILES[bot_profile_key]["default_channel"]

    try:
        # 봇이 현재 파일을 처리(타이핑) 중임을 메신저 상단에 표기
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action="typing"
        )

        file_name = None
        telegram_file = None
        file_type = "일반 문서"
        sub_dir = "documents"  # 기본값 폴백

        # 날짜/시간 접두사 생성 (넘버링 관리 및 중복 덮어쓰기 오류 방지 목적)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # 1. 일반 문서 (Document: .txt, .md, .json, .pdf 등) 감지 및 파일 정보 추출
        if update.message.document:
            doc = update.message.document
            orig_name = doc.file_name or "document.txt"
            file_name = f"{timestamp}_{orig_name}"
            telegram_file = await doc.get_file()
            file_type = "문서 (Document)"
            sub_dir = "documents"

        # 2. 이미지/사진 (Photo: .jpg, .png 등) 감지
        elif update.message.photo:
            # 텔레그램은 동일 사진의 해상도별 리스트를 보내므로, 가장 마지막의 최고 해상도 사진을 취득
            photo = update.message.photo[-1]
            file_name = f"{timestamp}_photo.jpg"
            telegram_file = await photo.get_file()
            file_type = "이미지 (Photo)"
            sub_dir = "images"

        # 3. 오디오 BGM/음원 (Audio: .mp3, .wav 등) 감지
        elif update.message.audio:
            audio = update.message.audio
            orig_name = audio.file_name or "audio.mp3"
            file_name = f"{timestamp}_{orig_name}"
            telegram_file = await audio.get_file()
            file_type = "음원 (Audio)"
            sub_dir = "audios"

        # 4. 동영상 (Video: .mp4 등) 감지
        elif update.message.video:
            video = update.message.video
            orig_name = video.file_name or "video.mp4"
            file_name = f"{timestamp}_{orig_name}"
            telegram_file = await video.get_file()
            file_type = "영상 (Video)"
            sub_dir = "videos"

        # 감지된 파일 정보가 유효하지 않을 경우의 방어적 텍스트 안내 및 리턴
        if not telegram_file:
            await update.message.reply_text("⚠️ 지원하지 않거나 인식할 수 없는 파일 포맷입니다.")
            return

        # 📍 파일이 저장될 로컬 입력 디렉토리 경로 정의 (채널별 및 분류별 격리 폴더 적용)
        input_dir = os.path.join("c:/1인기업/Apps/유튜브에이전트/input", channel_key, sub_dir)

        # 방어적 폴더 생성 처리 (폴더가 없으면 하위 분류 폴더까지 자동 생성)
        os.makedirs(input_dir, exist_ok=True)

        # 로컬 컴퓨터에 생성될 완성 경로 정의
        file_path = os.path.join(input_dir, file_name)

        # 실제 로컬 디스크로 다운로드 진행
        await telegram_file.download_to_drive(file_path)

        # 💡 [한글 설명] 만약 대표님이 '사용자음원추가' 단계에서 음원을 올리신 것이라면,
        # 다시 채널 선택 프롬프트를 띄우지 않고 곧바로 저장된 이미지와 합쳐서 E2E 제작을 시작합니다.
        is_user_audio_flow = False
        target_channel = None
        if context.chat_data is not None:
            if (
                context.chat_data.get("current_state") == "STATE_WAITING_USER_AUDIO"
                and sub_dir == "audios"
            ):
                target_channel = context.chat_data.get("pending_channel_key")
                if target_channel:
                    is_user_audio_flow = True

        if is_user_audio_flow and target_channel:
            # 📁 사용자 음원 세션 데이터 기록
            context.chat_data["last_uploaded_file"] = file_path
            context.chat_data["last_uploaded_sub_dir"] = sub_dir
            context.chat_data["last_uploaded_name"] = file_name
            context.chat_data["last_uploaded_audio"] = file_path
            context.chat_data["current_state"] = "STATE_ASSET_PROCESSING"

            # 설명(캡션) 임시 보관
            if update.message.caption:
                context.chat_data["last_uploaded_caption"] = update.message.caption

            local_link = f"file:///{input_dir}"
            audio_report = (
                f"⚙️ *코디아의 사용자 음원 연동 보고*\n\n"
                f"대표님, 전송해 주신 오리지널 음원 파일을 성공적으로 접수했습니다! 🎵\n\n"
                f"📂 *음원 파일 정보*\n"
                f"• **파일명**: `{file_name}`\n"
                f"• **저장된 로컬 경로**: [로컬 폴더 열기]({local_link})\n\n"
                f"🚀 `{target_channel}` 채널로 먼저 올리신 이미지(`{os.path.basename(context.chat_data.get('last_uploaded_image', '기본이미지.jpg'))}`)와 합쳐 E2E 영상 제작(FFmpeg 렌더링 검토)을 즉시 가동합니다!"
            )

            if success_img:
                with open(success_img, "rb") as photo_file:
                    await update.message.reply_photo(
                        photo=photo_file, caption=audio_report, parse_mode="Markdown"
                    )
            else:
                await update.message.reply_text(audio_report, parse_mode="Markdown")

            # E2E 제작 핸들러 호출
            from telegram_bot.handlers.production import (
                FakeMessageWrapper,
                CallbackUpdateWrapper,
                handle_production,
            )

            # 💡 [보완] 세션에 저장된 최신 업로드 에셋 목록 구성
            uploaded_assets = []
            if context.chat_data.get("last_uploaded_image"):
                uploaded_assets.append(
                    f"이미지({os.path.basename(context.chat_data['last_uploaded_image'])})"
                )
            uploaded_assets.append(f"음원({file_name})")

            assets_str = " 및 ".join(uploaded_assets)
            user_caption = context.chat_data.get("last_uploaded_caption", "")

            # 💡 [한글 설명] message.text의 readonly 속성을 우회하여 원하는 메타 정보를 전달할 수 있도록 wrapped_update를 생성합니다.
            wrapped_message = FakeMessageWrapper(update.message)
            req_text = f"{target_channel} 채널로 {assets_str} 사용하여 영상 만들어줘"
            if user_caption:
                req_text += f". 설명: {user_caption}"
            wrapped_message.text = req_text

            wrapped_update = CallbackUpdateWrapper(update, wrapped_message)
            await handle_production(wrapped_update, context, channel_key=target_channel)
            return

        # 봇 프로필에 따른 채널 정보를 가져오기 위해 CHANNEL_MAP 임포트
        from telegram_bot.config import CHANNEL_MAP

        # 성공 메시지 내 탐색기 바로가기 하이퍼링크 주소 생성
        local_link = f"file:///{input_dir}"
        channel_name = CHANNEL_MAP.get(channel_key, {}).get("name", channel_key)

        # 💡 [한글 설명] 이미지 또는 비디오가 업로드된 경우에는 채널을 수동 선택할 필요 없이, 해당 봇 기본 채널에서 숏폼(9:16)/롱폼(16:9) 포맷 선택 버튼을 즉각 출력합니다.
        if sub_dir in ["images", "videos"]:
            f_type_kor = "이미지" if sub_dir == "images" else "동영상"
            success_report = (
                f"⚙️ *코디아의 양방향 파일 전송 완료 보고*\n\n"
                f"대표님, 텔레그램으로 업로드해 주신 {f_type_kor} 자료를 로컬 컴퓨터로 안전하게 내려받았습니다! 🚀\n\n"
                f"📂 *저장된 상세 정보*\n"
                f"• **파일명**: `{file_name}`\n"
                f"• **저장된 로컬 경로**: [로컬 input 폴더 열기]({local_link})\n"
                f"   (복사용 경로: `{input_dir.replace('/', '\\')}`)\n\n"
                f"🎬 *[영상 포맷 설정]*\n"
                f"`{channel_name}` 채널 영상의 제작 규격을 선택해 주세요:"
            )

            keyboard = [
                [
                    InlineKeyboardButton(
                        "📱 숏폼 (Shorts, 9:16)",
                        callback_data=f"btn_format_shorts_{channel_key}",
                    ),
                    InlineKeyboardButton(
                        "📺 롱폼 (Long-form, 16:9)",
                        callback_data=f"btn_format_longform_{channel_key}",
                    ),
                ],
                [InlineKeyboardButton("❌ 이번 세션 취소", callback_data="btn_cancel")],
            ]
        else:
            success_report = (
                f"⚙️ *코디아의 양방향 파일 전송 완료 보고*\n\n"
                f"대표님, 텔레그램으로 업로드해 주신 자료를 로컬 컴퓨터로 안전하게 내려받았습니다! 🚀\n\n"
                f"📂 *저장된 파일 상세 정보*\n"
                f"• **파일명**: `{file_name}`\n"
                f"• **파일 유형**: `{file_type}`\n"
                f"• **저장된 로컬 경로**: [로컬 input 폴더 열기]({local_link})\n"
                f"   (복사용 경로: `{input_dir.replace('/', '\\')}`)\n\n"
                f"💡 *[영상 랜딩 지시]*\n"
                f"이 자료로 어느 유튜브 채널의 기획/제작을 진행할지 아래 버튼을 눌러 선택해 주세요:"
            )

            keyboard = [
                [
                    InlineKeyboardButton("🎨 루비아 에셋생성", callback_data="btn_prod_rubia"),
                    InlineKeyboardButton("📝 루비아 대본기획", callback_data="btn_plan_rubia"),
                ],
                [
                    InlineKeyboardButton("🎨 아우라 에셋생성", callback_data="btn_prod_aura"),
                    InlineKeyboardButton("📝 아우라 대본기획", callback_data="btn_plan_aura"),
                ],
                [
                    InlineKeyboardButton(
                        "🎨 그린스터디 에셋생성", callback_data="btn_prod_taipei"
                    ),
                    InlineKeyboardButton(
                        "📝 그린스터디 대본기획", callback_data="btn_plan_taipei"
                    ),
                ],
                [
                    InlineKeyboardButton("🎨 스마트 에셋생성", callback_data="btn_prod_smart"),
                    InlineKeyboardButton("📝 스마트 대본기획", callback_data="btn_plan_smart"),
                ],
                [InlineKeyboardButton("❌ 이번 세션 취소", callback_data="btn_cancel")],
            ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        # 💾 수신된 파일의 최신 경로 및 메타데이터를 세션에 저장
        if context.chat_data is not None:
            context.chat_data["last_uploaded_file"] = file_path
            context.chat_data["last_uploaded_sub_dir"] = sub_dir
            context.chat_data["last_uploaded_name"] = file_name

            # 💡 [한글 설명] 이미지/비디오 업로드 시 세션 상태를 포맷 설정 대기(STATE_WAITING_FORMAT_DECISION)로 지정합니다.
            if sub_dir in ["images", "videos"]:
                context.chat_data["current_state"] = "STATE_WAITING_FORMAT_DECISION"
                context.chat_data["pending_channel_key"] = channel_key
            else:
                context.chat_data["current_state"] = "STATE_FILE_RECEIVED"

            # 💡 [보완] 타입별 개별 캐싱으로 이미지+음원 연속 업로드 대응
            if sub_dir == "images":
                context.chat_data["last_uploaded_image"] = file_path
            elif sub_dir == "audios":
                context.chat_data["last_uploaded_audio"] = file_path
            elif sub_dir == "videos":
                context.chat_data["last_uploaded_video"] = file_path

            # 설명(캡션) 임시 보관
            if update.message.caption:
                context.chat_data["last_uploaded_caption"] = update.message.caption

        # 💡 [자동 기획/제작 트리거] 캡션 텍스트에서 명시적인 기획/제작 의도와 채널이 감지되면 즉시 실행
        if update.message.caption:
            caption_text = update.message.caption
            from telegram_bot.nlp.intent_parser import (
                parse_intent_fallback,
                INTENT_PLANNING,
                INTENT_PRODUCTION,
            )

            analysis = parse_intent_fallback(caption_text)
            detected_intent = analysis.get("intent")
            detected_channel = analysis.get("channel")

            # 의도와 대상 채널이 명확히 매핑된 경우 즉시 후속 핸들러로 연계
            if (
                detected_intent in [INTENT_PLANNING, INTENT_PRODUCTION]
                and detected_channel
            ):
                if context.chat_data is not None:
                    context.chat_data["target_format"] = analysis.get(
                        "video_format", "shorts"
                    )
                    context.chat_data["target_length"] = analysis.get("video_length", 1)

                if detected_intent == INTENT_PLANNING:
                    from telegram_bot.handlers.planning import handle_planning

                    await update.message.reply_text(
                        f"📝 캡션 지시어를 감지했습니다. `{detected_channel}` 채널 기획을 자동으로 시작합니다...",
                        parse_mode="Markdown",
                    )
                    await handle_planning(update, context, channel_key=detected_channel)
                    return
                else:
                    from telegram_bot.handlers.production import handle_production

                    await update.message.reply_text(
                        f"🚀 캡션 지시어를 감지했습니다. `{detected_channel}` 채널 영상 제작을 자동으로 시작합니다...",
                        parse_mode="Markdown",
                    )
                    await handle_production(
                        update, context, channel_key=detected_channel
                    )
                    return

        # 코디아 성공 축하 캐릭터 이미지와 함께 결과물 보고 송출 (버튼 마크업 동반)
        if success_img:
            with open(success_img, "rb") as photo_file:
                await update.message.reply_photo(
                    photo=photo_file,
                    caption=success_report,
                    reply_markup=reply_markup,
                    parse_mode="Markdown",
                )
        else:
            await update.message.reply_text(
                success_report, reply_markup=reply_markup, parse_mode="Markdown"
            )

    except Exception as e:
        # 비정상 에러 발생 시 원인 추적을 위해 로컬 콘솔에 디테일 로그 출력
        traceback.print_exc()
        await update.message.reply_text(
            f"❌ *파일 다운로드 및 로컬 저장 실패*\n" f"에러 원인: `{str(e)}`", parse_mode="Markdown"
        )
