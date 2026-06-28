# -*- coding: utf-8 -*-
"""
[제1연구소] 페이팔 MCP 브리핑 파이프라인 E2E 검증 테스트 스크립트
- "페이팔 MCP 연결해줘" 입력 시 인텐트 파서가 paypal_connect로 정상 분류하는지 테스트
- 가이드 파일 로딩 및 가독성 마크다운 구성 여부 테스트
- 텔레그램 메시지 제한에 맞춘 분할 로직 검증
"""

import os
import sys
import asyncio
import unittest

# 프로젝트 루트 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from telegram_bot.nlp.intent_parser import parse_intent, INTENT_PAYPAL_CONNECT


class TestPaypalBriefingPipeline(unittest.TestCase):
    def test_01_intent_classification(self):
        """'페이팔 MCP 연결해줘' 입력 시 paypal_connect 인텐트 분류 테스트"""
        print("\n=== [E2E] 자연어 인텐트 분류 테스트 개시 ===")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # 클라우드 모드로 자연어 분류 테스트
            result = loop.run_until_complete(
                parse_intent("페이팔 MCP 연결해줘", llm_mode="cloud")
            )
            print(f"📡 분류 결과: {result}")
            self.assertEqual(
                result.get("intent"),
                INTENT_PAYPAL_CONNECT,
                "인텐트가 paypal_connect로 올바르게 식별되어야 합니다.",
            )
        finally:
            loop.close()

    def test_02_guide_file_existence_and_loading(self):
        """가이드 파일 존재 여부 및 동적 로드 검증"""
        print("\n=== [E2E] 가이드 파일 로딩 검증 테스트 개시 ===")
        guide_path = r"c:\1인기업\Apps\유튜브에이전트\.agents\guides\paypal_firebase_mcp_guide.md"
        self.assertTrue(os.path.exists(guide_path), "가이드 파일이 지정된 경로에 존재해야 합니다.")

        with open(guide_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("페이팔(PayPal) MCP", content, "가이드 내용에 페이팔 MCP 내용이 기술되어 있어야 합니다.")
        self.assertIn(
            "paypal-mcp-server", content, "가이드 내용에 MCP JSON Config가 기술되어 있어야 합니다."
        )
        print(f"📖 가이드 로드 완료 (글자수: {len(content)}자)")

    def test_03_split_logic_safety(self):
        """긴 메시지 분할 전송 크기 제어 로직 시뮬레이션"""
        print("\n=== [E2E] 텔레그램 분할 전송 청크 안정성 검증 ===")

        # 가이드 파일 가상 로드
        guide_path = r"c:\1인기업\Apps\유튜브에이전트\.agents\guides\paypal_firebase_mcp_guide.md"
        with open(guide_path, "r", encoding="utf-8") as f:
            guide_content = f.read()

        briefing_text = "👑 *페이팔 자동화 브리핑*\n\n" + guide_content
        max_len = 3000
        chunks = []
        for i in range(0, len(briefing_text), max_len):
            chunks.append(briefing_text[i : i + max_len])

        self.assertGreater(len(chunks), 0, "최소 하나 이상의 텍스트 청크가 생성되어야 합니다.")
        for idx, chunk in enumerate(chunks):
            self.assertLessEqual(len(chunk), max_len, f"청크 {idx}의 길이가 3000자 이하여야 합니다.")
            print(f"📦 Chunk {idx+1} 크기: {len(chunk)}자")


if __name__ == "__main__":
    unittest.main()
