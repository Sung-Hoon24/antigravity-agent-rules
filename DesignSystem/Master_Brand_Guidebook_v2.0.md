# 🎨 마스터 브랜드 가이드북 (Project Name: Chronos-Engine) v2.0

## 📄 개요 및 목표
이 가이드는 유튜브 채널의 모든 시각적 요소(썸네일, 인트로 카드, 릴스 오버레이, 본편 영상 UI)에 일관성을 부여하는 최종 디자인 시스템입니다. 핵심 목표는 **'지식적 권위(Deep Indigo)'**와 **'기술적 오류/Anomaly(Electric Cyan)'**의 결합을 통해 시청자에게 '궁금증 유발 (Knowledge Gap)'과 '신뢰성 확보'를 동시에 전달하는 것입니다.

## 💡 디자인 원칙
1. **톤앤매너:** 친근함, 똘똘함 (권위적 지식 + 기술적 경고)
2. **핵심 메타포:** 시스템의 실패(System Failure), 데이터 파라미터의 붕괴(Collapse).
3. **정보 계층 구조:**
    *   **헤드라인/Hook:** 가장 강렬한 대비를 사용하여 시선을 즉시 사로잡는다 (Electric Cyan + White).
    *   **설명/본문:** 신뢰와 깊이를 주는 색상으로 안정감을 유지한다 (Deep Indigo, Light Gray).

---

## 🌈 컬러 팔레트 시스템 (Color Palette System)
| 역할 | 이름 | HEX Code | CMYK Value | 사용 원칙 및 예시 |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Depth** (기반/권위) | Deep Indigo | `#1A237E` | 90, 85, 45, 60 | 배경색, 본문 섹션 구분. 깊은 지식과 학술적 분위기 담당. |
| **Secondary Authority** (강조/클래식) | Aged Gold | `#FFC107` | 0, 25, 80, 0 | 핵심 키워드 하이라이트, 중요 인용구 강조. 신뢰성 부여. |
| **Accent Anomaly** (경고/기술적 오류) | Electric Cyan | `#00BCD4` | 75, 0, 15, 20 | V-CORE 모듈의 에너지 파라미터, '실패 지점', Hook 문구 강조. 가장 높은 시각적 긴급성 부여. |
| **Neutral Background** (배경) | Off-Black/Gray | `#121212` | 95, 88, 75, 90 | 배경색으로 사용될 때, 깊은 몰입감을 제공하여 콘텐츠에 집중하게 만듦. |
| **Highlight Text** (텍스트 강조) | Pure White | `#FFFFFF` | - | 필수적인 가독성을 위한 기본 텍스트 색상. |

## 🅰️ 타이포그래피 시스템 (Typography System)
모든 폰트는 모바일 환경(릴스/썸네일)과 데스크탑 환경에서 높은 가독성을 확보하는 **산세리프(Sans-serif)** 계열을 사용합니다.

| 용도 | 권장 폰트 | 역할 및 적용 규칙 | 크기 레퍼런스 (Relative) |
| :--- | :--- | :--- | :--- |
| **Headline/Hook** (제목/최상단 후크) | Pretendard Bold / Impact-Style Sans | 짧고 강렬하며, 굵은 무게감으로 시선 고정. `Electric Cyan`과 대비를 이루게 배치. | 대형(Lg): 64pt 이상 (릴스 기준 비율 조정 필수) |
| **Body Text** (설명/본문 내용) | Pretendard Medium / Noto Sans KR | 정보 전달의 핵심. 가독성이 최우선이며, 간결한 배열을 유지한다. | 중형(Md): 24pt ~ 36pt |
| **Detail/Metadata** (날짜/출처 등 보조 정보) | Pretendard Regular | 제목과 분리하여 안정감을 제공하며, 미니멀하게 처리한다. | 소형(Sm): 18pt 이하 |

## 💻 컴포넌트 적용 가이드라인
### 1. 썸네일 (Thumbnail - 정지 이미지)
*   **레이아웃:** 배경은 `Off-Black/Gray` 또는 Deep Indigo 그라데이션 사용.
*   **강조 요소:** '질문'이나 '충격적인 결론'을 담은 키워드는 **Electric Cyan**으로 처리하고, 타이포그래피를 크게 배치하여 텍스트 자체가 시각적 후크가 되도록 설계한다.
*   **V-CORE 적용:** 과학 개념 설명 부분에는 `Aged Gold`와 `Deep Indigo`의 데이터 그리드(Grid) 형태 레이아웃을 차용하되, 오류 발생 지점만 `Electric Cyan`의 글리치 효과를 추가하여 통일성을 유지한다.

### 2. 릴스 (Reels - 모바일/숏폼 비디오)
*   **속도감:** 모든 텍스트는 *매우 빠르게* 등장하고 사라지며, Hook 문구(최대 3초 이내)에는 `Electric Cyan`을 과감하게 사용하여 긴급성을 조성한다.
*   **오버레이:** V-CORE의 '파라미터 변화'를 시각화하는 **글리치 효과 (Glitch Effect)** 또는 **데이터 스캔라인 (Data Scanline)** 애니메이션을 주기적으로 오버레이하여, 영상 전체에 기술적 긴장감을 유지한다.

---
**[필수 체크 리스트]**
*   ✅ Deep Indigo는 '사색'의 영역으로 제한하고, Anomaly/Failure 시퀀스에는 Electric Cyan을 전면 배치할 것.
*   ✅ 모든 텍스트 요소는 최소한의 여백과 강렬한 대비를 유지하여 모바일 가독성을 극대화할 것.
