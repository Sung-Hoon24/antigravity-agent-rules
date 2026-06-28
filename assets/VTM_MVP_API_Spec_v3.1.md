# 🌌 VTM Module MVP API Specification (Version 3.1)

## 🎯 목적: 통합 테스트 환경을 위한 파라미터 제어형 시각 에셋 공급
본 모듈은 단순히 '글리치' 효과를 구현하는 것을 넘어, **데이터의 논리적 왜곡(Logical Distortion)**과 **지식의 단절점(Cognitive Gap)**을 시각화하여 M-CTA 및 M-KPI 컴포넌트의 테스트 트리거로 활용됩니다.

## 🎨 브랜드 가이드라인 준수
*   **Primary Palette:** Deep Indigo (Hex: #2B3A66) - 주된 배경색/텍스트 색상.
*   **Accent Palette:** Aged Gold (Hex: #C59840) - 강조점, 논리적 오류 발생 지점의 하이라이트.
*   **Tone:** 학술적 권위(Academic Authority), 기술적 불안정성(Technical Instability).

## ⚙️ 핵심 API 파라미터 정의 (Must-Have Variables)
모든 VTM 에셋은 아래 최소 3가지 이상의 변수 제어를 통해 구현되어야 합니다.

### 1. `[Distortion_Frequency]` (지각 왜곡 빈도)
*   **Type:** Float (0.0 to 1.0)
*   **Description:** 글리치 효과가 발생하는 주기 또는 반복 속도의 강도를 결정합니다.
    *   `0.0`: 안정적/정상 상태 (No Glitch).
    *   `0.2 - 0.4`: 미세한 떨림 (Minor Glitch) — 시청자의 주의를 살짝 빼앗는 수준.
    *   `0.8 - 1.0`: 극심한 왜곡 (Severe Glitch/Shock) — 논리적 충격을 유발하는 핵심 지점.

### 2. `[Chromatic_Shift_Intensity]` (색상 오프셋 강도)
*   **Type:** Float (0.0 to 360 degrees Hue Shift)
*   **Description:** RGB 채널 간의 분리(Color Separation) 정도를 제어합니다. Deep Indigo와 Aged Gold 계열에서 색이탈되는 패턴을 정의하는 데 사용됩니다.
    *   `0.0`: 완벽한 색상 일치 (Perfect Color Match).
    *   `1.5 - 2.5`: 강한 분리 (Chromatic Aberration) — 시각적 불안정성을 극대화합니다.

### 3. `[Temporal_Jitter_Rate]` (시간 흐름 교란율)
*   **Type:** Integer (0 to N frames/second)
*   **Description:** 프레임 단위의 불연속성(Stuttering, Frame Drop)을 제어합니다. '시스템 오류'라는 느낌을 가장 직접적으로 주는 변수입니다.
    *   `1`: 완벽한 프레임 재생 (Stable Playback).
    *   `3 - 7`: 간헐적 스터터링 (Intermittent Stutter) — 데이터 손실의 암시.

### 4. `[Data_Corruption_Pattern]` (데이터 손상 패턴) *추가 필수 변수*
*   **Type:** Enum (Enum Type: BLUR, BLOCKY, WIPE, PIXELATE)
*   **Description:** 글리치가 어떤 시각적 형태로 나타날지 정의합니다. 논리가 무너지는 방식을 구체화합니다.
    *   `BLUR`: 초점 흐림 효과 (Focus Blur).
    *   `BLOCKY`: 디지털 블록 단위의 왜곡 (Pixelation/Compression Artifacts).
    *   `WIPE`: 수평 또는 수직으로 화면이 찢어지는 효과 (Horizontal/Vertical Wipe).

---
## 🛠️ 개발자 통합 테스트 시퀀스 예시
| Test Case | 목표 시나리오 | 파라미터 값 설정 예시 | 예상 결과 및 활용 목적 |
| :--- | :--- | :--- | :--- |
| **T1: 초기 진입 (Setup)** | 논리적 안정 상태 → 미세한 의문 제기 | `[Distortion_Frequency]=0.2`, `[Chromatic_Shift_Intensity]=0.5`, `[Temporal_Jitter_Rate]=2` | 시청자에게 '뭔가 이상하다'는 느낌을 주지만, 내용 이해를 방해하지 않음 (Pre-CTA). |
| **T2: 핵심 논쟁 유발 (Glitch Trigger)** | 지식적 단절점 발견 → 시스템 오류 암시 | `[Distortion_Frequency]=0.9`, `[Chromatic_Shift_Intensity]=3.0`, `[Temporal_Jitter_Rate]=7`, `[Data_Corruption_Pattern]=BLOCKY` | 가장 높은 시각적 충격. M-CTA 모듈이 강제 발동되어 다음 행동(댓글/구독)을 요구함 (Critical Point). |
| **T3: 복합 오류 (Overload)** | 논리적 추론 불가능 상태 → 완전한 혼란 유도 | `[Distortion_Frequency]=1.0`, `[Chromatic_Shift_Intensity]=3.0`, `[Temporal_Jitter_Rate]=7`, `[Data_Corruption_Pattern]=WIPE` | 영상 클라이맥스 또는 결론 부분에서 사용. 시청자를 극도의 몰입 상태(Overload)로 유도하여 댓글 참여를 강제함. |
