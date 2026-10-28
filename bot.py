
import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import AsyncOpenAI

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
AI_API_KEY = os.environ.get("AI_API_KEY")

AI_BASE_URL = os.environ.get(
    "AI_BASE_URL", "https://openrouter.ai/api/v1"
)
AI_MODEL = os.environ.get(
    "AI_MODEL", "openai/gpt-4o-mini"
)

client = None

if AI_API_KEY:
    client = AsyncOpenAI(
        api_key=AI_API_KEY,
        base_url=AI_BASE_URL,
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "မင်္ဂလာပါ။ ကျွန်တော် JARVIS AI ပါ။ 🤖\n\n"
        "မြန်မာလို မေးခွန်းတွေ မေးနိုင်ပါတယ်။"
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not client:
        await update.message.reply_text(
            "AI API Key မသတ်မှတ်ရသေးပါ။"
        )
        return

    message = update.message.text

    try:
        response = await client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are JARVIS, a helpful AI assistant. "
                        "Reply in natural Burmese when the user "
                        "writes in Burmese. Be clear and friendly."
                    ),
                },
                {"role": "user", "content": message},
            ],
        )

        answer = response.choices[0].message.content
        if not answer:
            answer = "အဖြေမရရှိသေးပါ။ ထပ်မေးကြည့်ပါ။"

        for i in range(0, len(answer), 4000):
            await update.message.reply_text(answer[i:i + 4000])

    except Exception:
        logger.exception("AI request failed")
        await update.message.reply_text(
            "AI ချိတ်ဆက်ရာမှာ အခက်အခဲရှိနေပါတယ်။ "
            "ခဏစောင့်ပြီး ပြန်မေးကြည့်ပါ။"
        )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
    )

    logger.info("JARVIS bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
      
