# -*- coding: utf-8 -*-
"""
캐릭터 이미지 파일 매핑 및 로테이션 헬퍼
- assets/characters 디렉토리에서 각 에이전트 캐릭터의 이미지 파일을 탐색하고 로테이션하여 매핑합니다.
- 무드(mood) 키워드 매칭을 기반으로 동적 탐색하여 대표님이 추가하는 새 이미지도 자동으로 감지합니다.
"""

import os
import random
import glob

# 캐릭터 이미지 디렉토리 기본 경로
CHARACTERS_ROOT = r"c:\1인기업\Apps\유튜브에이전트\assets\characters"


def get_agent_image_path(agent_name: str, mood: str = "greeting") -> str:
    """
    지정된 에이전트와 무드에 맞는 이미지 파일의 절대 경로를 반환합니다.

    Args:
        agent_name: 에이전트 이름 (rubia, ravia, intella, cordia, signa, guardia, stella 등)
        mood: 상황/기분 키워드 (greeting, work/working, success, heart, scrutiny, yoga, vacation, with_leader, workout)

    Returns:
        str: 이미지 파일의 절대 경로 (없을 경우 fallback 이미지 경로 또는 None)
    """
    agent_name = agent_name.lower().strip()
    mood = mood.lower().strip()

    # 1. 에이전트 폴더명 찾기 (대소문자 방어)
    agent_dir = None
    if os.path.exists(CHARACTERS_ROOT):
        for folder_name in os.listdir(CHARACTERS_ROOT):
            if folder_name.lower() == agent_name:
                agent_dir = os.path.join(CHARACTERS_ROOT, folder_name)
                break

    if not agent_dir or not os.path.isdir(agent_dir):
        # 폴더를 찾지 못한 경우 None 반환
        return None

    # 2. 해당 폴더 내의 모든 png, jpg 파일 목록 가져오기
    image_files = glob.glob(os.path.join(agent_dir, "*.png")) + glob.glob(
        os.path.join(agent_dir, "*.jpg")
    )
    if not image_files:
        return None

    # 3. 무드 키워드 매칭 수행
    # 대표 무드 별칭 매핑
    mood_aliases = {
        "working": ["work", "working", "office", "reading"],
        "work": ["work", "working", "office", "reading"],
        "success": ["success", "triumphant", "excited", "thumbsup"],
        "heart": ["heart", "love"],
        "scrutiny": ["scrutiny", "command", "directorial"],
        "yoga": ["yoga", "stretch", "workout"],
        "workout": ["workout", "workout_v2", "yoga", "stretch"],
    }

    keywords = mood_aliases.get(mood, [mood])

    # 키워드 중 하나라도 파일명에 들어있는 파일 필터링
    matched_files = []
    for filepath in image_files:
        filename = os.path.basename(filepath).lower()
        if any(keyword in filename for keyword in keywords):
            matched_files.append(filepath)

    # 4. 일치하는 파일이 있으면 로테이션(랜덤 선택)
    if matched_files:
        # 최신 추가된 이미지(_v1, _v2, _new 등)에 약간 더 가중치를 주거나 단순히 랜덤 로테이션 수행
        return random.choice(matched_files)

    # 5. 매칭되는 무드가 없으면 기본 greeting 이미지 탐색
    greeting_files = [
        f for f in image_files if "greeting" in os.path.basename(f).lower()
    ]
    if greeting_files:
        return random.choice(greeting_files)

    # 6. 그것도 없으면 아무 이미지나 반환
    return random.choice(image_files)
