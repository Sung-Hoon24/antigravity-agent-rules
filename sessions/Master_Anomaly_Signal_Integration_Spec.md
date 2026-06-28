# 🚨 MASTER ANOMALY SIGNAL INTEGRATION SPECIFICATION (v1.0)

## 📄 목적
본 문서는 콘텐츠의 모든 시각적 요소(V-CORE 모듈, 데이터 스트림, 배경 그래픽 등)가 오디오 파라미터 변화를 기준으로 **'Anomaly Signal'**을 발생시키고 해소하는 전체적인 시스템 동작 규격을 정의합니다. 이는 개발자가 통합 테스트에 필요한 최종 사양서이며, 모든 에셋의 연동 지점과 타이밍 프레임을 확정합니다.

## 🔊 I. 핵심 트리거 및 동기화 원칙 (The Core Engine)
모든 시각적 변화는 단일 오디오 파라미터 $\text{P}_{Audio}$에 의해 제어됩니다.

1.  **트리거:** 사운드의 **주파수(Frequency, F)**가 임계값($F_{Critical}$)을 초과하거나 급격히 하강할 때 발생합니다. (예: 설명이 논리적 난제에 도달하는 순간의 주파수 변화).
2.  **신호 유형:**
    *   **정상 상태 (Normal State):** $\text{P}_{Audio}$가 안정적일 때. (Low-frequency hum, Deep Indigo 배경 톤 유지)
    *   **Anomaly Signal 발생 (Triggered Event):** $F > F_{Critical}$ 또는 급격한 진폭 변화 시. (Error/Distortion 패턴 활성화)
3.  **동기화 공식:** $\text{Visual Intensity} \propto |\frac{d\text{P}_{Audio}}{dt}|$

## 🎨 II. 사양서 구성 요소 및 디자인 파라미터

### A. Anomaly Signal Overlay (최상위 레이어, 필수)
| 항목 | 세부 정의 | 기술 스펙 (SVG/Lottie Keyframes) | 연동 지점 |
| :--- | :--- | :--- | :--- |
| **컬러 코드** | $\text{Hex}: \#FF4500$ (Anomaly Orange) & $\#1E90FF$ (Error Blue) | **SVG Path:** `M 0,0 L 100,0 C 120, -50 80, -50 100, 0` (파동 형태의 왜곡 패턴 반복). | $\text{P}_{Audio}$ 변화율이 최대일 때. 화면 전체에 '스캔라인' 효과로 오버레이됨. |
| **효과** | 시각적 노이즈, 필름 그레인 변형, 데이터 패킷 누락(Missing Data) 패턴 발생. | **Keyframe:** $\text{Opacity}(t): \text{EaseOut}(\sin(\frac{\pi}{T} t))$; $1\text{s}$ 지점에서 0% $\to$ 80%로 급증. | 모든 콘텐츠의 전환점 및 논리적 충돌 구간. |

### B. V-CORE Module (중간 레이어, 데이터 시각화)
| 항목 | 세부 정의 | 기술 스펙 (SVG/Lottie Keyframes) | 연동 지점 |
| :--- | :--- | :--- | :--- |
| **기능** | 학술 개념의 구조적 관계 및 논리 흐름을 모듈 형태로 시각화. | **Component:** `[Node]` (원형), `[Edge]` (연결선). Node 크기는 $\text{P}_{Audio}$의 진폭(Amplitude)에 비례하여 실시간 변동. | 사운드가 특정 개념/주제 설명 구간을 지날 때. |
| **Anomaly 반응** | 연결선($\text{Edge}$)이 파열되거나, 노드 사이의 데이터 전송량이 급증하며 과부하 상태를 표현. | **Keyframe:** Edge Path Interpolation Failure (점선 $\to$ 끊김). Node Color: $\#FF4500$. | 개념 간의 논리적 비약 또는 반박 지점이 나올 때. |

