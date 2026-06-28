# [Ver 2.2 하이브리드 운영 체제 및 스킬 셋 바인딩 규정]

본 문서는 제1연구소 자율 에이전트 연합의 실전 가동 성능 최적화 및 비용 효율화를 달성하기 위한 하이브리드 추론 라우팅(Hybrid Inference Routing) 규칙과 신규 바인딩된 스킬 셋 운용 명세입니다.

---

## 1. ⚙️ 기술 스택 및 MCP 스킬 셋 바인딩

시스템은 아래의 연동 규격에 따라 결제 및 분석 정보 스킬을 자율적으로 사용합니다:
- **PayPal MCP (`paypal-mcp-server`)**: 프리미엄 구독 상품화, 인보이스 자동 발행 및 결제 상태 트래킹 스킬 바인딩.
- **Firebase MCP (`firebase-mcp-server`)**: 채널 성과 지표(Ingestion) 추적 및 실전 대시보드 저장소 스킬 바인딩.
- **Stitch MCP**: 디자인 시스템 생성 및 화면 배포 레이아웃 무결성 필터 스킬 바인딩.
- **NotebookLM MCP**: 외부 최신 AI 동향 및 시장 리포트 정보 수집 지식 엔진 바인딩.

---

## 2. 🤖 하이브리드 추론 라우팅 프로토콜 (Hybrid Inference Routing)

로컬 연산 비용을 0원으로 억제(비용 제로화)하면서 클라우드의 정교한 추론 능력을 상황에 맞게 자동으로 분기하는 2중 추론 인프라를 가동합니다.

### 2-1. 라우팅 모드 구분
1. **스마트 자동 라우팅 (Auto)**:
   - **경량 업무 (Local)**: 단순 인사말(`INTENT_GREETING`), 단순 질의응답 및 Pydantic 스키마가 없는 단순 텍스트 생성은 로컬 LLM(Ollama/LM Studio)을 우선 호출합니다. 로컬 오류 발생 시 클라우드로 실시간 자가 치유 폴백(Fallback)합니다.
   - **복합 업무 (Cloud)**: Pydantic 구조화 JSON을 생성해야 하는 기획서(`INTENT_PLANNING`), 성과 환류 분석(`INTENT_PRODUCTION`), KPI 대시보드 연동 등 복잡한 데이터 분석 및 프롬프트 내에 특정 복합 분석 단어(`planning`, `kpi`, `feedback`, `monetization`, `분석`, `기획`, `수익`)가 식별되면 Gemini 클라우드로 즉시 자동 전송 처리합니다.
2. **수동 강제 제어 (Manual Override)**:
   - `/mode auto`: 지능형 자동 전환 모드 (기본값)
   - `/mode manual_local`: 로컬 LLM 강제 처리 (비용 0원 최적화)
   - `/mode manual_cloud`: 클라우드 LLM 강제 처리 (고성능 추론)

---

## 3. 🛡️ 실행 SOP (Standard Operating Procedure)

1. **지시 데이터 구조화**: 모든 자연어 지시는 nlp/intent_parser를 거쳐 구조화된 JSON 데이터로 변환 후 렌더러와 상호작용합니다.
2. **보안 게이트 의무**: RAG에 적재되거나 수집된 지표 정보는 반드시 가디아의 `validate_rag_ingestion` 무결성 검증 및 `Monetization Gate` 금융 차단 필터를 거쳐야 합니다. 위협 감지 시 1초 내로 Safe Mode로 잠금하고 롤백합니다.
3. **2중 인터랙션**: 정기/반복적인 의사결정은 버튼(인라인 팝업)을 통하고, 특수/복합 요구사항은 자연어 채팅을 통해서만 수락합니다.
