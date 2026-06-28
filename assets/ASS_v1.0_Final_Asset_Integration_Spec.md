# 🎨 TAS v1.0 최종 벡터 자산 통합 명세서 (Asset Integration Specification)

**문서 버전:** `V2.0.0` (Initial Blueprint: V1.0 $\rightarrow$ Production Spec: V2.0.0)
**작성일:** 2026년 6월 4일
**목표:** TAS v1.0에 정의된 모든 애니메이션 모핑 파라미터를 개발팀(Codari)이 즉시 통합 테스트 환경에서 구현할 수 있는 최종 자산 세트의 제작, 포맷 및 관리 기준을 확립한다.

---

## I. 📦 자산 패키지 구성 개요 (The Package Structure)

모든 에셋은 '원본 마스터 파일'과 이를 기반으로 한 '개발 컴포넌트 파일(최종 배포용)' 두 가지 형태로 구분되어야 하며, 버전 관리는 **`[주버전].[부버전].[패치]`** 시스템을 따른다. (예: `v2.0.1`)

| 자산 그룹 | 구현 요소 및 기능 | 필수 포맷 | 전달 담당자 | 비고/사용처 |
| :--- | :--- | :--- | :--- | :--- |
| **A. Geometry Morphing Core** | '지식의 간극' 시각화 핵심 모핑 구조 (예: 노드 분해, 연결선 흐름) | 1. SVG + Lottie JSON<br>2. GSAP/JS 컴포넌트 | Designer $\rightarrow$ Dev | 모든 영상의 메인 Hook 및 전이(Transition)에 사용됨. **가장 중요.** |
| **B. Key Visual Template Set** | 배경 아카이브 텍스처, 데이터 흐름 그래프 패턴 등 반복 요소 | High-res PNG (Alpha Channel)<br>Seamless SVG Pattern | Designer $\rightarrow$ Dev | 영상 전반의 분위기 유지 및 BGM 리듬에 맞춘 미묘한 움직임(Micro-movement) 부여. |
| **C. Typography/UI 컴포넌트** | 강조 텍스트 박스, 정보 출처 표시 위젯, CTA 버튼 애니메이션 세트 | Figma Library Link (최종 Export)<br>CSS/JS 코드 스니펫 | Designer $\rightarrow$ Dev | UI의 학술적 권위(Academic Authority)를 높이는 요소. **반드시 인터랙티브 구현.** |
| **D. 전이 효과 (Transition)** | 챕터 간 이동, 논리 구조 전환 시 사용되는 모션 그래픽 루프 (예: 스캔라인 변형) | Lottie JSON 또는 WebGL Shader Code | Designer $\rightarrow$ Dev | 영상의 흐름을 '논리적 사유' 과정으로 보이게 하는 장치. |

## II. 📐 주요 컴포넌트별 기술 명세 (Technical Specification Details)

### A-1. Geometry Morphing Core (`Morph_Core`)
*   **기능 정의:** '관점 변화(Perspective Shift)'와 '정보의 재조합(Recombination)'을 시각화하는 핵심 모핑 패턴.
*   **구현 원칙:** 단순한 애니메이션이 아닌, **수학적 파라미터 기반**으로 작동해야 함. (예: 노드의 밀도($\rho$), 연결 강도($k$)).
*   **파일 포맷 가이드:** Lottie JSON (`morph_core_v2.0.json`)을 기본으로 하며, 복잡한 인터랙션은 **GSAP GreenSock 라이브러리 기반의 JS 컴포넌트**로 제공한다. (SVG path 데이터와 동기화 필수).
*   **테스트 항목:** 1. 초기 상태 $\rightarrow$ 모핑 시작 시점 $\rightarrow$ 최종 안정화(Resting) 상태까지 각 단계별 키프레임 파라미터가 정확히 반영되는지 확인.

### D-1. 전이 효과 (Transition) - 'Gap Transition'
*   **기능 정의:** [오해]에서 [진실]로 전환될 때, 시청자의 인식이 끊어지는 듯한 느낌을 주는 모션 루프.
*   **구현 원칙:** **흑백 그레인 노이즈(Grain Noise)**를 기반으로 한 '데이터 손실/복원' 효과가 핵심. 색상 코드는 Deep Indigo와 Aged Gold의 대비 지점을 활용해야 함.
*   **파일 포맷 가이드:** Lottie JSON (반복 루프 설정 필수). WebGL Shader 코드(`shader_gap_v2.0.glsl`)를 제공하여 성능 최적화를 유도한다.

## III. 🛠️ 개발팀 전달 및 테스트 환경 지침 (Delivery & Testing Protocol)

### 1. 파일명 규칙 (Naming Convention)
*   `[Asset Type]_[Component Name]_[Version].[Format]`
*   예시: `morph_core_v2.0.json`, `bg_archive_pattern_v1.5.svg`

### 2. 버전 관리 및 히스토리 추적 (Versioning)
*   **MAJOR:** 근본적인 로직/구조 변경 발생 시 (예: 모핑 방식 자체를 바꿀 때).
*   **MINOR:** 새로운 파라미터 추가 또는 대규모 수정이 있을 때 (예: 노드 개수 증가, 색상 팔레트 확장).
*   **PATCH:** 사소한 버그 수정 또는 최적화 패치만 적용할 때.

### 3. 통합 테스트 환경 요구 사항 (Integration Testing Checklist)
개발팀은 다음 항목에 대한 명확한 코딩 가이드가 필요합니다:
1.  [ ] **Responsiveness Test:** 모바일/데스크톱 크기 변화에 관계없이 모든 컴포넌트의 비율과 동작이 유지되는지 확인.
2.  [ ] **Performance Benchmarking:** 애니메이션 로드가 30 FPS 이하로 떨어지는 구간이 없는지, 특히 Lottie/WebGL 사용 시 GPU 자원 소모를 측정할 것.
3.  [ ] **Interoperability Test:** 모든 컴포넌트가 하나의 스크립트(GSAP Timeline) 내에서 충돌 없이 순차적으로 재생되는지 검증.

---
**납기일 대비 액션 플랜 (D-3 기준)**
1. 오늘: 최종 명세서 작성 및 QA 팀 내부 승인 획득.
2. D-2: 개발팀(Codari)과 기술 회의를 통해 ASS 문서 기반으로 최초 통합 테스트 환경 구축 시작.
3. D-1: 에셋 원본 파일 일괄 패키징 및 버전 관리 시스템에 등록 완료.
