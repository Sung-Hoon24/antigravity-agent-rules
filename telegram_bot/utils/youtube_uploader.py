# -*- coding: utf-8 -*-
"""
유튜브 비디오 업로드 유틸리티 모듈
- Google OAuth2 Credentials를 활용하여 제작 완료된 MP4 영상을 지정된 YouTube 채널에 업로드합니다.
- [방어적 프로그래밍] 업로드 시 발생할 수 있는 네트워크/API 오류를 예외 처리하고 안전 장치를 둡니다.
- [보안 수칙] 안전을 위해 기본적으로 '비공개(private)' 상태로 업로드합니다.
"""

import os
import re
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


def parse_metadata_from_planning(planning_text, channel_key, video_format="shorts"):
    """
    라비아 기획안 텍스트에서 영상 제목, 설명, 태그를 파싱해 냅니다.
    파싱 실패 시 채널 정체성에 부합하는 기본 메타데이터로 폴백합니다.
    """
    title = ""
    description = ""
    tags = []

    if planning_text:
        lines = planning_text.split("\n")

        # 1. 제목 추천 목록 등에서 첫 번째 혹은 적절한 추천 제목 추출 시도
        # 영어/대만어/한글 다양한 타이틀 패턴 대응
        for line in lines:
            line_strip = line.strip()
            for prefix in ["제목:", "제목：", "Title:", "Title：", "推薦題目:", "推薦題目："]:
                if prefix in line_strip:
                    title_cand = (
                        line_strip.split(prefix)[-1]
                        .strip()
                        .strip('"')
                        .strip("'")
                        .strip()
                    )
                    if title_cand and not title:
                        title = title_cand
                        break

            # 해시태그 파싱 (#으로 시작하는 단어들)
            hashtags = re.findall(r"#\w+", line)
            for ht in hashtags:
                tag_name = ht.replace("#", "").strip()
                if tag_name and tag_name not in tags:
                    tags.append(tag_name)

    # 2. 설명란 구성 (채널별 고유 템플릿 적용)
    from telegram_bot.config import CHANNEL_IDENTITIES, CHANNEL_MAP

    identity = CHANNEL_IDENTITIES.get(channel_key, "Lifestyle & Music BGM")
    ch_info = CHANNEL_MAP.get(channel_key, {})

    # [기본값 처리] 제목 파싱 실패 시 채널별 자동 매핑
    if not title:
        if channel_key == "aura":
            title = "Aura Serenity Wellness | Deep Relaxation Solfeggio Meditation"
        elif channel_key in ["rubia", "taipei"]:
            title = "Cozy Greenhouse Lo-Fi 🎧 Chill Lofi Beats for Deep Focus, Coding, and Relaxation"
        elif channel_key == "smartage":
            title = "Smart Age Tech | Essential Digital Guides for Seniors"
        else:
            title = "Daily Chill Beats & BGM"

    # 설명란 조립
    license_info = ""
    if channel_key == "aura":
        license_info = (
            "\n\n---"
            "\n💡 [AURA ORIGINALITY & CREATIVE LICENSE]"
            "\nThis video features original high-quality audio synthesized and mixed via our proprietary sound design framework."
            "\n- Sound Synthesis: Crafted with specific Solfeggio frequencies (528Hz/432Hz) using specialized virtual instruments."
            "\n- Visual Artistry: Dynamic visual layers, organic color-shifting filters, and atmospheric overlays edited specifically to match the audio frequency and tempo."
            "\n- 100% Unique Creation: We do not use pre-rendered loops or mass-duplicated public assets. All rights reserved."
            "\n---"
        )
    elif channel_key in ["rubia", "taipei"]:
        license_info = (
            "\n\n---"
            "\n💡 [GREEN STUDY ORIGINALITY & CREATIVE LICENSE]"
            "\nThis lofi focus background music track is mixed and arranged originally to enhance deep focus and relaxation."
            "\n- Audio Mix: Produced with warm Rhodes electric piano and soft acoustic jazz guitar rhythms for concentration."
            "\n- Visual Artistry: Features customized ambient greenhouse and cozy library illustration layers designed for visual calm."
            "\n- All Rights Reserved: Safe for studying, coding, working, and relaxing. Re-use prohibited."
            "\n---"
        )

    description = (
        f"🌱 Welcome to {ch_info.get('name', 'YouTube Creator Channel')}.\n\n"
        f"{identity}\n\n"
        f"✨ Enjoy the relaxing vibes and find your inner peace."
        f"{license_info}\n\n"
        f"#LofiBeats #Meditation"
    )

    # [기본값 처리] 태그 파싱 실패 시 채널별 자동 매핑
    if not tags:
        if channel_key == "aura":
            tags = ["meditation", "yoga", "healing", "solfeggio"]
        elif channel_key in ["rubia", "taipei"]:
            tags = ["lofi", "chill", "greenstudy", "bgm", "focus", "coding", "relax"]
        else:
            tags = ["creator", "bgm"]

    # 🚨 [유튜브 쇼츠 자동 분류 규격화]
    # 비디오 포맷이 쇼츠(shorts)일 경우, 해시태그 #Shorts를 무조건 제목과 설명란 및 태그 목록에 병합합니다.
    if video_format == "shorts":
        if "#shorts" not in title.lower():
            title = title.strip()
            if len(title) > 90:
                title = title[:87] + "..."
            title = f"{title} #Shorts"

        if "#shorts" not in description.lower():
            description = description.strip() + "\n\n#Shorts"

        if "Shorts" not in tags and "shorts" not in tags:
            tags.append("Shorts")

    # 🧼 [방어적 프로그래밍] 설명란에 한국어 번역 설명이 유입되는 현상을 완전히 차단하기 위해,
    # 정규식 및 치환을 활용해 한글 경어 법적 문구를 원천 제거합니다.
    korean_license_pattern = r"\(이 오디오 콘텐츠는 심신 안정과 웰니스를 위해 세밀한 음향 기획 및 믹싱 과정을 거쳐 직접 제작된 오리지널 창작물입니다\. 무단 복제 및 재사용을 엄격히 금지합니다\.\)"
    description = re.sub(korean_license_pattern, "", description)
    # 일반적인 형태의 동일 문자열도 치환 방어
    description = description.replace(
        "(이 오디오 콘텐츠는 심신 안정과 웰니스를 위해 세밀한 음향 기획 및 믹싱 과정을 거쳐 직접 제작된 오리지널 창작물입니다. 무단 복제 및 재사용을 엄격히 금지합니다.)",
        "",
    )

    # 유튜브 제목 글자수 안전 한도 체크 (최대 100자 제한)
    if len(title) > 95:
        title = title[:92] + "..."

    return title, description, tags


