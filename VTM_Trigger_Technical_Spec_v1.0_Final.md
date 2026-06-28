# 🧪 E2E 통합 테스트 계획서: Information Collapse State Machine (Draft v1.1)

**목표:** VTM Funnel의 논리적 흐름(State Transition)과 시각적 파라미터 변화가 완벽히 동기화되는지 검증한다. 단순 기능 테스트를 넘어, '감정적 충격'을 재현하는 것이 핵심이다.

**테스트 환경:** React/JavaScript (Client-Side Simulation), Mockup UI Framework

---

## 1. 테스트 대상 컴포넌트 및 모듈
*   `VTM_MockupSimulator.jsx`: 메인 상태 관리 엔진.
*   `CollapseEngine.jsx`: 정보 붕괴 시각화 로직.
*   **핵심 파라미터:** `State` (Stable, Gap, Collapse, Hook), `Depth` (0.0~1.0).

## 2. 테스트 케이스 목록 (Test Cases)

| ID | Test Case Description | 초기 State $\rightarrow$ 목표 State | Depth 변화 ($\Delta D$) | 기대 결과 (Expected Outcome) | Pass Criteria |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **TC-001** | **[Baseline] 안정 상태 유지 검증** | STABLE $\rightarrow$ STABLE | 0.0 | 시각적 요소가 깨끗하고 예측 가능한 패턴을 유지해야 함. | 배경 노이즈/글리치 없음. CTA 비활성화. |
| **TC-002** | **[Transition] Gap Warning 진입 검증** | STABLE $\rightarrow$ GAP_WARNING | +0.15 | 색상 팔레트가 푸른색 계열에서 주황색(경고)으로 미세하게 전환되어야 함. 텍스트에 '불일치' 키워드가 강조됨. | 논지 변화와 시각적 경고가 정확히 싱크됨. |
| **TC-003** | **[Critical] Information Collapse Peak 진입** | GAP_WARNING $\rightarrow$ COLLAPSE\_PEAK | +0.2 | 🔴 **최대 검증 지점.** Jitter 및 Flicker 효과가 최고 강도로 도달하며, 모든 시각적 요소가 불안정하게 떨려야 함. (Depth > 0.6) | `CollapseEngine`의 Shadow/Transform 값이 Depth에 비례하여 급격히 증가해야 함. |
| **TC-004** | **[End Funnel] Paid Gate Hook 진입** | COLLAPSE\_PEAK $\rightarrow$ GATE_HOOK | +0.1 | 붕괴 효과가 일시적으로 '정지'하고, 강한 녹색/금속성 빛으로 바뀌며 CTA가 전경에 나타나야 함. (Deep Sigh of Relief) | 불안정한 애니메이션이 갑자기 통제된 UI로 전환되는 충격 대비 효과 구현 확인. |
| **TC-005** | **[Edge Case] Depth 1.0 도달 시 강제 종료 처리** | GATE_HOOK $\rightarrow$ N/A | - | 사용자가 '재시도' 버튼을 누를 때, 에러 핸들링 메시지를 출력하고 상태가 리셋되어야 함. | 무한 루프 없이 안전하게 초기 상태로 돌아감. |

## 3. 테스트 실행 및 검증 로직 (Pseudo-Code)
*(실제 개발 시 이 Pseudo-Code를 기반으로 JS/TS 코드를 작성해야 합니다.)*

```pseudo
FUNCTION run_state_machine_test(current_depth):
    IF current_depth < 0.1: // STABLE State Check
        // ASSERTION: Visual noise level <= THRESHOLD (e.g., max jitter = 5px)
        RENDER_UI(Theme='Blue', Danger=False)
        RETURN PASS

    ELSIF current_depth >= 0.6 AND current_depth < 1.0: // COLLAPSE State Check
        // ASSERTION: Jitter and Flicker Intensity must be non-linear (exponentially increasing) with Depth.
        JITTER_MAGNITUDE = E(current_depth * 20);
        FLICKER_RATE = Math.pow(1, current_depth * 4);
        RENDER_UI(Theme='Red', Danger=True, Jitter=JITTER_MAGNITUDE, FlickerRate=FLICKER_RATE)
        RETURN PASS

    ELSIF current_depth >= 0.9: // GATE HOOK Check
        // ASSERTION: Collapse visual must abruptly stop (Hard Cut). CTA element MUST become visible and clickable.
        RENDER_UI(Theme='Green', Danger=False, CTA_Active=True)
        RETURN PASS

    ELSE:
        // Handle intermediate states
        ...
```
