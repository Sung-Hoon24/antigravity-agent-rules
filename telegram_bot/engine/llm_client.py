# -*- coding: utf-8 -*-
"""
하이브리드 LLM 클라이언트
- 모드("cloud", "local")에 따라 Gemini API 또는 LM Studio/Ollama(로컬)로 요청을 분기합니다.
- 구조화된 JSON 데이터 생성을 지원하며 로컬 실패 시 클라우드로 자동 폴백합니다.
"""

import os
import sys
import json
import logging
import requests
from dotenv import load_dotenv
from typing import Optional


# 💡 [방어적 프로그래밍] 프로젝트 루트 경로를 sys.path 최상단에 추가하여 telegram_bot/config.py가 아닌 루트의 config.py 모듈 임포트를 확보합니다.
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from config import Config


# 로깅 설정: 디버깅 역량 강화 및 가디아 보안 감사 추적용
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLMClient")

try:
    from google import genai
    from google.genai import types
except ImportError:
    pass

# 💡 [방어적 프로그래밍] langchain-ollama 패키지가 설치되지 않았거나 로드 중 에러가 날 경우를 대비한 가비지 방지용 패치
try:
    from langchain_ollama import ChatOllama

    LANGCHAIN_OLLAMA_AVAILABLE = True
except ImportError:
    LANGCHAIN_OLLAMA_AVAILABLE = False


def determine_routing_mode(
    prompt: str, system_instruction: str, has_schema: bool = False
) -> str:
    """
    [하이브리드 라우팅 의사결정 필터]
    - config.HYBRID_ROUTING_MODE에 맞춰 실제 동작할 모드("cloud" 또는 "local")를 반환합니다.
    - "auto" 상태일 경우, 복합 업무(구조화 스키마 존재 여부, 분석/기획/수익 등 고도 추론 키워드 매칭)는 cloud로,
      경량 업무는 local로 라우팅합니다.
    """
    import telegram_bot.config as config

    routing_mode = getattr(config, "HYBRID_ROUTING_MODE", "auto")

    # 1. 수동 강제 로컬 모드
    if routing_mode == "manual_local":
        return "local"
    # 2. 수동 강제 클라우드 모드
    elif routing_mode == "manual_cloud":
        return "cloud"

    # 3. 스마트 자동 전환 모드 (auto)
    # - 구조화 JSON 스펙(schema)이 있거나, 복합 태스크 키워드가 포함되어 있다면 클라우드로 라우팅
    complex_keywords = [
        "planning",
        "kpi",
        "feedback",
        "monetization",
        "분석",
        "기획",
        "수익",
        "성공 문법",
        "대시보드",
    ]
    combined_text = (prompt + " " + system_instruction).lower()

    is_complex = has_schema or any(k in combined_text for k in complex_keywords)

    if is_complex:
        logger.info("🤖 [Hybrid Routing] 복합 분석 업무 감지 -> 구글 Gemini 클라우드 자동 배정")
        return "cloud"
    else:
        logger.info("🤖 [Hybrid Routing] 경량/단순 대화 업무 감지 -> 로컬 LLM(Ollama) 우선 자동 배정")
        return "local"


