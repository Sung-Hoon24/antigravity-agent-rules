# 🧩 VTM\_TRIGGER 시각적 파라미터 제어 매뉴얼 (v4.0)

## 📜 개요 및 적용 범위
본 매뉴얼은 메인 영상의 논지 전개 과정 중, 시청자의 지식적 간극(Cognitive Gap)이 최대치에 도달하는 'The Paradox Shift' 순간을 위한 모든 시각/애니메이션 파라미터를 정의합니다. 이 모듈은 단순한 효과가 아닌, **논리적 트리거** 역할을 수행해야 합니다.

*   **최종 버전:** v4.0
*   **대상 콘텐츠:** 4주 심화 시리즈 메인 영상 (VTM\_TRIGGER 지점)
*   **목표:** 시청자에게 극도의 '지적 압박감'과 '해결되지 않은 의문'을 부여하여 본편(Paid Gate)으로의 이탈 방지 및 유입 최적화.

---

## ⚙️ I. 시간 축 정의 (Timeline Mapping)
| 구간 명칭 | 스크립트 마커 | 예상 시간대 (T-Time) | 목표 논리 상태 변화 | 비주얼 전환 단계 |
| :--- | :--- | :--- | :--- | :--- |
| **[Pre-Trigger]** | L1.3 ~ L1.5 ("하지만...") | T + 0:00 to T + 0:45 | 정보 습득 $\rightarrow$ 불일치 감지 (Mild Confusion) | 아카이브 탐색 모션 루프 유지, 색상 안정화. |
| **[Trigger Point]** | L1.5 ("...그럼 이것은?") | T + 0:46 to T + 1:05 | 논리적 충격 $\rightarrow$ 존재론적 질문 (Paradox Shock) | **VTM_TRIGGER 활성화.** 모든 파라미터가 급변 및 과부하 상태 진입. |
| **[Post-Trigger]** | L2.1 ("이 간극은...") | T + 1:06 ~ End | 혼란 $\rightarrow$ 깊은 사색 (Deep Introspection) | 시각적 요소들이 '분해'되거나 '정지된 아카이브' 상태로 전환. |

---

## ✨ II. 핵심 비주얼 에셋별 파라미터 제어 상세 명세

### 1. 배경 레이어: 아카이브 노이즈 (Background Archive Noise)
| 파라미터 | [Pre-Trigger] 값 | [Trigger Point] 변화 함수 및 범위 | [Post-Trigger] 값 | 비고 |
| :--- | :--- | :--- | :--- | :--- |
| **Noise Intensity** | `0.1` (Low Grain) | $\text{Intensity}(t) = 0.3 + 0.2 \cdot \sin(\frac{\pi}{t_{rel}})$. $t_{rel} \in [0, 1]$ 초 단위로 증폭. | `0.05` (Minimal/Frozen) | **핵심:** 진동 주파수(Frequency)가 급증하며 시각적 과부하 유도. |
| **Color Overlay** | `#2E3A48` (Deep Indigo Base) | $\#6B139A$ $\rightarrow$ $\#FF5733$ (High-Contrast Magenta/Orange Shift). | `#0A0D13` (Near Black, Low Luminescence) | 충격 순간에 '경고'를 의미하는 색상으로 강제 전환. |
| **Texture** | Film Grain Loop A | Glitch Effect 2단계 (Pixel Separation & Chromatic Aberration). | Static Grid / Data Stream Overlay | 노이즈가 체계적인 '데이터 손실' 패턴을 따르도록 정의. |

### 2. 핵심 오브젝트: 논지 그래프/패러독스 구조체 (Logic Graph)
| 파라미터 | [Pre-Trigger] 값 | [Trigger Point] 변화 함수 및 범위 | [Post-Trigger] 값 | 비고 |
| :--- | :--- | :--- | :--- | :--- |
| **Scale/Position** | `Scale = 1.0`, Position: 중심 축 유지. | $\text{Scale}(t) = 1 + A \cdot \sin(\omega t)$ (Amplitude $A=0.5$, Angular Freq $\omega=$ Fast Oscillation). 중앙을 기준으로 급격히 **팽창 후 수축**하는 동작 구현. | Scale $= 0.8$. 위치가 화면 가장자리로 천천히 이동 (Fade Out). | 시각적 에너지를 최대치로 분산시키며 불안정성을 표현. |
| **Line Color** | `#A9B7CC` (Soft Grey) | $\#F4D03C$ $\rightarrow$ `#FF5733` (Yellow/Orange 경고색). | `#6B139A` (Deep Indigo Revival) | 충격 순간에 가장 눈에 띄는 '경보' 색상 사용. |
| **Animation** | Smooth Interpolation (Ease-out) | Jitter Effect & Rapid Expansion / Decay Curve 적용. | Slow Fade Out, Stuttering Motion. | 매끄러움 $\rightarrow$ 불안정함 $\rightarrow$ 정지된 데이터로 전환. |

### 3. 타이포그래피/텍스트: 질문의 폭발 (Question Burst)
| 파라미터 | [Pre-Trigger] 값 | [Trigger Point] 변화 함수 및 범위 | [Post-Trigger] 값 | 비고 |
| :--- | :--- | :--- | :--- | :--- |
| **폰트/스타일** | 세리프(Serif) 계열, 중앙 정렬. | `Typeface = Mono/Glitch Font`. 텍스트가 여러 레이어로 중첩되어 동시에 출력됨 (Overlapping Text Layers). | 산만하게 분산된 단어들 $\rightarrow$ 하나의 질문으로 응축 (`The Paradox?`). | 지적 혼란을 시각화하기 위해 다중 노출(Ghosting) 기법 필수. |
| **텍스트 변형** | 일반적인 Fade In/Out. | **Scale & Rotation:** 텍스트가 무작위 각도($\theta \in [0, 360^\circ]$)로 폭발하듯 나타나며 크기(Scale)가 급격히 변화함 ($\text{Scale} = e^{k t}$). | 단일 질문에 집중하여 중앙으로 다시 모여 안정화됨. | 충돌 에너지를 표현하는 가장 중요한 파라미터입니다. |
| **색상** | `#E0E5F4` (Off-White) | 배경 대비를 극대화한 $\#FFFFFF$ 또는 형광색 계열의 깜빡임 (`Blink Rate: 12Hz`). | 질문 문구만 강조된 노란색/금색(`Aged Gold`)으로 전환. |

---
## 📌 III. 요약 및 개발 가이드라인 (Action Items)
1.  **전환 주파수:** Trigger Point 구간에서는 모든 파라미터의 변화율(Derivative)을 최대화하여 '과부하' 상태를 연출해야 합니다.
2.  **컬러 대비 원칙:** 안정된 아카이브 톤 (`Deep Indigo`) $\rightarrow$ 충격적 경고 톤 (`Magenta`/`Orange`) $\rightarrow$ 사색적 질문 톤 (`Aged Gold/Black`)의 명확한 **3단계 컬러 변화**를 반드시 구현해야 합니다.
3.  **애니메이션 루프:** 배경 노이즈와 그래프 오브젝트는 독립적인 무작위성(Randomness)을 가지되, 트리거 시점에는 이 무작위성이 시스템적으로 '폭주'하는 것처럼 보일 때야 합니다.
