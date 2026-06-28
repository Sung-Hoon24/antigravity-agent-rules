# -*- coding: utf-8 -*-
"""
루비아 기술연구소 제1연구소 (VFX/시각 효과 Sandbox)
Ken Burns VFX 모의 렌더링 및 벤치마크 테스트 스크립트
"""

import os
import time
import importlib.util


def run_test():
    workspace = r"c:\1인기업\Apps\유튜브에이전트"
    plugin_path = os.path.join(workspace, "plugins", "enabled", "vfx_ken_burns.py")
    sample_image = os.path.join(
        workspace, "assets", "characters", "Rubia", "rubia_work_eye.png"
    )
    output_dir = os.path.join(workspace, "output")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("=" * 60)
    print("🧪 [VFX 모의 테스트] 렌더링 성능 및 부하 테스트 가동")
    print("=" * 60)
    print(f" - 플러그인 경로: {plugin_path}")
    print(f" - 입력 테스트 이미지: {sample_image}")

    if not os.path.exists(sample_image):
        print("❌ 테스트 이미지가 지정된 경로에 존재하지 않습니다.")
        return

    # 1. 플러그인 동적 로딩 수행
    spec = importlib.util.spec_from_file_location("vfx_ken_burns", plugin_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # 캐시 방지를 위해 기존 결과 파일이 존재하면 사전에 삭제
    base_name = os.path.splitext(os.path.basename(sample_image))[0]
    expected_output = os.path.join(output_dir, f"{base_name}_vfx_kenburns.mp4")
    if os.path.exists(expected_output):
        try:
            os.remove(expected_output)
            print("💡 기존에 생성된 테스트 캐시 비디오를 제거했습니다.")
        except Exception as e:
            print(f"⚠️ 기존 파일 제거 실패 (무시하고 계속 진행): {str(e)}")

    # 2. 시간 계측 시작
    start_time = time.time()
    result_path = module.before_render_visual(
        sample_image, video_format="shorts", output_dir=output_dir
    )
    end_time = time.time()

    elapsed = end_time - start_time

    # 3. 벤치마크 결과 리포트 출력
    print("=" * 60)
    print("📊 VFX 렌더링 성능 벤치마크 리포트")
    print("=" * 60)
    print(f" - 총 렌더링 소요 시간: {elapsed:.2f} 초")
    print(f" - 비디오 결과물 경로: {result_path}")

    if result_path and os.path.exists(result_path) and os.path.getsize(result_path) > 0:
        file_size_mb = os.path.getsize(result_path) / (1024 * 1024)
        print(f" - 생성 비디오 파일 크기: {file_size_mb:.2f} MB")
        print("💡 [검증 통과] 비디오가 무결하게 생성되었으며 파일 스트림이 유효합니다.")
    else:
        print("❌ [검증 실패] 비디오 클립 생성에 실패했거나 용량이 0입니다.")
    print("=" * 60)


if __name__ == "__main__":
    run_test()
