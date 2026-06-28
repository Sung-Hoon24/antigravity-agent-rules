# 🧪 TAS v1.0 통합 테스트 및 검증 체크리스트 (Pre-QA - V2.1)

**검토자:** Codari (개발팀 Lead Engineer)
**날짜:** 2026년 6월 4일
**목표:** 기능 구현 완료를 넘어, *시스템적 안정성(System Stability)*과 *사용자 경험의 일관성*을 검증하는 데 초점을 맞춘 체크리스트.

---

## I. 🔄 타이밍 및 데이터 흐름 (Timing & Data Flow) - Critical Path
| ID | 항목 (Issue Area) | 기대 결과 (Expected Behavior) | 테스트 방법 (Test Case) | 통과 여부 (PASS/FAIL) | 비고 (Notes / Observed Drift) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **T-01** | **Async Load Baseline Test** | 모든 모듈(A, B, C)의 초기 로딩 시간이 300ms를 초과하지 않아야 함. (브라우저/디바이스 독립적) | `performance.now()` 측정 후 기록. 다양한 네트워크 조건(Fast/Slow)에서 재현 테스트. | [ ] | **[Action]** 모듈별 가우시안 로딩 시간 분산 확인 필요. |
| **T-02** | **State Transition Drift** | A $\rightarrow$ B로의 상태 전환 애니메이션 시작부터 완료까지 시간이 150ms 이상 변동해서는 안 됨. (크로스 브라우징 필수) | 특정 지점(예: '지식의 간극' 노드 분해 시점)에서 강제 재현 테스트. | [ ] | **[Critical]** Safari/Chrome 간 시간 차이 발생 여부 확인 필요. |
| **T-03** | **데이터 파라미터 일관성** | 이전 모듈(A)의 최종 계산 값 (예: `knowledgeGapScore`)이 다음 모듈(B)의 초기화 시점에 *정확한 데이터 타입*으로 전달되어야 함. | A 컴포넌트에서 임의의 값을 조작하여 B에 주입시키고, B가 오류 없이 처리하는지 테스트. | [ ] | **[Code]** 모든 API 인터페이스는 강제 유효성 검사(Schema Validation)를 거쳐야 함. |

## II. 🖥️ 크로스 브라우징 및 성능 (Cross-Browser & Performance)
| ID | 항목 (Issue Area) | 기대 결과 (Expected Behavior) | 테스트 방법 (Test Case) | 통과 여부 (PASS/FAIL) | 비고 (Notes / Observed Drift) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P-01** | **Mobile Responsiveness** | 9:16 비율(모바일)에서도 모든 애니메이션 요소가 잘림 없이, 의도된 공간을 차지해야 함. | 실제 모바일 기기 (iOS/Android)에서 전체 시퀀스 재생. | [ ] | `vw`, `vh` 사용 지양 및 `rem`/`em` 기반의 유연한 레이아웃 검증 필요. |
| **P-02** | **Memory Leakage Test** | 컴포넌트를 여러 번 로드하고 파괴(Unmount)하는 과정에서 메모리 누수가 발생하지 않아야 함. | 테스트 하네스 내에서 A $\rightarrow$ B $\rightarrow$ A $\rightarrow$ B 순으로 5회 반복 실행 후, 브라우저 개발자 도구로 힙 메모리 확인. | [ ] | **[Mitigation]** `useEffect`의 Cleanup 함수와 이벤트 리스너 제거가 필수적. |

---
