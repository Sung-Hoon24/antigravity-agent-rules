# 🚀 Production Workflow Blueprint: 지식적 결핍 기반 콘텐츠 제작 파이프라인

**Version:** v1.0 (Initial Integration Draft)
**Target Output:** High-Retention, API-Driven YouTube Video Asset
**Objective:** 모든 창작 요소를 '기술적으로 충돌 없이' 통합하고, 측정 가능한 KPI를 내재화하는 반복 가능한 시스템을 정의한다.

## ⚙️ I. System Dependencies & Component Specification

이 워크플로우는 다음 세 가지 핵심 모듈의 종속성을 전제로 한다. 각 모듈은 API 호출 방식으로만 데이터를 주고받아야 하며, 로컬 파일 의존성은 최소화되어야 한다.

| ID | Module Name | Provider | Description | Input Parameters (Required) | Output Data Schema |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **M-VTM** | Visual Tension Module (Glitch/Distortion) | Designer | 논리적 충격을 시각화하는 파라미터 기반 효과. | `[Intensity]`, `[ColorOffset]`, `[Duration_ms]`, `[Trigger_Point]` | `{visual_data: string, timestamp: ms}` |
| **M-CTA** | Call to Action Flow Controller | Writer/Lead | 시청자를 다음 콘텐츠로 유도하는 논리적 전환 구조. | `[OpenLoop_Question]`, `[Target_Asset_ID]`, `[Placement_Time]` | `{cta_type: enum, link_data: string, duration: ms}` |
| **M-KPI** | KPI Tracking Injection Layer | Hyunbin/Developer | 핵심 비즈니스 지표 측정 및 데이터 수집을 위한 추적 코드. | `[Metric_ID]`, `[Segment_Start_Time]`, `[Segment_End_Time]` | `{tracking_payload: JSON, visibility: bool}` |
| **M-CORE** | Main Narrative Stream | Writer | 핵심 정보 전달 스크립트 (기본 비디오 트랙). | `[Script_Text]`, `[Total_Duration]` | `Stream<Audio/Video>` |

## 🔄 II. Execution Flowchart & Logic Sequence (The Master Pipeline)

전체 영상 길이를 $T_{total}$이라 가정하며, 시간 흐름에 따른 모듈 호출 순서(API Call Order)를 정의한다.

**[START] $\rightarrow$ [M-CORE: Narrative Stream Start ($t=0$)]**
1.  **(Phase 1: Hook - $t=0$ to $t_{hook}$):** M-CORE가 기본 정보를 전달하며, 시청자의 **'지적 결핍(Cognitive Gap)'**을 유발하는 질문으로 마무리한다.
2.  **(Phase 2: Core Argument - $t_{hook}$ to $t_{trigger}$):** M-CORE는 논리적 구조를 펼치며 정보를 전달한다.
    *   ***[TRIGGER POINT]***: 시청자의 몰입도가 가장 높아지는 순간, 다음 컴포넌트를 강제로 호출하여 충격파를 유도한다.
    *   `IF (Critical_Info_Passed) THEN CALL M-VTM(Intensity=High, TriggerPoint=$t_{trigger}$)`
3.  **(Phase 3: The Gap/Climax - $t_{trigger}$ to $t_{end\_loop}$):** 가장 논쟁적인 지점. 여기서 정보는 의도적으로 '단절'되거나 '왜곡'된다.
    *   `CALL M-VTM(Intensity=Max, TriggerPoint=$t_{gap}$)` $\rightarrow$ (Visual Disruption)
    *   `CALL M-KPI(Metric_ID='SegmentedCompletionRate', StartTime=$t_{trigger}$, EndTime=$t_{end\_loop}$) ` $\rightarrow$ (Data Capture)
4.  **(Phase 4: Resolution & Transition - $t_{end\_loop}$ to $T_{total}$):** 최종 결론을 제시하며, 시청자가 '궁금증'을 해결하기 위해 행동하도록 유도한다.
    *   `CALL M-CTA(Target_Asset_ID='DeepDive_Module', Placement_Time=$t_{final})` $\rightarrow$ (Transition to external/next content)
    *   `CALL M-KPI(Metric_ID='CrossPlatformCTR', StartTime=$t_{final}$, EndTime=$T_{total}$) ` $\rightarrow$ (Link Click Tracking)

## 🧪 III. Quality Assurance Test Suite (Test Sequences)

제작된 결과물이 다음 조건을 만족하는지 검증하기 위한 테스트 케이스를 정의한다. **(QA 단계에서 필수 실행)**

### A. Functional Tests (Does it work?)
1.  **[T-001] VTM Module Integration:** $t_{trigger}$ 지점에서 M-VTM이 정상적으로 렌더링되는가? (파라미터 값 변경 시, 효과의 강도가 비선형적으로 변하는가? $\rightarrow$ *테스트 목표: 파라미터 제어 가능성 검증*)
2.  **[T-002] CTA Activation Test:** M-CTA를 호출했을 때, 오버레이 UI/UX가 겹치지 않고 부드럽게(Fade-in) 나타나며, 링크 클릭 이벤트가 정상적으로 트래킹되는가? (Mock API 호출로 검증 필요)
3.  **[T-003] KPI Tracking Test:** 영상의 특정 세그먼트($t_{gap}$ 주변 15초) 동안 M-KPI 로직이 활성화되며, 백엔드에 `{Metric_ID: 'SegmentedCompletionRate', Status: 'Active'}` 형태의 더미 데이터가 전송되는지 확인한다.

### B. Constraint Tests (Does it break?)
1.  **[C-001] Overlap Check:** M-VTM과 M-CTA가 동일한 시간대에 동시에 호출되었을 때, 시각적/청각적 요소 간의 **정보 과부하(Information Overload)**가 발생하지 않는가? (Collision Detection Logic 필요)
2.  **[C-002] SEO Integrity Check:** 영상 제목과 설명란에 키워드가 자연스럽게 녹아들면서도, M-KPI에서 정의한 '학술적 권위' 톤을 해치지 않는가? (Keyword Density < 3%, Tone Score > 0.8)

---
**Required Action:** 이 블루프린트를 기반으로 각 모듈의 API 사양서(Spec Sheet)를 최종 확정하고, 이를 바탕으로 통합 개발 환경(Dev Environment) 구축을 시작해야 합니다.
