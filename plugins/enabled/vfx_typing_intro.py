# -*- coding: utf-8 -*-
"""
루비아 기술연구소 제4연구소 (VFX/인트로 텍스트 모션 Sandbox)
동적 타이핑 인트로 VFX 플러그인 (Ver 1.0 - Pillow + OpenCV Hybrid)

본 모듈은:
1) 정지 이미지를 켄번즈(Ken Burns) 줌인 비디오 클립으로 1차 렌더링하고,
2) 비디오의 초반 6초 분량에 대해 채널명 타이핑(Typewriter) 효과 및 부제목 페이드인 모션을 프레임별로 합성하여 최종 반환합니다.
"""

import os
import cv2
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def apply_artist_signature(image_path, channel_key, video_format):
    """
    [영상템플릿1] 우측 하단 예술 작가 서명 표준 적용
    정지 이미지의 우측 하단 안전 영역에 필기체(georgiabi.ttf)로 Aura 서명을 은은하게 합성합니다.
    """
    if channel_key != "aura":
        return image_path  # Aura 채널일 때만 서명 적용

    try:
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size
        
        # 폰트 로드 (georgiabi.ttf)
        font_path = r"C:\Windows\Fonts\georgiabi.ttf"
        if not os.path.exists(font_path):
            font_path = r"C:\Windows\Fonts\ariali.ttf" # Fallback Italic
            
        try:
            # 8시간 대형 렌더링 고려 폰트 크기 동적 조율
            font_sz = int(45 if video_format == "longform" else 35)
            font = ImageFont.truetype(font_path, font_sz)
        except Exception:
            font = ImageFont.load_default()

        # 서명 레이어 생성
        txt_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        signature_text = "Aura"
        
        # 텍스트 크기 획득
        try:
            l_left, l_top, l_right, l_bottom = draw.textbbox((0, 0), signature_text, font=font)
            text_w = l_right - l_left
            text_h = l_bottom - l_top
        except Exception:
            text_w = len(signature_text) * 20
            text_h = 40

        # 우측 하단 안전 영역 (우측 80px, 하단 80px 여백 안쪽)
        x = width - text_w - 80
        y = height - text_h - 80
        
        # 어두운 적갈색(RGB: 139, 34, 34) + 불투명도 60%(Alpha: 160)
        draw.text((x, y), signature_text, fill=(139, 34, 34, 160), font=font)
        
        composed = Image.alpha_composite(img, txt_layer).convert("RGB")
        
        # 원본을 훼손하지 않기 위해 새로운 경로로 저장
        dir_name = os.path.dirname(image_path)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        signed_path = os.path.join(dir_name, f"{base_name}_signed.jpg")
        composed.save(signed_path, "JPEG", quality=95)
        print(f"🎨 [VFX Artist Signature] '{signature_text}' 서명 이미지 합성 성공 -> {signed_path}")
        return signed_path
    except Exception as e:
        print(f"⚠️ [VFX Artist Signature Exception] 서명 합성 실패 (Bypass 폴백): {e}")
        return image_path

