# ⚙️ Void Transition Failure Development Kit (VTF-DK) v2.0

**[목표]**
`DATA_OVERLOAD` 상태에서 발생하는 시스템 오류(정보 결핍 Funnel의 핵심 장치)를 구현하기 위한 최종 디자인 및 애니메이션 명세서입니다. 이 가이드는 개발팀이 프론트엔드 로직과 백엔드 모킹을 연동하여 완벽한 통합 테스트 스위트를 구축하는 데 필요한 모든 시각적, 시간적 파라미터를 제공합니다.

**[1. 핵심 디자인 시스템 사양]**
*   **Deep Indigo (주조색):** `#2A0B4C` (어두운 지식의 영역)
*   **Aged Gold (강조색):** `#D9AE38` (결핍된 정보의 빛, 중요 포인트 강조)
*   **Error Red (경고/오류):** `#CC5252` (시스템 실패 및 유효성 검사 오류 발생 시)
*   **Typography:**
    *   Primary Font: 'Inter' (가독성이 높은 산세리프 계열, 본문 사용)
    *   Secondary Font: 'Roboto Mono', monospace (코드/에러 메시지 출력 시 필수 적용. 시스템적 느낌 부여)

**[2. 컴포넌트 및 애니메이션 타이밍 명세]**

| 요소 | 역할 | 초기 상태 (State A) | 실패 시작 (Transition T0) | 최종 실패 상태 (State C) |
| :--- | :--- | :--- | :--- | :--- |
| **컨테이너** | 배경 시스템 격자/그리드 | Deep Indigo 배경. 미묘하게 깜빡이는 그리드 애니메이션 (`@keyframes subtle-grid`). | 10ms 동안 Grid Flicker (고주파수 노이즈) 발생. | 전체 화면에 Aged Gold 계열의 '데이터 손상' 패턴 오버레이. |
| **텍스트** | 오류 메시지 출력부 | 평온하고 학술적인 톤 유지. | 순간적으로 글자 단위가 Glitch(좌우 흔들림/픽셀 깨짐) 발생하며 노이즈화. | `Roboto Mono`를 사용한, 실패 원인 코드(`ERROR_4001: PAYLOAD MISSING`) 출력. Aged Gold로 깜빡임. |
| **데이터 스트림** | 정보 흐름 시각화 (Funnel의 핵심) | 부드러운 Deep Indigo-to-Deep Indigo 애니메이션으로 상단에서 하단으로 흘러내리는 빛줄기(Payload). | 갑작스럽게 멈춤. Flow가 `Error Red`로 변하며 위아래로 진동하는 패턴을 보임. | Payload 전체가 깨진 파형(Sine Wave Distortion)으로 바뀜. 데이터가 'Void' 속으로 빨려 들어가는 시각적 연출 필수. |

**[3. 핵심 애니메이션 키프레임 (개발팀 참고용)]**
*   `@keyframes glitch-text`: (0%, 100%) { transform: translate(0, 0); } 5% { text-shadow: 2px 0 #FF0000, -2px 0 #0000FF; transform: translate(-3px, 3px); } 7% { opacity: 0.8; } ... (총 10프레임의 급격한 왜곡 및 깜빡임을 정의)
*   `@keyframes data-distortion`: from { opacity: 1; transform: scale(1); } to { opacity: 0.2; transform: scale(1.5) rotateZ(360deg); filter: hue-rotate(90deg); }

**[4. 시각적 예외 처리 가이드라인 (Visual Edge Case Manual)]**
개발팀은 다음의 모든 상태 변화 지점과 오류 발생 조건에 대해 예상되는 시각적 반응을 구현해야 합니다.

1.  **Edge Case 1: T-0 Failure (시스템 준비 단계에서의 실패)**
    *   **상황:** 데이터 로딩이 완전히 시작되기도 전에 `DATA_OVERLOAD`가 트리거 될 경우.
    *   **시각적 반응:** Void Transition Failure 애니메이션 대신, 화면 중앙에 'SYSTEM INITIALIZATION FAILED'라는 메시지가 **빨간색(Error Red)**으로 500ms 동안 플래싱되어야 합니다. 이 과정에서 Deep Indigo 배경의 Grid Pattern이 무작위로 폭발하는 시각 효과가 추가됩니다 (노이즈 기반).
2.  **Edge Case 2: Network Latency Failure (네트워크 지연에 의한 실패)**
    *   **상황:** API 응답을 기다리는 동안 네트워크 연결이 끊어지거나 극심한 지연(>3초)이 발생할 경우.
    *   **시각적 반응:** Void Transition Failure가 발동되지 않습니다. 대신, 화면 상단에 'CONNECTION LOST / DATA STREAM INTERRUPTED'라는 문구가 **회색 계열의 텍스트**로 표시되며, 데이터 스트림 시각화 부분이 일제히 흐릿해지고 (Blur Filter 적용), 재연결을 유도하는 CTA 위젯이 노출되어야 합니다.
3.  **Edge Case 3: Payload Validation Failure (데이터 유효성 검증 실패)**
    *   **상황:** 백엔드에서 `ERROR_4001` 코드를 반환했으나, 클라이언트가 이를 정상적으로 처리하지 못하고 강제 종료될 경우.
    *   **시각적 반응:** Void Transition Failure의 *초기 Glitch 텍스트* 단계까지만 실행됩니다. 이어서 'CRITICAL VALIDATION ERROR'라는 메시지가 나타나며, 실패한 필드명(예: `Missing_Payload_ID`)이 **Error Red**로 하이라이트되고, 해당 부분만 격자 패턴으로 경고 표시되어야 합니다.

---
