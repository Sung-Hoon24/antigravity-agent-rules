---
name: character-asset-labeler
description: Automatically overlays a premium gradient bar and English Name/Role label onto the bottom of character persona images in the workspace to optimize layout and reduce chat token consumption.
---

# 🎨 캐릭터 에셋 프리미엄 자동 라벨러 (Character Asset Labeler)

## Goal (목표)
대표님과의 대화 시 텍스트 헤더 중복 출력을 방지하여 **토큰 소모량을 대폭 절감**하고, 캐릭터 이미지 자체에 고해상도 프리미엄 자막(이름/역할)을 영구적으로 합성하는 자동화 도구입니다.

---

## 🏗️ 스킬 아키텍처 (3단계 구조)
- **Level 1 (Metadata):** 위 YAML 영역의 메타데이터 (언제 이 스킬을 쓸지 결정)
- **Level 2 (Instructions):** 본 가이드의 행동 지침 및 폰트 에셋 구조
- **Level 3 (Scripts):** 파이썬 Pillow 라이브러리로 제작된 이미지 변환 스크립트
  - [label_all_characters.py](file:///c:/1인기업/Apps/유튜브에이전트/.agents/skills/character-asset-labeler/scripts/label_all_characters.py)

---

## 🛠️ [SOP] 사용 지침

### 1. 폰트 및 에셋 요구사항
라벨링을 수행하기 위해 프로젝트 내 `assets/fonts` 폴더에 아래의 Google Fonts가 준비되어 있어야 합니다.
* `DancingScript-Variable.ttf` (성명 필기체용)
* `Montserrat-Variable.ttf` (기본 기하학 폰트 - 백업용)
* Windows 시스템 기본 폰트인 **Segoe UI Bold (`segoeuib.ttf`)** 또는 **Arial Bold (`arialbd.ttf`)**를 사용하여 역할명을 선명하게 출력합니다.

### 2. 캐릭터 매칭 테이블
| 에이전트 폴더 | 성명 (Name) | 역할 (Role) | 텍스트 컬러 |
| :--- | :--- | :--- | :--- |
| **Rubia** | Rubia | Project Director | 흰색 (#FFFFFF) |
| **Ravia** | Ravia | Planning Director | 흰색 (#FFFFFF) |
| **Intella** | Intella | Research Lead | 흰색 (#FFFFFF) |
| **Cordia** | Cordia | Technical Lead | 흰색 (#FFFFFF) |
| **Signa** | Signa | Optimization Lead | 흰색 (#FFFFFF) |
| **Guardia** | Guardia | Safety Lead | 흰색 (#FFFFFF) |

### 3. 이미지 합성 디자인 스펙 (v2 Approved)
* **배경 바:** 높이 18%의 2단계 수평 그라데이션.
  - 좌측 55% 구간: 95% ~ 75%의 높은 어두운 투명도로 텍스트 대비(시인성) 확보.
  - 우측 45% 구간: 75% ~ 0%로 은은하게 투명해짐.
* **상단 글로잉 보더:** 2px 두께의 금빛(#e6be78) 광원 효과 및 서서히 사라지는 그라데이션.
* **성명:** *Dancing Script* 필기체 적용, 1px 드롭 섀도우 처리.
* **역할명:** **Segoe UI Bold** 대문자 적용, 8방향 1px 아웃라인(외곽선) 처리로 어떤 색상의 배경 위에서도 시인성 100% 보장.

---

## 🚀 실행 명령어
신규 이미지가 추가되거나 라벨링 갱신이 필요할 경우, 터미널에서 다음 명령어를 실행하여 전체 에셋을 한 번에 업데이트합니다.
*(스크립트 실행 시 기존 이미지 원본은 자동으로 `backups/characters_backup_YYYYMMDD_HHMMSS` 폴더로 백업됩니다.)*

```powershell
python .agents/skills/character-asset-labeler/scripts/label_all_characters.py
```
