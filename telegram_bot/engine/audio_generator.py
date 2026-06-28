# -*- coding: utf-8 -*-
import os
import math
import subprocess
from dotenv import load_dotenv
import imageio_ffmpeg

# FFmpeg 바이너리 경로 획득
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

# google-genai 라이브러리 임포트 (클라우드 작곡 전용)
try:
    from google import genai
    from google.genai import types
except ImportError:
    pass


def loop_audio(input_path, target_duration_sec, output_path):
    """
    [안전 장치] 입력 오디오 파일을 목표 재생 시간(초)만큼 루핑하여 연장합니다.
    - 재인코딩이 없는 스트림 복사(-c copy) 방식을 사용하여 음질 저하를 원천 방지하고 초고속으로 처리합니다.
    """
    # 1분(60초) 단위로 대략적인 루프 횟수 계산 (안전 마진 확보)
    loop_count = math.ceil(target_duration_sec / 60.0) - 1
    if loop_count < 0:
        loop_count = 0

    cmd = [
        FFMPEG_PATH,
        "-y",
        "-stream_loop",
        str(loop_count),
        "-i",
        input_path,
        "-to",
        str(target_duration_sec),
        "-c",
        "copy",
        output_path,
    ]

    print(
        f"🎵 [Audio Generator] 오디오 루핑 시작 ({target_duration_sec}초 목표, 루프 횟수: {loop_count})"
    )
    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore"
    )
    if result.returncode != 0:
        raise RuntimeError(f"오디오 루핑 실패:\n{result.stderr}")
    return output_path


def concat_audio_files(audio_paths, output_path):
    """
    [플레이리스트 병합] 여러 개의 오디오 파일을 순차적으로 병합하여 하나의 롱폼 플레이리스트 음원을 만듭니다.
    - FFmpeg Concat demuxer 방식을 사용하여 재인코딩 없이 무손실로 초고속 결합합니다.
    """
    if not audio_paths:
        raise ValueError("병합할 오디오 파일 리스트가 비어 있습니다.")

    # demuxer에 전달할 임시 텍스트 파일 생성
    temp_dir = os.path.dirname(output_path) or os.getcwd()
    list_file_path = os.path.join(temp_dir, f"concat_list_{os.getpid()}.txt")

    try:
        with open(list_file_path, "w", encoding="utf-8") as f:
            for path in audio_paths:
                # 윈도우 경로 구분자 정규화 및 포맷팅
                safe_path = os.path.abspath(path).replace("\\", "/")
                f.write(f"file '{safe_path}'\n")

        cmd = [
            FFMPEG_PATH,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_file_path,
            "-c",
            "copy",
            output_path,
        ]

        print(
            f"🎵 [Audio Generator] 플레이리스트 음원 Concat 병합 개시 (총 {len(audio_paths)}개 세그먼트)"
        )
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )
        if result.returncode != 0:
            raise RuntimeError(f"오디오 병합 인코딩 실패:\n{result.stderr}")

    finally:
        # 사용이 완료된 임시 목록 파일 안전 제거
        if os.path.exists(list_file_path):
            try:
                os.remove(list_file_path)
            except Exception:
                pass

    return output_path


