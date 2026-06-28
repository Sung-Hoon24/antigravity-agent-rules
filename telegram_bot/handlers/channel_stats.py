# -*- coding: utf-8 -*-
"""
유튜브 API 연동 및 데이터 분석 핸들러
- YouTube Data API v3를 활용하여 실시간 채널 구독자, 조회수, 최신 영상 및 댓글을 조회합니다.
- 비동기 이벤트 루프가 차단되지 않도록 asyncio.to_thread 또는 executor를 활용합니다.
"""

import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from googleapiclient.discovery import build
import os
from google.oauth2.credentials import Credentials
from telegram_bot.config import YOUTUBE_API_KEY, CHANNEL_MAP
from telegram_bot.utils.image_helper import get_agent_image_path
from telegram_bot.handlers.basic import check_permission
import traceback

# ─────────────────────────────────────────────
# 🛠️ YouTube API 호출 동기 함수 (스레드로 실행 예정)
# ─────────────────────────────────────────────


def _get_youtube_client(token_file_name: str = None):
    """토큰 파일 기반 인증 우선, 실패 시 API 키 폴백 방식으로 YouTube 클라이언트를 생성합니다."""
    if token_file_name:
        project_root = r"c:\1인기업\Apps\유튜브에이전트"
        token_path = os.path.join(project_root, token_file_name)
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path)
            return build("youtube", "v3", credentials=creds)

    if not YOUTUBE_API_KEY:
        raise ValueError("YOUTUBE_API_KEY가 설정되어 있지 않거나 토큰 파일이 없습니다.")
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def _fetch_channel_data_sync(channel_id: str, token_file_name: str = None) -> dict:
    """유튜브 API를 동기식으로 호출하여 채널 기본 정보 및 통계를 반환합니다."""
    youtube = _get_youtube_client(token_file_name)
    request = youtube.channels().list(
        part="snippet,statistics,contentDetails", id=channel_id
    )
    response = request.execute()

    if not response.get("items"):
        return {}

    item = response["items"][0]
    stats = item.get("statistics", {})
    snippet = item.get("snippet", {})
    content_details = item.get("contentDetails", {})

    return {
        "title": snippet.get("title", "알 수 없음"),
        "subscribers": int(stats.get("subscriberCount", 0)),
        "views": int(stats.get("viewCount", 0)),
        "videos": int(stats.get("videoCount", 0)),
        "uploads_playlist_id": content_details.get("relatedPlaylists", {}).get(
            "uploads", ""
        ),
    }


def _fetch_recent_videos_sync(
    uploads_playlist_id: str, max_results: int = 5, token_file_name: str = None
) -> list:
    """채널 업로드 플레이리스트 ID를 기반으로 최신 영상 목록을 가져옵니다."""
    youtube = _get_youtube_client(token_file_name)
    playlist_request = youtube.playlistItems().list(
        part="snippet", playlistId=uploads_playlist_id, maxResults=max_results
    )
    playlist_response = playlist_request.execute()

    video_list = []
    items = playlist_response.get("items", [])

    for item in items:
        video_id = item["snippet"]["resourceId"]["videoId"]
        title = item["snippet"]["title"]

        # 각 영상의 상세 통계 조회
        try:
            video_request = youtube.videos().list(part="statistics", id=video_id)
            video_response = video_request.execute()
            stats = {}
            if video_response.get("items"):
                stats = video_response["items"][0].get("statistics", {})
        except Exception:
            stats = {}

        video_list.append(
            {
                "video_id": video_id,
                "title": title,
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
            }
        )

    return video_list


def _fetch_comments_sync(
    video_id: str, max_results: int = 5, token_file_name: str = None
) -> list:
    """특정 영상의 댓글 목록을 가져옵니다."""
    youtube = _get_youtube_client(token_file_name)
    try:
        comment_request = youtube.commentThreads().list(
            part="snippet", videoId=video_id, order="relevance", maxResults=max_results
        )
        comment_response = comment_request.execute()

        comments = []
        for item in comment_response.get("items", []):
            comment_text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            # HTML 태그 제거
            comment_text = comment_text.replace("<br>", "\n").replace("<br/>", "\n")
            comments.append(comment_text)
        return comments
    except Exception as e:
        # 댓글 비활성화 등 에러 시 빈 배열 반환
        print(f"Error fetching comments for video {video_id}: {e}")
        return []


