# -*- coding: utf-8 -*-
"""
[R&D Lab] 기획-렌더러 연계 인터페이스 무결성 검증 테스트 스크립트
- validate_planning_json 검증 게이트 작동 테스트 (정상 통과 및 쓰레기 데이터 차단)
- video_renderer.py 내 parse_script_to_ass의 JSON 자막 동기화 및 기존 줄글 텍스트 하위 호환성 테스트
"""

import os
import tempfile
import unittest
from telegram_bot.handlers.production import validate_planning_json
from telegram_bot.engine.video_renderer import parse_script_to_ass


class TestPipelineInterface(unittest.TestCase):
    def setUp(self):
        # 테스트용 임시 디렉토리 및 파일 경로 지정
        self.test_dir = tempfile.TemporaryDirectory()
        self.ass_path = os.path.join(self.test_dir.name, "test_subtitles.ass")

        # 1. 정상 구조화 JSON 샘플
        self.valid_json = {
            "concept": "힐링 요가 명상 숏폼",
            "youtube_title": "10분 아침 요가 스트레칭",
            "youtube_description": "상쾌한 아침을 여는 힐링 요가 음악입니다.",
            "youtube_tags": ["요가", "명상", "스트레칭"],
            "playlist": [{"title": "Morning Peace", "duration_sec": 300}],
            "captions": [
                {"time_code": "00:02", "text": "아침 요가를 시작합니다."},
                {"time_code": "00:15", "text": "숨을 천천히 들이마시고 내쉬세요."},
                {"time_code": "00:30", "text": "몸의 긴장을 완전히 풀어줍니다."},
            ],
            "visual_audio_guide": "따뜻한 아침 햇살 무드의 시각 연출",
        }

        # 2. 비정상 JSON 샘플 (필수 필드 'captions' 결손)
        self.invalid_json_no_captions = {
            "concept": "자막이 없는 기획안",
            "youtube_title": "제목만 있는 비디오",
            "youtube_description": "설명란 내용",
            "youtube_tags": ["태그"],
            "playlist": [{"title": "Track 1", "duration_sec": 60}],
            "captions": [],  # 비어 있음
            "visual_audio_guide": "가이드",
        }

        # 3. 비정상 JSON 샘플 (자막 구조 훼손)
        self.invalid_json_corrupted_captions = {
            "concept": "자막이 깨진 기획안",
            "youtube_title": "테스트 타이틀",
            "youtube_description": "설명",
            "youtube_tags": ["태그"],
            "playlist": [{"title": "Track 1", "duration_sec": 60}],
            "captions": [{"time_code": "00:02"}],  # 'text' 누락
            "visual_audio_guide": "가이드",
        }

        # 4. 하위 호환성 문자열(텍스트) 대본 샘플
        self.legacy_script_text = (
            "자막: Close your eyes and breathe in.\n"
            "자막: Feel the warm energy flowing.\n"
            "자막: Let go of all your tension."
        )

    def tearDown(self):
        # 임시 디렉토리 정리
        self.test_dir.cleanup()

    def test_validation_gate_success(self):
        """정상 JSON 데이터가 Validation Gate를 올바르게 통과하는지 검증"""
        try:
            validate_planning_json(self.valid_json)
        except Exception as e:
            self.fail(f"정상 JSON 데이터 검증 실패: {e}")

    def test_validation_gate_discard_empty_captions(self):
        """자막이 빈 쓰레기 JSON 데이터가 올바르게 차단(Discard)되는지 검증"""
        with self.assertRaises(ValueError) as context:
            validate_planning_json(self.invalid_json_no_captions)
        self.assertTrue(
            "자막 대본(captions) 리스트가 비어 있거나" in str(context.exception)
            or "필수 메타데이터 필드 'captions'가 유실되었습니다" in str(context.exception)
        )

    def test_validation_gate_discard_corrupted_captions(self):
        """필수 필드가 결손된 자막을 가진 쓰레기 JSON 데이터가 차단되는지 검증"""
        with self.assertRaises(ValueError) as context:
            validate_planning_json(self.invalid_json_corrupted_captions)
        self.assertIn("필수 항목(time_code, text)이 유실되었습니다", str(context.exception))

    def test_json_subtitle_generation(self):
        """JSON 데이터의 time_code를 기반으로 ASS 자막이 정상적으로 동기화 생성되는지 검증"""
        parse_script_to_ass(self.valid_json, self.ass_path, video_format="shorts")

        self.assertTrue(os.path.exists(self.ass_path), "ASS 자막 파일이 생성되지 않았습니다.")

        with open(self.ass_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Dialogue 타임스탬프와 텍스트 매칭 검증
        # 00:02 -> 0:00:02.00, 00:15 -> 0:00:15.00
        self.assertIn("Dialogue: 0,0:00:02.00,", content)
        self.assertIn("아침 요가를 시작합니다.", content)
        self.assertIn("Dialogue: 0,0:00:15.00,", content)
        self.assertIn("숨을 천천히 들이마시고 내쉬세요.", content)

    def test_legacy_text_subtitle_generation_compatibility(self):
        """기존 텍스트 줄글 대본을 주입했을 때 하위 호환성 경로가 정상 작동하는지 검증"""
        parse_script_to_ass(
            self.legacy_script_text, self.ass_path, video_format="shorts"
        )

        self.assertTrue(os.path.exists(self.ass_path), "하위 호환 ASS 자막 파일이 생성되지 않았습니다.")

        with open(self.ass_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 기존 정규식 기반 자막 내용이 존재해야 함
        self.assertIn("Close your eyes and breathe in.", content)
        self.assertIn("Feel the warm energy flowing.", content)
        self.assertIn("Let go of all your tension.", content)


if __name__ == "__main__":
    unittest.main()
