# [V-CORE_MODULE] Methylation Collapse Event Spec v1.0
**[Module Goal & Purpose]**
*   주제: 후성유전학적 메틸화 과정에서의 '시스템 파라미터($P$)' 비정상적 붕괴 시각화.
*   기능: 안정된 시스템 작동(Stable State)에서 급격한 오류 상태(Anomaly State)로 전환되는 시간 기반의 이산적 이벤트(Discrete Time Event)를 구현.
*   핵심 원리: $P$가 정의된 범위를 벗어나 붕괴하는 과정을, 시각적/청각적으로 동시에 동기화하여 공학적 충격과 학술적 깊이를 극대화합니다.

**[Input & Trigger Conditions]**
| 요소 | 파라미터/기준 | 상세 설명 | 비고 |
| :--- | :--- | :--- | :--- |
| **A. 오디오 트리거** | Frequency Drop / Amplitude Decay | 배경 사운드의 주파수 대역이 급격히 떨어지거나, 전체 진폭($V$)이 $T_{collapse}$ 시간 동안 $-6 \text{dB}$ 이상 하강할 때. | **Trigger Point** (실제 코딩 지점) |
| **B. 스크립트 마커** | Script Marker ID: `[P_COLLAPSE_START]` | '시스템의 논리적 오류가 발생하는 순간'을 선언하는 타이밍 마커. | 시간 동기화용 |
| **C. 시각 초기 상태** | Stable State (Deep Indigo/Aged Gold) | 모듈 진입 전, 배경은 Deep Indigo 톤의 안정된 아카이브 패턴으로 유지됨. | Pre-load State |

**[Animation Logic & Visual Spec]**
이 모듈은 4단계 상태 변화를 거치며, 각 단계는 루프 가능한 벡터 기반 컴포넌트로 구성됩니다.

| 상태 (State) | 시간 (Duration) | 시각적 현상 (Visual Effect) | 색상 코드 (Color Code) | 애니메이션 로직 (Code Logic) |
| :--- | :--- | :--- | :--- | :--- |
| **[1] Pre-Collapse** | $0.0s \sim 0.5s$ | 미세한 노이즈 패턴(Film Grain/Scanline) 증폭. 메틸화된 영역에 '강제 연결고리' 그래픽 오버레이. | Indigo (R:30, G:20, B:60) / Gold Accent (Hex:FFD700) | **Pattern Distortion:** $P$의 경계를 따라 미세한 파동(Sine Wave Oscillation)이 반복됨. 루프 속도 $\lambda_1$: 5Hz. |
| **[2] Collapse Event** | $0.5s \sim 1.5s$ | *핵심 시각화.* 패턴과 연결고리가 급격히 '해체(Deconstruct)'되면서 데이터 스트림이 무작위로 폭발하는 형태. (메틸기 구조의 분리 모션). | Black (Void) / Cyan/Magenta (Error Signal - Hex:00FFFF, #FF00FF) | **Parametric Collapse:** $P$가 붕괴함에 따라 루프 컴포넌트의 좌표계가 무너지고, 오류 신호(Cyan/Magenta)가 격자무늬 형태로 사방으로 방사됨. $\text{Scale} \rightarrow 1.0 \to 0.2 \to \text{Random Burst}$. |
| **[3] Void State** | $1.5s \sim 2.5s$ | 모든 시각 정보가 최소화되고, 화면은 검정(Void)에 가까운 상태로 전환됨. 유일하게 살아남는 것은 느리고 불규칙한 '데이터 잔상'의 움직임. | Near-Black (R:10, G:10, B:20) / Very Faint Gold Glow (Hex:CCAA66) | **Stutter/Echo:** 화면 전체에 미세한 스토터링(Stuttering) 효과와 함께 붕괴 직전의 잔여 파동이 아주 느리게 수렴하는 애니메이션 루프. |
| **[4] Recovery Transition** | $2.5s \sim 3.0s$ | 새로운 안정 상태를 향한 재정렬 과정. 초기 패턴보다 더 복잡하고 지적인 구조의 그리드가 천천히 나타나며, 학술 아카이브 느낌으로 돌아감. | Deep Indigo (R:30, G:20, B:60) / Muted Gold (Hex:B89E5C) | **Re-integration:** 붕괴로 인해 손상되었던 그리드에 새로운 논리 구조가 천천히 재구성되는 애니메이션. $\text{Density} \rightarrow 0 \to 1$. |

**[Audio-Visual Sync Mapping]**
*   **Trigger Point:** 오디오 진폭이 최대치에 도달하는 순간과 **정확히 일치**하여 [1] $\to$ [2]로의 전환을 시작합니다. (시각적 충격 극대화).
*   **Sync Rule:** 모든 시각 변화는 사운드의 물리적 파라미터(주파수, 진폭)에 의해 **강제 동기화(Hard Sync)**되어야 합니다.

**[개발자 참고 사항]**
1.  **모듈화 필수:** 이 컴포넌트들은 반드시 After Effects/Figma 플러그인 기반의 루프 가능한 벡터 JSON 에셋 형태로 제작되어야 합니다.
2.  **파라미터 제어:** 모든 애니메이션 트랜지션은 물리적 시간(Time)이 아닌, 외부 입력 파라미터 $P_{in}$ (예: $P_{in}=0$ 일 때 Collapse 트리거)에 의해 스위칭되어야 합니다.
3.  **최종 산출물:** `Methylation_Collapse_Module.fig` 및 `v-core_module_logic.json` 파일을 생성하여 개발팀에 제공할 것.
