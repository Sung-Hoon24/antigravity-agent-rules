import requests
import sys
import os

# 💡 [방어적 프로그래밍] 하위 디렉토리 실행 환경에서도 루트 경로의 config 모듈 임포트를 보장하기 위해 sys.path 보강
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


def test_lm_studio():
    # 💡 [한글 설명] 하드코딩된 API 주소 문자열을 Config 클래스의 호출로 대체하여 관리 지점을 일원화합니다.
    url = Config.LM_STUDIO_URL
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "google/gemma-4-e4b",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Reply in Korean.",
            },
            {"role": "user", "content": "안녕하세요! 간단한 인사 부탁드립니다."},
        ],
        "temperature": 0.7,
        "max_tokens": 100,
    }

    try:
        print("Sending request to LM Studio...")
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS! Response:")
            print(result["choices"][0]["message"]["content"])
        else:
            print(f"FAILED with status code {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error connecting to LM Studio: {e}")


if __name__ == "__main__":
    test_lm_studio()
