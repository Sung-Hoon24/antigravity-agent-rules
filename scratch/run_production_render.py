# -*- coding: utf-8 -*-
"""
[제1연구소 실전 프로덕션] 실전 데이터 환류 기반 비디오 렌더링 기동 스크립트 (run_production_render.py)
- 'rubia' 채널의 RAG 성공 문법이 주입된 기획 JSON을 토대로 실제 고화질 에셋을 합성합니다.
- 실전 결과물이므로 fast_gate=False 옵션으로 59.5초 Shorts 비디오 규격을 인코딩합니다.
"""

import sys
import os
import time
import logging

# 프로젝트 루트 디렉터리를 sys.path에 추가
WORKSPACE = r"c:\1인기업\Apps\유튜브에이전트"
sys.path.append(WORKSPACE)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ProductionRenderer")


def run_production_rendering():
    logger.info("=" * 60)
    logger.info("🎬 [Production Phase] 첫 번째 실전 환류 기반 영상 렌더링 시작")
    logger.info("=" * 60)

    # 1. RAG 성공 문법을 주입받아 빌드된 실전 기획안 JSON 정의
    # (Ver 2.0 수익화 결제 게이트웨이 및 monetization_point 필수 규격 반영)
    production_json_data = {
        "concept": "以雨中的臺北城市景觀為背景，結合Lo-Fi音樂與環境雨聲，打造一段能引發『고요한 집중』、『편안한 휴식』、『몽환적인 감성』의短影音內容。畫面將穿梭於濕潤的臺北街景與溫馨的室內空間，透過細膩의 視聽 元素，提供觀眾一個沉浸式의 放鬆體驗。",
        "youtube_title": "雨中臺北 Lo-Fi 🎧 寧靜氛圍 | 讀書放鬆BGM #Shorts",
        "youtube_description": "沉浸在雨中臺北의 寧靜氛圍中. 이 Lo-Fi 음악은 빗소리와 편안한 선율이 결합되어 讀書, 工作, 放鬆 또는 잠들기 전 듣기 매우 적합합니다. 🎧\n\n✨ 訂閱我們的 Premium 會員，享受高音質音源與無廣告沉浸式體驗！\n🔗 立即加入 Premium: https://www.sandbox.paypal.com/billing/subscriptions?plan_id=P-9RU42084R71183354MYS2Q&utm_source=youtube&utm_medium=rubia_desc\n💬 感謝您支持我們的音樂創作！",
        "youtube_tags": ["#臺北", "#雨天", "#LoFi", "#放鬆音樂", "#讀書BGM", "#寧靜氛圍", "#雨聲"],
        "playlist": [
            {"title": "雨巷漫步 (Rainy Alley Walk)", "duration_sec": 28},
            {"title": "窗邊的咖啡香 (Coffee at Window)", "duration_sec": 25},
        ],
        "captions": [
            {"time_code": "00:02", "text": "雨滴輕敲窗戶"},
            {"time_code": "00:15", "text": "城市在雨中低語"},
            {"time_code": "00:30", "text": "尋找片刻寧靜"},
            {"time_code": "00:45", "text": "只屬於你的療癒時光"},
        ],
        "visual_audio_guide": "整體畫面以臺北雨夜的城市景觀為主，慢속運鏡...",
        "monetization_point": "타이베이 비 오는 로파이 채널에 최적화된 PayPal 프리미엄 음악 구독 플랜(Plan: P-9RU42084R71183354MYS2Q) 바인딩 및 무광고 음원 감상 혜택을 소구하여 고관여 구독을 유도합니다.",
    }

    # 2. 실전 미디어 에셋 경로 바인딩
    # (타이베이 고해상도 생성 이미지 및 빗소리 분위기 lofi BGM 음원)
    visual_path = os.path.join(
        WORKSPACE, "input", "taipei", "images", "generated_20260606_073402.png"
    )
    audio_path = os.path.join(
        WORKSPACE, "input", "rubia", "images", "rubia_shorts_v1.mp4"
    )
    output_path = os.path.join(WORKSPACE, "output", "rubia_production_v2.0.mp4")

    # 기존 파일 삭제
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except Exception:
            pass

    # 3. 렌더링 파이프라인 가동 (실전 프로덕션용이므로 fast_gate=False 설정)
    from telegram_bot.engine.video_renderer import render_video

    logger.info(f"📹 렌더링 입력 비주얼 에셋: {visual_path}")
    logger.info(f"📹 렌더링 입력 오디오 BGM: {audio_path}")
    logger.info("🎬 렌더링 구동 개시 (Fast-Gate: False)...")

    start_time = time.time()
    try:
        render_video(
            visual_path=visual_path,
            audio_path=audio_path,
            planning_data=production_json_data,
            output_path=output_path,
            video_format="shorts",
            fast_gate=False,  # 실전 인코딩
        )
        elapsed = time.time() - start_time
        logger.info(f"✅ 렌더링 완료! 소요 시간: {elapsed:.2f}초")

        # 4. 파일 무결성 및 크기 확인
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            logger.info("=" * 60)
            logger.info("🎉 [Production Success] 첫 번째 실전 프로덕션 비디오가 정상 도출되었습니다!")
            logger.info(f"- 출력 경로: {output_path}")
            logger.info(f"- 비디오 크기: {os.path.getsize(output_path):,} bytes")
            logger.info("=" * 60)
        else:
            raise RuntimeError("렌더링은 완료되었으나 비디오 파일이 없거나 0바이트입니다.")

    except Exception as e:
        logger.error(f"❌ 렌더링 실패: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run_production_rendering()
