import os
import sys

# Google API 관련 라이브러리 임포트 (필요 시 pip install google-api-python-client google-auth-oauthlib google-auth-httplib2)
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 사용할 OAuth 2.0 스코프 (유튜브 계정 관리 및 채팅 쓰기 권한)
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# === 설정 영역 ===
VIDEO_ID = "OqO6C4EnSuw"
MESSAGE = "안녕하세요^^ 대표님들"

# 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLIENT_SECRET_FILE = os.path.join(
    BASE_DIR,
    "client_secret_295548450868-6so8a1374t2i7qt50hlhho870jqbqf7e.apps.googleusercontent.com.json",
)
TOKEN_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "live_chat_token.json"
)


def get_authenticated_service():
    """OAuth 2.0 인증을 수행하고 YouTube 서비스 객체를 반환합니다."""
    creds = None
    # 1. 이전에 발급받아 저장된 토큰이 있는지 확인
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # 2. 유효한 인증 토큰이 없는 경우 새로 발급 (웹 브라우저 로그인 창 띄움)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # 3. 다음 번 실행을 위해 발급받은 토큰을 파일로 저장
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def main():
    print("=" * 50)
    print("🚀 유튜브 라이브 채팅 자동 전송 테스트 (OAuth 2.0)")
    print("=" * 50)

    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"❌ 오류: 클라이언트 시크릿 파일을 찾을 수 없습니다.\n경로: {CLIENT_SECRET_FILE}")
        sys.exit(1)

    print("🔑 유튜브 API 인증 중...")
    youtube = get_authenticated_service()
    print("✅ 인증 완료!\n")

    # [1단계] 영상 ID로 활성화된 라이브 채팅방 ID(activeLiveChatId) 조회
    print(f"🔍 [1/2] 영상({VIDEO_ID})의 라이브 채팅방 ID를 조회합니다...")
    try:
        video_response = (
            youtube.videos().list(part="liveStreamingDetails", id=VIDEO_ID).execute()
        )

        items = video_response.get("items", [])
        if not items:
            print("❌ 오류: 영상을 찾을 수 없습니다. (비공개 영상이거나 ID가 잘못되었을 수 있습니다.)")
            sys.exit(1)

        live_details = items[0].get("liveStreamingDetails")
        if not live_details:
            print("❌ 오류: 이 영상은 실시간 스트리밍(라이브) 영상이 아니거나, 라이브 관련 정보가 없습니다.")
            sys.exit(1)

        live_chat_id = live_details.get("activeLiveChatId")
        if not live_chat_id:
            print("⚠️ 안내: 현재 활성화된 라이브 채팅방을 찾을 수 없습니다 (라이브 종료 상태).")
            print("👉 대신 동영상의 일반 댓글로 메시지 전송을 시도합니다...")
            send_regular_comment(youtube, VIDEO_ID, MESSAGE)
            print("=" * 50)
            return

        print(f"✅ 라이브 채팅방 ID 획득: {live_chat_id}\n")

    except Exception as e:
        print(f"❌ API 요청 중 오류 발생: {e}")
        sys.exit(1)

    # [2단계] 조회된 채팅방에 메시지 전송
    print(f"💬 [2/2] 메시지 전송 시도: '{MESSAGE}'")
    try:
        chat_response = (
            youtube.liveChatMessages()
            .insert(
                part="snippet",
                body={
                    "snippet": {
                        "liveChatId": live_chat_id,
                        "type": "textMessageEvent",
                        "textMessageDetails": {"messageText": MESSAGE},
                    }
                },
            )
            .execute()
        )

        print("\n🎉 메시지가 성공적으로 전송되었습니다!")
        # 실제 전송된 텍스트 확인 (HTML 이스케이프 등 처리 후의 모습)
        print(f"👉 확인된 메시지 내용: {chat_response['snippet']['displayMessage']}")

    except Exception as e:
        print("\n❌ 메시지 전송 실패 (API 오류):")
        print(e)

    print("=" * 50)


def send_regular_comment(youtube, video_id, message):
    """라이브가 종료되었을 때, 일반 동영상 댓글로 대체 전송합니다."""
    try:
        comment_response = (
            youtube.commentThreads()
            .insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": video_id,
                        "topLevelComment": {"snippet": {"textOriginal": message}},
                    }
                },
            )
            .execute()
        )
        print("\n🎉 일반 댓글이 성공적으로 등록되었습니다!")
        print(
            f"👉 등록된 댓글: {comment_response['snippet']['topLevelComment']['snippet']['textDisplay']}"
        )
    except Exception as e:
        print("\n❌ 일반 댓글 등록 실패:")
        print(e)


if __name__ == "__main__":
    main()