# ─────────────────────────────────────────────
# 🤖 Telegram 비동기 핸들러 함수
# ─────────────────────────────────────────────


async def _check_bot_permission_and_get_channels(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    channel_key: str,
    status_msg=None,
) -> tuple:
    """
    봇 프로필(Rofi/Aura)에 따라 채널 허용 여부를 검증하고 대상 채널 정보 목록과 에러 발생 여부를 반환합니다.
    """
    bot_profile_key = context.bot_data.get("bot_profile")
    from telegram_bot.config import BOT_PROFILES

    # 봇 프로필이 존재하는 경우 (멀티 봇 모드)
    if bot_profile_key and bot_profile_key in BOT_PROFILES:
        profile = BOT_PROFILES[bot_profile_key]
        allowed = profile["allowed_channels"]

        # 특정 채널을 요청했으나 허용되지 않은 경우 차단
        if channel_key and channel_key not in allowed:
            correct_bot = "다른 전용 봇"
            for pk, pv in BOT_PROFILES.items():
                if channel_key in pv["allowed_channels"]:
                    correct_bot = f"*{pv['name']}* ({pv['username']})"
                    break

            err_msg = (
                f"💡 *알림*: 현재 대화 중이신 봇은 *{profile['name']}* 전용입니다.\n"
                f"요청하신 채널 정보는 {correct_bot}을 통해 문의해 주세요! 🙏"
            )
            err_img = get_agent_image_path("rubia", "scrutiny") or get_agent_image_path(
                "guardia", "working"
            )

            # 로딩 메시지가 있으면 지우기
            if status_msg:
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=status_msg.message_id,
                    )
                except Exception:
                    pass

            if err_img:
                with open(err_img, "rb") as photo:
                    await update.message.reply_photo(
                        photo=photo, caption=err_msg, parse_mode="Markdown"
                    )
            else:
                await update.message.reply_text(err_msg, parse_mode="Markdown")
            return None, None, True

        # 채널명이 명시되지 않은 경우, 허용된 모든 채널을 대상으로 함
        if not channel_key:
            target_channels = {k: v for k, v in CHANNEL_MAP.items() if k in allowed}
            title_line = f"📊 *{profile['name']}* 관리 채널 성과 보고\n"
        else:
            target_channels = {channel_key: CHANNEL_MAP[channel_key]}
            title_line = f"📊 *{CHANNEL_MAP[channel_key]['name']}* 채널 성과 통계 보고\n"

        return target_channels, [title_line], False
    else:
        # 단일 봇/통합 모드인 경우
        if channel_key and channel_key in CHANNEL_MAP:
            target_channels = {channel_key: CHANNEL_MAP[channel_key]}
            title_line = f"📊 *{CHANNEL_MAP[channel_key]['name']}* 채널 성과 통계 보고\n"
        else:
            target_channels = CHANNEL_MAP
            title_line = "📊 *루비아 팀 4대 관리 채널 통합 성과 보고*\n"
        return target_channels, [title_line], False


