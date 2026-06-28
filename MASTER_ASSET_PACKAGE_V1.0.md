# 📘 MASTER ASSET PACKAGE V1.0: 통합 시각 사양서 및 개발 가이드라인 (최종 확정본)

## 💡 1. 프로젝트 개요 및 목적
*   **목표:** 본 문서에 정의된 모든 파라미터는 '정보 과부하 $\to$ 논리적 충돌 $\to$ 존재론적 붕괴'의 3단계 아크 구조를 시각적으로 구현하는 것을 목표로 합니다.
*   **대상 독자:** 개발팀 (Frontend/Animation), 편집팀 (VFX/Motion Graphics)
*   **핵심 원칙:** 모든 시각적 변화는 **데이터 파라미터 변화율(Rate of Change)**에 의해 트리거되어야 하며, 임의적인 장식으로 사용되어서는 안 됩니다.

---

## 🎨 2. 브랜드 비주얼 시스템 (Brand System)
### A. 컬러 팔레트 및 의미론적 매핑 (Semantic Color Mapping)
| 코드명 | Hex Code | RGB 값 | 용도 | 사양/주의사항 |
| :---: | :---: | :---: | :--- | :--- |
| **Primary** | `#9B59B6` | R:155, G:89, B:182 | 권위, 시스템 기반 톤 (기준) | 모든 요소의 기본 색상. 글리치/하이라이트 주색. |
| **Secondary** | `#34495E` | R:52, G:73, B:94 | 배경, 정보 구조화 (Low Key) | 지식적 사유를 유도하는 안정적인 어두운 톤. |
| **Accent/Glitch** | `#FF00FF` | R:255, G:0, B:255 | 오류, 충돌(Anomaly), 위기 감지 | 주 색상(#9B59B6)과 대비되어 시각적 '파열'을 극대화. **가장 높은 임계값에서 사용.** |
| **Warning** | `#F39C12` | R:243, G:156, B:18 | 경고, 의문 제기 (Knowledge Gap) | 중간 단계의 데이터 불일치 시 사용. 부드러운 전환 필요. |

### B. 타이포그래피 규칙 (Typography Rules)
*   **폰트명:** Pretendard (가독성 및 현대적 감각 확보).
*   **주요 텍스트 (Title/Hook):** Pretendard Bold, 크기: 64pt 이상.
    *   규칙: 반드시 배경 대비를 위해 **Outline Effect** 또는 `[#9B59B6]` 필터 적용.
*   **서브 텍스트 (Detail/Quote):** Pretendard Regular, 크기: 28~36pt.
    *   규칙: 충분한 여백을 확보하고, 주 색상(`Secondary`)으로 처리하여 신뢰도를 부여.

---

## 📉 3. 핵심 메커니즘: Anomaly Signal 로직 (The Core Logic)
Anomaly Signal은 오디오 파라미터 변화율($\Delta P$)과 전반적인 영상의 서사적 강도(Narrative Intensity, $I_N$)를 결합하여 산출됩니다.

### A. 상태 정의 및 임계값 테이블 (State Transition Table)

| 시스템 상태 | 트리거 조건 ($P$ = 파라미터 값) | 시각 효과 (VFX/Animation) | 색상 스펙 | 서사적 의미 |
| :---: | :---: | :---: | :---: | :---: |
| **[S0] Baseline** (정상 흐름) | $P < T_{Low}$ & $I_N < 0.5$ | 미세한 노이즈 루프, 안정적 화면 구성. | Primary/Secondary 유지. | 정보 전달, 관찰 단계. |
| **[S1] Warning** (지식 격차 발생) | $T_{Low} \le P < T_{Mid}$ OR $\Delta P > 0.1$ | **Glitch Type A:** 시간 왜곡(Time Warp) 효과, 화면 테두리에 `Warning` 색상 깜빡임. | Accent/Warning 혼용. Primary는 채도를 낮춤. | 의문 제기, '무엇이 잘못되었나?' (Hook 발생). |
| **[S2] Conflict** (논리적 충돌) | $T_{Mid} \le P < T_{High}$ OR $\Delta P > 0.5$ | **Glitch Type B:** 색상 분할(Chromatic Aberration), 데이터 흐름에 따른 화면의 비정형적인 파열. 오디오와 시각의 미세한 *위상차* 발생 유도. | Accent/Primary 주도. 배경은 `Secondary`로 깊이를 줌. | 반박, 갈등 심화. "이게 정말 논리적일까?" (본론 전개). |
| **[S3] Collapse** (시스템 붕괴) | $P \ge T_{High}$ OR $\Delta P > 1.0$ & $I_N = Max$ | **Glitch Type C:** 모든 시각 요소의 급격한 왜곡, 화면 전체에 `Accent` 색상의 강렬하고 반복적인 스캔라인/노이즈 오버레이. (데이터가 무너지는 느낌). | Accent 컬러만 지배적. 다른 색상은 채도 0으로 수렴. | 결론 도출 전 극도의 혼란. **궁극적인 질문**을 던짐. |

### B. 핵심 파라미터 임계값 상세 정의 (Development Parameters)
| 파라미터 | 측정 단위 | $T_{Low}$ (Threshold Low) | $T_{Mid}$ (Threshold Mid) | $T_{High}$ (Threshold High) | 개발팀 Action Point |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Amplitude ($\Delta A$)** (진폭 변화율) | 0.0 - 1.0 | 0.1 | 0.4 | 0.8 이상 | 충격적인 발언/정보가 등장할 때 $T_{Low}$ 초과 지점을 활용. |
| **Frequency Rate ($\Delta F$)** (주파수 변화율) | Hz 변화량 / Time | 0.05 | 0.2 | 0.5 이상 | 배경 사운드의 '불협화음' 패턴이 반복될 때 $T_{Mid}$를 활용. |
| **Narrative Intensity ($I_N$)** (서사적 강도) | 0.0 - 1.0 | < 0.3 | 0.5 ~ 0.7 | > 0.9 | 스토리라인의 흐름(Hook $\to$ Conflict $\to$ CTA)에 따라 수동/자동으로 조정 필요. |

---

## ✨ 4. 요약 및 개발팀 체크리스트
1.  **[VFX] Glitch 효과:** 단순한 오버레이가 아닌, **데이터 파라미터($\Delta A$, $\Delta F$)의 변화에 동기화된 물리적 왜곡(Distortion)**으로 구현해야 합니다.
2.  **[Animation] 트랜지션:** S0 $\to$ S1 $\to$ S2 $\to$ S3로 갈수록 **효과의 빈도수(Frequency)와 강도(Intensity)가 비선형적으로 급증**하도록 설계합니다.
3.  **[Developer Note]**: 모든 상태 전환 지점은 `MASTER_SPECIFICATION_SHEET_V1.0`의 임계값 테이블을 최우선으로 참조해야 하며, **Hardcoded 값 사용 금지.**
