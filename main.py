import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
PORT = int(os.environ.get('PORT', 8080))
RAILWAY_URL = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'telegram-bot-production-7147.up.railway.app')

client = Groq(api_key=GROQ_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('හායි මචන්! මම Groq AI Bot. මොනවද දැනගන්න ඕන?')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": user_message}],
            model="llama-3.1-8b-instant",
        )
        ai_response = chat_completion.choices[0].message.content

        # Fix 2.0 - Telegram 4096 limit Safe Split
        max_length = 4000 # 4096 නෙවෙයි 4000 දාන්නේ Emoji/Special chars නිසා
        if len(ai_response) <= max_length:
            await update.message.reply_text(ai_response, parse_mode=None)
        else:
            for i in range(0, len(ai_response), max_length):
                chunk = ai_response[i:i + max_length]
                await update.message.reply_text(chunk, parse_mode=None)

    except Exception as e:
        await update.message.reply_text(f'Error: {str(e)}')

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"https://{RAILWAY_URL}/{TELEGRAM_TOKEN}"
    )

if __name__ == '__main__':
    main()