### C. Background/Aesthetic Layer (배경, 낮은 레이어)
| 항목 | 세부 정의 | 기술 스펙 (SVG/Lottie Keyframes) | 연동 지점 |
| :--- | :--- | :--- | :--- |
| **색상** | Deep Indigo ($\#191970$) 기반의 미세한 패턴 루프. | **Pattern:** 아날로그 스코프 그리드(Grid Overlay). 좌표계에 지속적인 `Scanline` 효과 적용. | 영상 전체 구간 (지속성 확보). |
| **Anomaly 반응** | 배경 그리드가 왜곡되거나, 노이즈가 섞여 데이터 손실처럼 보이게 변형됨. | **Keyframe:** Grid distortion $\text{Scale}(t)$: $1.0 \to 1.05$ (미세한 진동). $|F_{Critical}|$ 초과 시 패턴 전체가 일시적으로 `#FF4500`으로 오버라이드(Override). | Anomaly Signal 발생 직전/직후의 분위기 고조. |

## 🎬 III. 시간 프레임 및 에셋 연동 플로우 (Integration Timeline)
이 표는 스크립트 내 특정 이벤트가 발생했을 때, 어떤 모듈이 어떻게 반응해야 하는지 정의합니다.

| Time Marker ($\text{T}$) | 오디오 파라미터 변화 ($\Delta \text{P}_{Audio}$) | 시나리오/내러티브 역할 | 🎨 필수 액션 (Asset) | 애니메이션 사양 (Keyframe Logic) |
| :--- | :--- | :--- | :--- | :--- |
| $\text{T}_{0} \to \text{T}_{1}$ (도입부, Hook) | 안정적 $F$, 낮은 진폭. | 지식적 결핍 제시. 주제 소개. | Background Layer만 활성화. V-CORE 모듈은 미니멀하게 2개 노드만 표시. | Deep Indigo 배경 위로 미세한 스코프 그리드가 반복됨 (Loop). **Anomaly Signal: Off.** |
| $\text{T}_{1} \to \text{T}_{2}$ (정보 제시, 설명) | $F$ 안정적, 중간 진폭 유지. | 학술 개념 A와 B를 연결하며 논리 전개. | V-CORE 모듈 활성화. Edge가 A $\to$ B로 부드럽게 연결됨. | Node 크기는 $\text{P}_{Audio}$의 Amplitude에 따라 선형적으로 증가/감소 (Smooth Transition). **Anomaly Signal: Off.** |
| $\text{T}_{2} \to \text{T}_{3}$ (논리적 충돌 지점) | $F$가 급격히 상승하거나(Jump), 진폭이 0으로 떨어짐($\text{Decay}$). ($\Delta \text{P}_{Audio}$ Max) | '하지만, 이 개념에는 오류가 있다!'는 반론 제기. 시스템 실패 메타포 극대화. | **Anomaly Signal (A) ON.** V-CORE Edge가 끊어지며 파열됨. Background Layer 왜곡. | 1. A: $0 \to 80\%$ Opacity 급증, 노이즈 패턴 활성화. 2. B: 모든 Node의 색상이 `#FF4500`으로 플래시. 3. C: 스코프 그리드가 일시적으로 깨지며 왜곡됨 (Scale $>1.0$). |
| $\text{T}_{3} \to \text{T}_{4}$ (해결/전환) | $F$가 서서히 안정화되거나, 새로운 파라미터로 전환됨. ($\Delta \text{P}_{Audio}$ Min) | '이 오류는 사실 시스템의 숨겨진 진실이었다.' 결론 도출. | Anomaly Signal 급격히 소멸(Fade Out). V-CORE 모듈에 새로운 연결고리 노드가 추가됨. | 1. A: Opacity가 $\text{EaseOut}$ 함수를 따르며 $80\% \to 0\%$로 감속적으로 감소. 2. 모든 요소가 안정적인 Deep Indigo 톤으로 회귀하며, 다음 주제를 암시하는 빛의 연결고리(Light Beam)가 생성됨. |

---
**[기술 구현 메모]**
*   모든 파라미터($F_{Critical}$, $\text{T}_{1}, \text{T}_{2} \dots$)는 JSON 기반 데이터셋으로 관리되어야 합니다.
*   Lottie/SVG 파일은 반드시 `Timeline`과 `Trigger_ID`를 메타데이터로 포함하여, 개발자가 코드를 통해 재사용 및 테스트할 수 있도록 해야 합니다.
