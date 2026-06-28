# -*- coding: utf-8 -*-
"""
[제1연구소 운영 비용 관리 모듈] API 호출 비용 로거 (cost_logger.py)
- 모든 유료 API(Gemini, Lyria, Imagen 등) 호출 시의 정확한 발생 요금을 database/api_cost_log.json에 기록합니다.
- 로컬 LLM 구동 시 절감된 가상 요금 또한 별도로 기록하여 주간 성적표(Evolution Report)에 반영합니다.
"""

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger("RubiaCostLogger")
DB_PATH = r"c:\1인기업\Apps\유튜브에이전트\database\api_cost_log.json"


def log_api_cost(api_name: str, cost: float, detail: str = "") -> None:
    """
    API 호출 비용을 실시간 로깅하고 DB에 영구 기록합니다.
    방어적 프로그래밍을 적용하여 파일이 잠겨 있거나 오류 발생 시에도 크래시를 유발하지 않고 격리합니다.
    """
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

        # 기존 로그 데이터 로드
        log_data = []
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f:
                    log_data = json.load(f)
            except Exception:
                log_data = []

        # 새 로그 객체 생성
        entry = {
            "timestamp": datetime.now().isoformat(),
            "api_name": api_name,
            "cost": float(cost),
            "detail": str(detail),
        }
        log_data.append(entry)

        # 파일 저장
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=4, ensure_ascii=False)

        logger.info(f"💵 [Cost Logged] {api_name} - ${cost:.5f} ({detail})")
    except Exception as e:
        logger.error(f"🚨 [Cost Logger Error] 비용 로깅 실패: {e}")
