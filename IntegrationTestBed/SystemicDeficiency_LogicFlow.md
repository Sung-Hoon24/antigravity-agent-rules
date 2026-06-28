# Funnel Gateway: 시스템적 결핍(Glitch) 로직 플로우 정의

## 🎯 목표 시간 축 무결성 검증 (T+320ms ~ T+510ms)

### I. 시퀀스 구조 및 논리 흐름
1. **진입점 (T+300ms):** 평온하고 명확한 정보 전달(Stable State).
2. **시스템적 결핍 유발 (T+320ms):** `u_intensity`가 급격히 상승하며, Shader의 Chromatic Aberration 및 Noise 효과를 통해 시각적 데이터 붕괴 시작. (시청자의 인지 부조화 최대점)
3. **결핍 최고조 (T+400ms):** 모든 파라미터(Color Shift, Jittering, Pattern Change)가 동시다발적으로 작동하며 '시스템 오류'의 극대화를 표현.
4. **탈출 및 전환 준비 (T+510ms):** `u_intensity`가 급감하고 노이즈 패턴이 멈추며, 화면 전체가 미세한 잔상(Afterglow)으로 마무리되어 다음 주제로 강제적인 시선 이동을 유도함.

### II. 기술적 구현 체크리스트 (Developer Checklist)
*   [ ] **Input:** `u_time` (초 단위), `u_intensity` (0.0-1.0).
*   [ ] **Shader Logic:** 반드시 3개 이상의 시간 의존적 변수(sin/cos 기반)를 사용하여 움직임을 구현해야 함.
*   [ ] **Output Verification:** T+510ms의 출력값은 단순한 '어둠'이 아니라, 다음 장면에 대한 '기대감'을 남기는 미세한 잔류 데이터 패턴이어야 함.

**결론:** 이 패키지는 단순히 썸네일 효과가 아닌, 영상 콘텐츠를 구성하는 시간 축 자체에 오류를 주입하여 메시지 전달의 무게감을 높이는 구조적 에셋입니다.
