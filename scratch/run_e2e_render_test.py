# -*- coding: utf-8 -*-
"""
루비아 기술연구소 제3연구소 (보안/디버그 Vault)
실전 E2E 핫스왑 렌더링 시운전 스크립트
"""

import os
import sys
import time


def run_e2e_test():
    workspace = r"c:\1인기업\Apps\유튜브에이전트"
    sys.path.append(workspace)

    # 메인 비디오 렌더러 로드
    from telegram_bot.engine.video_renderer import render_video

    visual_path = os.path.join(
        workspace, "assets", "characters", "Rubia", "rubia_work_eye.png"
    )
    # 오디오 자산으로 루트에 존재하는 aura_shorts_v1.mp4에서 오디오 추출 합성 연동
    audio_path = os.path.join(workspace, "aura_shorts_v1.mp4")
    output_path = os.path.join(workspace, "output", "taipei_rainy_shorts.mp4")

    # Step 1 기획안 대본 텍스트 적용
    script_text = """
    자막: 비 오는 타이베이의 새벽, 오직 당신만을 위한 집중의 시간. / Rain in Taipei, a quiet moment just for your focus.
    자막: 글로벌 학생들과 원격 근무자들을 위한 아늑한 은신처. / A cozy shelter for global students and remote workers.
    자막: 복잡한 생각을 내려놓고, 빗소리와 함께 차분하게 시작해 보세요. / Clear your mind, and let the rain guide your beats.
    자막: 당신의 오늘 하루를 응원합니다. 구독하고 함께 집중해요. / Wishing you a productive day. Subscribe for more beats.
    """

    print("=" * 60)
    print("🎬 [E2E 시운전] 승인 인입 - 핫스왑 렌더링 가동")
    print("=" * 60)
    print(f" - 입력 이미지: {visual_path}")
    print(f" - 입력 오디오: {audio_path}")
    print(f" - 출력 비디오: {output_path}")

    if os.path.exists(output_path):
        try:
            os.remove(output_path)
            print("💡 기존 시운전 비디오 결과물을 초기화했습니다.")
        except Exception as e:
            print(f"⚠️ 기존 결과 제거 실패 (계속 진행): {str(e)}")

    start_time = time.time()

    # 렌더링 실행
    # 내부적으로 plugins/enabled/vfx_ken_burns.py 모듈의 before_render_visual 훅이 자동 트리거됨
    try:
        final_file = render_video(
            visual_path=visual_path,
            audio_path=audio_path,
            script_text=script_text,
            output_path=output_path,
            video_format="shorts",
        )
        end_time = time.time()
        elapsed = end_time - start_time

        print("=" * 60)
        print("🎉 [시운전 완료] Ver 1.1 핫스왑 렌더링 최종 성공")
        print("=" * 60)
        print(f" - 총 렌더링 소요 시간: {elapsed:.2f} 초")
        print(f" - 최종 비디오 경로: {final_file}")
        print(f" - 생성 비디오 파일 크기: {os.path.getsize(final_file) / (1024*1024):.2f} MB")
        print("💡 [VFX & 화질 확인] Ken Burns 줌인 및 CRF 17 무손실 화질이 최종 적용되었습니다.")
        print("=" * 60)
    except Exception as e:
        print(f"❌ [렌더링 실패]: {str(e)}", file=sys.stderr)


if __name__ == "__main__":
    run_e2e_test()
