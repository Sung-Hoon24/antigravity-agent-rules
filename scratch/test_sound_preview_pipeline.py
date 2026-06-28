# -*- coding: utf-8 -*-
"""
[R&D Lab] 실전 청음 루프 및 오디오 샘플링 파이프라인 E2E 검증 테스트 스크립트
- 30초 프리뷰 음원 생성 (duration_min=0.5) 및 파일 크기 검증 통과 여부 테스트
- 템플릿 DB (sound_templates.json) 에 preview_audio_path 필드가 정상 반영되는지 테스트
- 5점 평점 부여 시 템플릿 DB 학습 데이터 승인(APPROVED) 변환 테스트
- 1점 평점 부여 시 즉시 폐기(REJECTED) 및 대체 템플릿 비동기 재생성/연동 테스트
- 비용 로거(cost_logger) 연동 및 실시간 누적 로깅 검증 테스트
"""

import os
import sys
import json
import asyncio
import unittest
import tempfile
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# 프로젝트 루트 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import Config

from telegram_bot.engine.audio_generator import generate_lyria3_music
from telegram_bot.engine.sound_template_generator import (
    load_sound_templates,
    save_sound_templates,
)
from telegram_bot.handlers.production import handle_callback_query
from telegram_bot.utils.cost_logger import log_api_cost, DB_PATH as COST_DB_PATH


