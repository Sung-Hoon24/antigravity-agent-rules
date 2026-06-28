import os
import sys
import glob
import subprocess
import importlib.util
import imageio_ffmpeg

# FFmpeg 바이너리 경로 획득
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()


def load_and_apply_plugins(event_name, *args, **kwargs):
    """
    [R&D Lab 핫스왑 플러그인 로더 - USB 포트 아키텍처]
    plugins/enabled/ 디렉토리의 모든 파이썬 플러그인을 스캔하여
    지정된 hook(event_name)에 해당하는 동작을 동적으로 실행합니다.
    완전 격리(try-except)를 통해 플러그인 에러가 메인 렌더링에 파급되지 않도록 보장합니다.
    """
    # 프로젝트 루트 기준의 plugins/enabled 절대 경로 획득
    engine_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(engine_dir))
    plugins_dir = os.path.join(project_root, "plugins", "enabled")

    current_value = args[0] if args else None

    if not os.path.exists(plugins_dir):
        return current_value

    plugin_files = glob.glob(os.path.join(plugins_dir, "*.py"))

    for plugin_file in plugin_files:
        if os.path.basename(plugin_file).startswith("__"):
            continue
        try:
            # 플러그인 모듈 동적 로드
            module_name = os.path.splitext(os.path.basename(plugin_file))[0]
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)
            if not spec or not spec.loader:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 이벤트에 대응하는 훅 함수 호출
            if hasattr(module, event_name):
                hook_func = getattr(module, event_name)
                print(
                    f"🔌 [R&D 플러그인 로더] '{module_name}' 모듈의 '{event_name}' 훅 적용을 시작합니다."
                )
                # 체이닝 방식으로 가공된 결과값을 누적 전달
                current_value = hook_func(current_value, *args[1:], **kwargs)
        except Exception as e:
            # [가디아 보안 규칙 및 방어적 프로그래밍] 플러그인 충돌 격리
            print(
                f"❌ [R&D 플러그인 오류] '{plugin_file}' 가동 중 에러 발생 (메인 렌더링 격리 차단): {str(e)}",
                file=sys.stderr,
            )

    return current_value


def parse_script_to_srt(script_text, srt_path):
    """
    [하위 호환성 유지용] 라비아 기획안 텍스트에서 다국어 자막 지시자 부분을 추출하여 SRT 파일로 저장합니다.
    """
    lines = script_text.split("\n")
    subs = []

    # 1. 다국어 자막 파싱 진행 (방어적 매칭 기법)
    for line in lines:
        matched_prefix = None
        for prefix in [
            "자막:",
            "자막：",
            "字幕:",
            "字幕：",
            "Subtitle:",
            "Subtitle：",
            "Sub:",
            "Sub：",
            "[자막]",
            "[字幕]",
        ]:
            if line.strip().startswith(prefix):
                matched_prefix = prefix
                break

        if not matched_prefix:
            for prefix in ["자막:", "자막：", "字幕:", "字幕：", "Subtitle:", "Subtitle："]:
                if prefix in line:
                    matched_prefix = prefix
                    break

        if matched_prefix:
            parts = line.split(matched_prefix)
            if len(parts) > 1:
                text = parts[1].strip().strip('"').strip("'").strip()
                if "/" in text:
                    parts_lang = text.split("/", 1)
                    kor = parts_lang[0].strip()
                    other_lang = parts_lang[1].strip().strip("(").strip(")")
                    text = f"{kor}\n{other_lang}"
                if text:
                    subs.append(text)

    if not subs:
        channel_key = "rubia"
        normalized_path = srt_path.replace("\\", "/").lower()
        for key in ["aura", "taipei", "rubia", "smartage"]:
            if f"/{key}" in normalized_path or key in os.path.basename(normalized_path):
                channel_key = key
                break

        if channel_key == "aura":
            subs = [
                "Close your eyes and breathe in.",
                "Feel the warm energy flowing.",
                "Let go of all your tension.",
            ]
        elif channel_key in ["rubia", "taipei"]:
            subs = ["閉上眼睛，深呼吸。", "感受溫暖的能量在流動。", "放下所有的疲憊與焦慮。"]
        elif channel_key == "smartage":
            subs = [
                "눈을 감고 천천히 숨을 쉬어보세요.",
                "편안한 음악과 함께 하루를 정리합니다.",
                "오늘 하루도 정말 수고하셨습니다.",
            ]
        else:
            subs = ["Close your eyes and breathe.", "Let the music carry you gently."]

    def format_srt_time(seconds):
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        msecs = int((seconds - int(seconds)) * 1000)
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{msecs:03d}"

    with open(srt_path, "w", encoding="utf-8") as f:
        start_sec = 2.0
        for i, text in enumerate(subs):
            end_sec = start_sec + 8.0
            start_str = format_srt_time(start_sec)
            end_str = format_srt_time(end_sec)
            f.write(f"{i+1}\n")
            f.write(f"{start_str} --> {end_str}\n")
            f.write(f"{text}\n\n")
            start_sec = end_sec + 3.0


