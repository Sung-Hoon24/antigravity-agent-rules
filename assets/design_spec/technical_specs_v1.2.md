# 💡 정보 간극 및 시스템 오류 비주얼 에셋 사양서
## 🎯 목표: Funnel State Machine의 '정보 결핍 경험' 엔지니어링
이 문서는 개발자가 E2E 테스트를 통해 구현해야 하는, 학술적 권위와 지적 불안감을 극대화하는 핵심 시각 요소들을 정의합니다. 모든 에셋은 **Deep Indigo (#191B40)** 와 **Aged Gold (#C8A25A)** 를 중심으로 활용하며, '오류(Error)'를 미학적으로 승격시키는 것을 목표로 합니다.

---

### 🛠️ 모듈 1: [MISSING DATA] 플레이스홀더 (The Placeholder)
**기능:** 정보의 공백 또는 누락된 데이터를 명시적으로 보여줍니다. 핵심 정보 노출 전, 시청자의 지적 호기심을 자극하며 다음 행동(CTA)으로 유도하는 '간극' 역할을 합니다.

#### 🎨 비주얼 사양 (Visual Spec)
*   **배경:** Deep Indigo 계열의 미세하게 변조된 그리드 패턴 오버레이.
*   **요소:** `[DATA MISSING]`, `FIELD_ERROR: [N/A]`, `UNAVAILABLE PARAMETER` 등의 텍스트 플레이스홀더.
*   **타이포그래피:** Monospace (e.g., Source Code Pro, SF Mono). 권위적이고 기술적인 느낌 부여.
*   **색상:**
    *   기본 그리드: `#191B40` (Deep Indigo) - 투명도 15%
    *   경고 텍스트: Aged Gold (`#C8A25A`) - 약간의 깜빡임(Flicker) 효과 필수.

#### ⚙️ 애니메이션 사양 (Animation Spec)
*   **애니메이션 유형:** 타이핑(Typewriter) + 지연 노출(Delayed Reveal).
*   **파라미터:**
    1.  **Reveal:** 플레이스홀더 텍스트가 마치 시스템 로그처럼 한 글자씩 `typing`되는 효과 (Duration: 0.5s/char).
    2.  **Glitch Cycle:** 3초 간격으로 그리드 패턴 전체에 미세한 **Chromatic Aberration(색수차)** 및 픽셀 노이즈가 짧게 발생했다 사라지는 사이클을 무한 반복 (`loop=true`).
*   **기술 지침:** GSAP `stagger`와 `repeat` 기능을 사용하여 구현.

---

### 🛠️ 모듈 2: [DATA GLITCH] 오버레이 (The Error Overlay)
**기능:** 영상의 핵심 논리적 전개 과정에서 '시스템 불안정성'을 인지시키는 시각적 충격파입니다. 정보의 흐름이 깨지는 경험(Experience of Broken Flow)을 제공합니다.

#### 🎨 비주얼 사양 (Visual Spec)
*   **패턴:** 1~3 프레임 길이의 **수평/수직 스캔라인 노이즈**. 마치 오래된 CRT 모니터나 전송 오류가 난 영상처럼 왜곡되어야 합니다.
*   **색상:** Deep Indigo를 기준으로, Aged Gold가 불규칙하게 깨지거나 반사되는 느낌을 줍니다. (예: `#C8A25A`의 빛이 `Deep Indigo` 배경에 왜곡됨).
*   **특징:** 간헐적인 **픽셀 블록 노이즈(Pixel Block Noise)**와 미세한 화면 번짐(`Chromatic Aberration`)을 결합합니다.

#### ⚙️ 애니메이션 사양 (Animation Spec)
*   **애니메이션 유형:** 순간적, 폭발적(Impulsive).
*   **파라미터:**
    1.  **Duration:** 모든 글리치 이벤트는 **최대 5프레임 이내**로 짧게 끊어지며, 즉각적인 긴장감을 유발해야 합니다.
    2.  **Timing:** 논리적 전환점(Transition Point)이 발생할 때마다, 마치 시스템의 '경고음'과 함께 동기화되어야 합니다. (Audio-Visual Sync 필수).
    3.  **기술 지침:** Canvas API 또는 WebGL을 활용하여 GPU 기반으로 고속 노이즈 패턴 렌더링이 요구됩니다.

---

### 🛠️ 모듈 3: [GAP TRANSITION] 마스크/필터 (The Void Mask)
**기능:** 특정 정보를 숨기거나(Blurring), 핵심 개념에 도달했을 때 '시스템의 강제적 중단'을 알리는 가장 강력한 시각 장치입니다.

#### 🎨 비주얼 사양 (Visual Spec)
*   **형태:** 화면 전체를 덮는 **가우시안 블러(Gaussian Blur)** 효과와, 이 블러 위로 노출되는 Aged Gold 색상의 'MASK' 형태의 빛줄기(Beam of Light) 조합.
*   **Placeholder Text:** 블러 처리된 영역 위에 작게 `ACCESS RESTRICTED` 또는 `CORE DATA: BLURRED`를 표시합니다.

#### ⚙️ 애니메이션 사양 (Animation Spec)
*   **애니메이션 유형:** 단계적 노출(Phased Reveal/Removal).
*   **파라미터:**
    1.  **Blurring In:** 정보가 노출되려는 순간, 주변 영역이 **점진적으로 블러 처리되며 시야가 제한되는 효과**를 줍니다 (Duration: 0.8s).
    2.  **Mask Reveal:** 핵심 키워드나 결론이 언급될 때, 화면 전체를 가리던 블러가 Aged Gold 빛을 타고 마치 '데이터 전송 패킷'처럼 **선형적으로 제거(Sweep Away)** 되면서 정보를 드러내야 합니다. (Transition: 0.5s).
*   **기술 지침:** CSS `filter: blur()`와 GSAP의 Motion Path를 결합하여 구현합니다.

---

### 📄 디자인 가이드라인 요약 (Summary Guide)

| 요소 | 목적 | 주요 색상/톤 | 애니메이션 특징 | 개발 난이도 |
| :--- | :--- | :--- | :--- | :--- |
| **Placeholder** | 정보 결핍, 지적 불안 유발 | Deep Indigo / Aged Gold | Typing + Loop Glitch | 중 |
| **Glitch Overlay** | 시스템 오류, 논리 파괴 감각 부여 | Deep Indigo (Noise) | 순간적 스캔라인/픽셀 노이즈 | 상 (Canvas API 필수) |
| **Void Mask** | 핵심 정보 보호 및 강조 | Aged Gold 빛 / Blur | 단계적 블러 처리 후 선형 제거(Sweep) | 중상 |