def get_audio_prompt(channel_key, duration_min=1):
    """채널 성격 및 타겟 재생 시간에 매칭되는 AI 작곡 지시어(Prompt)를 구성합니다."""
    # 30초 등 1분 미만의 재생 시간인 경우 초 단위로 프롬프트에 표현
    if duration_min < 1.0:
        duration_str = f"{int(duration_min * 60)} seconds long"
    else:
        duration_str = (
            f"{duration_min} minute long"
            if duration_min == 1
            else f"{duration_min} minutes long"
        )

    # 1. Sound Lab DB에서 승인된 템플릿(APPROVED) 랜덤 추출 시도
    import os, json, random

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    db_path = os.path.join(project_root, "database", "sound_templates.json")

    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                db = json.load(f)

            category = "lofi" if channel_key in ["rubia", "taipei"] else "wellness"
            # 채널 카테고리가 일치하거나 범용이고 승인된 템플릿 필터링
            approved_templates = [
                t
                for t in db
                if t.get("status") == "APPROVED"
                and (
                    category in t.get("channel", "").lower()
                    or channel_key in t.get("channel", "").lower()
                    or "all" in t.get("channel", "").lower()
                )
            ]

            if approved_templates:
                selected = random.choice(approved_templates)
                prompt_base = selected.get("prompt", "")
                print(f"🎵 [Sound Lab] 승인된 커스텀 템플릿 적용 완료: '{selected.get('title')}'")
                return f"{prompt_base} {duration_str}."
        except Exception as e:
            print(f"⚠️ [Sound Lab] 템플릿 DB 로드 중 오류 발생: {e}")
            pass

    # 2. 승인된 템플릿이 없을 경우 안전한 하드코딩 폴백 반환
    print("🎵 [Sound Lab] 사용 가능한 템플릿이 없어 기본 폴백 프롬프트를 사용합니다.")
    if channel_key in ["rubia", "taipei"]:
        return (
            "Lo-fi hip-hop, chill beat, medium-slow-tempo instrumental. "
            "Dusty, tape-saturated drum loop with warm Rhodes electric piano chords. "
            "Featured instruments: muted jazz guitar, subtle vinyl crackle and rain sound texture. "
            "Mood: nostalgic, cozy, relaxing, deep focus, like studying or coding in a warm greenhouse garden with rain. "
            f"No vocals. Steady groove. {duration_str}. BPM: 70-75."
        )
    else:
        # aura, smartage 등 웰니스 채널
        return (
            "Ambient, ethereal, slow-tempo meditative instrumental. "
            "Soft warm pad synthesizer with long sustained reverb. "
            "Layered with gentle bamboo flute, distant ocean wave sounds, and singing bowl. "
            "Mood: deeply calming, transcendent, peaceful, healing, 432Hz vibe. "
            f"No vocals. Continuous flow. {duration_str}. BPM: 55-60."
        )


