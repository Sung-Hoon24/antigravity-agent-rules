# .agents/scripts/upload_video.py
# 생성된 MP4 비디오 파일을 유튜브 채널에 비공개(Private)로 자동 업로드하는 스크립트
# 실행: python .agents/scripts/upload_video.py {비디오파일경로}

import os
import sys
import socket
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# 필요한 권한 스코프 (유튜브 업로드 전용)
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLIENT_SECRET_FILE = os.path.join(
    BASE_DIR,
    "client_secret_295548450868-6so8a1374t2i7qt50hlhho870jqbqf7e.apps.googleusercontent.com.json",
)
TOKEN_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "live_chat_token.json"
)

# 업로드 메타데이터 설정
TITLE = "[Deep Ocean Voyage] 🌊 432Hz Calm Waves Sound for Anxiety Relief"
DESCRIPTION = (
    "Welcome to Aura Serenity Wellness. 🌿\n\n"
    "Immerse yourself in the tranquility of the deep ocean. "
    "This 3-minute relaxation video combines mystical deep-sea visual loops with an original ambient BGM "
    "gently mixed with a actual 432Hz healing frequency tone.\n\n"
    "Listen quietly, follow the breathing patterns, and let your anxiety dissolve into the deep blue void.\n\n"
    "✨ Key Features:\n"
    "- 432Hz Healing Frequency Mixing\n"
    "- Deep Ocean Brown Noise for Sleep & Focus\n"
    "- 9:16 Vertical Short-form Layout\n"
    "- Interactive Breathing Guide Included"
)
CATEGORY_ID = "27"  # Education 카테고리


def get_authenticated_service():
    """OAuth 2.0 인증을 수행하고 유튜브 서비스 객체를 반환합니다."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        # 기존 토큰 로드 시도
        # 주의: 기존 토큰이 youtube.upload 스코프를 가지고 있지 않을 수도 있으므로
        # 예외 상황 및 재인증 가능성을 열어둡니다.
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

        if not creds:
            print("🔑 신규 유튜브 업로드 권한 인증을 시작합니다 (브라우저 로그인 창이 열립니다)...")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

            # 다음 업로드를 위해 토큰 저장
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def upload_video(video_path: str):
    """지정된 비디오 파일을 유튜브에 비공개(Private)로 업로드합니다."""
    print("=" * 60)
    print("🚀 유튜브 비디오 비공개(Private) 업로드 시작")
    print("=" * 60)

    if not os.path.exists(video_path):
        print(f"❌ 오류: 업로드할 비디오 파일을 찾을 수 없습니다.\n경로: {video_path}")
        sys.exit(1)

    print("🔑 유튜브 인증 서버 연결 중...")
    try:
        youtube = get_authenticated_service()
    except Exception as e:
        print(f"❌ 인증 오류 발생: {e}")
        print("   해결: 기존 live_chat_token.json 파일을 삭제한 뒤 스크립트를 재실행해 보세요.")
        sys.exit(1)

    print("✅ 유튜브 인증 성공!")

    # 채널 정보 출력하여 타겟 채널 검증
    try:
        ch_res = youtube.channels().list(part="snippet", mine=True).execute()
        ch_title = ch_res["items"][0]["snippet"]["title"]
        print(f"📺 타겟 업로드 채널: [{ch_title}]")
    except Exception:
        print("📺 타겟 채널: (정보 조회 실패 - 업로드 계속 진행)")

    print(f"📂 파일명: {os.path.basename(video_path)}")
    print(f"📝 제목: {TITLE}")

    body = {
        "snippet": {
            "title": TITLE,
            "description": DESCRIPTION,
            "tags": [
                "ambient",
                "432hz",
                "deepocean",
                "meditation",
                "sleepmusic",
                "shorts",
            ],
            "categoryId": CATEGORY_ID,
        },
        "status": {
            "privacyStatus": "private",  # 비공개 설정 (대표님 지시사항)
            "selfDeclaredMadeForKids": False,
        },
    }

    # 미디어 파일 업로드 스트림 설정
    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        chunksize=1024 * 1024,  # 1MB 청크 단위 업로드
        resumable=True,
    )

    request = youtube.videos().insert(
        part="snippet,status", body=body, media_body=media
    )

    print("\n⏳ 동영상 업로드 전송 중... (잠시만 기다려 주세요)")
    response = None
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"   - 진행률: {int(status.progress() * 100)}% 완료")
        except socket.error as e:
            print(f"⚠️ 임시 네트워크 오류 발생, 재시도 중: {e}")
        except Exception as e:
            print(f"❌ 업로드 중 크리티컬 에러 발생: {e}")
            sys.exit(1)

    print("\n🎉 업로드가 성공적으로 완료되었습니다!")
    print(f"👉 신규 영상 ID: {response['id']}")
    print(f"👉 유튜브 시청 주소: https://youtu.be/{response['id']}")
    print("=" * 60)


if __name__ == "__main__":
    path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "assets/brand/deep_ocean_voyage_shorts.mp4"
    )
    upload_video(path)
