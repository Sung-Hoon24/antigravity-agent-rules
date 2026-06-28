# -*- coding: utf-8 -*-
"""
유튜브 API 토큰 유효성 검사 및 자동 갱신 스크립트
- 4대 채널 토큰 파일들의 만료 여부를 체크합니다.
- 만료되었거나 유효하지 않은 경우 리프레시 토큰을 사용하여 자동으로 갱신하고 파일에 다시 씁니다.
- 갱신 후 YouTube Data API v3를 호출하여 실제 정상 동작 여부를 최종 확인합니다.
"""

import os
import json
import traceback
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import google.auth.exceptions

# [한글 주석] 스크립트 실행 위치 기준으로 프로젝트 루트를 동적 조립하여 절대경로 충돌을 방지합니다.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILES = {
    "rubia": {
        "file": "token_rubia.json",
        "channel_id": "UCgfReXSDhiDTe0JJgbyHGIw",
        "name": "Rubia Lofi - Daily Chill Beats & BGM",
    },
    "aura": {
        "file": "token_aura.json",
        "channel_id": "UC8jlSVeaw_wisJim9E_XHSQ",
        "name": "Aura Serenity Wellness",
    },
    "smartage": {
        "file": "token_smartagetech.json",
        "channel_id": "UCV9yGd2MS-RMcH30owlbB1w",
        "name": "SmartAgeTech",
    },
    "taipei": {
        "file": "token_taipei.json",
        "channel_id": "UCgfReXSDhiDTe0JJgbyHGIw",  # Rubia와 동일 채널
        "name": "Taipei Series",
    },
}


def validate_and_refresh():
    print("======================================================================")
    print("📺 YouTube OAuth2 Tokens Validation & Auto-Refresh System Starting...")
    print("======================================================================\n")

    summary_results = {}

    for channel_key, info in TOKEN_FILES.items():
        token_name = info["file"]
        token_path = os.path.join(PROJECT_ROOT, token_name)
        channel_name = info["name"]
        channel_id = info["channel_id"]

        print(f"[{channel_key.upper()}] 채널 점검 시작: {channel_name}")

        if not os.path.exists(token_path):
            print(f"❌ 토큰 파일 없음: {token_path}\n")
            summary_results[channel_key] = {"status": "FAIL", "reason": "토큰 파일이 부재합니다."}
            continue

        try:
            # 1. 파일에서 토큰 정보 로드
            with open(token_path, "r", encoding="utf-8") as f:
                token_data = json.load(f)

            # 2. Credentials 객체 생성
            creds = Credentials.from_authorized_user_file(token_path)

            # 초기 상태 확인
            print(f"  - 기존 만료일: {token_data.get('expiry', 'N/A')}")
            print(f"  - 토큰 유효성(creds.valid): {creds.valid}")
            print(f"  - 만료 여부(creds.expired): {creds.expired}")

            refreshed = False
            # 3. 만료되었거나 유효하지 않으면 갱신 시도
            if not creds.valid:
                if creds.refresh_token:
                    print("  🔄 토큰이 만료되었거나 유효하지 않아 갱신(Refresh)을 진행합니다...")
                    try:
                        creds.refresh(Request())

                        # 갱신된 정보 저장
                        updated_token_data = {
                            "token": creds.token,
                            "refresh_token": creds.refresh_token,
                            "token_uri": creds.token_uri,
                            "client_id": creds.client_id,
                            "client_secret": creds.client_secret,
                            "scopes": creds.scopes,
                            "universe_domain": getattr(
                                creds, "universe_domain", "googleapis.com"
                            ),
                            "account": token_data.get("account", ""),
                            "expiry": creds.expiry.isoformat()
                            if hasattr(creds.expiry, "isoformat")
                            else str(creds.expiry),
                        }

                        # 파일 쓰기
                        with open(token_path, "w", encoding="utf-8") as f:
                            json.dump(updated_token_data, f, ensure_ascii=False)

                        print("  ✨ 토큰 갱신 성공 및 파일 업데이트 완료!")
                        refreshed = True
                    except google.auth.exceptions.RefreshError as re:
                        print(f"  ❌ 토큰 갱신 실패 (리프레시 토큰이 만료되었거나 취소됨): {re}")
                        summary_results[channel_key] = {
                            "status": "EXPIRED",
                            "reason": "리프레시 토큰 만료",
                        }
                        continue
                else:
                    print("  ❌ 리프레시 토큰이 존재하지 않아 자동 갱신이 불가능합니다.")
                    summary_results[channel_key] = {
                        "status": "FAIL",
                        "reason": "리프레시 토큰 부재",
                    }
                    continue

            # 4. API 호출을 통한 최종 검증
            print("  📡 YouTube API 호출 테스트 중...")
            youtube = build("youtube", "v3", credentials=creds)

            # 채널 정보를 직접 쿼리하여 API 토큰 무결성 체크
            request = youtube.channels().list(part="snippet,statistics", id=channel_id)
            response = request.execute()

            if response.get("items"):
                item = response["items"][0]
                title = item["snippet"]["title"]
                subs = item["statistics"].get("subscriberCount", "0")
                print(f"  ✅ API 호출 성공! 채널명: {title} (구독자: {int(subs):,}명)")
                summary_results[channel_key] = {
                    "status": "SUCCESS",
                    "title": title,
                    "subscribers": int(subs),
                    "refreshed": refreshed,
                }
            else:
                print(f"  ⚠️ API 호출은 성공했으나 채널 ID({channel_id})를 조회하지 못했습니다.")
                summary_results[channel_key] = {"status": "WARN", "reason": "채널 ID 불일치"}

        except Exception as e:
            print(f"  ❌ 예외 발생: {e}")
            traceback.print_exc()
            summary_results[channel_key] = {"status": "ERROR", "reason": str(e)}

        print()

    print("======================================================================")
    print("📊 최종 진단 및 리프레시 결과 요약")
    print("======================================================================")
    for channel_key, res in summary_results.items():
        status = res["status"]
        if status == "SUCCESS":
            ref_msg = "(토큰 자동 갱신 완료)" if res["refreshed"] else "(기존 토큰 유효)"
            print(
                f"🟢 [{channel_key.upper()}] {res['title']} -> 정상 작동 {ref_msg} (구독자: {res['subscribers']:,}명)"
            )
        elif status == "EXPIRED":
            print(
                f"🔴 [{channel_key.upper()}] {TOKEN_FILES[channel_key]['name']} -> 만료됨. 구글 계정 재인증 필요! (사유: {res['reason']})"
            )
        elif status == "WARN":
            print(
                f"🟡 [{channel_key.upper()}] {TOKEN_FILES[channel_key]['name']} -> 경고 (사유: {res['reason']})"
            )
        else:
            print(
                f"🔴 [{channel_key.upper()}] {TOKEN_FILES[channel_key]['name']} -> 오류 발생 (사유: {res['reason']})"
            )
    print("======================================================================")


if __name__ == "__main__":
    validate_and_refresh()