def generate_text(
    prompt: str,
    system_instruction: str,
    mode: Optional[str] = None,
    local_url: Optional[str] = None,
) -> str:
    """지정된 모드에 따라 LLM 엔진을 호출하여 텍스트를 생성합니다."""

    # 💡 [한글 설명] 모드가 명시적으로 주어지지 않은 경우 하이브리드 라우팅 판단을 실행
    if mode is None:
        mode = determine_routing_mode(prompt, system_instruction, has_schema=False)

    if mode == "local":
        print(f"💡 [LLM Client] 로컬 엔진 가동 중... (URL: {local_url or '환경변수 기본값'})")

        load_dotenv(r"c:\1인기업\Apps\유튜브에이전트\.env")
        # 💡 [한글 설명] 하드코딩된 로컬 API URL 문자열을 중앙 관리용 Config 모듈의 호출로 대체합니다.
        base_url = local_url or Config.get_active_url()
        model_name = os.getenv("LOCAL_LLM_MODEL", "google/gemma-4-e4b")

        if (
            "11434" in base_url
            and not base_url.endswith("/v1/chat/completions")
            and not base_url.endswith("/api/generate")
        ):
            base_url = base_url.rstrip("/")
            base_url = f"{base_url}/v1/chat/completions"
            print(f"💡 [LLM Client] Ollama 포트 감지: API 엔드포인트를 '{base_url}'로 자동 보정합니다.")

        headers = {"Content-Type": "application/json"}
        data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 1500,
        }

        try:
            response = requests.post(base_url, headers=headers, json=data, timeout=120)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise RuntimeError(
                    f"로컬 LLM 오류: {response.status_code} - {response.text}"
                )
        except Exception as e:
            raise RuntimeError(
                f"로컬 LLM (Ollama/LM Studio) 연결 실패: {e}\n(로컬 LLM 엔진이 켜져 있고 모델이 정상 로드되었는지 확인하세요.)"
            )

    else:
        print("☁️ [LLM Client] 구글 Gemini 클라우드 엔진 가동 중...")
        load_dotenv(r"c:\1인기업\Apps\유튜브에이전트\.env")
        api_key_env = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEYS")
        if not api_key_env:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

        api_key = api_key_env.split(",")[0].strip()
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
            ),
        )
        return response.text


