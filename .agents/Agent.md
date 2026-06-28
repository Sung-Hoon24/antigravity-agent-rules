# 🌿 루비아 기술연구소 제4연구소 (음원제작연구) AI 에이전트 핵심 기술 스택 및 스킬 가이드

본 문서는 루비아 기술연구소 제4연구소 (음원제작연구)(유튜브 에이전트 시스템)의 기술 표준, 활용 가능한 외부 도구(MCP) 및 보안/트래픽 제어 스킬 목록을 정의합니다.

---

## 1. 🛠️ 핵심 기술 스택 (Core Technology Stack)

### [Backend & Infrastructure]
- **Language**: Python 3.10+ (텔레그램 봇, 비동기 스케줄러, 데이터 파이프라인 제어)
- **Database**: Local JSON-based Lightweight DB (`sound_templates.json`, `planning_sessions` 등 Memory Cache Layer)
- **External Integration (MCP)**:
  - **PayPal MCP**: 글로벌 1인 비즈니스의 수익화 핵심. 결제 인보이싱(Invoicing), 상품 생성/관리, 구독(Subscription) 결제 및 트랜잭션 추적 자동화.
  - **Firebase MCP**: 온라인 데이터 실시간 동기화, 사용자 권한 분리 및 빠른 MVP 인프라 대용.

### [AI & Content Pipeline]
- **Music Generation**: Google Lyria 3 Pro API (`lyria-3-pro-preview`) - 가변 길이 롱폼 플레이리스트 빌드 및 30초 오디오 샘플링 파이프라인.
- **Image Generation**: Google Imagen 4.0 API (`imagen-4.0-generate-001`) - 고화질 숏폼/롱폼 배경 이미지 렌더링.
- **Local LLM Hybrid**: Ollama / LM Studio (Llama 3.1, Phi-3, Mistral) - 자연어 NLU 변환 및 비용 0원 템플릿 생성.
- **Video Rendering**: FFmpeg & python-imageio-ffmpeg (재인코딩 없는 스트림 병합 및 로스율 제로 자막 합성).

---

## 2. 🛡️ 보안 및 제어 프로토콜 (Anti-Gravity Skill)

### [Anti-Gravity Skill Gateway]
- **정의**: 보안 게이트웨이 및 외부 API 결제 트래픽 제어 프로토콜.
- **역할**:
  1. 외부 결제 API(PayPal 등) 호출 시 이상 트래픽 및 중복 결제 요청의 원천 차단.
  2. 시스템 권한이 없는 비인가 사용자의 민감 명령어(유튜브 비공개/공개 배포, 결제 가이드 호출 등) 실행 통제.
  3. API 통신 장애 시 자가 치유(Self-healing) 및 대체 엔드포인트 자동 라우팅 활성화.
- **보안 수칙 (PayPal)**:
  - 연속 호출 제한: 5초 내 중복 요청 시 즉시 자동 거절(경고문 송출) 및 권한 감사 로그 생성.

### [Local LLM NLU Monitoring]
- **정의**: 로컬 LLM NLU API 호출 무결성 감시 프로토콜.
- **역할**:
  1. `intent_parser.py`를 통한 로컬 NLU 분석 성공 및 실패(파싱 에러, 타임아웃) 카운팅.
  2. 누적 호출 5회 이상, 실패율이 30%를 초과할 경우 시스템 경보 작동 (`LOCAL_NLU_WARNING_TRIGGERED=True` 상태 고정).

---

## 3. 🎯 핵심 트리거 워크플로우 (Trigger Workflow)

- **페이팔 MCP 연결 브리핑 SOP**:
  - 대표님이 "페이팔 mcp 연결", "파이어베이스 연결" 혹은 "결제 자동화 세팅" 명령을 입력할 때 즉시 관련 가이드 및 안티그래비티 MCP Config JSON 파일을 출력하여 환경 설정을 자동 조율합니다.
  - 관련 안내 가이드: [paypal_firebase_mcp_guide.md](file:///c:/1인기업/Apps/유튜브에이전트/.agents/guides/paypal_firebase_mcp_guide.md)

- **5단계 자율 순환 파이프라인**:
  - `[접수] ➔ [로컬 랜딩] ➔ [검토] ➔ [업로드 승인] ➔ [보고]`
  - 각 제작 단계 진행 시 상태바(Status Bar)에 시각화하여 표출.
  - 비디오 빌드가 정상 완수되면 `[📊 5단계: 보고서 발행 완료]`를 송출하고, `context.chat_data['current_state'] = None` 으로 복원하여 세션 잠금(Session Lock)을 안전하게 자동 해제.
  - **긴급 예외**: 에셋 빌드/제작 진행 중이더라도 '취소', '정지', '그만', 'cancel' 등 긴급 취소 키워드가 수신되면 세션 락을 바이패스하여 안전하게 탈출 및 해제. 모든 예외 발생 시 `finally` 블록을 통과하며 락을 해제하도록 안전 설계.

---

## 4. 📊 데이터 지침 (Data Strategy)
- **평점 기반 RAG 학습**: 1점(즉시 폐기/대체 템플릿 비동기 재생성), 3점(보류/데이터 안전 보존), 5점(승인/성공 사례 DB RAG 자동 주입) 규칙 엄격 적용.
- **주간 성적표**: 매주 [주간 음원 진화 성적표]를 통해 비용 절감액, 승인율, 대표 취향 반영도 수치화 보고.
