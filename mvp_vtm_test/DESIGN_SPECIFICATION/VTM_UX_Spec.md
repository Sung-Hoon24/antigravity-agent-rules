# 📽️ VTM 컴포넌트 최종 디자인 스펙 (Design Spec v1.0)

**작성자:** Designer Agent
**목표:** 시청자의 '지적 공백(Cognitive Gap)' 자산화 극대화를 위한 비주얼 충격 설계.
**핵심 팔레트:** Deep Indigo (`#1A237E`) / Aged Gold (`#B79532`)

## ⚙️ I. 컴포넌트별 파라미터 가이드라인

### 1. ErrorLayer (ErrorLayer1)
*   **기능:** 데이터 충돌, 인지적 오류 발생 시 시스템 불안정성 표현.
*   **애니메이션 타입:** Scanline Distortion + Color Shift (Glitch).
*   **파라미터 세부 명세:**
    *   **Wave Type:** Sinusoidal Pattern (좌우 반복 왜곡 패턴).
    *   **Frequency Control:** 딜레마 유형에 따라 조정.
        *   `D1: 지각의 오류` $\implies$ 높은 주파수, 수직적 '시차' 강조.
        *   `D2: 자유 의지의 환상` $\implies$ 불규칙한 간격의 짧고 빠른 깜빡임(Stutter).
    *   **Color Shift:** Deep Indigo 배경 위에 Aged Gold 톤이 순간적으로 오버레이 되어, **진실과 오류가 혼재하는 느낌**을 부여한다.
    *   **Timing/Duration:** `0.15s` ~ `0.25s`. (반복 루프 시 Easing: Ease-in-out).

### 2. VoidTransition (VoidTransition)
*   **기능:** 논점 전환(Point Transition), 정보의 단절을 통한 몰입도 극대화.
*   **애니메이션 타입:** Grain Noise Fade Out $\to$ Vacuum Blackout $\to$ Emergence Fade In.
*   **파라미터 세부 명세:**
    *   **Out-Phase (전환 전):** Deep Indigo 배경에 미세한 필름 그레인 노이즈를 추가하고, 이 입자들이 **0.5초 동안 서서히 걷히며(Dissolve)** 사라진다. (Easing: Ease-out).
    *   **Void Phase:** 정확히 `0.1s`의 블랙아웃. 이 순간은 오디오 사운드 디자인이 가장 중요함 (예: 낮은 주파수의 '쿵' 하는 소리, 또는 전기적 정전음).
    *   **In-Phase (다음 정보 등장):** 다음 텍스트/비주얼 요소는 완전한 어둠에서 시작하지 않고, **Aged Gold 빛줄기(Beam)**처럼 강하게 '표출되는(Emergence)' 방식으로 진입해야 한다.

## ✨ II. 최종 UX 테스트 케이스 (D1 적용 기준)
*   **시나리오:** "우리가 보는 것이 곧 진실이다" (Common Belief) $\to$ "지각 과정은 능동적 재구성이다" (Academic Paradox).
*   **흐름 설계:**
    1.  (Deep Indigo 상태로 Common Belief 제시 - 2초).
    2.  *(트리거)*: 오류 발생! `ErrorLayer1` 발동 (`0.2s`). 강한 스캔라인 왜곡이 Deep Indigo 배경을 뒤흔든다. Aged Gold 글씨들이 잠시 흔들린다.
    3.  (VoidTransition 작동): 노이즈 입자가 걷히며 사라지고, 0.1초의 블랙아웃.
    4.  (다음 정보 등장): 화면 전체에 Aged Gold 빛줄기가 강렬하게 '표출'되며 Academic Paradox가 새로운 논점으로 제시된다.

---
**개발팀 지침:** 이 스펙은 단순한 참고 자료가 아닙니다. 모든 애니메이션 파라미터는 **Timing, Easing Curve, Color HEX 코드**를 기반으로 구현되어야 합니다. 특히 VoidTransition의 0.1초 블랙아웃 구간과 다음 정보的 Emergence 효과에 가장 높은 우선순위를 두십시오.