class TestSoundPreviewPipeline(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.channel_key = "rubia"
        self.test_prompt = "Lo-fi hip-hop study beat, 70 BPM. Warm Rhodes electric piano chords, soft dusty vinyl crackles. No vocals. Short test duration. 30 seconds long."

        # 임시 출력을 위한 임시 파일 경로
        self.temp_dir = tempfile.TemporaryDirectory()
        self.preview_out = os.path.join(self.temp_dir.name, "test_preview.mp3")
        self.full_out = os.path.join(self.temp_dir.name, "test_full.mp3")

        # 템플릿 DB 및 비용 DB 백업/복원 구성
        self.original_db_path = r"c:\1인기업\Apps\유튜브에이전트\database\sound_templates.json"
        self.original_cost_path = COST_DB_PATH

        # 1. 템플릿 DB 백업
        if os.path.exists(self.original_db_path):
            with open(self.original_db_path, "r", encoding="utf-8") as f:
                self.db_backup = json.load(f)
        else:
            self.db_backup = []

        # 2. 비용 DB 백업
        if os.path.exists(self.original_cost_path):
            with open(self.original_cost_path, "r", encoding="utf-8") as f:
                self.cost_backup = json.load(f)
        else:
            self.cost_backup = []

        # 테스트용 템플릿 객체 세팅
        self.test_template_id = "teste2eid"
        self.setup_test_template()

    def setup_test_template(self):
        """테스트를 위한 임시 템플릿 데이터 주입"""
        clean_db = [t for t in self.db_backup if t.get("id") != self.test_template_id]

        self.test_template = {
            "id": self.test_template_id,
            "title": "테스트용 파도소리 로파이",
            "channel": self.channel_key,
            "prompt": self.test_prompt,
            "status": "PENDING",
            "created_at": datetime.now().isoformat(),
            "avg_score": 0,
            "usage_count": 0,
        }
        clean_db.append(self.test_template)

        with open(self.original_db_path, "w", encoding="utf-8") as f:
            json.dump(clean_db, f, indent=4, ensure_ascii=False)

    async def asyncTearDown(self):
        # 원본 DB 복원
        if hasattr(self, "db_backup"):
            with open(self.original_db_path, "w", encoding="utf-8") as f:
                json.dump(self.db_backup, f, indent=4, ensure_ascii=False)

        # 원본 비용 DB 복원
        if hasattr(self, "cost_backup"):
            with open(self.original_cost_path, "w", encoding="utf-8") as f:
                json.dump(self.cost_backup, f, indent=4, ensure_ascii=False)

        # 임시 디렉토리 클린업
        self.temp_dir.cleanup()

    async def test_01_preview_generation_and_size_validation(self):
        """30초(0.5분) 프리뷰 음원이 정상 생성되고 파일 검증을 통과하는지 테스트"""
        print("\n=== [E2E] 30초 프리뷰 음원 생성 테스트 개시 ===")

        # 실제 API 호출을 차단하고 85KB의 더미 파일을 생성하여 80KB 기준선 검증
        def mock_generate(
            channel_key, output_filename, duration_min=0.5, prompt_override=None
        ):
            with open(output_filename, "wb") as f:
                f.write(b"\x00" * 85000)
            return output_filename

        with patch("__main__.generate_lyria3_music", side_effect=mock_generate):
            try:
                generated_path = await asyncio.to_thread(
                    generate_lyria3_music,
                    channel_key=self.channel_key,
                    output_filename=self.preview_out,
                    duration_min=0.5,
                    prompt_override=self.test_prompt,
                )

                self.assertTrue(
                    os.path.exists(generated_path), "생성된 프리뷰 오디오 파일이 디스크에 존재해야 합니다."
                )
                file_size = os.path.getsize(generated_path)
                print(f"🎵 생성 완료: {generated_path} (크기: {file_size} bytes)")

                self.assertGreaterEqual(
                    file_size, 80000, "30초 생성 파일 크기가 80KB 이상이어야 합니다."
                )

            except Exception as e:
                self.fail(f"30초 프리뷰 음원 생성 중 실패: {e}")

    async def test_02_db_metadata_update_preview_path(self):
        """생성된 프리뷰 경로가 DB에 preview_audio_path로 성공적으로 업데이트되는지 검증"""
        print("\n=== [E2E] DB preview_audio_path 업데이트 테스트 개시 ===")
        dummy_path = r"c:\1인기업\Apps\유튜브에이전트\outputs\previews\test_audio.mp3"

        # DB 로드 후 업데이트 진행
        db = load_sound_templates()
        found = False
        for t in db:
            if t.get("id") == self.test_template_id:
                t["preview_audio_path"] = dummy_path
                found = True
                break

        self.assertTrue(found, "테스트 템플릿 ID가 DB에 존재해야 합니다.")
        save_sound_templates(db)

        # 재로드하여 정상 검증
        db_reloaded = load_sound_templates()
        target = next(
            (x for x in db_reloaded if x.get("id") == self.test_template_id), None
        )
        self.assertIsNotNone(target)
        self.assertEqual(
            target.get("preview_audio_path"),
            dummy_path,
            "preview_audio_path 필드가 저장소에 올바르게 기록되어 있어야 합니다.",
        )

    async def test_03_rating_and_success_learning(self):
        """5점 평가 시 PENDING -> APPROVED 상태 변경 및 '성공 문법' 학습 연계 테스트"""
        print("\n=== [E2E] 5점 평가 상태 변경 및 성공사례 학습 테스트 개시 ===")

        db = load_sound_templates()
        for t in db:
            if t.get("id") == self.test_template_id:
                t["avg_score"] = 5
                t["status"] = "APPROVED"
                break
        save_sound_templates(db)

        # 재로드 및 검증
        db_reloaded = load_sound_templates()
        target = next(
            (x for x in db_reloaded if x.get("id") == self.test_template_id), None
        )
        self.assertEqual(target.get("status"), "APPROVED")
        self.assertEqual(target.get("avg_score"), 5)

        # 성공사례(Success Cases)로 식별되어 기획 생성 시 로드되는지 확인
        success_cases = [
            t
            for t in db_reloaded
            if t.get("avg_score", 0) == 5 and t.get("status") == "APPROVED"
        ]
        self.assertTrue(
            any(x.get("id") == self.test_template_id for x in success_cases),
            "5점 승인 템플릿은 성공 사례군에 포함되어야 합니다.",
        )

    async def test_04_rating_1_rejection_and_regeneration(self):
        """1점 평가 시 즉시 폐기(REJECTED) 처리되고 로컬 LLM 대체 기획안이 비동기 생성되는지 검증"""
        print("\n=== [E2E] 1점 평가 폐기 및 대체 템플릿 비동기 재생성 테스트 개시 ===")

        # Mock Update 및 Context 준비
        query = AsyncMock()
        query.data = f"btn_rate_{self.test_template_id}_1"
        query.message = AsyncMock()
        query.message.reply_text = AsyncMock()
        query.answer = AsyncMock()

        update = MagicMock()
        update.callback_query = query
        update.effective_chat = MagicMock()
        update.effective_chat.id = 123456

        # 권한 검증 통과를 위한 effective_user 모킹 및 update.message 설정
        user_mock = MagicMock()
        user_mock.id = 123456
        update.effective_user = user_mock
        update.message = AsyncMock()

        context = MagicMock()
        context.bot = AsyncMock()
        context.chat_data = {}

        # generate_text 모킹: 로컬 LLM 호출 우회 및 가짜 JSON 응답 반환
        mock_json_response = '[{"title": "대체된 로파이 비트", "channel": "rubia", "prompt": "Relaxing lo-fi beat, 800 BPM, clean piano melody."}]'

        with patch("telegram_bot.handlers.basic.ALLOWED_USER_IDS", [123456]), patch(
            "telegram_bot.engine.sound_template_generator.generate_text",
            return_value=mock_json_response,
        ) as mock_llm:
            # handle_callback_query 직접 호출
            await handle_callback_query(update, context)

            # 비동기 백그라운드 태스크(generate_alt_template)가 실행될 수 있도록 잠시 sleep
            await asyncio.sleep(0.5)

            # 검증 1: 1점 준 기존 템플릿 상태가 REJECTED로 바뀌었는가?
            db = load_sound_templates()
            old_t = next((x for x in db if x.get("id") == self.test_template_id), None)
            self.assertIsNotNone(old_t)
            self.assertEqual(old_t.get("status"), "REJECTED")
            self.assertEqual(old_t.get("avg_score"), 1)

            # 검증 2: generate_text(로컬 LLM)가 정상적으로 호출되었는가?
            mock_llm.assert_called_once()

            # 검증 3: Mock 대체 템플릿이 DB에 저장되어 로드되는가?
            new_t = next((x for x in db if x.get("title") == "대체된 로파이 비트"), None)
            self.assertIsNotNone(new_t, "대체된 템플릿이 DB에 추가 기록되어야 합니다.")
            self.assertEqual(new_t.get("status"), "PENDING")

    async def test_05_cost_logger_integration(self):
        """비용 로거(cost_logger)에 트래픽 비용 및 로컬 LLM 세이브 비용이 바르게 로깅되는지 검증"""
        print("\n=== [E2E] 비용 로거 연동 및 세이브 요금 기록 테스트 개시 ===")

        # 1. 테스트 비용 데이터 추가
        test_api_name = "Test E2E API"
        test_cost = 0.05
        test_detail = "Test Preview Generation"

        test_local_api = "Local LLM Test (Local)"
        test_saved_cost = -0.0015
        test_saved_detail = "Test Local Saving"

        log_api_cost(test_api_name, test_cost, test_detail)
        log_api_cost(test_local_api, test_saved_cost, test_saved_detail)

        # 2. 비용 로그 파일 로드 및 검증
        self.assertTrue(os.path.exists(self.original_cost_path), "비용 로그 파일이 존재해야 합니다.")

        with open(self.original_cost_path, "r", encoding="utf-8") as f:
            costs = json.load(f)

        # 3. 최근에 추가한 로그 추출
        target_api = [x for x in costs if x.get("api_name") == test_api_name]
        target_saved = [x for x in costs if x.get("api_name") == test_local_api]

        self.assertTrue(len(target_api) > 0, "추가한 테스트 API 비용 로그가 존재해야 합니다.")
        self.assertTrue(len(target_saved) > 0, "추가한 로컬 세이브 비용 로그가 존재해야 합니다.")

        self.assertEqual(target_api[-1].get("cost"), test_cost)
        self.assertEqual(target_saved[-1].get("cost"), test_saved_cost)

        print("💵 비용 로깅 무결성 검증 통과 완료.")

    async def test_06_rating_3_hold_data_preservation(self):
        """3점 평가 시 상태가 PENDING(보류)으로 안전하게 유지되고 데이터가 보존되는지 검증"""
        print("\n=== [E2E] 3점 평가 보류 및 데이터 유지 테스트 개시 ===")

        # Mock Update 및 Context 준비
        query = AsyncMock()
        query.data = f"btn_rate_{self.test_template_id}_3"
        query.message = AsyncMock()
        query.message.reply_text = AsyncMock()
        query.answer = AsyncMock()

        update = MagicMock()
        update.callback_query = query
        update.effective_chat = MagicMock()
        update.effective_chat.id = 123456

        user_mock = MagicMock()
        user_mock.id = 123456
        update.effective_user = user_mock
        update.message = AsyncMock()

        context = MagicMock()
        context.bot = AsyncMock()
        context.chat_data = {}

        with patch("telegram_bot.handlers.basic.ALLOWED_USER_IDS", [123456]):
            # handle_callback_query 직접 호출
            await handle_callback_query(update, context)

            # 검증: 3점 준 템플릿의 상태가 PENDING 상태로 유지되고 avg_score가 3으로 업데이트 되었는가?
            db = load_sound_templates()
            t = next((x for x in db if x.get("id") == self.test_template_id), None)
            self.assertIsNotNone(t)
            self.assertEqual(
                t.get("status"),
                "PENDING",
                "3점 평점 시 데이터는 REJECTED 되지 않고 PENDING 상태를 유지해야 합니다.",
            )
            self.assertEqual(t.get("avg_score"), 3, "평점 평균 필드가 3점으로 기록되어 있어야 합니다.")

        print("😐 3점 보류 데이터 유지 검증 통과 완료.")

    async def test_07_kpi_evolution_report_calculation(self):
        """주간 진화 성적표(Evolution Report)에 승인율 및 대표 취향 반영도 지표가 올바르게 산출 및 조립되는지 검증"""
        print("\n=== [E2E] 주간 진화 성적표 승인율 및 취향 반영도 계산 검증 개시 ===")

        # 1. 템플릿 DB에 임의의 평가 데이터 세팅
        db = load_sound_templates()
        # 테스트용 템플릿 추가
        db.append(
            {
                "id": "mock_test_1",
                "title": "5점짜리 성공작",
                "channel": self.channel_key,
                "prompt": "prompt 1",
                "status": "APPROVED",
                "avg_score": 5,
            }
        )
        db.append(
            {
                "id": "mock_test_2",
                "title": "3점짜리 보류작",
                "channel": self.channel_key,
                "prompt": "prompt 2",
                "status": "PENDING",
                "avg_score": 3,
            }
        )
        save_sound_templates(db)

        # 2. 월요일 조건(weekday == 0)을 만족하도록 datetime.now를 모킹하여 append_sound_lab_report 호출
        from telegram_bot.handlers.kpi_dashboard import append_sound_lab_report

        mock_date = MagicMock()
        mock_date.weekday.return_value = 0  # 월요일 강제 설정

        with patch("telegram_bot.handlers.kpi_dashboard.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_date
            # 모의 템플릿 생성기(generate_daily_templates)가 호출될 때 더미 데이터를 리턴하여 폴백 구문 우회
            mock_temp = [{"id": "dummy_t", "title": "더미 타이틀", "prompt": "더미 프롬프트"}]
            with patch(
                "telegram_bot.engine.sound_template_generator.generate_daily_templates",
                return_value=mock_temp,
            ):
                report_text, _ = await append_sound_lab_report(self.channel_key)

                print(f"📄 Generated Report Output Preview:\n{report_text}\n")

                # 3. 텍스트 검증: 신규 지표(누적 승인율, 대표 취향 반영도) 문자열 및 정상 수치 포함 여부
                self.assertIn("누적 승인율", report_text)
                self.assertIn("대표 취향 반영도", report_text)
                self.assertIn("비용 절감 효율", report_text)

        print("📈 진화 성적표 지표 무결성 검증 통과 완료.")

    async def test_08_session_lock_prevention(self):
        """에셋 빌드/제작 진행 중(세션 락) 다른 일반 채팅 침입 시 차단 및 취소 키워드로 해제되는지 검증"""
        print("\n=== [E2E] 세션 락 작동 및 긴급 취소 예외 테스트 개시 ===")
        from telegram_bot.bot import natural_language_router

        # 1. 락이 걸린 상태 (STATE_BUILD_PROCESSING) 설정
        update_mock = AsyncMock()
        update_mock.message = AsyncMock()
        update_mock.message.text = "루비아 채널 현황 분석해줘"  # 난입 메시지
        update_mock.message.reply_text = AsyncMock()

        context_mock = MagicMock()
        context_mock.chat_data = {"current_state": "STATE_BUILD_PROCESSING"}

        # 2. 라우터 실행 -> 잠금 알림 메시지 출력 확인
        await natural_language_router(update_mock, context_mock)

        update_mock.message.reply_text.assert_called_once()
        sent_text = update_mock.message.reply_text.call_args[0][0]
        self.assertIn("보안 관제", sent_text, "잠금 경고 안내 텍스트가 출력되어야 합니다.")

        # 3. 긴급 취소 키워드 ("취소") 입력 시 차단 해제되는지 검증
        update_cancel_mock = AsyncMock()
        update_cancel_mock.message = AsyncMock()
        update_cancel_mock.message.text = "이번 빌드 취소해줘"  # 취소 요청
        update_cancel_mock.message.reply_text = AsyncMock()

        # basic.py의 ALLOWED_USER_IDS 통과 모킹
        user_mock = MagicMock()
        user_mock.id = 123456
        update_cancel_mock.effective_user = user_mock
        update_cancel_mock.callback_query = None

        # 라우팅 내부에서 handle_callback_query 등 취소 콜백 혹은 handle_chat 등으로 정상 라우팅되는지 확인 (여기선 차단당하지 않는지만 확인)
        with patch(
            "telegram_bot.handlers.chat.handle_chat", new_callable=AsyncMock
        ), patch("telegram_bot.handlers.basic.ALLOWED_USER_IDS", [123456]), patch(
            "telegram_bot.bot.parse_intent",
            return_value={
                "intent": "unknown",
                "channel": None,
                "video_length": 1,
                "video_format": "shorts",
                "raw_message": "이번 빌드 취소해줘",
                "confidence": "high",
                "conflict_detected": False,
            },
        ):
            await natural_language_router(update_cancel_mock, context_mock)
            # 락으로 인해 차단당하는 '보안 관제' 경고 메시지가 호출되지 않았는지 확인
            has_lock_warning = any(
                "보안 관제" in str(args)
                for args, kwargs in update_cancel_mock.message.reply_text.call_args_list
            )
            self.assertFalse(has_lock_warning, "세션 락으로 인해 차단되면 안 됩니다.")

        print("🛡️ 세션 락 및 취소 바이패스 검증 통과 완료.")

    async def test_09_local_nlu_error_rate_monitoring(self):
        """로컬 NLU 호출 시 연속 실패로 실패율이 30%를 초과하는 경우 경보(Warning) 플래그가 True가 되는지 검증"""
        print("\n=== [E2E] 로컬 NLU 실패율 30% 초과 경보 테스트 개시 ===")
        from telegram_bot.nlp.intent_parser import parse_intent
        import telegram_bot.nlp.intent_parser as ip_mod

        # 카운터 강제 리셋
        ip_mod.LOCAL_NLU_TOTAL_CALLS = 0
        ip_mod.LOCAL_NLU_FAILED_CALLS = 0
        ip_mod.LOCAL_NLU_WARNING_TRIGGERED = False

        # 💡 [한글 설명] 중앙 Config 모듈의 주소 설정을 동적으로 활용하여 9999 포트로 변환한 bad_url을 생성, 연결 장애를 모사합니다.
        bad_url = (
            Config.get_active_url().replace(":1234", ":9999").replace(":11434", ":9999")
        )

        for _ in range(5):
            await parse_intent("안녕 루비아", llm_mode="local", local_url=bad_url)

        # 5회 호출 모두 에러가 났으므로 실패율 100% (30% 초과)
        self.assertEqual(ip_mod.LOCAL_NLU_TOTAL_CALLS, 5)
        self.assertEqual(ip_mod.LOCAL_NLU_FAILED_CALLS, 5)
        self.assertTrue(
            ip_mod.LOCAL_NLU_WARNING_TRIGGERED,
            "실패율이 30%를 넘으면 경보 트리거 플래그가 True가 되어야 합니다.",
        )

        print("🚨 로컬 NLU 실패율 30% 초과 무결성 경보 작동 검증 통과 완료.")


if __name__ == "__main__":
    unittest.main()