def generate_lyria3_music(
    channel_key, output_filename, duration_min=1, prompt_override=None
):
    """
    구글 최신 음악 모델 Lyria 3 Pro를 사용하여 오디오를 생성합니다.
    - duration_min에 근거해 가변 길이 음원 작곡을 요청하며,
      롱폼(5분 이상)일 경우 분할 작곡 후 병합하는 플레이리스트 빌드 엔진을 가동합니다.
    """
    load_dotenv(r"c:\1인기업\Apps\유튜브에이전트\.env")

    api_key_env = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEYS")
    if not api_key_env:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

    api_key = api_key_env.split(",")[0].strip()
    client = genai.Client(api_key=api_key)

    # ⚙️ [5분 이상 롱폼 플레이리스트 대응]
    # - 최소 3분짜리 음원을 여러 개 생성(3+3+3+3=12분 등)한 후, concat하여 결합합니다.
    if duration_min >= 5:
        segment_duration = 3
        num_segments = math.ceil(duration_min / segment_duration)
        print(
            f"🎵 [Audio Generator] {duration_min}분 롱폼 플레이리스트 빌드 가동 - {segment_duration}분 음원 {num_segments}개 순차 생성 돌입"
        )

        base_dir = os.path.dirname(output_filename) or os.getcwd()
        base_name = os.path.splitext(os.path.basename(output_filename))[0]

        segment_files = []
        for i in range(num_segments):
            seg_filename = os.path.join(base_dir, f"{base_name}_part_{i+1}.mp3")
            try:
                # 3분 세그먼트 생성 재귀 호출
                seg_path = generate_lyria3_music(
                    channel_key, seg_filename, duration_min=segment_duration
                )
                segment_files.append(seg_path)
            except Exception as se:
                # 🚨 [Fallback 금지 규칙] 에셋 생성 실패 시 기존 파일 재사용을 전면 금지합니다.
                # 프로세스를 즉시 중단하고 상위 핸들러에 에러를 전파합니다.
                print(
                    f"🚨 [Audio Generator] 플레이리스트 파트 {i+1} 생성 실패 ({se}). 기존 파일 폴백 없이 즉시 중단합니다."
                )
                # 이미 생성된 세그먼트 임시 파일 정리
                for cleanup_f in segment_files:
                    if os.path.exists(cleanup_f) and "_part_" in cleanup_f:
                        try:
                            os.remove(cleanup_f)
                        except Exception:
                            pass
                raise RuntimeError(
                    f"🚨 [에셋 생성 실패] 플레이리스트 파트 {i+1}/{num_segments} 음원 생성 API 오류. "
                    f"기존 파일을 사용하지 않고 작업을 중단합니다. 원인: {se}"
                )

        # 생성된 복수 세그먼트 파일 일괄 결합
        merged_path = concat_audio_files(segment_files, output_filename)

        # 결합 완료 후 중간 임시 파트 파일 청소
        for f in segment_files:
            if f != output_filename and os.path.exists(f) and "_part_" in f:
                try:
                    os.remove(f)
                except Exception:
                    pass
        return merged_path

    # ⚙️ [단일 음원 생성 흐름: 1~3분]
    prompt = (
        prompt_override
        if prompt_override
        else get_audio_prompt(channel_key, duration_min)
    )
    model_id = "lyria-3-pro-preview"

    print(
        f"🎵 [Audio Generator] AI 작곡 시작 ({model_id}) - 채널: {channel_key}, 목표 시간: {duration_min}분"
    )

    api_output = output_filename + ".api.mp3"
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["AUDIO"]),
        )

        audio_saved = False
        if getattr(response, "candidates", None) and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content:
                for part in candidate.content.parts:
                    if hasattr(part, "inline_data") and part.inline_data is not None:
                        mime = getattr(part.inline_data, "mime_type", "")
                        if mime.startswith("audio/"):
                            if not api_output.endswith(".mp3") and "mpeg" in mime:
                                api_output = os.path.splitext(api_output)[0] + ".mp3"

                            with open(api_output, "wb") as f:
                                f.write(part.inline_data.data)
                            audio_saved = True
                            break

        if not audio_saved:
            raise RuntimeError("응답 객체에 유효한 inline_data 오디오 데이터가 포함되어 있지 않습니다.")

        # [품질 검증] 생성된 오디오 파일 크기가 비정상적으로 작은 경우 예외 유도
        # 1분 미만의 프리뷰 음원인 경우 검증 최소 파일 크기를 80KB(80,000 바이트)로 완화합니다.
        file_size = os.path.getsize(api_output)
        min_size_limit = 80000 if duration_min < 1.0 else 200000
        if file_size < min_size_limit:
            raise RuntimeError(
                f"생성된 음원 파일 크기가 비정상적으로 작습니다 ({file_size} bytes). 주파수 붕괴 의심."
            )

        print(
            f"✅ [Audio Generator] AI 작곡 1차 완료. 목표 길이({duration_min}분) 연장/루프 여부 체크 중..."
        )

        # 실제 요청한 시간(duration_min * 60)만큼 안전하게 연장 루핑하여 최종 파일로 이관
        target_sec = duration_min * 60
        loop_audio(api_output, target_sec, output_filename)

        # 💵 [비용 최적화] Lyria 3 Pro API 생성 비용 실시간 산출 로깅
        try:
            from telegram_bot.config import COST_LYRIA_SECOND
            from telegram_bot.utils.cost_logger import log_api_cost

            cost = target_sec * COST_LYRIA_SECOND
            log_api_cost(
                "Lyria 3 Pro (Audio)",
                cost,
                f"Duration: {target_sec}s, File: {os.path.basename(output_filename)}",
            )
        except Exception as cle:
            print(f"⚠️ [Cost Logging Fail] 비용 로깅 실패: {cle}")

    except Exception as e:
        # 🚨 [Fallback 금지 규칙] 음원 생성 실패 시 기존 파일 재사용을 전면 금지합니다.
        # 프로세스를 즉시 중단하고 상위 핸들러에 에러를 전파합니다.
        print(f"🚨 [Audio Generator] AI 작곡 실패 또는 제약 검출 ({e}). 기존 파일 폴백 없이 즉시 중단합니다.")
        raise RuntimeError(
            f"🚨 [에셋 생성 실패] 음원 생성 API 응답 없음 또는 오류. " f"기존 파일을 사용하지 않고 작업을 중단합니다. 원인: {e}"
        )

    finally:
        # API 1차 저장 임시 파일 안전 정리
        if os.path.exists(api_output):
            try:
                os.remove(api_output)
            except Exception:
                pass

    return output_filename