def upload_video_to_youtube(
    token_file_name, video_file_path, planning_text, channel_key, video_format="shorts"
) -> tuple:
    """
    지정된 토큰 파일을 읽어 비동기적으로 유튜브에 비디오를 업로드합니다.
    - 리턴: (video_id, video_url)
    """
    # 💡 [AGENTS.md §4 준수] 하드코딩 절대경로 대신 실행 환경 기준 동적 경로 조립
    uploader_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(uploader_dir))
    token_path = os.path.join(project_root, token_file_name)

    if not os.path.exists(token_path):
        raise FileNotFoundError(
            f"인증 토큰 파일 '{token_file_name}'을 찾을 수 없습니다. 경로: {token_path}"
        )

    if not os.path.exists(video_file_path):
        raise FileNotFoundError(f"업로드할 동영상 파일이 존재하지 않습니다: {video_file_path}")

    # 1. 기획안에서 메타데이터 파싱
    title, description, tags = parse_metadata_from_planning(
        planning_text, channel_key, video_format=video_format
    )

    # 2. OAuth2 Credentials 로드 및 API 서비스 빌드
    creds = Credentials.from_authorized_user_file(token_path)
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    # 3. 비디오 업로드 요청 바디 구성
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "10",  # Music 카테고리 적용
        },
        "status": {
            "privacyStatus": "private",  # 🔒 무조건 비공개(private) 업로드 후 수동 검토 권장
            "selfDeclaredMadeForKids": False,
        },
    }

    # 미디어 파일 로드 (Resumable 업로드 지원으로 대용량 네트워크 끊김 예방)
    media = MediaFileUpload(video_file_path, chunksize=-1, resumable=True)

    # 4. API 호출 실행
    print(f"🚀 [YouTube Uploader] 유튜브 영상 업로드 시작: {title}")
    request = youtube.videos().insert(
        part="snippet,status", body=request_body, media_body=media
    )

    response = request.execute()
    video_id = response.get("id")

    if not video_id:
        raise RuntimeError("유튜브 업로드 결과 비디오 ID를 반환받지 못했습니다.")

    video_url = f"https://youtu.be/{video_id}"
    print(f"✅ [YouTube Uploader] 유튜브 업로드 성공! ID: {video_id} / URL: {video_url}")

    return video_id, video_url