def before_render_visual(visual_path, video_format="shorts", output_dir=None, **kwargs):
    """
    [R&D 훅] 비주얼 자산 렌더링 전 전처리 훅
    정지 이미지를 켄번즈 줌인 비디오 클립으로 핫스왑하고, 그 위에 타이핑 인트로 효과를 합성합니다.
    """
    # 이미 동영상이거나 GIF인 경우 처리를 생략하고 즉시 반환
    if visual_path.lower().endswith((".mp4", ".mkv", ".avi", ".mov", ".gif")):
        return visual_path

    if not os.path.exists(visual_path):
        print(f"⚠️ [VFX Typing Intro] 이미지 파일이 존재하지 않습니다: {visual_path}")
        return visual_path

    # 우측 하단 예술 작가 서명 합성
    channel_key = kwargs.get("channel_key", "rubia").lower()
    visual_path = apply_artist_signature(visual_path, channel_key, video_format)

    # 플레이리스트 모드 혹은 롱폼 제작 시에만 작동하도록 안전 가드 설정 (기획서에 명시)
    # (일반 숏폼에서는 켄번즈 줌인만 적용되도록 하고, 플레이리스트 빌드 및 롱폼 시 타이핑 효과 합성)
    # vfx_mode가 'typing_intro'로 지정되었거나, 플레이리스트 모드로 호출된 경우 기동
    vfx_mode = kwargs.get("vfx_mode", "kenburns")
    is_playlist = kwargs.get("is_playlist", False)
    intro_text_effect = kwargs.get("intro_text_effect", "none")
    
    if vfx_mode != "typing_intro" and intro_text_effect != "typewriter" and not is_playlist:
        # 타이핑 효과가 아닐 경우, 기본 켄번즈 줌인 플러그인을 호출하여 원본 줌인 비디오 클립을 얻습니다.
        try:
            from plugins.enabled.vfx_ken_burns import before_render_visual as get_ken_burns
            return get_ken_burns(visual_path, video_format=video_format, output_dir=output_dir, **kwargs)
        except Exception as e:
            print(f"⚠️ [VFX Typing Intro] 켄번즈 플러그인 로드 실패: {e}")
            return visual_path

    # 출력 경로 결정
    out_dir = output_dir or os.path.dirname(visual_path) or os.getcwd()
    base_name = os.path.splitext(os.path.basename(visual_path))[0]
    final_output_path = os.path.join(out_dir, f"{base_name}_vfx_typing_intro.mp4")

    # 가디아 보안 검증 대응을 위한 드라이브 소문자 보정
    if final_output_path and len(final_output_path) > 1 and final_output_path[1] == ':':
        final_output_path = final_output_path[0].lower() + final_output_path[1:]

    # 캐시 비디오가 이미 존재한다면 재사용
    if os.path.exists(final_output_path) and os.path.getsize(final_output_path) > 0:
        print(f"🔌 [VFX Typing Intro] 이미 캐싱된 타이핑 인트로 클립을 재사용합니다: {final_output_path}")
        return final_output_path

    # 1. 배경 비디오 클립 획득 (슬로우 줌 루프 또는 기본 켄번즈)
    vfx_skill = kwargs.get("vfx_skill")
    if vfx_skill == "vfx_slow_zoom_loop":
        print("🔌 [VFX Typing Intro] 1단계: 슬로우 줌 루프 배경 비디오 클립 생성을 시작합니다.")
        try:
            from plugins.enabled.vfx_slow_zoom_loop import before_render_visual as get_slow_zoom
            sz_kwargs = kwargs.copy()
            # 💡 [한글 주석] 중첩 호출 시 무한 양보가 발생하지 않도록 intro_text_effect를 None으로 제거하여 호출합니다.
            sz_kwargs["intro_text_effect"] = None
            bg_video_path = get_slow_zoom(visual_path, video_format=video_format, output_dir=out_dir, **sz_kwargs)
        except Exception as e:
            print(f"❌ [VFX Typing Intro] 슬로우 줌 루프 배경 획득 중 크래시 발생: {e}")
            return visual_path
    else:
        print("🔌 [VFX Typing Intro] 1단계: 켄번즈 줌인 배경 비디오 클립 생성을 시작합니다.")
        try:
            from plugins.enabled.vfx_ken_burns import before_render_visual as get_ken_burns
            kb_kwargs = kwargs.copy()
            # 💡 [한글 주석] 지터 현상 제거: FFmpeg zoompan 필터의 떨림 버그를 차단하기 위해, 초고화질 지터리스 줌인(lanczos) 엔진으로 기동을 고정합니다.
            kb_kwargs["vfx_mode"] = "lanczos"
            bg_video_path = get_ken_burns(visual_path, video_format=video_format, output_dir=out_dir, **kb_kwargs)
        except Exception as e:
            print(f"❌ [VFX Typing Intro] 켄번즈 배경 획득 중 크래시 발생: {e}")
            return visual_path

    if bg_video_path == visual_path or not os.path.exists(bg_video_path):
        print("❌ [VFX Typing Intro] 배경 비디오 생성이 취소 또는 실패하여 정지 이미지를 폴백 사용합니다.")
        return visual_path

    # 2. OpenCV를 통한 프레임 합성 개시 (6초 타이핑 텍스트 합성)
    print(f"🔌 [VFX Typing Intro] 2단계: 텍스트 모션 합성 렌더링 개시 -> {final_output_path}")
    start_time = time.time()

    # 채널별 타이핑 텍스트 및 상세 파라미터 매핑
    channel_key = kwargs.get("channel_key", "rubia").lower()
    
    # 채널 정보에 따른 메인 텍스트 결정
    if channel_key == "aura":
        main_text = "Aura Serenity Wellness"
        sub_text = "Premium Healing & Ambient Music Space"
    elif channel_key == "rubia":
        main_text = "Rubia Lofi Room"
        sub_text = "Cozy Greenhouse & Daily Chill Beats"
    elif channel_key == "smartagetech":
        main_text = "SmartAgeTech Guide"
        sub_text = "Practical AI & Digital Tech for Seniors"
    else:
        main_text = "Wellness Sound Archive"
        sub_text = "Deep Focus BGM & Wellness Lounge"

    # 비디오 규격별 해상도 결정
    if video_format == "longform":
        width, height = 1920, 1080
    else:
        width, height = 1080, 1920

    # 폰트 로드 (가디아 폰트 안전 가드)
    font_candidates = [
        r"C:\1인기업\Apps\유튜브에이전트\outputs\RubiaHybrid.ttf",
        r"c:\1인기업\Apps\1.유튜브에이전트\outputs\RubiaHybrid.ttf",
        r"C:\Windows\Fonts\malgun.ttf",  # 맑은 고딕
        r"C:\Windows\Fonts\arial.ttf"
    ]
    
    main_font = None
    sub_font = None
    
    for f_path in font_candidates:
        if os.path.exists(f_path):
            try:
                # 롱폼 및 숏폼별 폰트 크기 가변화
                main_sz = int(72 if video_format == "longform" else 48)
                sub_sz = int(32 if video_format == "longform" else 24)
                main_font = ImageFont.truetype(f_path, main_sz)
                sub_font = ImageFont.truetype(f_path, sub_sz)
                print(f"🔤 [VFX Typing Intro] 사용 폰트 감지 성공: {f_path}")
                break
            except Exception as fe:
                print(f"⚠️ 폰트 파일 읽기 시도 중 경고: {fe}")

    if not main_font:
        main_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        print("⚠️ [VFX Typing Intro] 디폴트 기본 시스템 폰트로 폴백합니다.")

    # 비디오 캡처 객체 오픈
    cap = cv2.VideoCapture(bg_video_path)
    if not cap.isOpened():
        print(f"❌ [VFX Typing Intro] 배경 비디오 오픈 실패: {bg_video_path}")
        return bg_video_path

    # 원본 비디오 정보 획득
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # 윈도우 환경 전용 코덱 세팅 (mp4v 가 장치 호환성 및 데드락 면에서 가장 안전)
    # Pyrefly 정적 분석기의 cv2 모듈 바인딩 컴파일 오류 오탐지를 방지하기 위해 type ignore 처리합니다.
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # type: ignore
    out_video = cv2.VideoWriter(final_output_path, fourcc, fps, (width, height))

    # 타이핑 모션 진행 구간 (0초 ~ 6초)
    intro_duration_sec = 6
    # fps와 intro_duration_sec가 이미 int 타입이므로, 불필요한 int() 캐스팅 경고를 예방하기 위해 직접 곱셈 연산으로 수정합니다.
    intro_frames = fps * intro_duration_sec

    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 입력 해상도가 타겟 해상도와 다를 수 있으므로 리사이즈 처리
        if frame.shape[1] != width or frame.shape[0] != height:
            frame = cv2.resize(frame, (width, height))

        # 인트로 6초 구간에 대해서만 텍스트 오버레이 적용
        if frame_idx < intro_frames:
            # OpenCV BGR -> Pillow RGBA 변환
            frame_rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            
            # 리사이즈 및 켄번즈 효과 동화 (비주얼 프레임 매끄러운 바인딩을 위해 원본 복제 후 오버레이)
            pil_img = Image.fromarray(frame_rgba)
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            # --- 텍스트 연출 물리 공식 연산 ---
            # 1. 메인 타이틀 타이핑 진행율 (0초 ~ 3.5초에 타이핑 완료)
            typing_duration_frames = int(fps * 3.5)
            if frame_idx < typing_duration_frames:
                progress = frame_idx / typing_duration_frames
                char_count = int(len(main_text) * progress)
            else:
                char_count = len(main_text)
            
            char_count = max(0, min(char_count, len(main_text)))
            display_main = main_text[:char_count]

            # 우측 커서 깜빡임 효과 (2.0Hz 주파수 사인파)
            show_cursor = int(frame_idx / (fps / 4.0)) % 2 == 0
            if show_cursor and frame_idx < int(fps * 4.5):
                display_main += " |"

            # 2. 서브 타이틀 페이드인 (3.0초 ~ 4.8초에 서서히 피어오름)
            sub_fade_start = int(fps * 3.0)
            sub_fade_duration = int(fps * 1.8)
            sub_alpha = 0
            if frame_idx >= sub_fade_start:
                sub_progress = (frame_idx - sub_fade_start) / sub_fade_duration
                sub_alpha = int(255 * min(1.0, sub_progress))

            # 3. 전체 텍스트 페이드아웃 (5.0초 ~ 6.0초에 0으로 수렴)
            fadeout_start = int(fps * 5.0)
            fadeout_duration = int(fps * 1.0)
            text_alpha = 255
            if frame_idx >= fadeout_start:
                fadeout_progress = (frame_idx - fadeout_start) / fadeout_duration
                text_alpha = int(255 * (1.0 - min(1.0, fadeout_progress)))
                sub_alpha = int(sub_alpha * (1.0 - min(1.0, fadeout_progress)))

            # --- 드로잉 연산 (시인성 가딩을 위해 소프트 섀도 그라디언트 및 폰트 아웃라인 탑재) ---
            # 메인 타이틀 좌표 연산 (가로 세로 중앙 정렬)
            try:
                l_left, l_top, l_right, l_bottom = draw.textbbox((0, 0), display_main, font=main_font)
                m_w = l_right - l_left
                m_h = l_bottom - l_top
            except Exception:
                # 💡 [한글 설명] Pillow 10+ 버전에서 ImageDraw.textsize가 제거되었으므로,
                # 예외 발생 시 ImageFont.getbbox 또는 글자 수 수동 계산 방식으로 안전하게 우회(Fallback) 처리합니다.
                try:
                    if main_font is not None:
                        l_left, l_top, l_right, l_bottom = main_font.getbbox(display_main)
                        m_w = l_right - l_left
                        m_h = l_bottom - l_top
                    else:
                        m_w = len(display_main) * 15
                        m_h = 30
                except Exception:
                    m_w = len(display_main) * 15
                    m_h = 30

            main_x = (width - m_w) // 2
            main_y = (height - m_h) // 2 - int(40 if video_format == "longform" else 60)

            # 서브 타이틀 좌표 연산
            try:
                s_left, s_top, s_right, s_bottom = draw.textbbox((0, 0), sub_text, font=sub_font)
                s_w = s_right - s_left
                s_h = s_bottom - s_top
            except Exception:
                try:
                    if sub_font is not None:
                        s_left, s_top, s_right, s_bottom = sub_font.getbbox(sub_text)
                        s_w = s_right - s_left
                        s_h = s_bottom - s_top
                    else:
                        s_w = len(sub_text) * 10
                        s_h = 20
                except Exception:
                    s_w = len(sub_text) * 10
                    s_h = 20

            sub_x = (width - s_w) // 2
            sub_y = main_y + m_h + int(50 if video_format == "longform" else 80)

            # 텍스트가 완전히 투명해지지 않은 경우 드로잉 수행
            if text_alpha > 0:
                # 💡 [한글 설명] 시인성 확보를 위해 글자 뒤에 어두운 반투명 그림자 오버레이를 넓게 덮습니다.
                # 명도차를 확보하여 배경 이미지가 밝아도 텍스트가 명확히 감지되도록 방어합니다.
                shadow_y1 = main_y - 40
                shadow_y2 = sub_y + s_h + 40
                draw.rectangle(
                    [(0, shadow_y1), (width, shadow_y2)],
                    fill=(0, 0, 0, int(110 * (text_alpha / 255.0)))
                )

                # 메인 타이틀 그리기 (화이트 본문 + 연한 블랙 테두리 그림자)
                # 그림자
                draw.text((main_x + 2, main_y + 2), display_main, fill=(0, 0, 0, text_alpha), font=main_font)
                # 본문
                draw.text((main_x, main_y), display_main, fill=(255, 255, 255, text_alpha), font=main_font)

            if sub_alpha > 0:
                # 서브 타이틀 그리기 (파스텔 톤 옐로우 본문 + 연한 블랙 그림자)
                # 그림자
                draw.text((sub_x + 1, sub_y + 1), sub_text, fill=(0, 0, 0, sub_alpha), font=sub_font)
                # 본문
                draw.text((sub_x, sub_y), sub_text, fill=(255, 238, 173, sub_alpha), font=sub_font)

            # 프레임 합성 완료 후 OpenCV BGR 포맷으로 다시 원복하여 출력 라이터에 기록
            composed = Image.alpha_composite(pil_img, overlay)
            frame = cv2.cvtColor(np.array(composed), cv2.COLOR_RGBA2BGR)

        out_video.write(frame)
        frame_idx += 1

    # 자원 반환
    cap.release()
    out_video.release()
    
    elapsed = time.time() - start_time
    print(f"🔌 [VFX Typing Intro] 인트로 타이핑 모션 합성 성공! ({elapsed:.2f}초 소요, 경로: {final_output_path})")
    return final_output_path
