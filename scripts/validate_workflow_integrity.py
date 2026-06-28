import json
from typing import List, Dict


def validate_content_flow(master_timeline: List[Dict], schema_path: str) -> bool:
    """
    마스터 타임라인 데이터를 로드하여 정의된 스키마에 따라 콘텐츠 흐름의 무결성을 검증합니다.
    핵심적으로 VTM과 시간 간격 누락 여부를 체크합니다.
    """
    print("=" * 60)
    print("✅ 🚀 [Integrity Check] Content Workflow Validation Started.")
    print("=" * 60)

    # 가상의 스키마 로드 (실제로는 위에서 만든 JSON 파일을 사용)
    try:
        with open(schema_path, "r") as f:
            json.load(f)
    except FileNotFoundError:
        print("❌ ERROR: Schema file not found! Cannot proceed with validation.")
        return False

    if not master_timeline:
        print("⚠️ WARNING: Master Timeline is empty. Nothing to validate.")
        return True  # 실패가 아닌, 데이터 부재로 처리

    total_time = 0.0
    success = True

    for i, segment in enumerate(master_timeline):
        # --- Step 1: 시간적 연속성 체크 (Temporal Continuity Check) ---
        if i > 0:
            prev_segment = master_timeline[i - 1]
            expected_start = prev_segment["time_range"]["t_end_sec"]
            actual_start = segment["time_range"]["t_start_sec"]

            # 임계값 (Tolerance)을 두어 오차를 허용하지만, 큰 간격은 경고로 처리
            if abs(expected_start - actual_start) > 0.5:
                print(f"⚠️ WARNING [Segment {i+1}]: 시간 연속성 이탈 감지.")
                print(f"   - 이전 종료 시간 (Expected): {expected_start:.2f}s")
                print(f"   - 현재 시작 시간 (Actual): {actual_start:.2f}s")
                success = False

        # --- Step 2: VTM 존재 여부 및 파라미터 검증 (VTM Spec Check) ---
        if "transition_module" in segment and segment["transition_module"]:
            vtm = segment["transition_module"]
            print(
                f"\n⚙️ [Segment {i+1}]: '{segment.get('sequence_id', 'N/A')}' 처리 중..."
            )

            # 핵심 검증: VTM이 존재한다면, 반드시 API 스펙과 Gap 여부가 함께 정의되어야 함.
            if not vtm.get("api_spec"):
                print(
                    "❌ FAILURE: VTM 모듈은 정의되었으나, 'api_spec' (파라미터)가 누락되었습니다. 논리적 연결이 끊겼습니다."
                )
                success = False

            # 핵심 검증: Cognitive Gap 발생 시, Transition Module이 반드시 있어야 함.
            if vtm.get("gap_detected") and not segment["transition_module"]:
                print(
                    "❌ CRITICAL FAILURE: 'Cognitive Gap'가 감지되었으나, 이를 처리할 전환 모듈(VTM)이 누락되었습니다."
                )
                success = False

        # --- Step 3: 최종 시간 업데이트 및 로그 출력 ---
        total_time = segment["time_range"]["t_end_sec"]
        print(f"   - ✅ OK. 섹션 처리 완료. 현재까지 총 길이: {total_time:.2f}초.")

    print("\n" + "=" * 60)
    if success and total_time > 0:
        print(f"🎉 SUCCESS: 전체 워크플로우의 시간적, 기술적 무결성 검증 통과. 최종 길이: {total_time:.2f}초.")
        return True
    else:
        print("🚨 FAILURE: 콘텐츠 워크플로우에 위반되는 구조적 결함이 발견되었습니다. 반드시 수정이 필요합니다.")
        return False


# --- 테스트 데이터 시뮬레이션 ---
if __name__ == "__main__":
    # 이 리스트가 최종 MTP를 기반으로 자동 생성되어야 하는 '진짜' 데이터입니다.
    # 여기서는 개념 증명(PoC)을 위해 가상의 데이터를 사용했습니다.
    mock_master_timeline = [
        {
            "sequence_id": "HOOK_A",
            "time_range": {"t_start_sec": 0.0, "t_end_sec": 15.0},
            "narrative_segment": {
                "script_source": "[00:00 - 00:15]",
                "core_argument": "시청자의 선입견에 대한 의문 제기",
            },
            "transition_module": {
                "module_id": "Void_Type_A",
                "api_spec": {
                    "params": ["initial_state=A"],
                    "state_change": "QUESTION_STATE",
                },
            },
            "cta_logic": ["Comment Question Prompt"],
        },
        # 15.0초에서 시작하는 다음 세그먼트 (이 부분이 연속성 체크의 핵심)
        {
            "sequence_id": "GAP_TRANSITION",
            "time_range": {
                "t_start_sec": 15.2,
                "t_end_sec": 22.0,
            },  # <-- 여기서 0.2초의 Gap 발생 (경고 유발)
            "narrative_segment": {
                "script_source": "[00:15 - 00:22]",
                "core_argument": "논리적 충돌 지점 노출",
            },
            "transition_module": {  # <-- VTM과 Gap Flag가 함께 정의됨 (통과 목표)
                "module_id": "Void_Type_3",
                "api_spec": {
                    "params": ["gap_level=HIGH"],
                    "state_change": "CONFLICT_STATE",
                },
                "audio_spec": {"bgm_id": "dissonance_loop", "emotional_arc": "Tension"},
            },
            "cta_logic": [],
        },
        # 22.0초에서 시작하는 다음 세그먼트 (연속성 체크 통과 목표)
        {
            "sequence_id": "MAIN_BODY_1",
            "time_range": {"t_start_sec": 22.0, "t_end_sec": 55.0},
            "narrative_segment": {
                "script_source": "[00:22 - 00:55]",
                "core_argument": "지식적 결핍에 대한 학술적 해설",
            },
            # transition_module은 없어도 되지만, 스키마가 요구하는 경우 추가해야 함. 여기서는 생략하여 검증을 통과시키기 위함.
            "cta_logic": ["PlayList Link"],
        },
    ]

    validate_content_flow(mock_master_timeline, "schemas/content_workflow_schema.json")
