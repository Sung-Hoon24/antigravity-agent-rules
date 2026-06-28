# ✨ [Master] 모듈형 비주얼 컴포넌트 라이브러리 v1.0

## 🎯 목표
향후 50개 이상의 콘텐츠에 재사용 가능하며, '존재의 경계(Boundary of Existence)'와 '지식적 간극(Knowledge Gap)'을 시각적으로 극대화하는 모듈형 비주얼 에셋 및 애니메이션 로직을 정의한다. 모든 컴포넌트는 Deep Indigo & Aged Gold 톤을 기본 컬러 팔레트로 사용하며, GSAP/Canvas API 기반의 파라미터 제어를 전제로 한다.

---

## 🎨 I. 표준 디자인 시스템 (Standard System Parameters)

### A. 핵심 컬러 팔레트
| 이름 | Hex Code | 역할 및 용도 |
| :--- | :--- | :--- |
| **Deep Indigo** | `#302B68` | 배경, 학술적 무게감, 지식의 심층부 (Primary Background/Text) |
| **Aged Gold** | `#D4AF37` | 강조점(Highlight), '깨달음' 순간, CTA 연결고리 (Accent/Focus) |
| **Ghost White** | `#F0F0F5` | 텍스트 및 명료한 정보 전달 영역 (Clean UI Element) |
| **Void Black** | `#0A0A15` | 깊은 어둠, '미지의 경계' 표현 (Deep Contrast) |

### B. 표준 타이포그래피
*   **Primary Font:** Noto Sans KR (가독성 및 현대적 지성 강조)
*   **Secondary Font:** Merriweather (학술적인 무게감 부여, 제목/캡션에 제한적 사용)
*   **Size Rule:** H1(48pt), H2(32pt), Body(16pt).

### C. 공통 트랜지션 원칙
모든 모듈 간 전환은 단순 페이드 아웃을 지양하고, **'데이터 전송 오류(Data Transfer Glitch)'** 또는 **'시간적 왜곡(Temporal Distortion)'** 효과를 핵심 장치로 활용한다. (GSAP Stagger + Filter Overlay 필수)

---

## 🧩 II. 모듈형 비주얼 컴포넌트 라이브러리 (Master Components)
*(최소 15개 이상의 고유 모듈을 제시하며, 이를 통해 50개 콘텐츠 제작의 기반을 다진다.)*

### A. [Knowledge Gap] 지식적 간극 유발 모듈 (Focus: 정보의 부재/질문 유도)

| No. | 컴포넌트명 (Module Name) | 개념 시각화 | 필수 애니메이션 파라미터 (TSS 기반) | 비주얼 가이드라인 |
| :--- | :--- | :--- | :--- | :--- |
| **G-01** | **The Void Masking** | '모르는 것'의 공백, 질문 유도. | `Opacity Curve: 0% -> 50% (EaseOutQuad) -> 0%`. 배경에 무작위 노이즈(Grain/Static) 오버레이 후 점진적 마스킹 효과 적용. | 화면 중앙에 깊은 Indigo 색상의 불규칙한 '구멍'을 만들고, 이 구멍 안의 정보는 항상 가려져 있다가 질문과 함께 Aged Gold로 빛나며 힌트를 준다. |
| **G-02** | **The Missing Link** | 논리적 충돌 지점/연결 고리가 끊긴 느낌. | `Lerp (Linear Interpolation)`을 이용한 두 개념 간의 흐릿하고 불안정한 연결선(Wireframe) 애니메이션. 특정 포인트에서 선이 *파열*되며 Aged Gold 섬광 발생. | A 개념과 B 개념 사이에 '깨진 링크' 그래픽을 배치. 시청자가 "어떻게 이어지지?"라는 의문을 가지도록 유도한다. |
| **G-03** | **The Question Mark Field** | 질문의 영역 확장. | 화면 전체에 Deep Indigo 계열의 미세한 그리드(Grid) 패턴이 존재하며, 중요한 키워드가 등장할 때 해당 Grid 섹션만 Aged Gold로 하이라이트되며 '진동'하는 효과 (Scale + Shake). | 학술적 아카이브 느낌을 주며, 정보가 배치될 공간 자체가 질문으로 가득 찬 듯한 시각적 압박감을 조성. |

