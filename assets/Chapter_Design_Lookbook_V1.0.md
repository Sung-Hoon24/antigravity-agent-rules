# 📖 [최종 산출물] KGAS v3.0 챕터별 디자인 룩북 (V1.0)

## 🎯 목표
*   **목적:** 기술 사양서(v5.0)와 스토리라인을 통합하여, 개발팀이 모든 시각적 요소를 '코드 기반'으로 구현할 수 있는 최종 가이드라인 제공.
*   **톤앤매너:** 학술적 권위 (Academic Authority), 미스터리함 (Mystery), 첨단 기술적 불안정성 (Technological Instability).
*   **핵심 색상 팔레트:** Deep Indigo ($\text{#1A237E}$), Aged Gold ($\text{#FFC107}$), Anomaly Signal Violet ($\text{#9B59B6}$), Neutral Grid Gray ($\text{#424242}$).

---
## 🗺️ 섹션 1: 인트로/프롤로그 (The Hook - T-0s to T+5s)

*   **목적:** 시청자의 주의를 사로잡고, 영상의 주제(Knowledge Gap)에 대한 지적인 기대감을 조성.
*   **디자인 요소:**
    *   **레이아웃:** Dark Mode 기반, 중앙 집중형 텍스트 배치. 주변에는 미세한 데이터 흐름 그리드 오버레이 필수.
    *   **핵심 애니메이션 (Motion Graphic):**
        1.  **[Aged Gold] 타이포그래피 등장:** 슬라이드 인(Slide-in) 방식 대신, '스크래치 효과'를 이용해 텍스트가 표면 아래에서 드러나듯 구현.
        2.  **[Deep Indigo] 그리드 애니메이션:** 화면 전체에 미세하게 떨리는 (Sine Wave $\text{freq}=0.1\text{Hz}$) 격자 패턴을 깔아 시각적 깊이와 기술적 배경 느낌 부여.
    *   **전환점 사양 적용:** 이 구간에서는 $Threshold_1$ 임계치 변화가 없어야 함. 모든 파라미터는 $\text{Normal Operation}$ 범위 내에서 안정적으로 유지되어야 합니다.

## 🌊 섹션 2: 본론 - 논리적 충돌 (The Bridge - T+5s to T-30s)

*   **목적:** 핵심 개념을 전달하며, 점진적으로 '지식의 불완전성'에 대한 의문을 심어주는 구간.
*   **디자인 요소:**
    *   **레이아웃:** 정보 과부하(Information Density)가 높은 그리드 기반 섹션. 다양한 B-roll (오래된 아카이브, 측정 장비 등)을 삽입할 여지를 남김.
    *   **핵심 애니메이션/B-Roll:**
        1.  **[Anomaly Signal Violet] 활용:** 논리적 충돌이 언급되는 시점마다, 스펙트로그램 분석 결과나 데이터 오류 코드를 **강조색**으로 짧게 플래시(Flash) 처리합니다. (예: `ERROR_CODE: 404-KNOWLEDGE`)
        2.  **[Knowledge Gap] 시각화:** '지식의 빈 공간'을 표현할 때, 진폭($\text{Amplitude}$)이 갑자기 급감하는 파형 애니메이션(Dampening Wave)을 주파수 분석과 동기화하여 사용합니다.
    *   **전환점 사양 적용:** $\mathcal{C}_{complexity}$가 서서히 하락하며 불안정성을 유발해야 합니다. (미묘한 노이즈 추가 시작).

## 💥 섹션 3: 클라이맥스 - 존재론적 붕괴 (The Collapse - T-30s to End)

*   **목적:** 모든 것이 무너지는 절정의 순간을 시각적으로 구현하여, 충격과 경외감을 극대화.
*   **디자인 요소:**
    *   **레이아웃:** 파편화(Fragmentation)된 레이아웃. 중앙에 메시지가 남고 주변은 혼란스러운 비주얼로 가득 참.
    *   **핵심 애니메이션 (Critical Action):**
        1.  **[Anomaly Signal Violet] 폭발:** $T_{Collapse}$ 임계치 도달 시, 화면 전체가 Glitch Violet(#9B59B6)의 노이즈와 아티팩트로 뒤덮이며 데이터 붕괴를 표현합니다. (개발 사양 V5.0 참조).
        2.  **시각적 무게감:** 모든 움직임은 '무너짐'과 '진공 상태'에 초점을 맞추어, 빠르기보다는 **파국적인 느림(Catastrophic Slowdown)**을 유지합니다.
    *   **CTA 통합:** 붕괴 이후의 극도의 정적 상태에서, 깨끗한 Deep Indigo 배경 위에 Aged Gold로 간결하고 권위 있는 CTA 메시지를 배치합니다. (단순 요청 금지).

---
## 📝 요약 체크리스트 (개발자용)
1.  **[필수]** 모든 전환 애니메이션은 오디오 파라미터($\text{RMS}_{\Delta}, \Delta f, \mathcal{C}_{complexity}$)에 **코드 기반으로 강제 동기화** 되어야 함.
2.  **[필수]** 색상 코드는 Deep Indigo & Aged Gold를 주조색으로 사용하며, 위기 상황에서만 Anomaly Signal Violet을 사용함.
3.  **[검토 요청]** 레오에게 최종 스크립트의 시간대별 전환 마커(Time Marker) 리스트를 전달받아, 각 섹션의 시작/종료 시간을 확정해야 함.
