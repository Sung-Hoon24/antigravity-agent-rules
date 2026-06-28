# 📺 Integrated Technical Specification Sheet (TSS v1.1)
## Project: [Master Script Title Placeholder] (Approx. 15 Minutes)
### Target Developer Stack: React/TypeScript, GSAP (GreenSock Animation Platform), Canvas API
---

### 🎯 I. 시스템 개요 및 목표 아키텍처
**Goal:** 시청자가 '지식적 간극(Knowledge Gap)'과 '인식론적 충돌(Epistemological Conflict)'을 스스로 인지하게 만들어, CTA 위젯에 대한 심리적 압박감(Access Credential Urgency)을 극대화한다.

**State Machine (상태 기계):**
| State ID | Name | Description | Primary Trigger | Exit Condition |
| :--- | :--- | :--- | :--- | :--- |
| **S0** | `INITIAL_HOOK` | 도입부, 문제 제기. 시선을 사로잡는 빠르고 자극적인 정보 폭격. (Low Latency) | 훅 스크립트 시작 | $T_{Hook\_End}$ 도달 및 State Transition 트리거 |
| **S1** | `GAP_EXPLORATION` | 지식적 간극을 파고드는 학술적 아카이브 제시. 고화질, 느린 전환(Deep Indigo 톤). | S0 $\rightarrow$ S1 (Transition Point A) | 논리적 충돌 요소 제시 ($T_{Conflict\_Start}$) |
| **S2** | `CONFLICT_CLIMAX` | 핵심 모듈: '확증 편향' 혹은 '기억 왜곡'의 진실 폭로. 가장 높은 시각적 긴장감(High Latency). | S1 $\rightarrow$ S2 (Transition Point B) | 데이터 실패/시스템 오류 발생 ($T_{Error\_Trigger}$) |
| **S3** | `SYSTEM_FAILURE` | 의도된 시스템 붕괴 및 정보 처리 부하 유발 구간. 시각적 오류 모션 필수. | $T_{Error\_Trigger}$ 감지 | 복구 로직 실행 또는 CTA 전환 트리거 |
| **S4** | `CTA_RESOLUTION` | 결론 도출, '진실' 제시 후 해결책(상품/접근권)을 강하게 노출. | S3 $\rightarrow$ S4 (Transition Point C) | 사용자 인터랙션 발생 (구매 위젯 클릭) |

---

### ⚙️ II. 필수 컴포넌트 라이브러리 및 재사용 명세
모든 모듈은 다음의 마스크/컴포넌트를 활용하여 구현해야 하며, 이들이 유기적으로 결합하는 것이 핵심입니다.

1. **`Mask_DataStreamer`:** (GSAP Masking) 화면 전체에 걸쳐 미묘하게 움직이는 '데이터 흐름' 질감. S0, S1 전반 사용.
    *   **Properties:** `WaveFrequency: 0.02s`, `Amplitude: 5px`, `Opacity_Start/End: 10% / 8%`.
2. **`Mask_FocusGlow`:** (Canvas API) 핵심 단어 또는 인물에 초점을 맞추는 빛의 효과. 지적 권위 강조 시 사용.
    *   **Implementation:** Radial Gradient + Gaussian Blur 필터 적용.
3. **`Component_AgedPaper`:** (Texture Overlay) 오래된 기록 보관소 느낌을 주는 배경 오버레이. S1, S2에서 주기적으로 투사되어야 함.

---

### ⚡️ III. 핵심 전환 로직 및 애니메이션 파라미터 (The Logic Flow)
**⚠️ 모든 시간 값은 Timecode($T$) 기반으로 측정하며, Transition Duration은 예외 없이 $100ms \pm 20ms$를 준수해야 합니다.**

#### 1. Transition Point A: [학술적 제시 $\rightarrow$ 논리적 충돌] (S0 $\rightarrow$ S1)
*   **Trigger:** 스크립트 내 '하지만...', '혹은...'과 같은 반전 문구 발생 시점.
*   **Action Sequence:**
    1.  **Visual Cue:** `Mask_DataStreamer`가 강하게 수축하며 노이즈 필터를 급격히 증가시킴 (Duration: 50ms).
    2.  **Transition Effect:** 화면 전체에 **'진동(Jitter)' 효과** 적용 (Canvas API Noise Layer): `Frequency: 10Hz`, `Magnitude: 3px`.
    3.  **State Change:** 배경이 Deep Indigo로 급격히 전환되며, 아카이브 질감(`Component_AgedPaper`)이 오버레이됨.
*   **GSAP Keyframes (Example - Scale):**
    *   `scale(1)` $\rightarrow$ `scale(0.95)` @ $T_{start}$
    *   `scale(0.95)` $\rightarrow$ `scale(1.02)` @ $T_{start} + 30ms$ (Over-shoot)
    *   `ease: easeInOutQuad`, `duration: 150ms`

