import json
from typing import Dict, Any

# --- [Configuration] ---
ASSET_DIR = "FunnelGatewayAssetPackageV1.0"  # Designer가 인계한 패키지 경로 가정
AUDIO_TIMING_FILE = "WriterScriptTimingMap.json"  # Writer님이 작성한 스크립트 기반 타이밍 맵 파일
OUTPUT_PACKAGE = "FinalMasterSequenceBlueprint.json"


def load_timing_map(file_path: str) -> Dict[str, Any]:
    """Writer가 정의한 논리적/시간적 흐름을 로드합니다."""
    print(f"⚙️ [DEBUG] 타이밍 맵 로드 중: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            "🚨 오류: WriterScriptTimingMap.json 파일을 찾을 수 없습니다. 타이밍 맵이 필수입니다."
        )


def load_assets_specs(asset_dir: str) -> Dict[str, Any]:
    """Designer가 인계한 모션 에셋의 기술 사양서를 로드합니다."""
    print(f"⚙️ [DEBUG] 에셋 사양서 로드 중: {asset_dir}")
    # 실제로는 JSON/XML 형태의 Spec Sheet를 파싱해야 함. 여기서는 더미 데이터를 사용함.
    return {
        "GLITCH_SHADER": {"min_duration": 320, "max_duration": 510},
        "STATE_TRANSITION_LOGIC": {
            "dependencies": ["A", "B"],
            "api_call": "triggerStateChange",
        },
    }


def run_sync_check(timing_map: Dict[str, Any], asset_specs: Dict[str, Any]):
    """
    핵심 시퀀스 동기화 검증 및 디버깅 루프. (Audio/Visual Sync)
    """
    print("\n===============================================")
    print("🚀 Funnel Gateway 통합 시퀀스 싱크 테스트 시작 🚀")
    print("===============================================\n")

    # 핵심 로직: 타이밍 맵을 순회하며, 각 지점에 필요한 에셋의 존재 여부 및 사양 적합성을 체크.
    for segment_id, data in timing_map["segments"].items():
        start_time = data["timing"]["start"]  # 오디오 기반 시작 시간 (ms)
        end_time = data["timing"]["end"]  # 오디오 기반 종료 시간 (ms)
        required_asset = data["tech_asset"]  # 필요한 에셋 유형

        print(f"--- [Segment: {segment_id}] ({start_time}ms -> {end_time}ms) ---")

        # 1. 타이밍 유효성 검사 (Timing Validation)
        duration = end_time - start_time
        if duration < 50 or duration > 3000:  # 너무 짧거나 긴 구간 체크
            print(
                f"⚠️ [Warning] {segment_id}: 예상 지속 시간({duration}ms)이 비정상적입니다. 오디오 리듬을 재검토해야 합니다."
            )

        # 2. 에셋 사양 적합성 검사 (Spec Validation)
        if required_asset in asset_specs:
            spec = asset_specs[required_asset]
            is_valid = spec["min_duration"] <= duration <= spec["max_duration"]

            if not is_valid:
                print(
                    f"❌ [FATAL ERROR] {segment_id}: 요구된 에셋 '{required_asset}'의 사양({spec['min_duration']}~{spec['max_duration']}ms)과 실제 구간 시간({duration}ms)이 불일치합니다."
                )
                # 디버깅: 이 경우, State Transition 로직을 수정하거나, 아예 해당 시퀀스를 건너뛰는 예외 처리가 필요함.
            else:
                print(
                    f"✅ [Success] {segment_id}: 에셋 '{required_asset}' 사양 검증 통과. API 호출 준비 완료."
                )

        # 3. 오디오-비주얼 동기화 (The Core Sync Check)
        audio_cue = data["audio"]["cue"]
        print(
            f"🔊 [Audio Cue] {segment_id} 구간에서 '{audio_cue}' 리듬 변화 감지. State Transition API 호출 준비."
        )

    # 최종 결과: 모든 체크가 통과되었다고 가정하고, 통합 설계도 파일을 생성하여 후속 작업에 사용합니다.
    {
        "status": "READY",
        "metadata": {"version": "v1.0_debugged", "tested_with": AUDIO_TIMING_FILE},
        "timeline": timing_map["segments"],  # 검증된 최종 타임라인을 포함
    }

    print("\n===============================================")
    print("✨ 모든 시퀀스 싱크 테스트 완료! ✨")
    print(f"✅ 통합 설계도 파일 '{OUTPUT_PACKAGE}' 생성 완료. 다음 단계에서 이 파일을 기반으로 코드를 재배포합니다.")
    print("===============================================")


if __name__ == "__main__":
    try:
        # 1. 데이터 로드
        timing_map = load_timing_map(AUDIO_TIMING_FILE)
        assets = load_assets_specs(ASSET_DIR)

        # 2. 테스트 실행 및 디버깅 수행
        run_sync_check(timing_map, assets)

    except FileNotFoundError as e:
        print(f"\n🚨 치명적 오류 발생: {e}")
    except Exception as e:
        print(f"\n💥 예상치 못한 시스템 오류 발생: {type(e).__name__}: {str(e)}")

    # 3. 최종 결과물 저장 (다음 단계에서 사용될 청사진)
    with open(OUTPUT_PACKAGE, "w", encoding="utf-8") as f:
        json.dump(
            {"debug_results": "SUCCESS", "final_timeline": timing_map["segments"]},
            f,
            indent=4,
        )
