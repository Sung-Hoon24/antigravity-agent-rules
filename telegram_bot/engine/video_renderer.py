import os
import sys
import glob
import subprocess
import importlib.util
import json
import imageio_ffmpeg
from typing import Optional


# FFmpeg 바이너리 경로 획득
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()


def get_pc_spec():
    """
    [코디아 자원 최적화] 로컬지식 폴더 내 pc_system_spec.json 파일을 안전하게 로드합니다.
    파일이 없거나 형식이 깨진 경우 기본 CPU 렌더링 스펙을 반환합니다.
    """
    # 스크립트 실행 경로 기준 동적 조립 (AGENTS.md 규칙 4번 준수)
    engine_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(engine_dir))
    spec_path = os.path.join(project_root, "로컬지식", "pc_system_spec.json")

    default_spec = {"hw_acceleration_supported": False, "ffmpeg_codec": "libx264"}

    if not os.path.exists(spec_path):
        return default_spec

    try:
        with open(spec_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            # 외장 GPU 리스트에서 하드웨어 가속 지원 여부 추출
            gpu_list = data.get("graphics_cards", [])
            for gpu in gpu_list:
                if gpu.get("hw_acceleration_supported") and gpu.get("ffmpeg_codec"):
                    return {
                        "hw_acceleration_supported": True,
                        "ffmpeg_codec": gpu.get("ffmpeg_codec"),
                    }
        return default_spec
    except Exception as e:
        print(f"⚠️ [Spec Loader] PC 사양 JSON 파싱 에러 (CPU 폴백 적용): {e}")
        return default_spec


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
            subs = [
                "Close your eyes and breathe deeply.",
                "Feel the warm energy flowing through you.",
                "Release all your stress and focus on the sound.",
            ]
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


def validate_planning_json(data: dict) -> None:
    """
    [R&D Validation Gate]
    렌더링에 주입될 기획안 JSON 데이터의 무결성을 검증합니다.
    필수 메타데이터가 결손되거나 쓰레기 데이터가 감지되면 즉각 Exception을 발생시켜 빌드를 폐기(Discard)합니다.
    """
    # 💡 [한글 주석] 이 게이트는 렌더링 파이프라인의 입구에서 통신 스키마가 규격에 맞는지
    # 최종적으로 철저하게 검사하며, 단 하나의 필수 필드라도 누락되면 렌더링에 진입하지 못하게 차단합니다.
    if not data:
        raise ValueError("데이터 무결성 오류: 기획 데이터가 존재하지 않습니다.")

    if not isinstance(data, dict):
        raise ValueError("데이터 무결성 오류: 기획 데이터가 올바른 JSON(dict) 형식이 아닙니다.")

    required_fields = ["concept", "youtube_title", "captions", "playlist"]
    for field in required_fields:
        if field not in data or not data.get(field):
            raise ValueError(f"데이터 무결성 오류: 필수 메타데이터 필드 '{field}'가 유실되었습니다.")

    # 자막 리스트 정밀 검증
    captions = data.get("captions", [])
    if not isinstance(captions, list) or len(captions) == 0:
        raise ValueError("데이터 무결성 오류: 자막 대본(captions) 리스트가 비어 있거나 올바르지 않습니다.")

    for idx, cap in enumerate(captions):
        if not isinstance(cap, dict) or "time_code" not in cap or "text" not in cap:
            raise ValueError(
                f"데이터 무결성 오류: {idx}번째 자막의 필수 항목(time_code, text)이 유실되었습니다."
            )
        if not cap.get("text"):
            raise ValueError(f"데이터 무결성 오류: {idx}번째 자막 내용이 비어 있습니다.")

    # 플레이리스트 정밀 검증
    playlist = data.get("playlist", [])
    if not isinstance(playlist, list) or len(playlist) == 0:
        raise ValueError("데이터 무결성 오류: 플레이리스트(playlist) 구성안이 비어 있거나 올바르지 않습니다.")


def parse_script_to_ass(
    planning_data, ass_path, video_format="shorts", custom_style=None, script_text=None
):
    """
    [R&D Lab] 기획안 데이터(JSON dict 또는 줄글 text)에서 자막 지시자 부분을 추출하여 ASS 파일로 저장합니다.
    """
    if script_text is not None:
        planning_data = script_text

    sub_events = []  # List of tuples: (start_sec, end_sec, text)

    # 1. 기획안 데이터가 dict(JSON 구조)인 경우 직접 파싱
    if isinstance(planning_data, dict):
        raw_captions = planning_data.get("captions", [])
        temp_subs = []
        for cap in raw_captions:
            if not isinstance(cap, dict):
                continue
            tc = cap.get("time_code", "00:00")
            text = cap.get("text", "")
            if text:
                try:
                    parts = tc.split(":")
                    if len(parts) == 2:
                        seconds = float(int(parts[0]) * 60 + int(parts[1]))
                    elif len(parts) == 3:
                        seconds = float(
                            int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                        )
                    else:
                        seconds = 0.0
                except Exception:
                    seconds = 0.0
                temp_subs.append({"start": seconds, "text": text})

        # 시간순 정렬
        temp_subs.sort(key=lambda x: x["start"])

        # end_sec 산출 및 sub_events 구성
        for i, sub in enumerate(temp_subs):
            start_sec = sub["start"]
            if i < len(temp_subs) - 1:
                next_start = temp_subs[i + 1]["start"]
                end_sec = min(start_sec + 8.0, next_start - 1.0)
                if end_sec <= start_sec:
                    end_sec = start_sec + 3.0
            else:
                end_sec = start_sec + 8.0
            sub_events.append((start_sec, end_sec, sub["text"]))

    # 2. 기획안 데이터가 str(줄글 텍스트)인 경우 기존 파서(하위 호환) 작동
    else:
        script_str = str(planning_data or "")
        lines = script_str.split("\n")
        subs = []

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

        # [방어적 프로그래밍] 자막 누락 시 기본 자막 세팅
        if not subs:
            channel_key = "rubia"
            normalized_path = ass_path.replace("\\", "/").lower()
            for key in ["aura", "taipei", "rubia", "smartage"]:
                if f"/{key}" in normalized_path or key in os.path.basename(
                    normalized_path
                ):
                    channel_key = key
                    break

            if channel_key == "aura":
                subs = [
                    "Close your eyes and breathe in.",
                    "Feel the warm energy flowing.",
                    "Let go of all your tension.",
                ]
            elif channel_key in ["rubia", "taipei"]:
                subs = [
                    "Close your eyes and breathe deeply.",
                    "Feel the warm energy flowing through you.",
                    "Release all your stress and focus on the sound.",
                ]
            elif channel_key == "smartage":
                subs = [
                    "눈을 감고 천천히 숨을 쉬어보세요.",
                    "편안한 음악과 함께 하루를 정리합니다.",
                    "오늘 하루도 정말 수고하셨습니다.",
                ]
            else:
                subs = [
                    "Close your eyes and breathe.",
                    "Let the music carry you gently.",
                ]

        start_sec = 2.0
        for text in subs:
            end_sec = start_sec + 8.0
            sub_events.append((start_sec, end_sec, text))
            start_sec = end_sec + 3.0

    # 3. 비디오 규격에 따른 자막 폰트 크기 및 여백 (기본값 설정)
    if video_format == "longform":
        play_res_x = 1920
        play_res_y = 1080
        default_font_size = 45
        default_margin_v = 80
    else:
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

    # ASS 파일 쓰기
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

        for start_sec, end_sec, text in sub_events:
            start_str = format_ass_time(start_sec)
            end_str = format_ass_time(end_sec)
            text_clean = str(text).replace("**", "").replace("\n", "\\N")
            f.write(
                f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{{\\fad(1500,1500)}}{text_clean}\n"
            )


# 💡 [개선] 음원의 실제 재생 길이를 ffmpeg로 측정하여 렌더링 길이에 반영합니다.
# ffprobe가 별도 설치되지 않은 환경에서도 ffmpeg -i 출력의 Duration 필드를 파싱하여 안전하게 동작합니다.
def get_audio_duration(audio_path):
    """ffmpeg -i 출력에서 음원의 실제 길이(초)를 반환합니다. 실패 시 None."""
    import re as _re

    try:
        result = subprocess.run(
            [FFMPEG_PATH, "-i", audio_path, "-hide_banner"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=10,
        )
        # ffmpeg -i 는 입력 파일 정보를 stderr에 출력하고 returncode=1로 끝남 (정상 동작)
        match = _re.search(r"Duration:\s*(\d+):(\d+):(\d+)\.(\d+)", result.stderr)
        if match:
            h, m, s, cs = match.groups()
            total = int(h) * 3600 + int(m) * 60 + int(s) + int(cs) / 100
            print(f"📏 [Duration] 음원 실제 길이 측정 완료: {total:.2f}초 ({audio_path})")
            return total
        return None
    except Exception as e:
        print(f"⚠️ [Duration] 음원 길이 측정 실패 (폴백 적용): {e}")
        return None


def render_video(
    visual_path,
    audio_path,
    planning_data,
    output_path,
    video_format="shorts",
    custom_style=None,
    script_text=None,
    fast_gate=False,
    channel_key=None,
    progress_path=None,
):
    """
    FFmpeg를 이용하여 이미지/비디오 배경, 오디오, 텍스트 자막을 합성하여 MP4 영상을 렌더링합니다.
    - video_format: 'shorts' (세로형 9:16, 1080x1920) 또는 'longform' (가로형 16:9, 1920x1080)
    - visual_path가 동영상(.mp4 등)일 경우 무한 루프 처리하여 백그라운드 영상으로 활용합니다.
    - fast_gate: 테스트/검증 모드 활성화 스위치. True인 경우 비디오 인코딩 길이를 3초로 강제 차단하여 속도를 단축합니다.
    """
    # 🛡️ [가디아 비상 제동 장치] Safe Mode 활성화 시 렌더링 강제 잠금
    from telegram_bot.nlp.rag_validator import check_safe_mode_lock

    check_safe_mode_lock()

    # 💡 [한글 주석] 대표님의 포그라운드 작업 환경 버벅임을 완벽 차단하기 위해
    # psutil을 통해 백그라운드 렌더링 프로세스의 CPU 우선순위를 IDLE(최하) 상태로 낮춥니다.
    try:
        import psutil  # type: ignore[import-untyped]

        p = psutil.Process(os.getpid())
        if sys.platform == "win32":
            p.nice(psutil.IDLE_PRIORITY_CLASS)
            print("🛡️ [Resource Control] 프로세스 CPU 우선순위를 IDLE_PRIORITY_CLASS로 조정했습니다.")
    except Exception as priority_err:
        print(f"⚠️ [Resource Control] 프로세스 우선순위 조정 실패 (비침습적 유지): {priority_err}")

    import time

    start_t = time.time()

    try:
        if script_text is not None:
            planning_data = script_text

        # 💡 [한글 설명 - 데이터 무결성 최우선 Gate]
        # 기획 데이터(JSON)가 렌더러로 넘어오는 인터페이스 구간에서 2차 검증을 강제 수행합니다.
        # 쓰레기 데이터는 렌더링에 진입하기 전에 이 단계에서 원천 차단(Discard)됩니다.
        if isinstance(planning_data, dict):
            validate_planning_json(planning_data)
            print("🛡️ [Validation Gate] 렌더러 진입부 JSON 데이터 무결성 검증 통과 완료.")
        else:
            try:
                lines = str(planning_data or "").split("\n")
                temp_captions = []
                for line in lines:
                    if "자막:" in line or "字幕:" in line:
                        txt = line.split(":", 1)[1].strip()
                        if txt:
                            temp_captions.append({"time_code": "00:00", "text": txt})

                mock_json = {
                    "concept": "Legacy String Fallback Concept",
                    "youtube_title": "Legacy Title",
                    "youtube_description": "Legacy Description",
                    "youtube_tags": [],
                    "playlist": [{"title": "Legacy Track", "duration_sec": 60}],
                    "captions": temp_captions,
                }
                validate_planning_json(mock_json)
                print("🛡️ [Validation Gate] 레거시 줄글 텍스트에 대한 구조화 임시 검증 통과.")
            except Exception as mock_err:
                raise ValueError(
                    f"데이터 무결성 오류: 수신된 기획 데이터가 명세화된 규격(JSON)이 아니며 구조화에 실패했습니다. (사유: {mock_err})"
                )

        # 1. ASS 자막 파일 생성
        base_dir = os.path.dirname(output_path) or os.getcwd()
        base_name = os.path.splitext(os.path.basename(output_path))[0]
        ass_path = os.path.join(base_dir, f"{base_name}.ass")

        parse_script_to_ass(
            planning_data,
            ass_path,
            video_format=video_format,
            custom_style=custom_style,
        )

        safe_ass = ass_path.replace("\\", "/").replace(":", "\\:")

        # 💡 [한글 주석] 대표님 지침 준수: 이퀄라이저(비주얼라이저)는 R&D 튜닝 완료 전까지 메인 렌더링에 절대 영향을 주지 않도록 False로 완벽 고정 차단합니다.
        use_visualizer = False

        # 💡 [한글 주석] 기획안 JSON 데이터(planning_data)에서 vfx_mode 및 vfx_skill 연출 파라미터를 안전하게 추출하여 플러그인에 전달합니다.
        vfx_mode = "kenburns"
        vfx_skill = None
        if isinstance(planning_data, dict):
            vfx_mode = planning_data.get("vfx_mode", "kenburns")
            vfx_skill = planning_data.get("vfx_skill")

        # 🚨 [R&D Lab 플러그인 훅 가동]
        # 💡 [한글 주석] 플러그인들이 기획안 템플릿의 세부 연출 설정(intro_text_effect 등)을 꺼내 쓸 수 있도록 planning_data 전체를 안전하게 풀어헤쳐 전달합니다.
        plugin_kwargs = {
            "video_format": video_format,
            "output_dir": base_dir,
            "vfx_mode": vfx_mode,
            "vfx_skill": vfx_skill,
            "use_equalizer": use_visualizer,
            "audio_path": audio_path,
        }
        if isinstance(planning_data, dict):
            plugin_kwargs.update(planning_data)

        processed_visual_path = load_and_apply_plugins(
            "before_render_visual",
            visual_path,
            **plugin_kwargs
        )
        if processed_visual_path and processed_visual_path != visual_path:
            print(
                f"🔌 [VFX 핫스왑] 비주얼 자산이 플러그인 처리 결과물로 대체되었습니다:\n -> {processed_visual_path}"
            )
            visual_path = processed_visual_path

        # 2. visual 소스 타입 판별
        is_video = visual_path.lower().endswith(
            (".mp4", ".mkv", ".avi", ".mov", ".gif")
        )

        filter_complex = None
        vf = None

        if use_visualizer:
            print("🎛️ [Visualizer] 오디오 반응형 showwaves 필터 합성을 준비합니다.")
            if video_format == "longform":
                filter_complex = (
                    f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,split=2[orig_raw][blurred_raw];"
                    f"[blurred_raw]gblur=sigma=20[blurred];"
                    f"[orig_raw]format=rgba,fade=t=in:st=0:d=5:alpha=1[orig_fade];"
                    f"[blurred][orig_fade]overlay=format=auto[base];"
                    f"[base]subtitles='{safe_ass}'[subbed];"
                    f"[subbed]hue='H=0.02*sin(2*PI*t/30)'[vid_base];"
                    f"[1:a]showwaves=s=1920x150:mode=line:colors=white:scale=sqrt,format=rgba[wave];"
                    f"[vid_base][wave]overlay=x=0:y=900:format=auto"
                )
            else:
                filter_complex = (
                    f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,split=2[orig_raw][blurred_raw];"
                    f"[blurred_raw]gblur=sigma=20[blurred];"
                    f"[orig_raw]format=rgba,fade=t=in:st=0:d=5:alpha=1[orig_fade];"
                    f"[blurred][orig_fade]overlay=format=auto[base];"
                    f"[base]subtitles='{safe_ass}'[subbed];"
                    f"[subbed]hue='H=0.02*sin(2*PI*t/30)'[vid_base];"
                    f"[1:a]showwaves=s=1080x200:mode=line:colors=white:scale=sqrt,format=rgba[wave];"
                    f"[vid_base][wave]overlay=x=0:y=1500:format=auto"
                )
        else:
            print("⚠️ [Visualizer Fallback] 음원 파일 누락으로 비주얼라이저를 배제한 기본 필터를 적용합니다.")
            if video_format == "longform":
                vf = (
                    "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,split=2[orig_raw][blurred_raw];"
                    "[blurred_raw]gblur=sigma=20[blurred];"
                    "[orig_raw]format=rgba,fade=t=in:st=0:d=5:alpha=1[orig_fade];"
                    f"[blurred][orig_fade]overlay=format=auto[base];"
                    f"[base]subtitles='{safe_ass}'[subbed];"
                    f"[subbed]hue='H=0.02*sin(2*PI*t/30)'"
                )
            else:
                vf = (
                    "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,split=2[orig_raw][blurred_raw];"
                    "[blurred_raw]gblur=sigma=20[blurred];"
                    "[orig_raw]format=rgba,fade=t=in:st=0:d=5:alpha=1[orig_fade];"
                    f"[blurred][orig_fade]overlay=format=auto[base];"
                    f"[base]subtitles='{safe_ass}'[subbed];"
                    f"[subbed]hue='H=0.02*sin(2*PI*t/30)'"
                )

        # 4. FFmpeg 명령어 동적 조립
        cmd = [FFMPEG_PATH, "-y"]
        if progress_path:
            cmd.extend(["-progress", progress_path])

        if is_video:
            cmd.extend(["-stream_loop", "-1", "-i", visual_path])
        else:
            cmd.extend(["-loop", "1", "-i", visual_path])

        cmd.extend(["-i", audio_path])

        # 💡 [한글 주석] pc_system_spec.json을 로드하여 NVIDIA GPU 가속(NVENC)이 지원되는 경우
        # libx264 대신 h264_nvenc 인코더를 동적 적용합니다. (CPU 부하 90% 이상 세이브)
        pc_spec = get_pc_spec()
        is_nvenc = (
            pc_spec.get("hw_acceleration_supported")
            and pc_spec.get("ffmpeg_codec") == "h264_nvenc"
        )

        if is_nvenc:
            print("🚀 [GPU Acceleration] NVIDIA NVENC 가속 렌더링을 시작합니다 (-c:v h264_nvenc).")
            if use_visualizer:
                # 💡 [한글 주석] filter_complex가 None이 아님을 보장하여 Pyrefly 타입 가드를 통과시킵니다.
                assert filter_complex is not None
                cmd.extend(["-filter_complex", filter_complex])
            else:
                # 💡 [한글 주석] vf가 None이 아님을 보장하여 Pyrefly 타입 가드를 통과시킵니다.
                assert vf is not None
                cmd.extend(["-vf", vf])
            cmd.extend(
                [
                    "-c:v",
                    "h264_nvenc",
                    "-preset",
                    "fast",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    "-pix_fmt",
                    "yuv420p",
                ]
            )
        else:
            print("💻 [CPU Rendering] CPU 기반 인코딩을 적용합니다 (-c:v libx264).")
            if use_visualizer:
                # 💡 [한글 주석] filter_complex가 None이 아님을 보장하여 Pyrefly 타입 가드를 통과시킵니다.
                assert filter_complex is not None
                cmd.extend(["-filter_complex", filter_complex])
            else:
                # 💡 [한글 주석] vf가 None이 아님을 보장하여 Pyrefly 타입 가드를 통과시킵니다.
                assert vf is not None
                cmd.extend(["-vf", vf])
            cmd.extend(
                [
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

        if fast_gate:
            cmd.extend(["-t", "3.0"])
            print("⚡ [Fast-Gate] 테스트 모드로 인해 비디오 인코딩 길이를 3.0초로 제한합니다.")
        elif video_format == "shorts":
            # 💡 [개선] 음원 실제 길이를 측정하여 숏폼 한도(60초) 이하면 음원 길이로, 초과면 전체 길이로 렌더링합니다.
            audio_dur = get_audio_duration(audio_path)
            if audio_dur is not None and audio_dur <= 59.5:
                # 음원이 60초 이하 → 유튜브 Shorts 규격 내에서 음원 전체 길이로 렌더링
                cmd.extend(["-t", str(round(audio_dur, 2))])
                print(
                    f"📏 [Duration] 음원 길이({audio_dur:.1f}초) ≤ 60초 → Shorts 규격 내 음원 전체 렌더링"
                )
            else:
                # 음원이 60초 초과 또는 측정 실패 → 음원 전체 길이를 살려서 렌더링 (일반 영상이 됨)
                cmd.extend(["-shortest"])
                if audio_dur:
                    print(
                        f"📏 [Duration] 음원 길이({audio_dur:.1f}초) > 60초 → 전체 길이 렌더링 (Shorts 한도 초과)"
                    )
                else:
                    print("📏 [Duration] 음원 길이 측정 실패 → -shortest 폴백 적용")
        else:
            cmd.extend(["-shortest"])

        cmd.append(output_path)

        print(
            f"🎬 [Video Renderer] FFmpeg 렌더링 시작 ({video_format} 모드, 비디오여부: {is_video}, FastGate: {fast_gate}): {output_path}"
        )
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )

        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg 렌더링 실패:\n{result.stderr}")

        # 가디아 24/7 렌더링 성능 지연 감시
        elapsed = time.time() - start_t
        if elapsed > 180.0:
            try:
                from telegram_bot.nlp.rag_validator import send_telegram_alert

                send_telegram_alert(
                    f"⚠️ *[렌더러 물리 엔진 지연 감지]*\n"
                    f"• **출력 경로**: `{output_path}`\n"
                    f"• **소요 시간**: `{elapsed:.2f}초` (기준값 180초 초과)\n"
                    f"• **상태**: 렌더링은 완료되었으나 성능 지연 현상이 감지되었습니다."
                )
            except Exception as inner_err:
                print(f"⚠️ [Guardia Alert Fail] 경보 송출 실패: {inner_err}")

        print(f"✅ [Video Renderer] 렌더링 완료: {output_path} (소요시간: {elapsed:.2f}초)")
        return output_path

    except Exception as e:
        # 가디아 24/7 렌더링 에러 감시
        try:
            from telegram_bot.nlp.rag_validator import send_telegram_alert

            send_telegram_alert(
                f"🚨 *[렌더러 물리 엔진 오류 감지]*\n"
                f"• **출력 경로**: `{output_path}`\n"
                f"• **에러 메시지**: `{str(e)}`\n"
                f"• **상태**: 렌더링 실패 및 작업 Discard 처리."
            )
        except Exception as inner_err:
            print(f"⚠️ [Guardia Alert Fail] 경보 송출 실패: {inner_err}")
        raise e


def render_shorts(image_path, audio_path, script_text, output_path, fast_gate=False):
    """
    [하위 호환성용] 기존 숏폼 전용 렌더러 인터페이스로, 내부적으로 일반화된 render_video를 호출합니다.
    """
    return render_video(
        visual_path=image_path,
        audio_path=audio_path,
        planning_data=script_text,
        output_path=output_path,
        video_format="shorts",
        fast_gate=fast_gate,
    )


def render_videos_parallel(tasks: list, max_workers: Optional[int] = None) -> list:
    """
    [코디아 병렬화 최적화]
    ThreadPoolExecutor를 활용하여 다중 영상 렌더링 요청을 동시 병렬 처리(Parallel Processing)합니다.
    tasks: 딕셔너리 리스트. 예: [{'visual_path': ..., 'audio_path': ..., 'planning_data': ..., 'output_path': ...}]
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import multiprocessing

    if max_workers is None:
        # 💡 [한글 주석] 64GB RAM 사양은 충분하나 GPU VRAM(6GB) 제한 및 윈도우 프리징 예방을 위해
        # 동시 영상 렌더링 최대 병렬 스레드 수를 3개로 엄격하게 상한 제한합니다.
        max_workers = min(3, max(1, multiprocessing.cpu_count() - 1))

    results = []
    print(
        f"🚀 [Parallel Processing] {len(tasks)}개 영상 작업을 {max_workers}개 스레드로 동시 병렬 인코딩합니다."
    )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                render_video,
                task["visual_path"],
                task["audio_path"],
                task["planning_data"],
                task["output_path"],
                task.get("video_format", "shorts"),
                task.get("custom_style"),
                task.get("script_text"),
                task.get("fast_gate", False),
            ): task
            for task in tasks
        }

        for future in as_completed(futures):
            task = futures[future]
            try:
                out_path = future.result()
                results.append(
                    {"status": "success", "task": task, "output_path": out_path}
                )
            except Exception as exc:
                print(f"❌ [Parallel Processing Error] 병렬 인코딩 실패: {exc}")
                results.append({"status": "failed", "task": task, "error": str(exc)})

    return results
