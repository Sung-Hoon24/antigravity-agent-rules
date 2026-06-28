# .agents/scripts/generate_ocean_resources.py
# 아우라 채널 'Deep Ocean Voyage' 콘텐츠용 432Hz 치유 주파수 믹싱 및 앰비언트 음원 생성 스크립트
# 요구 사양: FFmpeg 설치 및 환경 변수 등록 필요

import os
import sys
import subprocess
import shutil

# 상수 설정
DURATION_SEC = 180  # 3분 (180초)
FREQUENCY_HZ = 432  # 432Hz 힐링 주파수
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "assets",
    "brand",
)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "deep_ocean_432hz_healing.mp3")

# 디렉토리 생성 보장
os.makedirs(OUTPUT_DIR, exist_ok=True)


def check_ffmpeg() -> bool:
    """시스템에 FFmpeg가 정상적으로 설치 및 환경변수 등록되어 있는지 확인합니다."""
    return shutil.which("ffmpeg") is not None


def generate_healing_audio(bgm_path: str = None):
    """
    432Hz 치유 주파수 오디오를 생성하고, BGM 음원과 자연스럽게 믹싱합니다.
    방어적 프로그래밍: BGM 파일이 없거나 찾을 수 없는 경우, 브라운 노이즈(Brown Noise)를
    자체 생성하여 깊은 바닷속 백색소음 앰비언트로 대체해 줍니다.
    """
    print("=" * 60)
    print("🌊 Deep Ocean Voyage 432Hz 힐링 오디오 생성 및 믹싱")
    print("=" * 60)

    if not check_ffmpeg():
        print("❌ 오류: 시스템에서 FFmpeg를 찾을 수 없습니다.")
        print("   해결: FFmpeg가 설치되어 있고 환경 변수(Path)에 등록되어 있는지 확인해 주세요.")
        sys.exit(1)

    print(f"📌 설정 주파수: {FREQUENCY_HZ}Hz (치유 주파수)")
    print(f"📌 재생 시간: {DURATION_SEC}초 (3분)")

    # 1. BGM 경로 확인 및 방어적 폴백 설정
    use_fallback = False
    if not bgm_path or not os.path.exists(bgm_path):
        print("⚠️  BGM 음원 파일이 누락되었거나 찾을 수 없습니다.")
        print("👉 [방어적 폴백] FFmpeg 브라운 노이즈(Brown Noise)로 심해 파도 소리를 자체 생성합니다.")
        use_fallback = True
    else:
        print(f"🎵 사용 BGM 파일: {os.path.basename(bgm_path)}")

    # 2. FFmpeg 필터를 활용한 믹싱 커맨드 구성
    # BGM이 없을 경우 432Hz 기반 3중 화음(432Hz + 540Hz + 648Hz) + 핑크 노이즈로
    # 영롱한 명상 싱잉볼 사운드 자체 생성
    if use_fallback:
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency={FREQUENCY_HZ}:duration={DURATION_SEC}",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=540:duration={DURATION_SEC}",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=648:duration={DURATION_SEC}",
            "-f",
            "lavfi",
            "-i",
            f"anoisesrc=color=pink:duration={DURATION_SEC}",
            "-filter_complex",
            "[0:a]volume=0.15[a0];[1:a]volume=0.10[a1];[2:a]volume=0.10[a2];[3:a]volume=0.65[a3];[a0][a1][a2][a3]amix=inputs=4:duration=first",
            OUTPUT_FILE,
        ]
    else:
        # 외부 BGM 음원이 지정되었을 경우 (BGM 볼륨 85% + 432Hz 주파수 15%)
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency={FREQUENCY_HZ}:duration={DURATION_SEC}",
            "-i",
            bgm_path,
            "-filter_complex",
            f"[0:a]volume=0.15[a0];[1:a]volume=0.85[a1];[a0][a1]amix=inputs=2:duration=first -t {DURATION_SEC}",
            OUTPUT_FILE,
        ]

    print("\n🛠️  FFmpeg 합성 및 믹싱 프로세스 가동 중...")
    try:
        # 백그라운드로 FFmpeg 실행
        subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        print("\n🎉 432Hz 치유 앰비언트 오디오 생성이 완료되었습니다!")
        print(f"👉 저장 경로: {OUTPUT_FILE}")
        print("=" * 60)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ FFmpeg 실행 중 에러 발생: {e}")
        print(f"   에러 로그: {e.stderr}")
        print("=" * 60)


if __name__ == "__main__":
    # 인수 인계가 있다면 첫 번째 파라미터를 BGM 경로로 취급
    bgm = sys.argv[1] if len(sys.argv) > 1 else None
    generate_healing_audio(bgm)
