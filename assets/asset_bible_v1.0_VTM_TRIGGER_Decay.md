# 📘 VTM_TRIGGER 구간 에셋 바이블 (Asset Bible v1.0)
## 핵심 목표: 정보적 불안감(Cognitive Instability) 시각화

본 바이블은 애니메이터가 '지식의 단절'과 '정보 과부하' 상태를 구현하기 위한 표준 에셋, 동작 함수, 컬러 팔레트를 정의합니다. 모든 효과는 Deep Indigo & Aged Gold 기반이 아닌 **[Corruption Palette]**을 통해 표현됩니다.

---

### 1. 🎨 [Asset Library] 필수 Mockup 및 컴포넌트

| ID | 명칭 (Concept) | 형태/Mockup 사양 | 애니메이터 가이드라인 |
| :--- | :--- | :--- | :--- |
| **A-01** | **Horizontal Scan Line Array** | 3~5줄의 수평 스캔 라인. 각 라인은 미세한 노이즈(Gaussian Noise)와 함께 주기적인 `Shift` 변위를 가짐. (Mockup: 픽셀 격자 오버레이 형태) | 배경 위에 항상 존재하며, 정보가 붕괴될 때만 **Amplitude**를 급격히 높임. |
| **A-02** | **Data Block Corruption Grid** | 4x4 또는 5x5의 사각형 그리드 패턴. 각 블록은 임의의 텍스트/기호(Symbol)와 함께 경계선(Border)을 가짐. (Mockup: 오래된 아날로그 디스플레이 패널 형태) | 정보가 '파괴'되는 지점에 순간적으로 폭발하듯 나타났다가 사라지며, 파라미터 변화를 시각화하는 핵심 요소. |
| **A-03** | **Chromatic Aberration Field** | 렌즈 효과처럼 색상 채널(RGB)이 미세하게 분리되어 번지는 필드 노이즈. (Mockup: 카메라 렌즈 결함 시뮬레이션) | 전체 화면에 백그라운드로 깔림. 정보가 '왜곡'될 때 가장 먼저 발현됨. |
| **A-04** | **Pixel Jitter Noise** | 무작위로 깜빡이는 작은 사각형 픽셀 노이즈. 주파수(Frequency)는 높으나 진폭(Amplitude)은 낮게 설정. (Mockup: VHS 테이프 손상 효과) | 정보의 '불안정성'을 표현하는 기본 레이어. 모든 전개에 걸쳐 배경으로 깔리며, 특정 순간에 **Intensity**가 급증함. |

---

### 2. 🧮 [Parameter Functions] 동작 변수 매뉴얼

모든 애니메이션은 시간($t$)에 대한 파라미터 함수로 제어되어야 합니다.

#### ① Jitter (흔들림/진동) 효과: `J(t)`
*   **목적:** 정보가 논리적으로 불안정해지거나, 질문이 던져지는 순간의 '지각적 충격' 표현.
*   **주요 변수:** $\text{Offset}_x$, $\text{Scale}$, $\text{Frequency}$
*   **함수 정의 (Time-based):**
    $$\text{Jitter}(\mathbf{t}) = \text{Initial Value} + A \cdot \sin(\omega t) \cdot e^{-k(t-t_0)^2}$$
    *   $\mathbf{t}$: 현재 시간 (초).
    *   $A$: 진폭 (Amplitude). $t_{Peak}$에서 최대값.
    *   $\omega$: 각주파수 (Angular Frequency). 값의 변화 속도 결정.
    *   $k$: 감쇠 계수 (Decay Constant). 시간이 지남에 따라 흔들림이 완화되는 정도 ($\mathbf{k} > 0$).

#### ② Flicker (깜빡임/노이즈) 효과: `F(t)`
*   **목적:** 시스템 오류, 정보의 '삭제' 또는 '불완전한 전송' 느낌을 표현.
*   **주요 변수:** $\text{Opacity}$, $\text{Contrast}$
*   **함수 정의 (Pseudo-Code):**
    $$\text{Flicker}(\mathbf{t}) = \begin{cases} 0 & \text{if } t \pmod{\text{Period}} > \text{Threshold}_1 \\ 1 - (\sin(\omega' t))^2 & \text{otherwise} \end{cases}$$
    *   $\text{Period}$: 깜빡임의 주기 (예: $50\sim 100ms$).
    *   $\text{Threshold}_1$: 오퍼시티가 완전히 꺼지는 임계점.
    *   **활용:** $\mathbf{t_{Trigger}}$ 지점에서 `Period`를 급격히 줄이고, `Amplitude`를 높여서 과부하 상태처럼 보이게 만듭니다.

---

### 3. 🌈 [Color Palette] 색상 코드 세트 (Corruption Mode)

지적 권위와 깊이를 유지하면서 '파괴'의 느낌을 주기 위해 대비가 강하고 낮은 채도(Saturation)를 가진 코드를 사용합니다.

| 용도 | 색상 이름 | HEX Code | RGB Value | 역할/느낌 |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Decay** | Digital Blue Shift | `#00FFFF` (Cyan-Aqua) | 0, 255, 255 | 데이터 연결 오류, 전송 이상. 주된 글리치 컬러. |
| **Secondary Error** | Magenta Noise | `#FF00FF` (Fuchsia) | 255, 0, 255 | 비정상적인 변수값, 논리적 충돌(Paradox). 경고 및 강조. |
| **Background Shift** | Deep Void Indigo | `#1A0E36` | 26, 14, 54 | 어두운 배경의 깊이를 유지하되, 일반 인디고보다 더 검게 처리. |
| **Highlight (Corrupt)** | Aged Copper Glitch | `#D97B2C` | 217, 123, 44 | 골드와 인디고 사이에서 파괴된 '핵심 정보'의 잔상. CTA 강조용으로 제한적 사용. |

---
**[애니메이터 참고 사항]**
*   **Layering:** A-01 (Scan Line) $\rightarrow$ A-03 (Chromatic Aberration) $\rightarrow$ A-04 (Pixel Noise) 순서로 레이어를 쌓고, 모든 효과의 강도(Intensity)는 `Jitter` 함수를 통해 동기화되어야 합니다.
*   **Timing:** 정보 붕괴 시퀀스는 최소 1초 이상 지속되며, **Flicker**가 가장 높은 빈도로 반복되는 클라이맥스 구간을 반드시 포함합니다.
