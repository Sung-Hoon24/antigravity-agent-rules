# 🚀 [Production Sync Document] VTM 에셋 통합 및 미니 퍼널 활성화 전략 v1.0

## 📄 🎯 목표: Gap 1 (확신에 대한 의문) 유도 및 Mini Funnel Activation
본 문서는 Designer가 제작한 VTM 컴포넌트 라이브러리(Deep Indigo/Aged Gold 기반)를 스크립트에 논리적으로 통합하여, 시청자에게 '지금 알고 있는 것이 틀릴 수도 있다'라는 지적 의문을 강제하고 다음 콘텐츠로 유도하는 기술 설계서입니다.

## 🎬 [Scene Mapping & Trigger Points]
VTM은 단순히 배경 효과가 아니라, **정보의 파괴 순간(Moment of Disruption)**을 의미합니다. 아래는 스크립트의 핵심 논리 흐름에 따른 VTM 트리거 지점 정의입니다.

| # | 스토리 구간 (Script Timing) | 내용 요약 및 맥락 (Context) | 목표되는 감정/논리 상태 | 필수 적용 모듈 (VTM Component) |
| :---: | :---: | :--- | :--- | :--- |
| **T1** | 02:30 - 02:45 (본론 중반부 전환) | [주제 A]에 대한 일반적인 통념/학설 제시. (시청자 '확신' 상태) | 확신 → 미스터리 | `VTM_Glitch()` (DATA_CONFLICT, Intensity: 0.6-0.7) |
| **T2** | 03:10 - 03:25 (핵심 증거 제시 직전) | 기존 학설이 간과하거나 무시하는 '제3의 관점'이나 자료를 제시하며, 갑작스러운 논리적 단절 발생. | 혼란 → 지적 충격 | `ColorShift_Desync()` (SYSTEM_OVERLOAD, Duration: 1.5s) |
| **T3** | 04:00 - 04:30 (결론 직전/Mini Funnel 유도점) | 최종 결론을 내리기 위해 '누락된 핵심 전제(Missing Premise)'를 제시하며, 시청자가 스스로 의문을 품도록 강제. | 질문 → 불확실성 | `VTM_Glitch()` + [특수 노이즈] (INPUT_ERROR, Intensity: 0.8) |

## ⚙️ [기술 구현 상세 명세서 - Developer Facing]

### 1. VTM_Glitch() 활용 가이드
*   **T1 (논리 충돌):** '학설 X'를 언급하는 순간 `DATA_CONFLICT` 트리거 사용. 왜곡 패턴은 수평적(Horizontal Banding)으로, 정보의 계층적 오류를 표현해야 함.
*   **T3 (최종 의문):** 가장 강한 충격이 필요합니다. `INPUT_ERROR`와 결합하여 **전체 화면을 빠르게 파괴하는 듯한 모션**을 적용하고, 이 과정에서 '심화 분석 자료'라는 CTA가 잠깐 비쳐 보이게 설계해야 합니다.

### 2. ColorShift_Desync() 활용 가이드
*   **T2 (관점 전환):** Deep Indigo와 Aged Gold의 색상 영역이 순간적으로 어긋나면서(Chromatic Aberration), 시청자가 **"지금 보는 것이 실제 정보가 아닐 수도 있다"**는 느낌을 받도록 연출합니다.

## 🚀 [Mini Funnel Activation 로직 플로우차트]
**(T3 지점 이후의 핵심 흐름)**

1.  **[VTM_Glitch Trigger]**: 시청자가 '결정적인 결론' 직전에 도달하여 높은 몰입 상태 (Peak Interest)에 진입.
2.  **[Visual Shock]**: VTM이 최고 강도로 작동하며 정보가 파괴되는 충격 연출.
3.  **[CTA Overlap]**: 파괴의 순간(04:15-04:30) 동안, 'Mini Academic Portfolio' (심화 자료) 이미지가 노이즈와 함께 빠르게 오버레이 되어 시야에 포착됨.
4.  **[Auditory Cue]**: 배경 음악/사운드스케이프가 갑자기 멈추거나, 긴장감 있는 질문 사운드로 전환되며 **'답을 찾기 위한 노력'**을 유도.
5.  **[Final Gap Output]**: 영상이 끝날 때까지 시청자에게 '당신이 본 것은 전체 그림이 아니다'라는 인상을 남기고, 설명란의 CTA를 자연스럽게 바라보게 함.

---
**⚠️ 필요 조치:** 이 문서를 바탕으로 Writer는 T1, T2, T3 구간에 맞춰 스크립트 타이밍을 재조정하고, Designer는 해당 지점의 파라미터(Intensity/Duration)를 확정해야 합니다.
