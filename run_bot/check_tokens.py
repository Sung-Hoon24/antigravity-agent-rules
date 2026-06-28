# -*- coding: utf-8 -*-
"""봇 토큰 유효성 검증 스크립트"""
import asyncio
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from telegram import Bot


async def verify(name, tok):
    bot = Bot(token=tok)
    try:
        me = await bot.get_me()
        print(f"✅ {name}: @{me.username} (id:{me.id})")
    except Exception as e:
        print(f"❌ {name}: {e}")


async def main():
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

    tokens = {
        "rofi": os.getenv("TELEGRAM_Taipei_Lofi_New_Bot_TOKEN", ""),
        "aura": os.getenv("TELEGRAM_rubia_smart_bot_TOKEN", ""),
        "analyst": os.getenv(
            "TELEGRAM_Youtube_Total_Music_Taipei_Lofi_New_Bot_TOKEN", ""
        ),
    }

    for name, tok in tokens.items():
        if tok:
            await verify(name, tok)
        else:
            print(f"⚠️ {name}: 토큰 미설정")


asyncio.run(main())
