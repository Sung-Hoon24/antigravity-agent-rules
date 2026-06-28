# -*- coding: utf-8 -*-
"""
루비아 기술연구소 제1연구소 (VFX/시각 효과 Sandbox)
Ken Burns 동적 카메라 줌인 VFX 플러그인 (Ver 1.0)

본 모듈은 정지 이미지를 실시간 줌인 비디오 클립으로 렌더링하여 핫스왑 방식으로 메인 렌더러에 주입합니다.
"""

import os
import subprocess
import imageio_ffmpeg

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()


def before_render_visual(visual_path, video_format="shorts", output_dir=None, **kwargs):
    """
    [R&D 훅] 비주얼 자산 렌더링 전 전처리 훅
    정지 이미지를 10초짜리(250프레임, 25fps) 중심점 유지 줌인 비디오 클립(.mp4)으로 핫스왑합니다.
    """
    # 이미 동영상이거나 GIF인 경우 줌팬 처리를 생략하고 즉시 반환
    if visual_path.lower().endswith((".mp4", ".mkv", ".avi", ".mov", ".gif")):
        return visual_path

    if not os.path.exists(visual_path):
        print(f"⚠️ [VFX Ken Burns] 이미지 파일이 존재하지 않습니다: {visual_path}")
        return visual_path

    # 출력 경로 결정
    out_dir = output_dir or os.path.dirname(visual_path) or os.getcwd()
    base_name = os.path.splitext(os.path.basename(visual_path))[0]
    vfx_output_path = os.path.join(out_dir, f"{base_name}_vfx_kenburns.mp4")

    # 이미 동일한 캐시 VFX 비디오 클립이 렌더링되어 있다면 재활용 (렌더링 속도 최적화)
    if os.path.exists(vfx_output_path) and os.path.getsize(vfx_output_path) > 0:
        print(f"🔌 [VFX Ken Burns] 이미 존재해 캐싱된 VFX 클립을 재사용합니다: {vfx_output_path}")
        return vfx_output_path

    # 비디오 규격별 해상도 및 화면 비율 설정
    if video_format == "longform":
        width, height = 1920, 1080
        aspect = "1920x1080"
    else:
        width, height = 1080, 1920
        aspect = "1080x1920"

    print(f"🔌 [VFX Ken Burns] 이미지 줌인 비디오 클립 렌더링을 가동합니다:\n -> {vfx_output_path}")

    # FFmpeg 필터 그래프 조립:
    # 1. scale로 2배 오버샘플링(화질 저하 방지) -> crop으로 정확한 비비율 정밀 크롭
    # 2. zoompan으로 중심 유지하며 프레임당 0.001씩 최대 1.4배까지 점진적 줌인 구현
    vf_chain = (
        f"scale={width*2}:{height*2}:force_original_aspect_ratio=increase,crop={width*2}:{height*2},"
        f"zoompan=z='min(zoom+0.001,1.4)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=250:s={aspect}:fps=25"
    )

    cmd = [
        FFMPEG_PATH,
        "-y",
        "-loop",
        "1",
        "-i",
        visual_path,
        "-vf",
        vf_chain,
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "17",
        "-t",
        "10",
        "-pix_fmt",
        "yuv420p",
        vfx_output_path,
    ]

    try:
        # 백그라운드로 안전 격리 프로세스 실행
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )
        if result.returncode == 0:
            print("🔌 [VFX Ken Burns] 성공적으로 동적 비디오 클립을 생성했습니다.")
            return vfx_output_path
        else:
            # 실패 시 메인 렌더링에 영향이 가지 않도록 원본 정지 이미지 경로를 그대로 폴백 반환
            print(
                f"❌ [VFX Ken Burns 실패] FFmpeg 오류 발생, 원본 이미지를 폴백 사용합니다.\n{result.stderr}"
            )
            return visual_path
    except Exception as e:
        print(f"❌ [VFX Ken Burns 오류] 예외 발생, 원본 이미지를 폴백 사용합니다: {str(e)}")
        return visual_path
