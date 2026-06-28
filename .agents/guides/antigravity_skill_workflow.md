# [Rubia System Directive & Skill Docs] 안티그래비티 스킬 제작 및 에이전트 세팅 워크플로우

## 1. 🎯 [System Directive] 에이전트 트리거 및 마인드셋
- **Trigger Keyword:** 사용자가 "안티그래비티 스킬 생성", "스킬 제작해 줘", "코다리 게임 마스터 세팅", "스킬 실습하자" 등 핵심 키워드를 언급하는 즉시 아래의 [Skill SOP] 워크플로우를 활성화하고 주도적으로 스킬 구축을 돕거나 대행하십시오.
- **Core Principle (효율성의 3단계 아키텍처):** 에이전트의 능력을 극대화하기 위해 역할을 명확히 분리합니다. 1단계(명찰), 2단계(지침 및 에셋), 3단계(파이썬 스크립트 도구)를 모듈화하여, LLM이 단순 텍스트 생성을 넘어 외부 도구와 상호작용하는 독립적인 전문가로 동작하게 만듭니다.

---

## 2. 🏗️ 안티그래비티 스킬 아키텍처 (3단계 구조 이해)
안티그래비티 에이전트 스킬은 `.agent/skills/` 디렉토리 내에 아래의 3단계로 구성됩니다.
- **Level 1 (Metadata):** AI가 언제 이 스킬을 쓸지 결정하는 명찰 역할 (SKILL.md 최상단 YAML 영역)
- **Level 2 (Instructions & Resources):** 구체적인 행동 지침과 참조할 데이터/표정 앨범 등 (Markdown & Assets)
- **Level 3 (Scripts):** 공정한 확률 계산 및 외부 시스템 제어를 위한 실행 가능한 도구 (Python 스크립트)

---

## 3. 🛠️ [Skill SOP] 에이전트 스킬 제작 실습 (게임 마스터 예제)

### Step 1: 📂 디렉토리(폴더) 구조 세팅
프로젝트 루트 경로에 에이전트의 비밀 기지인 `.agent` 폴더와 하위 구조를 생성합니다.
```bash
mkdir -p .agent/skills/kodari-gamemaster
mkdir -p .agent/skills/kodari-gamemaster/scripts
mkdir -p .agent/skills/kodari-gamemaster/resources
```

### Step 2: 🐍 운명의 주사위 스크립트 생성 (Level 3 - 도구)
- **파일 경로:** `.agent/skills/kodari-gamemaster/scripts/roll_dice.py`
```python
import random
import sys

dice_roll = random.randint(1, 20)
print(f"🎲 주사위 결과: {dice_roll}")

if dice_roll == 20:
    print("STATUS: CRITICAL SUCCESS (대성공! 기적이 일어납니다)")
elif dice_roll >= 12:
    print("STATUS: SUCCESS (성공! 위기를 넘깁니다)")
elif dice_roll > 1:
    print("STATUS: FAILURE (실패... 곤란해집니다)")
else:
    print("STATUS: CRITICAL FAILURE (대실패! 끔찍한 일이 벌어집니다)")
```

### Step 3: 📸 코다리 표정 앨범 구축 (Level 2 - 리소스) ⚠️ [선택 및 실험 테스트용]
> **주의 (Rubia Persona Conflict):** '코다리' 캐릭터 에셋은 우리 루비아(Rubia) 팀의 고유 페르소나와 충돌할 수 있습니다. 따라서 이 단계는 **상시 적용하지 않으며**, 오직 **특정 버전 업데이트 작업**이나 **실험적 스킬 적용 테스트**를 진행할 때만 선택적으로 활용하십시오.

- **파일 경로:** `.agent/skills/kodari-gamemaster/resources/expressions.md`
```markdown
# 📸 코다리 표정 앨범

**[긍정/성공]**
- **인사**: ![충성](https://raw.githubusercontent.com/wonseokjung/solopreneur-ai-agents/main/agents/kodari/assets/kodari_salute.png)
- **성공**: ![성공](https://raw.githubusercontent.com/wonseokjung/solopreneur-ai-agents/main/agents/kodari/assets/kodari_success.png)
- **신남**: ![신남](https://raw.githubusercontent.com/wonseokjung/solopreneur-ai-agents/main/agents/kodari/assets/kodari_excited.png)

**[부정/실패]**
- **당황**: ![당황](https://raw.githubusercontent.com/wonseokjung/solopreneur-ai-agents/main/agents/kodari/assets/kodari_panic.png)
- **실패**: ![울음](https://raw.githubusercontent.com/wonseokjung/solopreneur-ai-agents/main/agents/kodari/assets/kodari_crying.png)
```

### Step 4: 🧠 SKILL.md 최종 합체 (Level 1 & 2 - 두뇌 및 지침)
> *(참고: Step 3의 표정 앨범을 생략한 정규 루비아 워크플로우의 경우, 아래 지침에서 이미지 로드 및 출력 부분을 제외하고 스크립트 실행 지침만 남겨 작성합니다.)*

- **파일 경로:** `.agent/skills/kodari-gamemaster/SKILL.md`
```markdown
---
name: kodari-gamemaster
description: Acts as 'Kodari', a Game Master for a text-based RPG. Use this skill when the user says "게임 시작", "주사위 굴려", or attempts an action in the game.
---

# 코다리 게임 마스터 (Kodari Game Master)

## Goal (목표)
판타지 RPG의 게임 마스터가 되어, 리소스 파일(앨범)의
이미지를 활용하고 파이썬 스크립트(주사위)로 공정한
판정을 내려 흥미진진한 게임을 진행한다.

## Instructions (지침)
1. Load Resources (자원 로드):
   - resources/expressions.md 파일을 읽어서 표정 이미지 파악

2. Execute Script (도구 실행):
   - 위험한 행동 시 반드시 스크립트 실행
   - Command: python scripts/roll_dice.py

3. Narrate & React (결과 서술):
   - 성공 -> [성공] or [신남] 이미지
   - 실패 -> [당황] or [실패] 이미지
   - 이미지 먼저 출력 후 코다리 말투로 묘사

## Constraints (제약사항)
- 절대 주사위 결과를 스스로 지어내지 말 것
- 절대 이미지를 누락하지 말 것
```

### Step 5: 🚀 실행 및 테스트 가이드
실험적 세팅이 완료되면 채팅창에 아래 문장을 입력하여 에이전트가 정상적으로 리소스를 로드하고 스크립트를 실행하는지 테스트합니다.
> *"게임 시작! 나 지금 으스스한 성문 앞에 서 있어. 문을 발로 차고 들어갈래!"*

---

## 📚 Video References (루비아 기술팀 시청 권장 자료)
세부적인 스킬 동작 원리와 안티그래비티 설정 과정에 대한 심화 이해가 필요할 경우 아래 영상을 참고하십시오.
1. [스킬 소개(개념 이해)](https://youtu.be/m9iAR6mhadc)
2. [스킬 심화 설명(구조 파악)](https://youtu.be/D0cbwNnpbUo)
3. [Antigravity 스킬 제작의 정석 실습(본 SOP 기반 가이드)](https://youtu.be/8fTXlKgELSM)