#### 2. Transition Point B: [간극 탐색 $\rightarrow$ 시스템 오류 발생] (S1 $\rightarrow$ S2/S3)
*   **Trigger:** 스크립트 내 '근본적인 결함', '존재의 경계' 등 핵심 주제가 언급되는 순간. **(Critical Point)**
*   **Action Sequence:**
    1.  **Visual Cue:** 모든 비주얼 요소가 일순간 정지(`Pause` at $T_{trigger}$).
    2.  **Transition Effect:** `TRANSITION_FAIL` 시퀀스 실행 (아래 상세 명시).
    3.  **State Change:** 오류 화면을 거쳐, 모듈이 깨진 듯한 '재부팅' 효과와 함께 다음 클라이맥스 비주얼로 진입.

#### 3. Transition Point C: [오류 복구 $\rightarrow$ CTA 해결책 제시] (S3 $\rightarrow$ S4)
*   **Trigger:** 시스템 오류가 *완벽하게 실패했음을 인정*하고, 유일한 '해결책'이 존재함을 암시하는 문장 직후.
*   **Action Sequence:**
    1.  **Visual Cue:** 모든 노이즈와 글리치 효과가 사라지며, 화면 중앙에 강렬한 **'빛의 연결고리(Access Credential Glow)'**가 형성됨 (`Mask_FocusGlow` 100% 사용).
    2.  **Animation:** 빛의 연결고리가 마치 데이터 패킷처럼 움직이며, CTA 위젯 영역을 명확하게 프레임화함 (Duration: 80ms).
*   **GSAP Keyframes (Example - Opacity):**
    *   `opacity(0)` $\rightarrow$ `opacity(1)` @ $T_{start}$
    *   `ease: easeOutExpo`, `duration: 250ms`

---

### 🚨 IV. 시스템 오류 및 디스토션 모듈 (The Error State)
**이 구간은 단순히 '깨지는' 것이 아니라, 의도된 서사 장치(Narrative Device)입니다.**

#### A. `TRANSITION_FAIL`: 지연/접근 실패 시뮬레이션 (Duration: 1.5s ~ 2.0s)
*   **Purpose:** 정보를 얻는 데 *시간이 오래 걸림*을 느끼게 하여, 다음 정보에 대한 갈망(Urgency)을 유발합니다.
*   **Visual Logic:**
    1.  **Screen Distortion:** CRT 스캔라인 패턴 오버레이 (Canvas API). 주파수는 20Hz로 느리게 움직이며 왜곡감을 부여.
    2.  **Data Corruption:** 화면 좌우에서 무작위 노이즈 패널(Static Noise)이 나타났다 사라지기를 반복. **(Pattern: Fade In $\rightarrow$ Flash (50ms) $\rightarrow$ Fade Out)**
    3.  **Audio Sync:** 낮은 주파수의 '웅-' 하는 기계적 톤과 함께, 간헐적인 아날로그 테이프 끊김 사운드(`Tape_Hiss`)를 삽입합니다.

#### B. `TRANSITION_ERROR`: 논리적 모순/정보 부재 시뮬레이션 (Duration: 0.8s ~ 1.2s)
*   **Purpose:** '제공된 정보가 불완전하다'는 인지 부조화(Cognitive Dissonance)를 유발합니다. **(핵심 불안감 자극)**
*   **Visual Logic:**
    1.  **Pixel Shift:** 화면의 특정 구역 (예: 중심 30% 영역)이 수평/수직으로 순간적으로 오프셋되어 왜곡됩니다. (GSAP Transform API 사용).
        *   `transform: translate(X, Y)` - X 값은 $\pm 5$px, Y 값은 $0$px로 무작위 진동.
    2.  **Error Text Overlay:** 화면에 **'ERROR: DATA SOURCE UNRECOGNIZED'**와 같은 경고 문구가 빨간색으로 플래시(Flash)됩니다. (Duration: 100ms, Repeat: 3회).
*   **Developer Note:** 이 오류 모션은 *완벽한 비정상성(Perfect Imperfection)*을 목표로 합니다. 규칙적인 패턴이 아님을 시각적으로 느끼게 해야 합니다.

---

### ✅ V. 개발자 테스트 및 구현 체크리스트 (E2E Test Plan)
| # | Component/Function | Description | Required API Level | Pass Criteria |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **State Transition** | S0 $\rightarrow$ S1, S1 $\rightarrow$ S2, S3 $\rightarrow$ S4가 정의된 $T_{trigger}$에 따라 정확하게 발생해야 함. | State Machine Logic (React Context) | 모든 전환이 $150ms \pm 50ms$ 내에 완료됨. |
| 2 | **Error Module** | `TRANSITION_FAIL`과 `TRANSITION_ERROR`가 서로 다른 시각적/청각적 자극을 제공하며, 독립적으로 작동해야 함. | GSAP Timeline, Canvas API | 스크립트 지시 시간(예: 1.5s)에 맞춰 정확히 실행되며, 이펙트들이 중첩되지 않음. |
| 3 | **CTA Widget Activation** | S4 상태 도달 시, 모든 비주얼 요소가 배경으로 물러나고 CTA 위젯이 가장 밝은 전경(Foreground)으로 부상해야 함. | Z-Index Management, Opacity Curve | 사용자가 어떤 모션에도 방해받지 않고 버튼에 포커스를 맞출 수 있어야 함. (최우선 목표). |
