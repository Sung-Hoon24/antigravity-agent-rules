# -*- coding: utf-8 -*-
"""
유튜브 API 토큰 수동 재발급 도구
- 사용법: python scratch/generate_oauth_token.py [aura | smartage | rubia | taipei]
- 실행 시 로컬 브라우저가 열리고, 구글 계정 로그인 동의를 마치면 자동으로 새 token_*.json 파일이 갱신되어 저장됩니다.
"""

import os
import sys
import json
from google_auth_oauthlib.flow import InstalledAppFlow

PROJECT_ROOT = r"c:\1인기업\Apps\유튜브에이전트"
CLIENT_SECRET_FILE = os.path.join(
    PROJECT_ROOT,
    "client_secret_295548450868-6so8a1374t2i7qt50hlhho870jqbqf7e.apps.googleusercontent.com.json",
)

# 유튜브 업로드 및 조회 관련 권한 스코프
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

TOKEN_FILES = {
    "rubia": "token_rubia.json",
    "taipei": "token_taipei.json",
    "aura": "token_aura.json",
    "smartage": "token_smartagetech.json",
}


def main():
    if len(sys.argv) < 2:
        print("❌ 사용법: python scratch/generate_oauth_token.py [채널키]")
        print("  예시: python scratch/generate_oauth_token.py aura")
        print("  예시: python scratch/generate_oauth_token.py smartage")
        sys.exit(1)

    channel_key = sys.argv[1].lower().strip()
    if channel_key not in TOKEN_FILES:
        print(f"❌ 지원하지 않는 채널 키입니다. ({', '.join(TOKEN_FILES.keys())} 중 입력)")
        sys.exit(1)

    token_filename = TOKEN_FILES[channel_key]
    token_path = os.path.join(PROJECT_ROOT, token_filename)

    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"❌ 클라이언트 비밀번호 파일(client_secret_...)을 찾을 수 없습니다: {CLIENT_SECRET_FILE}")
        sys.exit(1)

    print(f"🔄 [{channel_key.upper()}] 채널용 구글 인증 흐름을 개시합니다...")
    print("📢 잠시 후 로컬 웹 브라우저 창이 열리면 해당 채널의 구글 계정으로 로그인해 주세요.\n")

    try:
        # 1. OAuth2 흐름 빌드 및 구동
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)

        # 2. 토큰 데이터 조립
        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
            "universe_domain": getattr(creds, "universe_domain", "googleapis.com"),
            "account": "",
            "expiry": creds.expiry.isoformat()
            if hasattr(creds.expiry, "isoformat")
            else str(creds.expiry),
        }

        # 3. 신규 토큰 저장 (구버전 강제 덮어쓰기)
        with open(token_path, "w", encoding="utf-8") as f:
            json.dump(token_data, f, ensure_ascii=False, indent=2)

        print("\n=======================================================")
        print(f"✨ [{channel_key.upper()}] 토큰 인증 정보가 정상 저장되었습니다!")
        print(f"📂 파일 경로: {token_path}")
        print("=======================================================")

    except Exception as e:
        print(f"\n❌ 인증 실패 또는 에러 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
