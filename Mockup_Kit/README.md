# 🛠️ Mockup Interface Kit V2.0: Technical Specification & Usage Guide

**목표:** '기술적 불안정성 증명' USP를 시각화한 모듈형 컴포넌트 라이브러리.
**버전:** V2.0 (Asset Bible V2.0 기반)
**톤앤매너:** Deep Indigo (#191B35) & Aged Gold (#D4AF37).
**핵심 원칙:** 모든 시각 요소는 파라미터($P$)와 State Transition에 의해 구동되어야 함.

---
## 🔍 I. 핵심 컴포넌트 라이브러리 (Components/)
모든 컴포넌트는 `[P_ID]: <파라미터 이름> = [함수/값]` 형태로 정의됨.

1.  **`Component_A_DataStreamDisplay.fig`**:
    *   **기능:** 가상의 데이터 스트림을 시각화하는 모듈. (학술적 권위 부여)
    *   **파라미터 ($P$):** $P_{stream\_rate} \in [0.5, 2.0] Hz$, $P_{data\_density} = f(t)/sin(\omega t)$.
    *   **활용:** 정보 과부하(Information Overload)를 유도할 때 사용.

2.  **`Component_B_CognitiveGapMarker.fig`**:
    *   **기능:** 논리적 간극(Cognitive Gap)을 시각적으로 강조하는 영역. (사용자 주의 분산/집중 유도)
    *   **파라미터 ($P$):** $P_{gap\_intensity} \in [0, 1]$ (최대 1), $P_{highlight\_duration} = T_{delay}$.
    *   **활용:** '하지만 왜 그럴까?'라는 질문이 생기는 순간에 배치.

3.  **`Component_C_TransitionErrorOverlay.fig`**:
    *   **기능:** 시스템의 오류나 불안정성을 흉내내는 오버레이 레이어. (USP 핵심)
    *   **파라미터 ($P$):** $P_{jitter\_amplitude} \in [1, 5] pixels$, $P_{flicker\_frequency} \in [8, 20] Hz$.
    *   **활용:** VTM_TRIGGER 직전 또는 핵심 개념 전환 시 필수적.

---
## ✨ II. 동적 효과 에셋 (Effects/)
### A. Jitter/Flicker 기술 사양서 (Technical Spec)
**파일:** `Effect_JitterMath.json`
```json
{
  "effect": "Jitter",
  "description": "좌표계의 무작위 노이즈 변동 효과.",
  "params": {
    "P_amplitude": "A * cos(t) + B * sin(t)",
    "P_frequency": "f0 + 2*rand(-1, 1)",
    "P_decay": "e^(-k*t)"
  },
  "implementation_note": "Jitter는 모든 컴포넌트의 바운딩 박스에 적용되어야 함."
}
```

**파일:** `Effect_FlickerMath.json`
```json
{
  "effect": "Flicker",
  "description": "광도(Luminosity)의 급격한 변화.",
  "params": {
    "P_period": "1 / f (Hz)",
    "P_depth": "L_{min} + L_{max} * sin(2\pi f t)",
    "P_randomness": "0.1 * rand()"
  },
  "implementation_note": "Flicker는 비주얼 노이즈 발생 시, 강제적으로 켜고 꺼지는 타이밍에 활용."
}
```

### B. 에셋 폴더 구조
`./Assets/`: (필요한 모든 벡터 및 텍스처 원본 파일)
*   `Indigo_Grid_Texture_HighRes.png`
*   `Gold_Aged_Paper_Grain.jpg`
*   `SystemError_Signal_Waveform.svg`

---
## 📐 III. 최종 Mockup 레이아웃 (Layouts/)
**파일:** `VTM_TRIGGER_Mockup_Template.fig`
*   **구조:** [Component\_B] (Cognitive Gap Marker)가 중심을 잡고, 배경에 [Component\_A]의 데이터 스트림이 불안정하게 투사됨.
*   **연출 지침:** 이 템플릿은 **최소한 3개의 State Transition Point**를 포함해야 함. 각 전환점마다 `Effect_JitterMath`와 `Effect_FlickerMath`가 동시에 발동하여 시각적 충격(Shock Value)을 극대화할 것.
