# -*- coding: utf-8 -*-
"""
영상 템플릿 1번(render_template_1.json) 기반 30초 테스트 비디오 생성 스크립트
"""

import os
import sys
import json
import time
import subprocess
import imageio_ffmpeg

# 프로젝트 루트 경로를 모듈 탐색 경로에 등록
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from telegram_bot.engine.video_renderer import render_video

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

def run_test():
    print("=" * 60)
    print("🎬 [영상 템플릿 1번] 30초 테스트 영상 렌더링 가동")
    print("=" * 60)

    # 1. 경로 정의
    template_path = os.path.join(project_root, "configs", "render_template_1.json")
    visual_path = os.path.join(project_root, "assets", "characters", "Rubia", "rubia_work_eye.png")
    
    # 💡 [한글 주석] 기존 음원 소스(lyria_shorts_v1.mp3)에서 30초 분량만 추출하여 임시 오디오를 구성합니다.
    source_audio_video = os.path.join(project_root, "specs", "assets", "lyria_shorts_v1.mp3")
    temp_dir = os.path.join(project_root, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_audio_path = os.path.join(temp_dir, "temp_audio_30s.mp3")
    
    output_dir = os.path.join(project_root, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "template_1_test_30s.mp4")

    # 💡 [한글 주석] 이전 빌드 때 캐싱된 임시 비디오 캐시들을 강제로 지워 새로운 스킬 공식이 반드시 재렌더링되게 만듭니다.
    cached_videos = [
        output_path,
        os.path.join(output_dir, "rubia_work_eye_vfx_slow_zoom_loop.mp4"),
        os.path.join(output_dir, "rubia_work_eye_vfx_typing_intro.mp4"),
        os.path.join(project_root, "assets", "characters", "Rubia", "rubia_work_eye_vfx_slow_zoom_loop.mp4"),
        os.path.join(project_root, "assets", "characters", "Rubia", "rubia_work_eye_vfx_typing_intro.mp4"),
    ]
    for c_path in cached_videos:
        if os.path.exists(c_path):
            try:
                os.remove(c_path)
                print(f"🧹 오래된 캐시 비디오를 삭제했습니다: {c_path}")
            except Exception as e:
                print(f"⚠️ 캐시 삭제 실패: {c_path} ({e})")

    # 2. 30초 임시 음원 슬라이싱 추출 (FFmpeg 이용)
    print("🎼 테스트용 30초 음원 추출을 시작합니다...")
    if not os.path.exists(source_audio_video):
        # 만약 원본 오디오가 없으면 다른 경로 탐색 (백업 및 폴백)
        source_audio_video = r"c:\1인기업\Apps\유튜브에이전트\specs\assets\lyria_shorts_v1.mp3"
        if not os.path.exists(source_audio_video):
            raise FileNotFoundError(f"원본 오디오 소스를 찾을 수 없습니다: {source_audio_video}")

    cmd_slice = [
        FFMPEG_PATH, "-y",
        "-ss", "00:00:00",
        "-i", source_audio_video,
        "-t", "30",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        temp_audio_path
    ]
    res = subprocess.run(cmd_slice, capture_output=True)
    if res.returncode != 0:
        raise RuntimeError(f"임시 음원 생성 실패:\n{res.stderr.decode('utf-8', errors='ignore')}")
    print("✅ 30초 임시 음원 생성 완료.")

    # 3. 템플릿 JSON 로드 및 기획안 구성
    print(f"📖 템플릿 1번 로드 중: {template_path}")
    with open(template_path, "r", encoding="utf-8") as f:
        planning_data = json.load(f)

    # 기획안 데이터에 자막과 플레이리스트 정보 추가 주입
    planning_data["concept"] = "Template 1 Slow Zoom Test"
    planning_data["youtube_title"] = "Test Title"
    planning_data["youtube_description"] = "Test Description"
    planning_data["youtube_tags"] = ["test"]
    planning_data["playlist"] = [{"title": "Test Track 30s", "duration_sec": 30}]
    planning_data["captions"] = [
        {"time_code": "00:00", "text": "자막: 비 오는 타이베이의 새벽, 오직 당신만을 위한 집중의 시간. / Rain in Taipei, a quiet moment just for your focus."},
        {"time_code": "00:08", "text": "자막: 글로벌 학생들과 원격 근무자들을 위한 아늑한 은신처. / A cozy shelter for global students and remote workers."},
        {"time_code": "00:16", "text": "자막: 복잡한 생각을 내려놓고, 빗소리와 함께 차분하게 시작해 보세요. / Clear your mind, and let the rain guide your beats."}
    ]

    print(f"🧬 적용된 VFX 스킬: {planning_data.get('vfx_skill')}")

    # 4. 렌더링 실행
    start_time = time.time()
    try:
        final_file = render_video(
            visual_path=visual_path,
            audio_path=temp_audio_path,
            planning_data=planning_data,
            output_path=output_path,
            video_format="shorts", # 30초 테스트 숏츠 포맷
        )
        elapsed = time.time() - start_time
        print("=" * 60)
        print("🎉 [테스트 렌더링 완료] 성공적으로 비디오가 빌드되었습니다.")
        print("=" * 60)
        print(f" - 소요 시간: {elapsed:.2f} 초")
        print(f" - 결과 비디오: {final_file}")
        print(f" - 파일 크기: {os.path.getsize(final_file) / (1024*1024):.2f} MB")
        print("=" * 60)
    except Exception as render_err:
        print(f"❌ 렌더링 중 오류 발생: {str(render_err)}", file=sys.stderr)
    finally:
        # 임시 음원 파일 정리
        if os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except Exception:
                pass

if __name__ == "__main__":
    run_test()
