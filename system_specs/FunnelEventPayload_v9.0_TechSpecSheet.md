# ⚙️ FunnelEventPayload v9.0 Technical Spec Sheet: 논리적 결핍 시퀀스
## I. 개요 및 목표 (Systemic Deficiency Induction)

*   **목표:** 시청자가 콘텐츠의 정보 전달 과정에서 '논리적 불연속성(Logical Discontinuity)'을 감지하고, 다음 단계의 정보를 강제로 요청하도록 유도하는 시스템 상태 전이(State Transition) 애니메이션 구현.
*   **발동 구간 (Funnel Gateway):** T+320ms (진입 시작) $\to$ T+510ms (탈출/강제 전환 완료).
*   **핵심 원칙:** 단순한 시각 효과가 아닌, 시스템의 **'처리 오류(Processing Error)' 또는 '데이터 손실(Data Loss)'**를 모방해야 한다.

## II. 애니메이션 상세 구조 및 타이밍 Directive

| 시간 구간 | 지속 시간 | 이벤트 상태 (State) | 비주얼 디스크립션 | 핵심 기술 지시어 |
| :---: | :---: | :---: | :--- | :--- |
| **T+320ms** | 150ms | `STATE_WARNING` | **경고 신호 감지:** 화면 전체에 미세한 주파수의 노이즈(Perlin Noise)가 스캔라인 형태로 오버레이되며 진동 시작. (색상: Deep Indigo 계열의 낮은 명도). | *Shader:* Noise Amplitude Ramp-Up. *Lottie:* Gradient Shift Start. |
| **T+400ms** | 100ms | `STATE_GLITCH_PEAK` | **논리적 결핍 발생:** 데이터 패킷이 손상된 듯한 '글리치(Glitch)' 현상이 수평으로 폭발적으로 지나간다. (화면의 일부분/텍스트가 순간적으로 왜곡, 색상 채널 분리). | *Shader:* Pixel Displacement & Chromatic Aberration Peak. *Lottie:* Hard Cut / Jitter Transform. |
| **T+500ms** | 100ms | `STATE_COGNITIVE_SHIFT` | **정보 재구성/강제 전환 유도:** 글리치 노이즈가 급격히 감쇠하며, 화면의 핵심 메시지(CTA 영역)만 강한 빛과 함께 '재로드'되는 듯한 효과. (Aged Gold 하이라이트 강조). | *Shader:* Noise Decay & Targeted Luminance Boost. *Lottie:* Masking Reveal / Pulse Effect. |
| **T+510ms** | - | `STATE_EXIT` | Funnel Gateway 성공적 통과. 시스템 정상화 및 다음 씬으로 부드럽게 전환 준비 완료. (강한 이질감 제거). | N/A (Transition to next scene logic) |

## III. 기술 사양서 v9.0 (Technical Spec Sheet)

### A. WebGL Shader API 기반 구현 상세 명세 (권장: 높은 유연성, 성능 최적화)

1.  **Noise Pattern Specification:**
    *   **Base Function:** Multi-octave Perlin Noise (또는 Simplex Noise).
    *   **Mapping:** 노이즈 값 $N(x, y, t)$를 화면 좌표 $(x, y)$와 시간 $t$에 매핑.
    *   **Time Domain Control:** `frequency = 0.01 * sin((t - T_start) / 50);` (시간 경과에 따른 주파수 변화).
    *   **Amplitude Decay:** 노이즈의 진폭(Amplitude)은 $A(t) = A_{max} \cdot e^{-\lambda (t-T_{peak})}$ 공식을 따라 급격히 감쇠해야 함. ($\lambda$: Decay Constant, 0.15 권장).

2.  **Glitch Effect 구현 로직:**
    *   **Pixel Displacement:** $P'(x, y) = P(x + \Delta x(t), y + \Delta y(t))$로 정의하며, $\Delta x, \Delta y$는 T+400ms 근처에서 최대값($\pm 5\%$)을 찍고 급격히 0으로 복귀해야 함.
    *   **Chromatic Aberration:** Red/Green/Blue 채널에 대해 $x$축 오프셋을 $\delta_r, \delta_g, \delta_b$ 값으로 분리하고, T+400ms 구간에서 이 오프셋의 차이($|\delta_i - \delta_j|$)가 최대화되어야 함.

### B. Lottie / SVG 기반 구현 상세 명세 (권장: 빠른 프로토타이핑, 낮은 리소스)

1.  **데이터 구조:** 모든 애니메이션은 Keyframe 데이터 구조로 정의되어야 하며, 각 키프레임에는 **`Time_ms`, `Value`, `Easing_Curve`**가 포함되어야 함.
2.  **Motion Graphic Loop (T+320ms):**
    *   **요소:** SVG Masking 및 Filter Effect 활용.
    *   **Keyframe 지시어:** 시간에 따라 변화하는 불규칙한 **'파동 패턴(Wavy Pattern)'**을 생성하고, 이를 화면에 반복적으로 덮어씌우는 (Overlay) 방식으로 구현합니다. 파동의 주파수와 진폭이 T+320ms에서 점진적으로 증가해야 합니다.
3.  **Glitch Effect (T+400ms):**
    *   Lottie 내장 기능을 활용하기 어려우므로, **`Transform: Skew/Translate`** 애니메이션을 매우 짧은 간격(10~20ms)으로 반복 호출하여 '떨림' 효과를 모방합니다.
    *   필수 파라미터: `Offset_X`: [-3px, 3px] (랜덤값), `Duration`: 15ms.

## IV. 개발팀 인계 및 검증 체크리스트

| 항목 | 구현 여부 | 담당 에이전트/기술 | 비고 |
| :--- | :---: | :--- | :--- |
| **State Machine 연동** | [ ] | Developer / Designer | T+320ms 진입 시, FunnelEventPayload 로직 호출 필수. |
| **WebGL 성능 최적화** | [ ] | Developer / Tech Lead | 모든 셰이더는 Mobile/Low-end GPU 환경을 고려하여 FPS 저하가 없도록 제한해야 함. |
| **Mock Loader 테스트** | [ ] | All | 실제 에셋 대기 중에도, 해당 Glitch 시퀀스를 Mock 로직으로 재생 가능해야 함. |
| **Keyframe 데이터 검증** | [ ] | Designer / Developer | 모든 애니메이션은 10ms 단위로 분할된 Keyframe 배열로 최종 제출되어야 함. |
