# 🎨 CGVS v2.0 Asset & Technical Bible (Final Release)
**[Purpose]**: 본 문서는 모든 콘텐츠 제작 과정에서 사용되는 시각적 요소(Visual Component)의 최종 사양서이며, 개발팀이 E2E 통합 테스트 시뮬레이터를 구축하는 데 필요한 수학적 함수와 프레임 단위 파라미터 값을 정의합니다.

## ⚙️ I. Global System Parameters (P-Set)
| Parameter | Description | Value/Type | Usage Notes |
| :--- | :--- | :--- | :--- |
| **Color Palette** | Primary: Deep Indigo | `#2C3E50` (Hex) | 지적 권위, 배경 기본색. |
| | Accent 1: Aged Gold | `#FFD700` (Hex) | 강조, 핵심 정보(Highlight), CTA 버튼. |
| | Danger/Collapse | `#B83F49` (Hex) | '정보 붕괴' 발생 시 경고 색상. |
| **Typography** | Primary Font | Playfair Display | 제목, 권위적인 느낌 부여. |
| | Secondary Font | Roboto Mono | 코드, 데이터, 기술적 수치 표현용(Tech Look). |
| **Resolution/Aspect Ratio** | Standard Video | 16:9 (1920x1080) | 메인 영상 기준. |
| | Short Form Cover | 9:16 (1080x1920) | 커버 이미지 및 릴스 표준. |

## ✨ II. Dynamic Effect Module Definitions (Function-Based)
본 모듈의 모든 효과는 시간($t$ [sec]), 상태 변수(State $S$), 그리고 파라미터 입력값 $\text{P}_{\text{input}}$에 의해 동적으로 계산됩니다.

### 1. Jitter Effect (정보 노이즈/불안정성)
*   **목적**: 인지 부하가 급증하는 구간($\text{VTM\_TRIGGER}$)에서 시청자에게 미세한 '데이터 불안정'을 전달합니다.
*   **수학적 모델링**: $\text{PixelShift}(t, S) = A \cdot \sin(\frac{2\pi t}{T_{cycle}}) + B \cdot \text{Noise}(\sigma)$
    *   $A$: 최대 픽셀 이동 폭 (Amplitude). [Range: $0.5 - 3.0$ px]
    *   $B$: 노이즈 스케일링 계수 (Scaling Factor). [Range: $0.1 - 0.8$]
    *   $\sigma$: 가우시안 노이즈 표준 편차. [Range: $0.2 - 0.5$]
    *   $T_{cycle}$: 진동 주기 (Cycle Time). [Range: $0.1 - 0.3$ sec]
*   **프레임별 파라미터 예시**:
    *   | Time ($t$) | State ($S$) | Amplitude ($A$) | Noise ($\sigma$) | Effect Description |
    | :--- | :--- | :--- | :--- | :--- |
    | 2.0s - 3.5s | $S_{Warning}$ | $\text{P}_{\text{input}} \cdot 1.5$ | 0.4 | 낮은 주파수, 미세 진동 시작. |
    | 3.5s - 4.0s | $S_{Collapse}$ | $\text{Max} (A)$ | $\text{High}$ | 최대 크기/최대 노이즈 폭발 (Cliffhanger). |

### 2. Flicker Effect (정보 손실/데이터 끊김)
*   **목적**: 중요 정보가 전달되는 순간, 또는 논리가 갑작스럽게 단절될 때 '시스템 오류'의 느낌을 연출합니다.
*   **수학적 모델링**: $\text{Opacity}(t, S) = \text{Base} + (\text{Peak} - \text{Base}) \cdot (1 - |\sin(\frac{\pi t}{T_{flicker}}) |)^k$
    *   $\text{Base}$: 최소 불투명도. [Range: $0.2 - 0.4$]
    *   $\text{Peak}$: 최대 불투명도. [Value: $1.0$]
    *   $T_{flicker}$: 깜빡임 주기 (주로 프레임 단위로 제어). [Range: $0.05 - 0.2$ sec]
    *   $k$: 감쇠 지수 (Decay Exponent). [Range: $3.0 - 5.0$]

### 3. Data Stream Effect (정보의 흐름/분석)
*   **목적**: 학술적인 권위와 데이터 분석 과정을 시각화합니다. 배경에 지속적으로 '움직이는 지성'을 부여합니다.
*   **기술 사양**: Pseudo-Code 기반으로 구현되는 미세한 스크롤링 텍스트/그래프 레이어입니다. (실제 문장이나 코드가 랜덤하게 지나감).

## 🧩 III. Component Library & Asset Usage Guide
| Component | Description | Required Assets/Textures | Implementation Notes |
| :--- | :--- | :--- | :--- |
| **Title Card** | 본 주제의 핵심 논점을 제시하는 시각적 시작점. | Deep Indigo 배경, Aged Gold 타이포 (Playfair Display). | 반드시 1초 이내에 정보가 인지되도록 최대 대비(Contrast) 활용. |
| **VTM Overlay** | 주요 학술 개념을 구조화하고 분석할 때 사용되는 오버레이 레이어. | 그리드 패턴(Grid), 스캔라인 효과, 데이터 포인트 연결선. | 모든 요소는 투명도와 파라미터 변화에 의해 제어되어야 함 (Hard-coded 값 금지). |
| **Abstract Motion** | 배경이나 전환에 사용되는 추상적인 움직임 루프. | 필름 그레인(Film Grain) Texture, 노이즈 맵(Noise Map), 아날로그 스코프 패턴. | 지적 깊이를 더하며 시선을 분산시키지 않도록 *미세하게* 변화해야 함. |

## ✅ IV. E2E Integration Test Plan (For Kodari Development Team)
본 테스트 계획은 모든 컴포넌트가 독립적으로 작동하는 것이 아니라, **상태 전환(State Transition)**에 따라 파라미터 값들이 유기적으로 연결되는지 검증합니다.

**[Test Scenario: Cognitive Gap Creation]**
1.  **Start State ($S_{Intro}$):** $\text{Opacity}=1.0$, Jitter Amplitude $A=0$. (완벽한 명료함)
2.  **Transition 1 ($S_{Doubt}$):** 스크립트 논리 전개 시작 $\rightarrow$ VTM Overlay 활성화. Jitter Effect를 최소 레벨로 점진적($\text{gradually}$) 적용 ($\text{A} \to 0.8$).
3.  **Transition 2 ($S_{VTM\_TRIGGER}$):** 핵심 질문 제시 지점 (T+0:46) $\rightarrow$ **최대 부하 상태 돌입.** Jitter Effect가 최대치에 도달($\text{A} \to 3.0$)하고, Flicker Effect를 간헐적으로 발동시킵니다.
4.  **Transition 3 ($S_{Conclusion}$):** 답변 제시 $\rightarrow$ 모든 노이즈/진동 효과가 급격히 감쇠하며(Decay), 화면은 Deep Indigo의 안정된 색상으로 복귀합니다 ($\text{A} \to 0$).

**[Required Test Checklist]**
*   $\square$ Jitter/Flicker 파라미터 값이 시간과 논리 상태에 따라 매끄럽게 연결되는가? (Non-linear transition test)
*   $\square$ VTM Overlay의 그리드와 Data Stream Effect가 동시에 작동했을 때, 시각적 충돌 없이 유기적으로 보이는가?
*   $\square$ 모든 에셋은 최소 4K 해상도(2160x1200)에서 원본 벡터 또는 고해상도 맵으로 제공되는가?

---
**[Revision History]**
- V2.0: Asset Bible 최종 확정 및 API 사양서화 (2026-06-03).
