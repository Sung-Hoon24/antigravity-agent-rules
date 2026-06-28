# [Rubia System Directive & Skill Docs] 페이팔 & 파이어베이스 MCP 자동화 워크플로우

## 1. 🎯 [System Directive] 에이전트 트리거 및 마인드셋

- **Trigger Keyword:** 사용자가 "페이팔 mcp 연결", "파이어베이스 mcp 연결", "결제 자동화 세팅" 혹은 이와 유사한 핵심 키워드를 언급하는 즉시 아래의 [Skill SOP] 워크플로우를 활성화하고 주도적으로 안내 및 세팅을 대행하십시오.
- **Core Principle (Just Ship It):** 1년에 12개 스타트업, 70개 서비스를 런칭하여 95%가 실패하더라도 5%의 성공으로 연 40억 매출을 올리는 피터 레벨스(Peter Levels)의 1인 기업가 철학을 따릅니다. 완벽주의에 빠지지 말고, 빠른 실행과 시장 검증에 집중하여 자동화 파이프라인(결제/백엔드)을 신속하게 구축하세요.

---

## 2. 🛠️ [Skill SOP] 페이팔(PayPal) MCP 연동 워크플로우

### Step 1: 비즈니스 샌드박스 세팅

1. **계정 유형:** 페이팔 코리아 접속 후 반드시 `비즈니스(Business)` 계정 가입 (생산자/수익화 목적). *사업자등록증이 없는 개인/프리랜서도 무관함.*
2. **영문 주소:** 구글 및 LLM 프롬프트를 활용하여 한국 주소를 영문 폼으로 자동 변환하여 주입.
3. **계좌 연동(Link Bank):** 은행 고유의 영문명 및 Swift Code 확인 후 입력 (주로 세이빙 계좌 활용).
4. **API 키 발급:** 비즈니스 툴 > API Credentials 접속 후 `Sandbox(테스트 환경)` 모드에서 App을 생성하여 **Client ID** 및 **Secret Key** 확보.
5. **가상 테스트 계정:** 글로벌 결제 테스트를 위해 테스팅 툴에서 해외 `Sandbox Accounts (Buyer)` 계정을 별도로 생성해 둘 것.

### Step 2: 🚨 안티그래비티 MCP 서버 설정 (Raw Config 주입)

안티그래비티 UI에서 직접 컨피그 설정 시 초기화 오류(`Initialize Error`)가 잦으므로, 반드시 `View Raw Config`를 열어 아래의 JSON 규격으로 직접 수정하거나 에이전트에게 수정을 지시해야 합니다.

**[에이전트 주입용 MCP Config JSON]**

```json
{
  "mcpServers": {
    "paypal-mcp-server": {
      "command": "npx",
      "args": [
        "-y",
        "@paypal/mcp",
        "--tools=all",
        "--access-token=발급받은_엑세스토큰_또는_Client_Secret_입력",
        "--paypal-environment=sandbox"
      ],
      "env": {}
    }
  }
}
```

---

## 3. 🔥 [Skill SOP] 파이어베이스(Firebase) MCP 연동 워크플로우

### Step 1: 파이어베이스 플랫폼 활용 목적

- **인프라 자동화:** 빠른 MVP 빌딩 및 시장 검증을 위해 복잡한 물리 서버 세팅 없이 데이터베이스, 회원가입/로그인 로직, 스토리지 관리를 파이어베이스 온라인 기반으로 대치.
- **수익화 최적화:** 유튜브 에드센스와 웹/앱 기반의 구글 애드몹(AdMob)을 구글 생태계 내에서 통합 연동하여 솔로프레너의 광고 수익 구조 최적화.

### Step 2: MCP 서버 설치 및 체크

1. 안티그래비티 MCP Servers 메뉴 접속 > `firebase` 검색 > `Install` 클릭.
2. 설치 완료 후 반드시 아래 명령어로 에이전트 툴 로드 상태를 체크할 것.

- **검증 프롬프트:** `"파이어베이스 연동 체크해 줘. MCP 툴 목록에 정상 반영됐는지 확인해 봐."`
- 에이전트는 이를 통해 로그인/로그아웃, 프로젝트 관리, 데이터베이스 연결, 앱 등록(iOS, Android, Web) 등의 백엔드 구축 과정을 획기적으로 자동화합니다.
