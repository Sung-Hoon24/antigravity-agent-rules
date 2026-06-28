# ⚙️ Interactive KGAS Component Spec (Knowledge Gap Sequence) V3.0

## 🎯 목표 및 기능 정의
본 컴포넌트는 시청자가 학술적 주제의 '필수 지식(Pre-requisite Knowledge)'이 부족함을 인지하는 순간, 그 결핍 자체를 시각적 오류/위기로 체험하게 하는 인터랙티브 메커니즘입니다.

**기술 스택:** React + SVG (Web Audio API 연동 필수)
**핵심 색상 코드:** `Glitch Violet (#9B59B6)`
**반응 방식:** 오디오 파라미터(주파수, 진폭 변화)에 강제 동기화되어 시각적 불안정성을 유발합니다.

---

## 🧭 State Machine Diagram (상태 전환 다이어그램)

컴포넌트는 최소한 다음 네 가지 상태를 거치며 전환됩니다. 각 상태는 개발자가 제어할 수 있는 파라미터 세트를 가집니다.

| State ID | 명칭 | 설명 (Story Function) | 시각적 특징 (Visual Output) | Trigger Condition (Triggering Event) |
| :---: | :--- | :--- | :--- | :--- |
| **S0** | **[Idle/Normal]** | 정상적인 지식 흐름. 평온하고 안정된 아카이브 느낌 유지. | Deep Indigo 배경, 미세한 스캔라인 오버레이(Opacity 5%). 부드러운 데이터 플로우 그래픽 (SVG). | 초기 로딩 / 스토리 시작 시점. |
| **S1** | **[Anomaly Detected]** | 논리적 모순 또는 지식의 단절 감지. 경고가 발생하기 직전 단계. | `Glitch Violet` 색상의 노이즈 오버레이 증가. 데이터 플로우 그래픽에 주기적인 '끊김(Stutter)' 효과 추가. | **[Acoustic Trigger]** 배경 음악/내레이션 주파수 급격한 변화 감지 (e.g., 440Hz $\to$ 120Hz). |
| **S2** | **[Knowledge Gap/Collapse]** | 지식적 결핍 극대화 및 시스템 오류 시각화. 가장 임팩트가 큰 상태. | SVG 요소의 파라미터 값(좌표, 색상)이 무작위로 붕괴/재조립되는 애니메이션 루프. 전체 화면에 '데이터 손실' 글리치 효과(Chromatic Aberration) 강제 적용. | **[Critical Threshold]** 내레이션의 핵심 질문 제기 시점 (e.g., "하지만, 이 과정은 왜 생략되었을까요?"). |
| **S3** | **[Resolution/CTA Funnel]** | 위기 상황 해소 및 다음 지식으로의 연결 제시. 해결책 또는 출구(CTA)를 안내함. | `Glitch Violet` 노이즈가 급격히 걷히며, 중앙에 명료한 '정보 흐름' 그래픽이 나타남. CTA 요소(예: Watch Full Episode)가 빛을 발하며 활성화됨. | **[Funnel Trigger]** 논리적 난제 제시 후, 해결책의 존재를 암시하는 오디오 톤 변화 (e.g., 고음역대의 명료한 신호). |

---

## 💻 Animation Loop Coding Specification (개발자 가이드)

### 1. S0 $\to$ S1 Transition Logic: Stutter Effect
*   **Trigger:** Audio Frequency Deviation ($\Delta F > X$)
*   **Action:** SVG Path `d` 속성의 값이 순간적으로 무작위 노이즈 값($N_{random}$)으로 치환됩니다.
    *   **Pseudo-Code (React Hook):**
        ```javascript
        useEffect(() => {
          if (audioParams.frequencyDeviation > 0.1) {
            setStutterActive(true);
            // SVG Path element reference: ref={dataFlowSVG}
            // Loop through path segments and apply rapid coordinate jittering for N frames.
            const dataFlowSVG = containerRef.current.querySelector('.data-flow');
            if (dataFlowSVG) {
                dataFlowSVG.setAttribute('d', generateJitterPath(originalD, audioParams));
            }
          } else {
             setStutterActive(false);
          }
        }, [audioParams]);
        ```
