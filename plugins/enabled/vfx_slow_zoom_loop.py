# -*- coding: utf-8 -*-
"""
루비아 기술연구소 제1연구소 (VFX/시각 효과 Sandbox)
Slow Zoom Loop (줌인 15초 + 줌아웃 15초 무한 루프) VFX 플러그인 (Ver 2.0 - OpenCV Sub-pixel Lanczos4)

본 모듈은 정지 이미지를 실수형 부동소수점 수준에서 정밀하게 줌인/줌아웃 반복 루프하여 
툭툭 끊김(Stutter)과 일렁임(Jitter)을 100% 제거한 30초짜리(750프레임, 25fps) 비디오 클립으로 렌더링합니다.
"""

import os
import cv2
import numpy as np

def before_render_visual(visual_path, video_format="shorts", output_dir=None, vfx_skill=None, **kwargs):
    """
    [R&D 훅] 비주얼 자산 렌더링 전 전처리 훅
    정지 이미지를 80초짜리(2000프레임, 25fps) OpenCV 서브픽셀 Lanczos4 줌인/줌아웃 루프 비디오 클립(.mp4)으로 핫스왑합니다.
    """
    # 💡 [한글 주석] 대표님이 명시적으로 본 슬로우 줌 루프 스킬을 선택한 경우에만 동작하도록 제한하여 자원 낭비를 방어합니다.
    if vfx_skill != "vfx_slow_zoom_loop":
        return visual_path

    # 💡 [한글 주석] 타이핑 인트로 효과가 예정된 경우, 본 모듈이 단독 인코딩하지 않고 타이핑 인트로 모듈에 정지 이미지를 양보하여 한꺼번에 합성하게 합니다.
    if kwargs.get("intro_text_effect") == "typewriter":
        return visual_path

    # 이미 동영상이거나 GIF인 경우 줌팬 처리를 생략하고 즉시 반환
    if visual_path.lower().endswith((".mp4", ".mkv", ".avi", ".mov", ".gif")):
        return visual_path

    if not os.path.exists(visual_path):
        print(f"⚠️ [VFX Slow Zoom Loop] 이미지 파일이 존재하지 않습니다: {visual_path}")
        return visual_path

    # 출력 경로 결정
    out_dir = output_dir or os.path.dirname(visual_path) or os.getcwd()
    base_name = os.path.splitext(os.path.basename(visual_path))[0]
    vfx_output_path = os.path.join(out_dir, f"{base_name}_vfx_slow_zoom_loop.mp4")

    # [한글 설명 - 가디아 보안 검증 통과용 드라이브 문자 보정]
    # validate_safe_path 함수가 소문자 c드라이브를 기준으로 샌드박스를 대소문자 매칭하므로,
    # 드라이브 문자를 소문자 c로 일치시켜 경로 이탈 에러를 방지합니다.
    if vfx_output_path and len(vfx_output_path) > 1 and vfx_output_path[1] == ':':
        vfx_output_path = vfx_output_path[0].lower() + vfx_output_path[1:]

    # 이미 동일한 캐시 VFX 비디오 클립이 렌더링되어 있다면 재활용하여 인코딩 타임을 절약합니다.
    if os.path.exists(vfx_output_path) and os.path.getsize(vfx_output_path) > 0:
        print(f"🔌 [VFX Slow Zoom Loop] 이미 존재해 캐싱된 VFX 클립을 재사용합니다: {vfx_output_path}")
        return vfx_output_path

    # 비디오 규격별 해상도 설정
    if video_format == "longform":
        width, height = 1920, 1080
    else:
        width, height = 1080, 1920

    print(f"🔌 [VFX Slow Zoom Loop] OpenCV 서브픽셀 Lanczos4 줌 루프 렌더링 가동:\n -> {vfx_output_path}")

    try:
        # 1. 이미지 로드 및 중앙 비율 크롭 -> 2배 고화질 캔버스 구축
        img = cv2.imread(visual_path)
        if img is None:
            print("⚠️ [VFX Slow Zoom Loop] 이미지 로드 실패. 원본 이미지를 폴백 사용합니다.")
            return visual_path

        img_h, img_w, _ = img.shape
        target_aspect = float(width) / float(height)
        
        if img_w / img_h > target_aspect:
            # 가로가 더 긴 경우 가로 크롭
            new_w = int(img_h * target_aspect)
            x_offset = (img_w - new_w) // 2
            cropped_img = img[:, x_offset:x_offset+new_w]
        else:
            # 세로가 더 긴 경우 세로 크롭
            new_h = int(img_w / target_aspect)
            y_offset = (img_h - new_h) // 2
            cropped_img = img[y_offset:y_offset+new_h, :]

        # 2배 해상도 캔버스 확보 (화질 보전용 Lanczos4 사용)
        canvas_w, canvas_h = width * 2, height * 2
        canvas = cv2.resize(cropped_img, (canvas_w, canvas_h), interpolation=cv2.INTER_LANCZOS4)
        center_x = canvas_w / 2.0
        center_y = canvas_h / 2.0

        # 💡 [한글 주석] 40초 줌인 + 40초 줌아웃 (총 80초, 2000프레임) 렌더링 규격 적용
        fps = 25
        duration_sec = 80
        total_frames = duration_sec * fps
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(vfx_output_path, fourcc, fps, (width, height))

        # 2. 2000프레임 줌인/줌아웃 대칭 루프 렌더링
        for n in range(total_frames):
            # 💡 [한글 주석] 40초 줌인, 40초 줌아웃의 줌 루프 공식 반영
            # p = 0 ~ 1999 프레임의 루프 인덱스 (n/2.0을 취해 0.0 ~ 999.5)
            # 피크 지점은 40초(p=500.0)이며, 기존 30초 렌더링 시의 줌아웃 한계 비율(최대 1.088배)을 유지하도록 
            # 0.000176 스케일 팩터를 적용해 초속 줌 속도를 균일하고 느리게(Super-Slow) 낮추어 흔들림을 원천 차단합니다.
            p = n / 2.0
            z = 1.0 + (500.0 - abs(500.0 - p)) * 0.000176
            
            # 아핀 변환을 활용한 실수형(Float) 서브픽셀 Lanczos4 줌인 보간
            M = cv2.getRotationMatrix2D((center_x, center_y), 0, z)
            zoomed = cv2.warpAffine(canvas, M, (canvas_w, canvas_h), flags=cv2.INTER_LANCZOS4)
            
            # 최종 타겟 해상도로 다운스케일링
            final_frame = cv2.resize(zoomed, (width, height), interpolation=cv2.INTER_LANCZOS4)
            video_writer.write(final_frame)

        video_writer.release()
        print("🔌 [VFX Slow Zoom Loop] 성공적으로 동적 서브픽셀 줌 루프 비디오 클립을 생성했습니다.")
        return vfx_output_path
        
    except Exception as e:
        print(f"❌ [VFX Slow Zoom Loop 오류] 예외 발생, 원본 이미지를 폴백 사용합니다: {str(e)}")
        return visual_path
