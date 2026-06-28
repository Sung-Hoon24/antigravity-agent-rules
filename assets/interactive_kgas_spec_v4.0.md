# 🌐 [KGAS v3.0] Anomaly Signal Renderer 기술 통합 마스터 사양서 (버전 4.0)

**최종 승인일:** 2026-06-04
**작성자:** Designer Lead
**적용 범위:** 모든 비주얼 에셋 컴포넌트, 특히 S2(Knowledge Gap/Collapse) 상태 전환 로직
**개발 요구사항:** 모든 시각 변화는 반드시 `useAudioAnalysis` Hook이 제공하는 실시간 파라미터에 종속되어야 합니다.

---

## 1. 시스템 개요 및 상태 정의 (State Machine Logic)

| State | 이름 | 트리거 조건 (Trigger) | 주된 비주얼 연출 목표 |
| :--- | :--- | :--- | :--- |
| **S0** | Normal Flow | $\Delta F$ 안정적, $V_A$ 정상 범위 유지. | 기본 시각 언어(Deep Indigo/Gold). 깨끗한 데이터 흐름. |
| **S1** | Warning (Pre-Gap) | **[Primary Trigger]** 주파수 변화율 ($\Delta F$)이 임계치($\text{Threshold}_F$)를 초과하며 상승세 유지. 또는 진폭 분산($V_A$)이 급격히 증가하기 시작함. | 시각적 노이즈 증가, 경고 컬러 오버레이 (Glitch Violet). 데이터 흐름의 떨림(Jitter) 발생. |
| **S2** | Critical (Knowledge Collapse) | **[Forced Trigger]** $V_A$가 최저 임계치($\text{Threshold}_{VA}$) 이하로 하락하는 동시에, $\Delta F$가 급격히 붕괴 지점(Collapse Point)에 도달함. | 시스템 기능 정지/파열 메타포. 구조적 오류 시각화. **강제 동기화 필수.** |

---

## 2. 핵심 오디오 파라미터 정의 및 임계치 (Quantifiable Inputs)

| 파라미터 명 | 기호 | 정의 | S1 진입 조건 ($\text{Threshold}_{S1}$) | S2 진입 조건 ($\text{Threshold}_{S2}$) |
| :--- | :--- | :--- | :--- | :--- |
| **주파수 에너지 변화율** | $\Delta F$ | 시간 대비 주파수의 평균 제곱근 변화량 (Hz/sec). | $\Delta F > 5 \text{ Hz/sec}$ & 추세가 상승일 때. | $\Delta F < 0.5 \text{ Hz/sec}$ (**갑작스러운 급락**) |
| **진폭 분산** | $V_A$ | 특정 시간 구간 내 진폭 값의 표준 편차 (Amplitude Std Dev). | $V_A > 0.4 \text{ (Normal Max)}$ & 지속시간 1초 초과. | $V_A < 0.15 \text{ (기준점 대비 극도로 안정화/붕괴)}$ |
| **템포 불균형 지수** | $TDI$ | 오디오 BPM 변화율에 따른 예측 시간 간격의 편차. | $TDI > 0.2$. | $TDI > 1.5 \text{ (시스템 타이밍 이탈)}$. |

---

## 3. S2 상태 전환 시각 사양서 (The Collapse Mechanics)

S2는 단순히 '어두워지는 것'이 아니라, **데이터 자체가 파괴되는 물리적/논리적 과정**을 표현해야 합니다. 개발자는 아래의 *파라미터 변화*를 따라 애니메이션 루프를 구현해야 합니다.

### A. 시퀀스 구성 (Timeline Definition)
1.  **[T=0s] - State Shift:** S1 $\rightarrow$ S2 전환이 감지됨과 동시에, 전체 비주얼 필드에 **Glitch Violet (#9B59B6)** 색상의 미세한 노이즈(High-Frequency Noise Overlay)가 겹쳐짐.
2.  **[T=0s ~ T+1s] - Frequency Collapse:** $\Delta F$ 임계치 도달과 동시에, 화면의 모든 데이터 라인(Vector Lines)이 **진폭 $V_A$에 반비례하여 수평/수직으로 붕괴(Collapse)**하기 시작함.
    *   **기술 디테일:** 파형은 사인파 형태를 유지하되, 주기는 급격히 길어지고 진폭의 변화율이 0에 수렴하며 '정지'하는 것처럼 보이게 합니다.
3.  **[T+1s ~ T+3s] - Structural Failure:** 데이터 흐름을 담당하던 배경 그리드(Grid)가 **WebGL 기반의 왜곡(Distortion)** 효과를 일으키며, 마치 코드가 멈추고 오버플로우 된 것처럼 사각형 단위로 '깨지는' 애니메이션이 반복됩니다.
    *   **필수 요소:** 화면 중앙에 `[ERROR: KNOWLEDGE GAP DETECTED]` 문구의 아날로그/디지털 오류 그래픽을 오버레이합니다.
4.  **[T+3s] - Transition End:** 파괴가 최고조에 달하는 지점에서, 모든 시각 효과가 일순간 **완벽한 블랙아웃(Blackout)** 처리되며 다음 장면으로 연결됩니다.

### B. 개발 가이드라인 (Developer Notes)
*   이 사양서는 애니메이션의 *시작점*, *종료점*, 그리고 *그 사이를 지배하는 수학적 변화*를 정의합니다. 단순 키프레임(Keyframe) 타이밍에 의존해서는 안 됩니다.
*   **권장 구현 기술:** React-Three-Fiber (WebGL 기반) 또는 Web Audio API의 파라미터 제어와 연동된 SVG 애니메이션 루프가 필수적입니다.

---
