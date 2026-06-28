import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
PORT = int(os.environ.get('PORT', 8080))
RAILWAY_URL = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'telegram-bot-production-7147.up.railway.app')

client = Groq(api_key=GROQ_API_KEY)

# System Prompt - Language Mimic කරන එක
SYSTEM_PROMPT = """You are a smart AI assistant called 'Groq AI Bot'.

CRITICAL RULES:
1. DETECT the user's language style from their last message and REPLY IN THAT EXACT SAME STYLE.
2. If user writes in Sinhalish like 'mama oyata kiyanne', you reply in Sinhalish too. Example: 'hari machan, mama dan eka karannam'.
3. If user writes in proper Sinhala like 'මම ඔයාට කියන්නේ', you reply in proper Sinhala.
4. If user writes in English, you reply in English.
5. NEVER change the user's language. Match their tone and script exactly.
6. Remember all previous messages and use context.
7. Be casual and friendly. Use 'මචන්' when replying in Sinhala/Sinhalish."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['history'] = []
    await update.message.reply_text('හායි මචන්! උඹ කතා කරන විදියටම මමත් කතා කරනවා. /start ගැහුවොත් Memory Reset.')

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['history'] = []
    await update.message.reply_text('Memory Clear කරා මචන්.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

        if 'history' not in context.user_data:
            context.user_data['history'] = []

        if len(context.user_data['history']) == 0:
            context.user_data['history'].append({"role": "system", "content": SYSTEM_PROMPT})

        context.user_data['history'].append({"role": "user", "content": user_message})

        chat_completion = client.chat.completions.create(
            messages=context.user_data['history'],
            model="llama-3.1-8b-instant",
            temperature=0.8, # ටිකක් Creative වෙන්න
        )
        ai_response = chat_completion.choices[0].message.content

        context.user_data['history'].append({"role": "assistant", "content": ai_response})

        # Memory limit - System prompt + last 10 messages
        if len(context.user_data['history']) > 11:
            context.user_data['history'] = [context.user_data['history'][0]] + context.user_data['history'][-10:]

        # Telegram Limit Fix
        max_length = 4000
        if len(ai_response) <= max_length:
            await update.message.reply_text(ai_response, parse_mode=None)
        else:
            for i in range(0, len(ai_response), max_length):
                await update.message.reply_text(ai_response[i:i + max_length], parse_mode=None)

    except Exception as e:
        await update.message.reply_text(f'Error මචන්: {str(e)}')

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_webhook(listen="0.0.0.0", port=PORT, url_path=TELEGRAM_TOKEN, webhook_url=f"https://{RAILWAY_URL}/{TELEGRAM_TOKEN}")

if __name__ == '__main__':
    main()
