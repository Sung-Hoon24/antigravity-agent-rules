import json
import os
from datetime import timedelta

# --- Mock Data Loading (실제 프로젝트 경로에 맞게 수정 필요) ---
# VTM 사양서 로드: vtm_interface_spec.json을 실행 환경 기준 동적 탐색
current_dir = os.path.dirname(os.path.abspath(__file__))
vtm_spec_path = os.path.join(
    current_dir, "VTM_API_Integration", "vtm_interface_spec.json"
)

try:
    with open(vtm_spec_path, "r", encoding="utf-8") as f:
        VTM_SPECS = json.load(f)
except FileNotFoundError:
    print("[ERROR] VTM Spec 파일을 찾을 수 없습니다. 로컬 경로를 확인해주세요.")
    VTM_SPECS = {}

# MTP v2.0 가상 데이터 구조 정의 (핵심 테스트 시퀀스를 담음)
MTP_V2_SIMULATED = [
    {"time": 0, "section": "Hook", "state": "Initial Setup", "api_call": None},
    {
        "time": 45,
        "section": "Conflict Point A",
        "state": "Knowledge Gap Trigger",
        "trigger_id": "KGAP-A",
        "expected_vtm_spec": {"effect": "Masking", "intensity": 0.9, "duration_s": 3},
    },
    {
        "time": 75,
        "section": "Conflict Point B",
        "state": "Logical Paradox",
        "trigger_id": "KGAP-B",
        "expected_vtm_spec": {"effect": "Noise", "intensity": 1.0, "duration_s": 2},
    },
    {
        "time": 120,
        "section": "CTA Funnel Entry",
        "state": "Tension Build",
        "api_call": None,
    },
]

# --- Core Simulation Functions ---


def simulate_vtm_call(spec):
    """VTM API 호출을 시뮬레이션하고 성공/실패를 반환합니다."""
    print(f"  -> [API Call]: VTM({spec.get('effect')}) 실행 시도...")
    # 실제 로직에서는 이 부분에서 API 엔드포인트 호출 및 에러 핸들링이 발생해야 함.
    if spec["intensity"] > 1.0:  # 의도적인 실패 조건 추가
        return False, "Intensity Parameter Out-of-Bounds (Max 1.0)"
    return True, "SUCCESS"


def run_e2e_test(mtp_data):
    """전체 통합 테스트 시퀀스를 실행하고 리포트를 생성합니다."""
    print("\n=============================================")
    print("⚙️ [E2E] 콘텐츠 통합 테스트 시작 (MTP v2.0 기반)")
    print("=============================================")

    results = {"success_cases": [], "failure_cases": []}
    current_time = timedelta(seconds=0)

    for i, segment in enumerate(mtp_data):
        # 시간 진행 시뮬레이션
        time_diff = timedelta(seconds=segment["time"] - current_time.total_seconds())
        print(
            f"\n[Time Skip] {current_time} -> {timedelta(seconds=segment['time'])} ({time_diff})"
        )

        # 논리적 충돌 지점 검증 로직
        if segment.get("expected_vtm_spec"):
            test_case = {"Section": segment["section"], "Time (s)": segment["time"]}

            success, message = simulate_vtm_call(segment["expected_vtm_spec"])
            test_case["VTM_Status"] = "PASS" if success else "FAIL"
            test_case["Details"] = message

            if success:
                results["success_cases"].append(test_case)
                print(
                    f"✅ SUCCESS: {segment['section']} -> VTM('{segment['expected_vtm_spec']['effect']}') 적용 성공. ({message})"
                )
            else:
                results["failure_cases"].append(test_case)
                print(
                    f"❌ FAILURE: {segment['section']} -> VTM API 호출 실패! 예상 오류 발생. ({message})"
                )

        current_time = timedelta(seconds=segment["time"])

    return results


def generate_report(results):
    """테스트 결과를 보기 좋게 포맷팅하여 리포트를 출력합니다."""
    print("\n\n=============================================")
    print("📜 [FINAL REPORT] 통합 테스트 시퀀스 검증 보고서")
    print("=============================================")

    total_tests = len(results["success_cases"]) + len(results["failure_cases"])
    passed_count = len(results["success_cases"])
    failed_count = len(results["failure_cases"])

    print(
        f"\n[SUMMARY] 총 테스트 케이스 수: {total_tests}개 | 성공: {passed_count}개 ✅ | 실패: {failed_count}개 🐛"
    )

    if results["failure_cases"]:
        print("\n🚨 [CRITICAL FAILURE CASES DETECTED]")
        for case in results["failure_cases"]:
            print(f"  - 섹션: {case['Section']} ({case['Time (s)']}s)")
            print(
                f"    -> 예상 VTM: {case.get('expected_vtm_spec', {}).get('effect')} | 상태: {case['VTM_Status']}"
            )
            print(f"    -> 상세 오류: {case['Details']}\n")
        print("👉 액션 필요: 해당 파라미터의 유효성 검사 로직을 수정하고, 테스트 케이스를 보강해야 합니다.")

    if results["success_cases"]:
        print("\n✅ [VERIFIED SUCCESS CASES]")
        for case in results["success_cases"]:
            print(f"  - 섹션: {case['Section']} ({case['Time (s)']}s)")
            print(
                f"    -> VTM 적용: {case.get('expected_vtm_spec', {}).get('effect')} | 상태: PASS"
            )


# --- Main Execution ---
if __name__ == "__main__":
    final_results = run_e2e_test(MTP_V2_SIMULATED)
    generate_report(final_results)
