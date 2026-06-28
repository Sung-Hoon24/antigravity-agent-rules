# .agents/scripts/youtube_analyzer.py
# 유튜브 Data API v3를 사용하여 관리 채널 3개의 최신 영상 및 댓글을 수집하는 스크립트
# 실행 전 필수: pip install google-api-python-client python-dotenv

import os
import sys

# .env 파일 로드 (프로젝트 루트 기준)
try:
    from dotenv import load_dotenv

    # 스크립트 위치 기준 2단계 상위 = 프로젝트 루트
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    load_dotenv(os.path.join(project_root, ".env"))
except ImportError:
    # python-dotenv가 없어도 환경 변수에서 직접 읽을 수 있으므로 계속 진행
    pass

from googleapiclient.discovery import build


# ============================================================
# [설정 영역] 관리 중인 3개 채널 정보
# ============================================================
OUR_CHANNELS = [
    {
        "name": "Rubia Lofi",
        "brand": "The Urban Universe (감성)",
        "handle": "SayCompany-BGMRubiaLofi",
        "channel_id": "UCgfReXSDhiDTe0JJgbyHGIw",
    },
    {
        "name": "Aura Serenity Wellness",
        "brand": "The Nature (휴식)",
        "handle": "AuraSerenityWellness",
        "channel_id": "UC8jlSVeaw_wisJim9E_XHSQ",
    },
    {
        "name": "스마트 에이지테크",
        "brand": "The Education (지식)",
        "handle": "smartagetech-v7e",
        "channel_id": "UCV9yGd2MS-RMcH30owlbB1w",
    },
]


def main():
    # 1. 환경 변수에서 API 키 가져오기
    api_key = os.environ.get("YOUTUBE_API_KEY")

    if not api_key:
        print("❌ 오류: YOUTUBE_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("   해결: 프로젝트 루트에 .env 파일을 만들고 YOUTUBE_API_KEY=... 을 추가하세요.")
        sys.exit(1)

    # API 클라이언트 초기화 (실패 시 명확한 에러 메시지 출력)
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
    except Exception as e:
        print(f"❌ YouTube API 클라이언트 초기화 실패: {e}")
        sys.exit(1)

    print(f"🚀 채널 분석 시작... (총 {len(OUR_CHANNELS)}개 채널)\n")

    # 2. 각 채널 순회하며 분석
    for ch_info in OUR_CHANNELS:
        channel_id = ch_info["channel_id"]
        print(f"\n{'=' * 60}")
        print(f"📺 [{ch_info['brand']}] {ch_info['name']} (@{ch_info['handle']})")
        print(f"   채널 ID: {channel_id}")
        print(f"{'=' * 60}")

        # 채널의 업로드 재생목록 가져오기
        try:
            channel_req = youtube.channels().list(
                part="contentDetails,statistics", id=channel_id
            )
            channel_res = channel_req.execute()
        except Exception as e:
            print(f"   ❌ 채널 정보를 가져오는 중 오류 발생: {e}")
            continue

        if not channel_res.get("items"):
            print("   ❌ 채널을 찾을 수 없습니다. 채널 ID를 확인해주세요.")
            continue

        # 채널 전체 통계 출력
        ch_stats = channel_res["items"][0].get("statistics", {})
        print(f"   📈 구독자: {ch_stats.get('subscriberCount', '비공개')}")
        print(f"   👁️  총 조회수: {ch_stats.get('viewCount', '0')}")
        print(f"   🎥 총 영상 수: {ch_stats.get('videoCount', '0')}")

        uploads_playlist_id = channel_res["items"][0]["contentDetails"][
            "relatedPlaylists"
        ]["uploads"]

        # 최신 영상 5개 가져오기
        try:
            playlist_req = youtube.playlistItems().list(
                part="snippet", playlistId=uploads_playlist_id, maxResults=5
            )
            playlist_res = playlist_req.execute()
        except Exception as e:
            print(f"   ❌ 재생목록 데이터를 가져오는 중 오류 발생: {e}")
            continue

        # 3. 각 영상의 제목, 통계, 댓글 수집
        for item in playlist_res.get("items", []):
            video_id = item["snippet"]["resourceId"]["videoId"]
            video_title = item["snippet"]["title"]
            print(f"\n  🎬 영상: {video_title}")

            # 영상 조회수, 좋아요 가져오기
            try:
                stat_req = youtube.videos().list(part="statistics", id=video_id)
                stat_res = stat_req.execute()

                if stat_res.get("items"):
                    stats = stat_res["items"][0]["statistics"]
                    print(
                        f"     📊 조회수: {stats.get('viewCount', 0)}, 좋아요: {stats.get('likeCount', 0)}"
                    )
                else:
                    print("     📊 통계 데이터를 가져올 수 없습니다.")
            except Exception as e:
                print(f"     📊 통계 조회 실패: {e}")

            # 댓글 가져오기 (최대 10개, 관련성 높은 순)
            try:
                comment_req = youtube.commentThreads().list(
                    part="snippet", videoId=video_id, order="relevance", maxResults=10
                )
                comment_res = comment_req.execute()

                comments = comment_res.get("items", [])
                if comments:
                    print("     💬 주요 댓글:")
                    for c_item in comments:
                        comment_text = c_item["snippet"]["topLevelComment"]["snippet"][
                            "textDisplay"
                        ]
                        # HTML 태그 간단 제거
                        comment_text = comment_text.replace("<br>", " ").replace(
                            "<br/>", " "
                        )
                        print(f"       - {comment_text}")
                else:
                    print("     💬 댓글이 없습니다.")
            except Exception:
                # 댓글이 비활성화된 영상 등에서 발생하는 에러 처리
                print("     💬 댓글을 가져올 수 없습니다 (댓글 사용 중지 등)")

            print(f"     {'─' * 40}")

    print(f"\n{'=' * 60}")
    print("✅ 전체 데이터 추출 완료!")
    print("위 텍스트를 바탕으로 시청자 니즈를 분석하고 기획안을 도출하세요.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