def parse_color_to_ass(color_str):
    """
    한글/영문 색상명 또는 헥스코드를 ASS 색상 코드 형식(&H00BBGGRR)으로 변환합니다.
    """
    if not color_str:
        return None

    color_map = {
        "흰색": "&H00FFFFFF",
        "white": "&H00FFFFFF",
        "노란색": "&H0000FFFF",
        "yellow": "&H0000FFFF",
        "빨간색": "&H000000FF",
        "red": "&H000000FF",
        "파란색": "&H00FF0000",
        "blue": "&H00FF0000",
        "초록색": "&H0000FF00",
        "green": "&H0000FF00",
        "검은색": "&H00000000",
        "black": "&H00000000",
        "분홍색": "&H00FFC0CB",
        "pink": "&H00FFC0CB",
        "주황색": "&H0000A5FF",
        "orange": "&H0000A5FF",
        "보라색": "&H00800080",
        "purple": "&H00800080",
        "회색": "&H00808080",
        "gray": "&H00808080",
    }

    clean_color = color_str.strip().lower()
    if clean_color in color_map:
        return color_map[clean_color]

    # Hex 코드 매칭 및 BGR 순서로 변환
    import re

    hex_match = re.match(r"#?([0-9a-fA-F]{6})", clean_color)
    if hex_match:
        hex_val = hex_match.group(1)
        r = hex_val[0:2]
        g = hex_val[2:4]
        b = hex_val[4:6]
        return f"&H00{b}{g}{r}".upper()

    return None


