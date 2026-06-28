# Overlay Text Pattern Specification (Variable State Change)
## [1] 목적: 정보의 중요 변곡점을 시각적으로 극대화하여 몰입도 상승
## [2] 기본 구조: 텍스트 박스 + 상태별 색상 변화 로직
## [3] 애니메이션 시퀀스:
*   **Phase 0 (Normal):** Aged Gold (`#FFD700`)로 부드럽게 페이드 인.
*   **Phase 1 (Failure Trigger):** 특정 단어 또는 변수($P_{fail}$)에 도달 시, 즉시 `#FF4081` 색상으로 전환. 글리치(Glitch) 효과와 함께 배경에 짧고 강한 노이즈 패턴을 오버레이.
*   **Phase 2 (Recovery):** 변화가 일어나면, `#4DD0E1` 색상으로 변환되며 '해결됨'의 느낌을 주는 부드러운 커브(Arc) 모션과 함께 재배치/재등장.