*   **Parameter:** `jitterAmount`: 최대 5%의 좌표 변위 ($\pm$).
*   **Timing:** $20 \text{ms}$ 간격으로 $\text{N}=3$번 반복.

### 2. S1 $\to$ S2 Transition Logic: Parameter Collapse (핵심 애니메이션)
이 단계는 컴포넌트의 핵심이자 가장 복잡합니다. 모든 그래픽 요소가 '붕괴'하는 원리를 정의해야 합니다.

*   **Concept:** 데이터 구조의 논리적 붕괴를 시각화. SVG 경로와 좌표계 자체가 불안정해짐을 표현.
*   **Mechanism:** **Vector Path Disruption.** 기존에 정립된 모든 `<path>` 엘리먼트가 다음 순서로 파라미터 오류를 일으킵니다.

1.  **Phase 1 (Desync):** 모든 `stroke-dasharray` 값이 무작위 사인파(Sine Wave) 패턴으로 변조됩니다. (`Math.sin(t * freq)`)
2.  **Phase 2 (Chromatic Aberration):** `<svg>` 컨테이너에 **세 개의 오프셋된 복사본 레이어**를 배치합니다 (R, G, B). 각 레이어를 $X$축으로 미묘하게 다르게 이동($\Delta X_{offset} = [0, \pm 2px]$)시키고, 시간에 따라 이 오프셋 값을 무작위로 변동시킵니다.
3.  **Phase 3 (Data Corruption):** 컴포넌트 내 모든 텍스트 요소가 **글리치 효과(Glitch Effect)**를 받습니다. (예: `transform: translate($\text{random}(-2px, 2px)$), skewY(...)`를 $50ms$ 간격으로 반복 적용).

*   **Pseudo-Code:**
    ```javascript
    const Collapse = ({ totalTime }) => {
        // Use requestAnimationFrame for smooth transition over the time period.
        return (
            <svg className="collapse-container">
                {/* 1. Layered SVG elements with R/G/B offsets */}
                <g style={{ transform: `translateX(${offsetR})` }} />
                <g style={{ transform: `translateX(${offsetG})` }} />
                {/* ... other components receiving dynamic class for glitching */}
            </svg>
        );
    };
    ```

### 3. S2 $\to$ S3 Transition Logic: Re-synchronization & CTA Activation
*   **Trigger:** 사용자 주의 집중도(Attention Score) 최대치 도달, 또는 내레이션의 명확한 해결책 제시 시점.
*   **Action:** 모든 오류 애니메이션이 즉시 정지하고, **'안정화 필터(Stabilizing Filter)'**가 적용됩니다.
    1.  **De-glitch:** 오버레이된 노이즈와 글리치가 $500ms$에 걸쳐 점진적으로 투명해집니다 (Opacity $\to 0$).
    2.  **Focus Element Isolation:** 다음 단계의 정보(CTA가 포함된 핵심 지식)를 담는 SVG 요소만 남고, 이 부분이 화면 중앙에서 부드럽게 '클램핑(Clamping)'되어 안정화됩니다.
    3.  **CTA Pop-up:** 최종 CTA 버튼/영역이 가장 밝은 `Glitch Violet` 계열의 하이라이트로 강조되며, 사용자의 상호작용을 유도하는 미세한 빛 애니메이션을 시작합니다.

---

## 📊 핵심 개발 파라미터 요약 (Developer Cheat Sheet)

| 파라미터 | 값/유형 | 단위 | 적용 상태 | 설명 |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Color** | `#9B59B6` | Hex Code | S1, S2, S3 | 모든 경고 신호 및 핵심 연결 고리. |
| **Noise Frequency ($F_{noise}$)** | $0.01 \sim 0.1$ | Hz | S1 $\to$ S2 | 노이즈 변화의 속도와 빈도를 결정. |
| **Jitter Amplitude ($\Delta X$)** | $-5\text{px} \sim +5\text{px}$ | Pixel | S1, S2 | 좌표계 불안정성 정도를 수치화한 값. |
| **Transition Duration ($T_{trans}$)** | $0.5 \sim 1.0$ | Second | 모든 전환 | 상태 간 이동 시의 부드러운 시간 흐름 제어. |