def parse_script_to_ass(
    script_text, ass_path, video_format="shorts", custom_style=None
):
    """
    라비아 기획안 텍스트에서 다국어 자막 지시자 부분을 추출하여 ASS 파일로 저장합니다.
    """
    lines = script_text.split("\n")
    subs = []

    # 1. 다국어 자막 파싱 진행
    for line in lines:
        matched_prefix = None
        for prefix in [
            "자막:",
            "자막：",
            "字幕:",
            "字幕：",
            "Subtitle:",
            "Subtitle：",
            "Sub:",
            "Sub：",
            "[자막]",
            "[字幕]",
        ]:
            if line.strip().startswith(prefix):
                matched_prefix = prefix
                break

        if not matched_prefix:
            for prefix in ["자막:", "자막：", "字幕:", "字幕：", "Subtitle:", "Subtitle："]:
                if prefix in line:
                    matched_prefix = prefix
                    break

        if matched_prefix:
            parts = line.split(matched_prefix)
            if len(parts) > 1:
                text = parts[1].strip().strip('"').strip("'").strip()
                if "/" in text:
                    parts_lang = text.split("/", 1)
                    kor = parts_lang[0].strip()
                    other_lang = parts_lang[1].strip().strip("(").strip(")")
                    text = f"{kor}\\N{other_lang}"
                if text:
                    subs.append(text)

    # 2. [방어적 프로그래밍] 자막 누락 시 기본 자막 세팅
    if not subs:
        channel_key = "rubia"
        normalized_path = ass_path.replace("\\", "/").lower()
        for key in ["aura", "taipei", "rubia", "smartage"]:
            if f"/{key}" in normalized_path or key in os.path.basename(normalized_path):
                channel_key = key
                break

        if channel_key == "aura":
            subs = [
                "Close your eyes and breathe in.",
                "Feel the warm energy flowing.",
                "Let go of all your tension.",
            ]
        elif channel_key in ["rubia", "taipei"]:
            subs = ["閉上眼睛，深呼吸。", "感受溫暖的能量在流動。", "放下所有的疲憊與焦慮。"]
        elif channel_key == "smartage":
            subs = [
                "눈을 감고 천천히 숨을 쉬어보세요.",
                "편안한 음악과 함께 하루를 정리합니다.",
                "오늘 하루도 정말 수고하셨습니다.",
            ]
        else:
            subs = ["Close your eyes and breathe.", "Let the music carry you gently."]

    # 3. 비디오 규격에 따른 자막 폰트 크기 및 여백 (기본값 설정)
    if video_format == "longform":
        play_res_x = 1920
        play_res_y = 1080
        default_font_size = 45
        default_margin_v = 80
    else:
        # 쇼츠(9:16) 맞춤 폰트 대폭 확대 및 유튜브 UI 회피 마진 적용
        play_res_x = 1080
        play_res_y = 1920
        default_font_size = 80
        default_margin_v = 350

    default_font_name = "Malgun Gothic"
    default_color = "&H00FFFFFF"

    # custom_style 딕셔너리가 존재하면 오버라이드 적용
    style = custom_style or {}
    font_size = style.get("font_size") or default_font_size
    margin_v = style.get("margin_v") or default_margin_v
    font_name = style.get("font_name") or default_font_name
    border_style = style.get("border_style") or 1
    shadow = style.get("shadow") if "shadow" in style else 1

    primary_color_raw = style.get("primary_color")
    primary_color = (
        parse_color_to_ass(primary_color_raw) if primary_color_raw else default_color
    )
    if not primary_color:
        primary_color = default_color

    def format_ass_time(seconds):
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        csecs = int(round((seconds - int(seconds)) * 100))
        if csecs == 100:
            csecs = 0
            secs += 1
            if secs == 60:
                secs = 0
                mins += 1
                if mins == 60:
                    mins = 0
                    hrs += 1
        return f"{hrs}:{mins:02d}:{secs:02d}.{csecs:02d}"

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write("[Script Info]\n")
        f.write("Title: Rubia Lofi Subtitles\n")
        f.write("ScriptType: v4.00+\n")
        f.write("WrapStyle: 0\n")
        f.write(f"PlayResX: {play_res_x}\n")
        f.write(f"PlayResY: {play_res_y}\n")
        f.write("ScaledBorderAndShadow: yes\n\n")

        f.write("[V4+ Styles]\n")
        f.write(
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        )
        f.write(
            f"Style: Default,{font_name},{font_size},{primary_color},&H00000000,&H66000000,&H80000000,0,0,0,0,100,100,0,0,{border_style},2,{shadow},2,30,30,{margin_v},1\n\n"
        )

        f.write("[Events]\n")
        f.write(
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        )

        start_sec = 2.0
        for text in subs:
            end_sec = start_sec + 8.0

            start_str = format_ass_time(start_sec)
            end_str = format_ass_time(end_sec)

            # 마크다운 별표(**) 완벽 제거 및 줄바꿈 처리 적용
            text_clean = text.replace("**", "").replace("\n", "\\N")

            f.write(
                f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{{\\fad(1500,1500)}}{text_clean}\n"
            )

            start_sec = end_sec + 3.0


