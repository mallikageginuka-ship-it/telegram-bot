import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
PORT = int(os.environ.get('PORT', 8080))
RAILWAY_URL = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'telegram-bot-production-7147.up.railway.app')

client = Groq(api_key=GROQ_API_KEY)

# System Prompt - Sinhalish + Memory දෙකටම
SYSTEM_PROMPT = """You are a helpful friend called 'Groq AI Bot'.
1. You MUST understand Sinhala, English, and Sinhalish. Sinhalish is Sinhala language written using English letters.
2. Always reply in proper Sinhala using Sinhala script. Be casual and friendly. Use 'මචන්' often.
3. Remember all previous messages in this conversation and use that context to answer.
4. If user speaks in Sinhalish like 'oyata therenne na', you must understand it means 'ඔයාට තේරෙන්නේ නෑ'."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['history'] = []
    await update.message.reply_text('හායි මචන්! දැන් මට සිංග්ලිෂ් + මතකෙත් තියෙනවා. /start ගැහුවොත් Memory Clear වෙනවා.')

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['history'] = []
    await update.message.reply_text('Memory Clear කරා මචන්. අලුතෙන් පටන් ගමු.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

        # Memory initialize කරනවා
        if 'history' not in context.user_data:
            context.user_data['history'] = []

        # පලවෙනි Message එක නම් System Prompt එක දානවා
        if len(context.user_data['history']) == 0:
            context.user_data['history'].append({"role": "system", "content": SYSTEM_PROMPT})

        # Userගේ message එක Memory එකට
        context.user_data['history'].append({"role": "user", "content": user_message})

        # Groq එකට Memory එකත් එක්කම යවනවා
        chat_completion = client.chat.completions.create(
            messages=context.user_data['history'],
            model="llama-3.1-8b-instant",
            temperature=0.7, # Creativity ටිකක් වැඩි කරනවා
        )
        ai_response = chat_completion.choices[0].message.content

        # AI reply එකත් Memory එකට
        context.user_data['history'].append({"role": "assistant", "content": ai_response})

        # Memory ලොකු වෙන එක නවත්තනවා. System prompt + අන්තිම 10 messages
        if len(context.user_data['history']) > 11:
            context.user_data['history'] = [context.user_data['history'][0]] + context.user_data['history'][-10:]

        # Telegram 4096 Limit Fix
        max_length = 4000
        if len(ai_response) <= max_length:
            await update.message.reply_text(ai_response, parse_mode=None)
        else:
            for i in range(0, len(ai_response), max_length):
                chunk = ai_response[i:i + max_length]
                await update.message.reply_text(chunk, parse_mode=None)

    except Exception as e:
        await update.message.reply_text(f'Error මචන්: {str(e)}')

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear)) # Memory clear කරන්න
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"https://{RAILWAY_URL}/{TELEGRAM_TOKEN}"
    )

if __name__ == '__main__':
    main()
