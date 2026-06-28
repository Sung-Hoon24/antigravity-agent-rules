# -*- coding: utf-8 -*-
"""
CLI 독립형 비디오 빌더 스크립트 (generate_video.py)
- 개발자 터미널(안티그레비티)에서 명령어를 입력하여 즉각 숏폼 및 롱폼 영상을 빌드할 수 있습니다.
- 캐릭터 이미지 필터링 기능이 기본 탑재되어 오동작 합성을 방지합니다.
"""

import os
import sys
import argparse

# 프로젝트 루트 경로를 Python Path에 주입하여 모듈 로딩 보장
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram_bot.engine.audio_generator import generate_lyria3_music
from telegram_bot.engine.video_renderer import render_video


def main():
    parser = argparse.ArgumentParser(
        description="Rubia Team - 유튜브 숏폼/롱폼 하이브리드 비디오 빌더 CLI"
    )

    # CLI 실행 옵션 정의
    parser.add_argument(
        "--channel",
        type=str,
        default="rubia",
        choices=["rubia", "taipei", "aura", "smartage"],
        help="대상 유튜브 채널 키 (기본값: rubia)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="shorts",
        choices=["shorts", "longform"],
        help="영상 제작 포맷 (기본값: shorts)",
    )
    parser.add_argument(
        "--duration", type=int, default=1, help="영상 목표 재생 시간 (분 단위, 기본값: 1)"
    )
    parser.add_argument(
        "--input-visual", type=str, default=None, help="사용할 이미지 또는 동영상 배경 파일 경로 (선택사항)"
    )
    parser.add_argument(
        "--input-audio",
        type=str,
        default=None,
        help="사용할 커스텀 음원 파일 경로 (선택사항, 없을 시 AI 실시간 작곡)",
    )
    parser.add_argument(
        "--script", type=str, default=None, help="자막용 대본 텍스트 내용 혹은 텍스트 파일 경로 (선택사항)"
    )
    parser.add_argument(
        "--output", type=str, default=None, help="출력될 완성 비디오 파일 경로 (선택사항)"
    )

    args = parser.parse_args()

    channel_key = args.channel
    video_format = args.mode
    video_length = args.duration

    print("=" * 60)
    print("🚀 [CLI Video Builder] 영상 제작 파이프라인 가동")
    print(f"• 채널 키: {channel_key}")
    print(f"• 영상 포맷: {video_format.upper()}")
    print(f"• 목표 재생 시간: {video_length}분")
    print("=" * 60)

    # 1. 출력 디렉토리 설정
    if args.output:
        file_path = args.output
        output_dir = os.path.dirname(file_path) or os.getcwd()
    else:
        output_dir = os.path.join("c:/1인기업/Apps/유튜브에이전트/output", channel_key)
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{channel_key}_{video_format}_cli_v1.mp4")

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

    # 2. 비주얼(visual) 소스 결정 및 캐릭터 필터링
    if args.input_visual and os.path.exists(args.input_visual):
        visual_source = args.input_visual
        print(f"📸 [CLI] 입력 비주얼 지정됨: {os.path.basename(visual_source)}")
    else:
        input_channel_dir = os.path.join("c:/1인기업/Apps/유튜브에이전트/input", channel_key)
        images_dir = os.path.join(input_channel_dir, "images")
        videos_dir = os.path.join(input_channel_dir, "videos")

        visual_paths = []

        # 1. 이미지 폴더 스캔 (images/)
        if os.path.exists(images_dir):
            for f in os.listdir(images_dir):
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                    f_path = os.path.join(images_dir, f)
                    try:
                        # 파일명에 에이전트 캐릭터 키워드가 포함되어 있다면 배경용 리소스에서 안전 스킵
                        if any(char in f.lower() for char in character_names):
                            print(f"⚠️ [CLI] 에이전트 캐릭터 리소스 파일명 제외: {f}")
                            continue
                        visual_paths.append(f_path)
                    except Exception:
                        visual_paths.append(f_path)

        # 2. 비디오 폴더 스캔 (videos/)
        if os.path.exists(videos_dir):
            for f in os.listdir(videos_dir):
                if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
                    visual_paths.append(os.path.join(videos_dir, f))

        # 수정 시간 기준으로 정렬
        visual_paths = sorted(
            visual_paths, key=lambda x: os.path.getmtime(x), reverse=True
        )

        if visual_paths:
            visual_source = visual_paths[0]
            print(f"📸 [CLI] 입력 폴더에서 최근 비주얼 자동 로드: {os.path.basename(visual_source)}")
        else:
            # 🚨 [Fallback 금지] 가용 이미지가 없으면 즉시 에러 출력 후 종료
            print("=" * 60)
            print("🚨 [에셋 생성 실패] 가용 이미지 리소스가 없습니다.")
            print("기존 파일을 사용하지 않고 작업을 중단합니다.")
            print("이미지를 새로 생성하거나 --input-visual 옵션으로 지정해 주세요.")
            print("=" * 60)
            sys.exit(1)

    # 3. 오디오(audio) 소스 결정 및 AI 작곡 실행
    if args.input_audio and os.path.exists(args.input_audio):
        audio_source = args.input_audio
        print(f"🎵 [CLI] 입력 음원 지정됨: {os.path.basename(audio_source)}")
    else:
        # 커스텀 오디오 서브폴더 탐색
        audios_dir = os.path.join("c:/1인기업/Apps/유튜브에이전트/input", channel_key, "audios")
        audio_paths = []
        if os.path.exists(audios_dir):
            for f in os.listdir(audios_dir):
                if f.lower().endswith((".mp3", ".wav", ".m4a")):
                    audio_paths.append(os.path.join(audios_dir, f))

        audio_paths = sorted(
            audio_paths, key=lambda x: os.path.getmtime(x), reverse=True
        )

        if audio_paths:
            audio_source = audio_paths[0]
            print(f"🎵 [CLI] 입력 폴더에서 최근 음원 자동 로드: {os.path.basename(audio_source)}")
        else:
            # AI 실시간 작곡 진행
            print("🎵 [CLI] BGM 음원 자동 작곡 가동 (Lyria 3 Pro Engine)...")
            audio_filename = f"{channel_key}_music_cli_generated.mp3"
            audio_path = os.path.join(output_dir, audio_filename)
            try:
                audio_source = generate_lyria3_music(
                    channel_key, audio_path, duration_min=video_length
                )
                print(f"✅ [CLI] AI 음악 작곡 및 루프 가공 성공: {audio_source}")
            except Exception as e:
                # 🚨 [Fallback 금지] 음원 생성 실패 시 기존 파일 재사용 전면 금지
                print("=" * 60)
                print(f"🚨 [에셋 생성 실패] AI 음악 작곡 실패: {e}")
                print("기존 파일을 사용하지 않고 작업을 중단합니다.")
                print("재시도하거나 --input-audio 옵션으로 음원 파일을 지정해 주세요.")
                print("=" * 60)
                sys.exit(1)

    # 4. 자막용 대본 텍스트 결정
    script_text = None
    if args.script:
        if os.path.exists(args.script):
            try:
                with open(args.script, "r", encoding="utf-8") as f:
                    script_text = f.read()
                print(f"📝 [CLI] 자막 대본 파일 로드됨: {os.path.basename(args.script)}")
            except Exception as se:
                print(f"⚠️ [CLI] 대본 파일 읽기 실패: {se}")
        else:
            script_text = args.script
            print("📝 [CLI] 입력된 텍스트 인자를 자막 대본으로 적용합니다.")

    if not script_text:
        # 채널별 디폴트 자막 템플릿
        if channel_key == "aura":
            script_text = "자막: Close your eyes and breathe in.\n자막: Feel the warm energy flowing.\n자막: Let go of all your tension."
        elif channel_key in ["rubia", "taipei"]:
            script_text = "字幕: 閉上眼睛，深呼吸。\n字幕: 感受溫暖的能量在流動。\n字幕: 放下所有的疲憊與焦慮。"
        elif channel_key == "smartage":
            script_text = "자막: 눈을 감고 천천히 숨을 쉬어보세요.\n자막: 편안한 음악과 함께 하루를 정리합니다.\n자막: 오늘 하루도 정말 수고하셨습니다."
        else:
            script_text = "자막: 오늘 하루도 정말 수고 많으셨습니다.\n자막: 편안하게 들으면서 지친 마음을 달래보세요."

    # 5. 🛡️ [타임스탬프 교차 검증 - TSS v1.1 기준 개정] FFmpeg 렌더링 직전,
    # 해당 이미지/음원 파일의 생성 시각(mtime)이 현재 렌더링 시도 시각으로부터 과거 15분 이내(< 900초)인지 확인합니다.
    import time

    now_ts = time.time()

    img_mtime = os.path.getmtime(visual_source)
    audio_mtime = os.path.getmtime(audio_source)

    if not (0 <= now_ts - img_mtime <= 900):
        print("=" * 60)
        print("🚨 [타임스탬프 검증 실패] 이미지 파일이 15분 유효시간을 초과한 구형 캐시입니다.")
        print(f"파일: {os.path.basename(visual_source)}")
        print("렌더링을 거부합니다. 이미지를 새로 생성해 주세요.")
        print("=" * 60)
        sys.exit(1)

    if not (0 <= now_ts - audio_mtime <= 900):
        print("=" * 60)
        print("🚨 [타임스탬프 검증 실패] 음원 파일이 15분 유효시간을 초과한 구형 캐시입니다.")
        print(f"파일: {os.path.basename(audio_source)}")
        print("렌더링을 거부합니다. 음원을 새로 생성해 주세요.")
        print("=" * 60)
        sys.exit(1)

    print("✅ [타임스탬프 검증 통과] 모든 에셋 파일이 15분 이내에 생성된 유효한 자산입니다.")

    # 6. 비디오 렌더링 시작
    print("🎬 [CLI] 비디오 최종 FFmpeg 렌더링 및 합성 개시...")
    try:
        render_video(
            visual_path=visual_source,
            audio_path=audio_source,
            script_text=script_text,
            output_path=file_path,
            video_format=video_format,
        )
        print("=" * 60)
        print("🎉 [CLI] 비디오 제작 파이프라인 최종 성공!")
        print(f"📁 완성본 파일 경로: {file_path}")
        print("=" * 60)
    except Exception as re:
        print("=" * 60)
        print(f"❌ [CLI] 비디오 렌더링 중 오류 발생: {re}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