def render_video(
    visual_path,
    audio_path,
    script_text,
    output_path,
    video_format="shorts",
    custom_style=None,
):
    """
    FFmpeg를 이용하여 이미지/비디오 배경, 오디오, 텍스트 자막을 합성하여 MP4 영상을 렌더링합니다.
    - video_format: 'shorts' (세로형 9:16, 1080x1920) 또는 'longform' (가로형 16:9, 1920x1080)
    - visual_path가 동영상(.mp4 등)일 경우 무한 루프 처리하여 백그라운드 영상으로 활용합니다.
    """
    # 1. ASS 자막 파일 생성 (페이드 및 세부 폰트 제어가 가능한 고성능 포맷)
    base_dir = os.path.dirname(output_path) or os.getcwd()
    base_name = os.path.splitext(os.path.basename(output_path))[0]
    ass_path = os.path.join(base_dir, f"{base_name}.ass")

    parse_script_to_ass(
        script_text, ass_path, video_format=video_format, custom_style=custom_style
    )

    # FFmpeg 필터에 맞게 경로 이스케이프 처리 (윈도우 절대경로 처리)
    safe_ass = ass_path.replace("\\", "/").replace(":", "\\:")

    # 🚨 [R&D Lab 플러그인 훅 가동]
    # 비주얼 렌더링 전에 플러그인 훅을 통해 이미지를 동적 영상 클립(Ken Burns 등)으로 가공/핫스왑
    processed_visual_path = load_and_apply_plugins(
        "before_render_visual",
        visual_path,
        video_format=video_format,
        output_dir=base_dir,
    )
    if processed_visual_path and processed_visual_path != visual_path:
        print(f"🔌 [VFX 핫스왑] 비주얼 자산이 플러그인 처리 결과물로 대체되었습니다:\n -> {processed_visual_path}")
        visual_path = processed_visual_path

    # 2. visual 소스 타입 판별 (동영상인지 정지 이미지인지 확장자로 판별)
    is_video = visual_path.lower().endswith((".mp4", ".mkv", ".avi", ".mov", ".gif"))

    # 3. 비디오 포맷에 따른 필터 구성 (가로/세로 비율 및 도입부 습기 걷힘 디블러 VFX 추가)
    if video_format == "longform":
        # 16:9 가로형 규격 (1920x1080)
        vf = (
            "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,split=2[orig_raw][blurred_raw];"
            "[blurred_raw]gblur=sigma=20[blurred];"
            "[orig_raw]format=rgba,fade=t=in:st=0:d=5:alpha=1[orig_fade];"
            f"[blurred][orig_fade]overlay=format=auto[base];"
            f"[base]subtitles='{safe_ass}'"
        )
    else:
        # 9:16 세로형 규격 (1080x1920) - 기본값
        vf = (
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,split=2[orig_raw][blurred_raw];"
            "[blurred_raw]gblur=sigma=20[blurred];"
            "[orig_raw]format=rgba,fade=t=in:st=0:d=5:alpha=1[orig_fade];"
            f"[blurred][orig_fade]overlay=format=auto[base];"
            f"[base]subtitles='{safe_ass}'"
        )

    # 4. FFmpeg 명령어 동적 조립
    # - loop 1 (이미지) 혹은 stream_loop -1 (비디오) 처리
    cmd = [FFMPEG_PATH, "-y"]

    if is_video:
        # 비디오 루핑 옵션은 반드시 입력 파일(-i) 앞에 들어가야 동작함
        cmd.extend(["-stream_loop", "-1", "-i", visual_path])
    else:
        # 이미지 루핑
        cmd.extend(["-loop", "1", "-i", visual_path])

    # 오디오 입력 추가
    cmd.extend(["-i", audio_path])

    # 공통 렌더링 필터 및 오디오/비디오 인코딩 옵션 지정
    cmd.extend(
        [
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-pix_fmt",
            "yuv420p",
        ]
    )

    # 🚨 [유튜브 쇼츠 강제 인식 규격화]
    # 쇼츠(shorts) 규격일 경우 길이를 무조건 59.5초로 잘라 60초 초과 오류를 원천 차단합니다.
    if video_format == "shorts":
        cmd.extend(["-t", "59.5"])
    else:
        cmd.extend(["-shortest"])

    cmd.append(output_path)

    print(
        f"🎬 [Video Renderer] FFmpeg 렌더링 시작 ({video_format} 모드, 비디오여부: {is_video}): {output_path}"
    )
    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore"
    )

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg 렌더링 실패:\n{result.stderr}")

    print(f"✅ [Video Renderer] 렌더링 완료: {output_path}")
    return output_path


def render_shorts(image_path, audio_path, script_text, output_path):
    """
    [하위 호환성용] 기존 숏폼 전용 렌더러 인터페이스로, 내부적으로 일반화된 render_video를 호출합니다.
    """
    return render_video(
        visual_path=image_path,
        audio_path=audio_path,
        script_text=script_text,
        output_path=output_path,
        video_format="shorts",
    )