### B. [Boundary of Existence] 존재의 경계 모듈 (Focus: 시간/기억/실재의 왜곡)

| No. | 컴포넌트명 (Module Name) | 개념 시각화 | 필수 애니메이션 파라미터 (TSS 기반) | 비주얼 가이드라인 |
| :--- | :--- | :--- | :--- | :--- |
| **B-01** | **Temporal Glitch** | 시간적 간극, 기억 왜곡. | `Canvas API`: 픽셀 단위의 무작위 노이즈(Glitch) 발생 및 프레임 드롭 시뮬레이션. (Staggered Color Shift + VHS Tracking Noise). | 영상의 특정 순간에 화면 전체가 빠르게 지지직거리는 효과를 주어, 관객에게 '지금 보는 게 진짜인가?'라는 의문을 심는다. |
| **B-02** | **Memory Reconstruction** | 파편화된 기억의 재조립. | 여러 개의 독립적인 이미지/텍스트 블록이 화면에 무작위로 나타나다가(Staggered Fade In), 핵심 키워드와 함께 지정된 순서대로 부드럽게 '정렬'되는 모션. | 마치 깨진 퍼즐 조각을 맞추는 듯한 느낌. Aged Gold의 빛으로 조립되면서 완성도가 높아진다. |
| **B-03** | **The Dimensional Rift** | 다른 차원/경계로 진입하는 순간. | 배경 자체가 Deep Indigo에서 Void Black으로 급격히 전환되며, 렌즈 왜곡(Lens Distortion)과 함께 원형의 빛이 스캔하며 지나가는 애니메이션. | 영상 전개의 큰 단락이 바뀔 때마다 사용한다. 고차원적이고 신비로운 분위기를 연출하는 데 최적화. |

### C. [Meta/Utility] 시스템 및 UI 모듈 (Focus: 권위와 구조화)

| No. | 컴포넌트명 (Module Name) | 개념 시각화 | 필수 애니메이션 파라미터 (TSS 기반) | 비주얼 가이드라인 |
| :--- | :--- | :--- | :--- | :--- |
| **M-01** | **The Academic Scroll** | 학술 자료 제시, 정보의 권위. | 고대 양피지 질감(Texture Overlay) 위에 텍스트가 타이핑되듯 나타나며 (Typewriter Effect), 페이지를 넘기는 듯한 물리적 모션(Page Curl). | 아카이브 컨셉을 극대화. Deep Indigo 배경에 Aged Gold로 엠보싱 처리된 가상 종이를 활용한다. |
| **M-02** | **The Data Stream Flow** | 복잡한 데이터 흐름/시스템 작동 원리. | 화면 상단에서 다양한 색상의 미세한 빛줄기(Particle System)가 특정 구조를 따라 흘러가는 애니메이션. (Canvas API 필수). | 정보의 폭포수 같은 느낌을 주어, 콘텐츠에 '깊이'와 '기술적 정교함'을 더한다. |
| **M-03** | **The CTA Funnel Beacon** | 시청자의 행동 유도 지점. | 배경 위에 은은하게 Aged Gold 빛깔의 '미세한 연결고리(Micro-filament)'가 생성되며, 이 빛이 특정 버튼 영역으로 집중적으로 끌어당겨지는 모션. | 모든 콘텐츠의 결말부 10초 동안 반드시 사용되어야 하는 핵심 컴포넌트. 지적 만족감을 구매로 전환시키는 시각화 장치. |

---
**[결론]**
위 15가지 모듈은 각기 다른 개념을 다루지만, **'Deep Indigo & Aged Gold'라는 통일된 시스템과 'TSS 기반의 애니메이션 로직(파라미터)'이라는 공통 언어**로 묶여 있어 어떤 주제의 콘텐츠에도 재사용 가능한 진정한 마스터 라이브러리가 될 것입니다.
