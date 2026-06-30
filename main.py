import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
PORT = int(os.environ.get('PORT', 8080))
RAILWAY_URL = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'telegram-bot-production-7147.up.railway.app')

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise ValueError("TELEGRAM_TOKEN or GROQ_API_KEY not found")

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are 'FF Master Bot', a Free Fire gaming assistant.

RULES:
1. If user writes in Sinhala/Sinhalish, reply in Sinhalish. If English, reply in English.
2. You are a Free Fire expert: characters, pets, guns, sensitivity, rank push, tips.
3. Keep answers short, clear, helpful. Use emojis 🔥🎮
4. If you don't understand Sinhala, ask them to write in English.
5. Never make up words. Be accurate.
6. Always call user 'මචන්' if they use Sinhala/Sinhalish."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['history'] = []
    await update.message.reply_text('ඔන්න ආවා FF Master Bot 🔥 මචන්\nFree Fire ගැන අහපන්. /ff ගහලා commands බලපන්.')

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['history'] = []
    await update.message.reply_text('Memory Clear කරා මචන් 🎮')

async def ff_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """**FF Master Bot** 🔥

`sensitivity denna` - Best Sensitivity
`rank push tips` - Grandmaster යන Tricks
`character combo` - Best Combo
`one tap setting` - Headshot Settings

Photo එකක් එක්කත් අහන්න පුලුවන් 📸

`/clear` - Memory Clear කරන්න"""
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        if 'history' not in context.user_data:
            context.user_data['history'] = []
        if len(context.user_data['history']) == 0:
            context.user_data['history'].append({"role": "system", "content": SYSTEM_PROMPT})
        context.user_data['history'].append({"role": "user", "content": user_message})

        chat_completion = client.chat.completions.create(
            messages=context.user_data['history'],
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=512
        )

        ai_response = chat_completion.choices[0].message.content
        context.user_data['history'].append({"role": "assistant", "content": ai_response})

        if len(context.user_data['history']) > 9:
            context.user_data['history'] = [context.user_data['history'][0]] + context.user_data['history'][-8:]

        max_length = 4000
        for i in range(0, len(ai_response), max_length):
            await update.message.reply_text(ai_response[i:i + max_length])
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text('Bot අවුල් ගියා මචන් 😭 ටිකකින් try කරපන්.')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        caption = update.message.caption if update.message.caption else "මේ photo එක ගැන Free Fire tips දෙන්න මචන්"
        if 'history' not in context.user_data:
            context.user_data['history'] = []
        if len(context.user_data['history']) == 0:
            context.user_data['history'].append({"role": "system", "content": SYSTEM_PROMPT})

        user_prompt = f"[User sent a photo] {caption}"
        context.user_data['history'].append({"role": "user", "content": user_prompt})

        chat_completion = client.chat.completions.create(
            messages=context.user_data['history'],
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=512
        )

        ai_response = chat_completion.choices[0].message.content
        context.user_data['history'].append({"role": "assistant", "content": ai_response})

        if len(context.user_data['history']) > 9:
            context.user_data['history'] = [context.user_data['history'][0]] + context.user_data['history'][-8:]

        max_length = 4000
        for i in range(0, len(ai_response), max_length):
            await update.message.reply_text(ai_response[i:i + max_length])
    except Exception as e:
        logging.error(f"Photo Error: {e}")
        await update.message.reply_text('Photo එක බලන්න බැරි උනා මචන් 😭')

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("ff", ff_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"https://{RAILWAY_URL}/{TELEGRAM_TOKEN}"
    )

if __name__ == '__main__':
    main()