@check_permission
async def handle_channel_stats(
    update: Update, context: ContextTypes.DEFAULT_TYPE, channel_key: str = None
) -> None:
    """채널 통계(구독자, 조회수, 영상 수) 조회 핸들러"""
    # 📊 데이터 처리는 시그나가 담당
    working_img = get_agent_image_path("signa", "working")
    success_img = get_agent_image_path("signa", "success")

    # 대표님께 로딩 알림 전송 (시그나 작업 이미지 포함)
    load_msg = "📊 *시그나*가 실시간 YouTube API 데이터를 집계하고 있습니다. 잠시만 기다려주세요..."
    if working_img:
        with open(working_img, "rb") as photo:
            status_msg = await update.message.reply_photo(
                photo=photo, caption=load_msg, parse_mode="Markdown"
            )
    else:
        status_msg = await update.message.reply_text(load_msg, parse_mode="Markdown")

    try:
        # 봇 권한 검사 및 조회할 대상 채널 필터링
        target_channels, lines, is_error = await _check_bot_permission_and_get_channels(
            update, context, channel_key, status_msg
        )
        if is_error:
            return

        total_subs = 0
        total_views = 0
        total_videos = 0

        for key, conf in target_channels.items():
            ch_id = conf["channel_id"]
            if not ch_id:
                lines.append(f"⚠️ `{conf['name']}`: 채널 ID 설정이 누락되었습니다.")
                continue

            # 동기 API 호출을 스레드 풀에서 실행하여 비차단 처리
            # 💡 [방어적 프로그래밍] API Key 대신 OAuth 토큰 우선 사용
            token_file = conf.get("token_file")
            data = await asyncio.to_thread(_fetch_channel_data_sync, ch_id, token_file)
            if not data:
                lines.append(f"❌ `{conf['name']}`: API 조회를 실패했습니다.")
                continue

            lines.append(f"🔹 *{data['title']}*")
            lines.append(f"   • 구독자: `{data['subscribers']:,}명`")
            lines.append(f"   • 총 조회수: `{data['views']:,}회`")
            lines.append(f"   • 업로드 영상: `{data['videos']:,}개` \n")

            total_subs += data["subscribers"]
            total_views += data["views"]
            total_videos += data["videos"]

        if len(target_channels) > 1:
            lines.append("─────────────────────")
            lines.append("📈 *관리 채널 통합 요약*")
            lines.append(f"   • 누적 구독자: `{total_subs:,}명`")
            lines.append(f"   • 누적 조회수: `{total_views:,}회`")
            lines.append(f"   • 누적 영상수: `{total_videos:,}개` \n")

        final_text = "\n".join(lines)

        # 완료 메시지 전송
        if success_img:
            with open(success_img, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo, caption=final_text, parse_mode="Markdown"
                )
        else:
            await update.message.reply_text(final_text, parse_mode="Markdown")

    except Exception as e:
        traceback.print_exc()
        error_msg = f"❌ *오류 발생*: 데이터를 불러오지 못했습니다.\n상세: `{str(e)}`"
        await update.message.reply_text(error_msg, parse_mode="Markdown")
    finally:
        # 로딩 상태 메시지 삭제
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id, message_id=status_msg.message_id
            )
        except Exception:
            pass


@check_permission
async def handle_recent_videos(
    update: Update, context: ContextTypes.DEFAULT_TYPE, channel_key: str = None
) -> None:
    """최근 영상 목록 및 조회수 조회 핸들러"""
    # 📡 리서치는 인텔라가 담당
    working_img = get_agent_image_path("intella", "working")
    success_img = get_agent_image_path("intella", "success")

    bot_profile_key = context.bot_data.get("bot_profile")
    from telegram_bot.config import BOT_PROFILES

    # 채널명이 명시되지 않은 경우, 현재 봇 프로필의 기본 채널로 설정
    if not channel_key:
        if bot_profile_key and bot_profile_key in BOT_PROFILES:
            channel_key = BOT_PROFILES[bot_profile_key]["default_channel"]
        else:
            channel_key = "rubia"

    conf = CHANNEL_MAP.get(channel_key)
    if not conf:
        await update.message.reply_text("❌ 유효하지 않은 채널명입니다.")
        return

    load_msg = f"📡 *인텔라*가 `{conf['name']}`의 최신 영상 성과를 파악하고 있습니다..."

    if working_img:
        with open(working_img, "rb") as photo:
            status_msg = await update.message.reply_photo(
                photo=photo, caption=load_msg, parse_mode="Markdown"
            )
    else:
        status_msg = await update.message.reply_text(load_msg, parse_mode="Markdown")

    try:
        # 봇 권한 검사
        target_channels, _, is_error = await _check_bot_permission_and_get_channels(
            update, context, channel_key, status_msg
        )
        if is_error:
            return

        ch_id = conf["channel_id"]
        token_file = conf.get("token_file")

        # 1. 채널 정보에서 uploads_playlist_id 가져오기
        ch_data = await asyncio.to_thread(_fetch_channel_data_sync, ch_id, token_file)
        uploads_playlist_id = ch_data.get("uploads_playlist_id")

        if not uploads_playlist_id:
            await update.message.reply_text(
                f"❌ `{conf['name']}` 채널의 업로드 목록을 조회할 수 없습니다.", parse_mode="Markdown"
            )
            return

        # 2. 최신 5개 영상 정보 조회
        video_list = await asyncio.to_thread(
            _fetch_recent_videos_sync, uploads_playlist_id, 5, token_file
        )

        lines = [f"📡 *{conf['name']}* 최신 업로드 영상 리스트\n"]
        for idx, vid in enumerate(video_list, 1):
            lines.append(f"{idx}. *{vid['title']}*")
            lines.append(f"   • 조회수: `{vid['views']:,}회` | 좋아요: `{vid['likes']:,}개`")
            lines.append(
                f"   • [영상 보기](https://youtube.com/watch?v={vid['video_id']})\n"
            )

        final_text = "\n".join(lines)

        if success_img:
            with open(success_img, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo, caption=final_text, parse_mode="Markdown"
                )
        else:
            await update.message.reply_text(final_text, parse_mode="Markdown")

    except Exception as e:
        traceback.print_exc()
        await update.message.reply_text(
            f"❌ *오류 발생*: 영상을 가져오지 못했습니다.\n`{str(e)}`", parse_mode="Markdown"
        )
    finally:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id, message_id=status_msg.message_id
            )
        except Exception:
            pass


