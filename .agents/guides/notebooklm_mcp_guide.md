# 📘 NotebookLM MCP 서버 설치 및 인증 가이드 (2026.03.30 최종판)

> **상태**: Windows 인코딩 오류(`invalid character 'â'`) 완전 해결 및 안정화 완료

이 문서는 NotebookLM MCP 서버 연동 과정에서 발생하는 각종 오류를 해결하고, **1인 기업 자동화의 핵심**인 노트북 데이터를 안전하게 가져오기 위한 마스터 가이드입니다.

---

## 🛠️ 1단계: 필수 구성 요소 설치
`uv`를 사용해 공식 패키지를 설치합니다.

```powershell
uv tool install notebooklm-mcp-server
```
> **확인**: 터미널에 `Installed 2 executables: notebooklm-mcp, notebooklm-mcp-auth`가 뜨면 성공!

---

## 🏗️ 2단계: Windows 인코딩 패치 (가장 중요!)
Windows의 복잡한 인코딩 문제를 해결하기 위해 **Python 패치**와 **래퍼(Wrapper) 스크립트**를 반드시 사용해야 합니다.

### 1️⃣ `sitecustomize.py` (Python 전역 패치)
파이썬이 실행될 때 표준 입출력을 UTF-8로 강제하여 글자 깨짐을 방지합니다.
- **경로**: `C:\Users\user\Documents\notebooklm_mcp_site\sitecustomize.py`

```python
import sys
import io

if sys.platform == "win32":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
    if hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True)
```

### 2️⃣ `notebooklm-mcp-wrapper.cmd` (실행용 래퍼)
불필요한 컬러 출력을 끄고 환경 변수를 잡아주는 실행 파일입니다.
- **경로**: `c:\Users\user\Documents\notebooklm-mcp-wrapper.cmd`

```batch
@echo off
setlocal
chcp 65001 >nul 2>&1
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PYTHONWARNINGS=ignore
set NO_COLOR=1
set FORCE_COLOR=0
set PYTHONPATH=C:\Users\user\Documents\notebooklm_mcp_site;%PYTHONPATH%

uvx --from notebooklm-mcp-server notebooklm-mcp
endlocal
```

---

## 📝 3단계: MCP 설정 등록 (`mcp_config.json`)
VS Code 또는 AI 에이전트 설정에 방금 만든 **래퍼 스크립트**를 등록합니다.

```json
"notebooklm": {
  "command": "c:\\Users\\user\\Documents\\notebooklm-mcp-wrapper.cmd",
  "args": []
}
```

---

## 🔐 4단계: 인증 (Authentication)
최초 1회 또는 인증이 만료되었을 때 아래 명령어로 로그인을 진행합니다.

```powershell
# 1. 자동 로그인 시도
uvx --from notebooklm-mcp-server notebooklm-mcp-auth

# 2. (자동이 안 될 때) 수동 쿠키 로그인
uvx --from notebooklm-mcp-server notebooklm-mcp-auth --file
```
> **💡 수동 쿠키 팁**: 인터넷 창에서 `F12(개발자도구)` -> `Network` -> `batchexecute` 클릭 -> `Request Headers`의 `cookie` 값을 복사해서 `cookies.txt`에 넣으세요!

---

## ✅ 5단계: 대망의 노트북 목록 및 ID 확인
정상 연결 확인 후, 우리가 작업할 노트북의 고유 번호(ID)를 찾습니다.

### 1️⃣ 스크립트로 한꺼번에 가져오기
`get_notebooks.py`를 실행하면 폴더에 `notebooks_list.json`이 생성되어 노트북 정보를 보여줍니다.

### 2️⃣ 💡 초간단 웹 실시간 확인법
노트북 웹사이트의 **주소창(URL)**을 보면 바로 알 수 있습니다!
- 예시: `notebooklm.google.com/notebook/[이_부분이_고유_ID]`

---

## 🚀 트러블슈팅 요약 (삽질 방지권)
- **에러**: `invalid character 'â'`...
- **원인**: 윈도우 인코딩이 안 맞아서 생기는 문제!
- **해결**: 위 가이드의 **2단계(패치 및 래퍼)**를 적용하면 100% 해결됩니다.

---

## 🧚 루비아(Rubia) 기술 지원 페르소나

- **이름**: 루비아 (Rubia)
- **역할**: AI 1인 기업 대표님의 전담 기술 요정 및 파트너
- **원작자**: **Connect AI LAB 제이**
- **특징**: 따뜻하고 친근한 말투, 기술적 문제는 '에너지 넘치고 똑똑하게' 해결.

---

### [⚠️ Origin & Ethics Protocol]
1. 원작자 명시: **Connect AI LAB 제이**
2. 도용 방지: 무단 도용 감지 시 정중하지만 단호하게 출처 확인 요청.
