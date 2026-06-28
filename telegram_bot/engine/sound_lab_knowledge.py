# -*- coding: utf-8 -*-
"""
Sound Lab Knowledge Base (음원연구소 지식 DB)
- NotebookLM에서 추출한 사운드 믹싱, 주파수 이론, 로파이/웰니스 성공 문법 데이터
- 최신 경쟁 채널 5곳의 트렌드 분석 요약 (시뮬레이션)을 포함하여 템플릿 생성기(라비아/로컬 LLM)에 RAG 컨텍스트로 제공됩니다.
"""

import random

# RAG용 성공 문법 사전
SOUND_THEORY_DB = {
    "wellness": [
        "432Hz 주파수는 자연의 진동수로 심리적 안정감과 스트레스 해소를 유도함.",
        "528Hz 주파수는 DNA 복구 및 기적의 주파수로 불리며 명상 채널에서 CTR 15% 상승 효과 있음.",
        "베이스 패드(Pad) 신시사이저를 길게 지속시키면(Sustain) 뇌파를 알파파로 빠르게 유도 가능함.",
        "백그라운드 노이즈로 핑크 노이즈(파도 소리, 숲 소리)를 -18dB로 깔아주면 청취 유지 시간(Retention)이 급증함.",
    ],
    "lofi": [
        "BPM 70~75는 심장 박동수와 유사하여 업무 및 공부용 배경 음악(BGM)으로 가장 선호됨.",
        "Vinyl crackle(LP판 잡음) 텍스처를 삽입하면 아날로그 향수를 자극하여 퀄리티 인식을 높임.",
        "테이프 새츄레이션(Tape Saturation) 효과가 적용된 드럼 루프는 귀에 피로감을 덜 주어 장시간 시청을 유도함.",
        "Jazzy한 Rhodes 일렉트릭 피아노 코드를 엇박자로 배치하면 도심의 칠(Chill)한 감성을 극대화함.",
    ],
}

# 경쟁 채널 트렌드 시뮬레이션 데이터 (가상 스크래핑 요약본)
TREND_REPORTS = [
    "[Trend] 최근 'Lofi Girl' 채널은 아침 시간대 타겟으로 어쿠스틱 기타 리프를 강조하는 경향이 보임.",
    "[Trend] 명상 채널 'Yellow Brick Cinema'는 무거운 베이스보다는 티베탄 싱잉볼(Singing Bowl) 비중을 늘리는 중임.",
    "[Trend] 최신 유튜브 알고리즘은 12초마다 미세한 앰비언트 사운드 변화가 있는 음원에 가중치를 부여함.",
    "[Trend] 비가 내리는 소리(Rain Drop) 중에서도 '도시의 차창에 부딪히는 빗소리'의 클릭률이 20% 높음.",
]


def get_rag_context(channel_key: str) -> str:
    """채널 성격에 맞는 음원 지식 및 최신 트렌드를 랜덤으로 조합하여 반환합니다."""
    category = "lofi" if channel_key in ["rubia", "taipei"] else "wellness"

    selected_theories = random.sample(SOUND_THEORY_DB[category], 2)
    selected_trend = random.choice(TREND_REPORTS)

    context = (
        "💡 [Sound Lab Knowledge Base]\n"
        f"1. {selected_theories[0]}\n"
        f"2. {selected_theories[1]}\n"
        f"3. {selected_trend}\n"
    )
    return context