@check_permission
async def handle_comment_check(
    update: Update, context: ContextTypes.DEFAULT_TYPE, channel_key: str = None
) -> None:
    """채널 최신 영상들의 댓글 확인 핸들러"""
    # 👑 댓글 감사는 총괄 루비아가 직접 리드
    working_img = get_agent_image_path("rubia", "working")
    success_img = get_agent_image_path("rubia", "success")

    bot_profile_key = context.bot_data.get("bot_profile")
    from telegram_bot.config import BOT_PROFILES

    # 채널명이 명시되지 않은 경우, 현재 봇 프로필의 기본 채널로 설정
    if not channel_key:
        if bot_profile_key and bot_profile_key in BOT_PROFILES:
            channel_key = BOT_PROFILES[bot_profile_key]["default_channel"]
        else:
            channel_key = "rubia"

    conf = CHANNEL_MAP.get(channel_key)
    if not conf:
        await update.message.reply_text("❌ 유효하지 않은 채널명입니다.")
        return

    load_msg = f"👑 *루비아*가 `{conf['name']}`의 시청자 댓글 니즈를 수집 및 필터링하고 있습니다..."

    if working_img:
        with open(working_img, "rb") as photo:
            status_msg = await update.message.reply_photo(
                photo=photo, caption=load_msg, parse_mode="Markdown"
            )
    else:
        status_msg = await update.message.reply_text(load_msg, parse_mode="Markdown")

    try:
        # 봇 권한 검사
        target_channels, _, is_error = await _check_bot_permission_and_get_channels(
            update, context, channel_key, status_msg
        )
        if is_error:
            return

        ch_id = conf["channel_id"]
        token_file = conf.get("token_file")

        # 1. 최신 영상 조회
        ch_data = await asyncio.to_thread(_fetch_channel_data_sync, ch_id, token_file)
        uploads_playlist_id = ch_data.get("uploads_playlist_id")

        if not uploads_playlist_id:
            await update.message.reply_text(
                f"❌ `{conf['name']}` 채널의 업로드 목록 조회를 실패했습니다.", parse_mode="Markdown"
            )
            return

        video_list = await asyncio.to_thread(
            _fetch_recent_videos_sync, uploads_playlist_id, 1, token_file
        )
        if not video_list:
            await update.message.reply_text(
                f"📝 `{conf['name']}` 채널에 등록된 영상이 없습니다.", parse_mode="Markdown"
            )
            return

        target_video = video_list[0]
        # 2. 최신 영상 1개에 대해 댓글 조회
        comments = await asyncio.to_thread(
            _fetch_comments_sync, target_video["video_id"], 5, token_file
        )

        lines = [
            f"👑 *{conf['name']} 시청자 피드백 요약 리포트*",
            f"🎬 대상 영상: *{target_video['title']}*\n",
            "💬 *주요 시청자 반응 (최신/인기):*",
        ]

        if not comments:
            lines.append("   • (수집된 댓글이 없거나 댓글 기능이 비활성화되었습니다)")
        else:
            for comment in comments:
                lines.append(f'   • "{comment.strip()[:100]}"')

        final_text = "\n".join(lines)

        if success_img:
            with open(success_img, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo, caption=final_text, parse_mode="Markdown"
                )
        else:
            await update.message.reply_text(final_text, parse_mode="Markdown")

    except Exception as e:
        traceback.print_exc()
        await update.message.reply_text(
            f"❌ *오류 발생*: 댓글 수집을 완료하지 못했습니다.\n`{str(e)}`", parse_mode="Markdown"
        )
    finally:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id, message_id=status_msg.message_id
            )
        except Exception:
            pass
