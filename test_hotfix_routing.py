import asyncio
from unittest.mock import MagicMock, AsyncMock


async def main():
    print("🚀 [Hotfix Reload Test] 텔레그램 콜백 핸들러 리로드 및 가상 라우팅 테스트 시작...")

    import telegram_bot.handlers.production as prod_module

    # 모킹 설정
    update = MagicMock()
    context = MagicMock()

    update.callback_query = MagicMock()
    update.callback_query.data = "btn_regen_img"
    update.callback_query.message.reply_text = AsyncMock()
    update.callback_query.message.reply_photo = AsyncMock()

    context.chat_data = {
        "pending_script": "테스트용 가상 대본",
        "pending_channel_key": "rubia",
        "pending_video_format": "shorts",
        "pending_output_dir": "c:/1인기업/Apps/유튜브에이전트/outputs/shorts/rubia",
        "awaiting_build_approval": True,
    }

    # 호출 여부 확인을 위해 함수 모킹
    original_regen_image = prod_module.regenerate_image_only
    original_regen_audio = prod_module.regenerate_audio_only
    original_handle_prod = prod_module.handle_production

    prod_module.regenerate_image_only = AsyncMock()
    prod_module.regenerate_audio_only = AsyncMock()
    prod_module.handle_production = AsyncMock()

    print("▶ 테스트 명령: '이미지 재생성' (btn_regen_img) 버튼 클릭 시뮬레이션")
    await prod_module.handle_callback_query(update, context)

    print("\n📊 [라우팅 경로 분석 결과 로그]")
    if prod_module.regenerate_image_only.called:
        print("✅ 검증 완료: 'regenerate_image_only' 함수만 독립적으로 호출됨.")
    else:
        print("❌ 검증 실패: 'regenerate_image_only' 함수가 호출되지 않음.")

    if prod_module.regenerate_audio_only.called:
        print("❌ 오류: 'regenerate_audio_only' 함수가 중복 호출됨 (음원 비용 낭비 발생).")
    else:
        print("✅ 검증 완료: 음원 생성 모듈(Audio/ElevenLabs/Lyria) 호출 0건. (비용 청구 원천 차단)")

    if prod_module.handle_production.called:
        print("❌ 오류: 이전 모놀리식 통합 파이프라인(handle_production)으로 잘못 라우팅됨.")
    else:
        print("✅ 검증 완료: 기존 모놀리식 호출(handle_production) 고리가 완전히 소멸되었음.")

    # 모킹 복구
    prod_module.regenerate_image_only = original_regen_image
    prod_module.regenerate_audio_only = original_regen_audio
    prod_module.handle_production = original_handle_prod


if __name__ == "__main__":
    asyncio.run(main())