def generate_structured_json(
    prompt: str,
    system_instruction: str,
    response_schema: type,
    mode: str = None,
    local_url: str = None,
) -> dict:
    """
    로컬 LLM(Ollama) 또는 Gemini Cloud API를 호출하여 Pydantic 스키마 형태의 정형 JSON 데이터를 생성합니다.
    로컬 호출 실패 및 파싱 에러 발생 시 자동으로 Gemini Cloud로 폴백합니다.
    """
    if mode is None:
        mode = determine_routing_mode(prompt, system_instruction, has_schema=True)

    load_dotenv(r"c:\1인기업\Apps\유튜브에이전트\.env")

    # 💡 [폴백 라우팅 설계] 로컬 환경 오류 감지 시 클라우드로 즉시 복구될 수 있는 안전 레이어를 구성합니다.
    if mode == "local":
        # 💡 [한글 설명] 하드코딩된 로컬 API URL 문자열을 중앙 관리용 Config 모듈의 호출로 대체합니다.
        base_url = local_url or Config.get_active_url()
        model_name = os.getenv("LOCAL_LLM_MODEL", "google/gemma-4-e4b")

        # 💡 [방어적 프로그래밍] Ollama 전용 base_url 파싱
        # langchain_ollama는 기본 포트 11434를 그대로 호스트로 사용하므로 v1 엔드포인트를 떼어내어 파싱합니다.
        ollama_host = (
            base_url.replace("/v1/chat/completions", "").replace("/v1", "").rstrip("/")
        )

        logger.info(
            f"💡 [LLM Client] 로컬 JSON 구조화 엔진 시도 중... (Host: {ollama_host}, Model: {model_name})"
        )

        try:
            # 1단계 시도: langchain-ollama 패키지 활용
            if LANGCHAIN_OLLAMA_AVAILABLE and "11434" in base_url:
                try:
                    logger.info("💡 [LLM Client] 1단계: langchain-ollama 라이브러리 연동 시도")
                    chat_model = ChatOllama(
                        base_url=ollama_host,
                        model=model_name,
                        temperature=0.7,
                        format="json",  # Ollama 레벨에서 JSON으로 제한 강제
                        timeout=120,
                    )
                    structured_chain = chat_model.with_structured_output(
                        response_schema
                    )
                    # Chat 메시지 포맷에 시스템 지시문과 프롬프트를 래핑하여 주입
                    messages = [("system", system_instruction), ("human", prompt)]
                    # 동기 실행
                    result = structured_chain.invoke(messages)

                    # 결과값 유효성 체크 및 사전 변환
                    if hasattr(result, "dict"):
                        return result.dict()
                    elif isinstance(result, dict):
                        return result
                    else:
                        raise ValueError(
                            f"정상적인 Pydantic 형식을 반환받지 못했습니다. 반환타입: {type(result)}"
                        )
                except Exception as chain_err:
                    # 💡 [한글 설명] langchain-ollama 연동이 서버 환경이나 모델 호환성 문제로 실패하면,
                    # 즉시 렌더링을 차단하지 않고 OpenAI 규격의 HTTP API 호출 방식으로 핫스왑 구제하여 로컬 자립성을 보존합니다.
                    logger.warning(
                        f"⚠️ [LLM Client] langchain-ollama 호출 실패 ({chain_err}). 2단계 OpenAI 호환 API 직접 호출로 구제를 시도합니다."
                    )

            # 2단계 시도: OpenAI 호환 직접 HTTP 요청 (langchain-ollama 미보유 시 혹은 1단계 에러 시)
            logger.info("💡 [LLM Client] 2단계: OpenAI 호환 로컬 API 구조화 직접 시도")
            headers = {"Content-Type": "application/json"}
            data = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
                "response_format": {"type": "json_object"},  # API 레벨 JSON 출력 보장 지시
                "max_tokens": 2000,
            }

            # API 호출 엔드포인트 세팅
            endpoint = base_url
            if "11434" in endpoint and not endpoint.endswith("/v1/chat/completions"):
                endpoint = f"{ollama_host}/v1/chat/completions"

            response = requests.post(endpoint, headers=headers, json=data, timeout=120)
            if response.status_code == 200:
                content_str = response.json()["choices"][0]["message"][
                    "content"
                ].strip()

                # 💡 [한글 설명 - 방어적 프로그래밍] 로컬 모델이 마크다운 백틱 이나 잡단 텍스트를 JSON 바깥에 노출시켰을 경우,
                # 정규식을 이용해 순수 JSON 중괄호 영역만 강제 정화하여 파싱 에러를 미연에 방지합니다.
                import re

                json_match = re.search(r"\{.*\}", content_str, re.DOTALL)
                if json_match:
                    content_str = json_match.group(0)

                json_data = json.loads(content_str)
                # Pydantic 모델을 통한 최종 데이터 형식 강제 검증 수행 (쓰레기 데이터 1차 폐기)
                validated_model = response_schema(**json_data)
                return validated_model.dict()
            else:
                raise RuntimeError(
                    f"로컬 API 오류 응답: {response.status_code} - {response.text}"
                )

        except Exception as local_err:
            # 🚨 [가디아 보안 규칙 및 자가 치유 로그 기록]
            # 로컬 LLM JSON 생성 중 발생하는 모든 에러를 포착하고 상세 내역을 수집합니다.
            logger.error(
                f"🚨 [JSON_PARSE_FAILED] 로컬 구조화 엔진 호출 최종 실패. 즉시 구글 Gemini 클라우드로 전환합니다.\n"
                f"Error Details: {local_err}",
                exc_info=True,
            )
            # 클라우드로 즉시 모드 전환을 실행하고 다음 단계로 진입
            mode = "cloud"

    # ☁️ [Gemini Cloud API 폴백 및 기본 경로]
    logger.info("☁️ [LLM Client] Gemini 클라우드 JSON 구조화 엔진 가동 시작...")
    api_key_env = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEYS")
    if not api_key_env:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

    api_key = api_key_env.split(",")[0].strip()
    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
                response_mime_type="application/json",  # Gemini JSON 스펙 강제
                response_schema=response_schema,  # 구글 SDK 정형 스키마 바인딩
            ),
        )
        # 반환값 JSON 로드 및 검증
        output_dict = json.loads(response.text)
        validated_model = response_schema(**output_dict)
        return validated_model.dict()
    except Exception as cloud_err:
        logger.critical(
            f"🔥 [CRITICAL] 클라우드 폴백 엔진마저 오류가 발생했습니다. 시스템 복구 대기를 시작합니다.\n"
            f"Error Details: {cloud_err}",
            exc_info=True,
        )
        raise RuntimeError(f"최종 LLM 구조화 데이터 획득 실패: {cloud_err}")
