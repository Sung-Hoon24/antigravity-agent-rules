# ⚙️ E2E 통합 테스트 하네스 (Master Test Suite)
## 목적
본 스위트는 마스터 타임라인(`MTP v3.0`)과 VTM API 사양서(`v2.0`)를 기반으로, 영상 콘텐츠의 엔드투엔드(End-to-End) 워크플로우 견고성을 검증합니다. 단순 기능 테스트를 넘어, 시스템적 오류 발생 시나리오까지 포함하여 아키텍처 레벨의 안정성을 확보하는 것이 목표입니다.

## 🛠️ 필수 전제 조건
1. **Dependencies:** Python 3.8+ 환경
2. **Input Files (절대 경로):**
    * `Master_Timeline_Blueprint_v3.0.json`
    * `VTM_Master_Specification_v2.0.json`
3. **Execution Environment:** CI/CD 파이프라인에 통합되어야 합니다.

## 🔬 테스트 케이스별 검증 포인트 (Critical Checkpoints)

| Test ID | 기능 영역 | 검증 목표 | 성공 기준 (Pass Criteria) | 실패 시 디버깅 지점 (Failure Point) |
| :--- | :--- | :--- | :--- | :--- |
| `test_01` | **구조 무결성** | 타임라인 전체의 기본 구조 및 필수 필드 존재 여부. | 모든 세그먼트가 'title', 'entry_state', 'exit_state'를 가짐. | JSON Schema Validation 실패 지점 확인. |
| `test_02` | **VTM 커버리지** | 모든 시간 구간(S1~Sn)에 VTM API 호출이 의무적으로 배치되었는지 검증. | 세그먼트당 VTM 호출 ID가 95% 이상 충족되어야 함. | 빈 구간 또는 논리적 비약 발생 지점 확인 (Missing Transition). |
| `test_03` | **상태 전이** | 인접한 섹션 간의 상태 변화(State Machine)가 매끄럽게 이루어지는지 검증. | `current['exit_state'] == next_seg['entry_state']`를 만족해야 함. | State Mismatch 로그 발생 (직전 세그먼트 출구 정의 오류). |
| `test_04` | **Conflict Point** | 논리적 충돌 지점에서 VTM API 호출이 실패했을 때의 강제 에러 처리 로직 검증. | 500 Internal Server Error 시, **Fallback UI(Deep Indigo)**가 즉시 표시되고 개발자 콘솔에 상세 스택 트레이스가 출력되어야 함. | 예외 핸들링(`try...except`) 블록이 누락되었거나, 폴백 메커니즘이 작동하지 않음. |
| `test_05` | **Knowledge Gap** | 지식적 결핍 유도 구간에서 시스템의 '멈춤(Suspension)' 상태 구현 검증. | API 호출 대신, 사용자에게 시각적/논리적 긴장감을 주는 **지연 효과(Delay Effect)**가 성공적으로 발동되어야 함. | `async/await` 또는 타이머 기반 지연 로직이 누락됨. |

## 🚀 개발팀 액션 아이템
1. 위 스위트를 CI 환경에 배치하고, 모든 테스트 케이스를 **Failure Mode**까지 포함하여 실행합니다.
2. 특히 `test_04`와 `test_05`의 시뮬레이터 함수(`_simulate_vtm_error_handling`, `_simulate_suspension_state`)가 실제 에러 상황을 정확히 모방하는지 디버깅해주세요.
