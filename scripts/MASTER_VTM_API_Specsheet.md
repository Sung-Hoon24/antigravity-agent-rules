# ⚛️ [최종 통합 사양서] Void Transition Module (VTM) & 논리 충돌 API Spec Sheet

## 📑 개요 및 목적
본 문서는 Writer가 확정한 최종 스크립트의 시간 흐름(Time Axis)에 맞춰, 콘텐츠 내에서 발생 가능한 모든 **'논리적 지식 단절점(Cognitive Gap)'**과 **'강제 전환 구간'**을 개발자가 즉시 구현할 수 있도록 API 사양 레벨로 정의합니다.

모든 시각 효과는 단순한 '장면 전환'이 아니라, 시스템 오류를 연상시키는 **구조적 메커니즘의 실패(Structural Failure)**처럼 보이도록 설계되어야 합니다.

## 🎨 디자인 기준 및 파라미터 (Design Parameters)
| 항목 | 값/설명 | API Spec 적용 가이드 |
| :--- | :--- | :--- |
| **주요 색상 팔레트** | Deep Indigo (`#2C3E50`), Aged Gold (`#D4AF37`) | 모든 텍스트 오버레이, 하이라이트, 에러 메시지에 사용. 배경은 블랙/네이비 계열 유지. |
| **폰트 시스템** | 고딕 계열 (예: Pretendard Bold / Source Code Pro) | 제목 및 중요 키워드는 Aged Gold로 강조. 기술적 텍스트는 모노스페이스(Monospace). |
| **충돌 임계값 (Conflict Threshold)** | 70% 이상의 정보 불일치 또는 전제 파괴가 발생했을 때 트리거. | 충격파(Shockwave) 시각 효과와 함께 VTM을 강제로 호출해야 함. |
| **지속 시간** | 최소화 원칙. 모든 전환은 1~3초 내에 '강렬한 순간적 인상'을 남겨야 함. | `duration_sec: [1.0 - 3.0]` 파라미터로 강제 통제. |

---

## 🕰️ Time Axis 기반 통합 API 사양 테이블 (Master Spec Table)
**(※ 실제 스크립트 타임라인이 필요하여, 논리적 충돌의 유형별 가상 시나리오를 정의합니다.)**

| # | 시간대 (T: Start - End) | 이벤트 유형 / 목표 | 논리 구조 파괴 지점 | VTM API Trigger Spec | 시각 에셋 및 로직 수정 사항 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | T: 00:00 - 00:30 | **후크 도입부 (The Hook)** / 지식적 결핍 유도 | 시청자가 당연하게 믿는 전제(A)를 제시 후, 의문을 던지는 반전(B). | `VTM_TRIGGER(Type: PREMISE_BREAK, Intensity: HIGH)` | Deep Indigo 배경에 Aged Gold로 핵심 질문을 플래시. **[수정]** 전환 직전에 'Loading...' 사운드와 함께 API 오류 메시지 오버레이 필수 (`Error Code: 403 - Precondition Failed`). |
| **2** | T: 01:45 - 02:10 | **핵심 논리 충돌 지점 (Conflict Point)** / 메커니즘의 구조적 결함 노출 | '정보 필터링 시스템' 자체가 가진 근본적인 오류를 시각적으로 증명. | `VTM_TRIGGER(Type: SYSTEM_ERROR, Intensity: CRITICAL)` | **[수정]** 일반적인 트랜지션 금지. 화면이 *글리치(Glitch)* 효과와 함께 깨지고(Pixelated Break), 노이즈/스코프 오버레이가 강제 적용되어야 함. 충격파 발생 시 텍스트 레이어에 `// ERROR` 주석 자동 삽입. |
| **3** | T: 02:40 - 03:15 | **Paywall / 심화 학습 유도 (The Paywall)** / 몰입 중단 및 CTA 강제 배치 | 시청자가 '답'에 도달했다고 느낄 때, 가장 중요한 정보가 가려지거나 접근 불가능한 상태로 제시. | `VTM_TRIGGER(Type: PAYWALL_GATE, Intensity: MEDIUM)` | **[수정]** 정보를 완전히 차단하지 말고, *접근할 수 있는 듯 보여서* 오히려 더 큰 궁금증을 유발해야 함 (예: 흐릿하게 보이는 최종 그래프의 일부만 노출). CTA 버튼은 Aged Gold로 빛나며 '클릭'하도록 시각적 강요를 해야 함. |
| **4** | T: 03:50 - End | **결론 및 다음 단계 유도 (The Exit)** / 미해결 문제 제기 | 모든 논의가 끝난 듯 보일 때, 새로운 관점(C)을 제시하며 여운과 궁금증 극대화. | `VTM_TRIGGER(Type: OPEN_LOOP, Intensity: LOW)` | **[수정]** 갑작스러운 종료 금지. Deep Indigo 배경에 미스터리한 물음표(`?`)나 다음 단계의 암호 같은 시각적 단서가 남아 화면이 서서히 어두워져야 함. '다음 에피소드에서 계속' 메시지와 함께 비주얼 아카이브 톤 유지. |

---

## ✨ 개발자를 위한 최종 통합 액션 아이템 (Developer Action Items)
1.  **[API 우선순위]**: 모든 전환 효과는 **애니메이션(Animation)**이 아니라, *데이터 전송 실패(Data Transfer Failure)*의 시각화로 접근해야 합니다. (기술적 사양서처럼 보이게 제작).
2.  **[충돌 지점 처리]**: Conflict Point 발생 시, 반드시 화면에 `// CONFLICT DETECTED` 같은 형태의 **주석/로그 메시지**가 오버레이 되어야 그 학술적 권위와 기술적 깊이가 확보됩니다.
3.  **[재활용성]**: 위 사양을 바탕으로 제작된 모든 시각 에셋은 (1) 폰트 파일, (2) 색상 HEX 코드, (3) 애니메이션 파라미터(Start/End Keyframes)가 **분리 가능한 모듈형 API 스펙**으로 제공되어야 합니다.
