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

SYSTEM_PROMPT = """You are 'FF Master Bot', a Free Fire expert and gaming buddy.

CRITICAL RULES:
1. LANGUAGE: Detect user's language style and REPLY IN THAT EXACT SAME STYLE. Sinhalish, Sinhala, or English.
2. FREE FIRE EXPERT: You know everything about Free Fire - characters, pets, guns, sensitivity, rank push, CS tips, BR tips, guild, diamond top up, events, new updates, redeem codes, pro tips, best settings, headshot tricks, gloo wall, one tap.
3. MEMORY: Remember all previous messages and use context.
4. STYLE: Be a friendly gamer bro. Use 'මචන්' for Sinhala/Sinhalish. Use emojis 🔥🎮💀👑"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['history'] = []
    await update.message.reply_text('ඔන්න ආවා FF Master Bot 🔥 මචන්\nFree Fire ගැන ඕනම දෙයක් අහපන්. Photo එකක් එක්ක උනත් අහන්න පුලුවන් 📸\n/ff ගහලා Commands බලපන්.')

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['history'] = []
    await update.message.reply_text('Memory Clear කරා මචන් 🎮')

async def ff_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """**FF Master Bot** 🔥

`sensitivity denna` - Best Sensitivity
`rank push tips` - Grandmaster යන Tricks
`character combo` - Best Combo
`one tap setting` - Headshot Settings
`new update` - අලුත් Update Info

**Photo එකක් එක්කත් අහන්න පුලුවන්** 📸
උදා: Screenshot එකක් එක්ක `mage sensitivity hari da` කියලා

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
            temperature=0.8,
            max_tokens=1024
        )
        
        ai_response = chat_completion.choices[0].message.content
        context.user_data['history'].append({"role": "assistant", "content": ai_response})
        
        if len(context.user_data['history']) > 11:
            context.user_data['history'] = [context.user_data['history'][0]] + context.user_data['history'][-10:]
        
        max_length = 4000
        for i in range(0, len(ai_response), max_length):
            await update.message.reply_text(ai_response[i:i + max_length], parse_mode=None)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text('Bot අවුල් ගියා මචන් 😭')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        caption = update.message.caption
        if 'history' not in context.user_data:
            context.user_data['history'] = []
        if len(context.user_data['history']) == 0:
            context.user_data['history'].append({"role": "system", "content": SYSTEM_PROMPT})
        
        if caption:
            user_prompt = f"[User sent a Free Fire screenshot/photo] {caption}"
        else:
            user_prompt = "[User sent a Free Fire screenshot/photo] මේ photo එක ගැන කියපන් මචන්"
        
        context.user_data['history'].append({"role": "user", "content": user_prompt})
        
        chat_completion = client.chat.completions.create(
            messages=context.user_data['history'],
            model="llama-3.1-8b-instant",
            temperature=0.8,
            max_tokens=1024
        )
        
        ai_response = chat_completion.choices[0].message.content
        context.user_data['history'].append({"role": "assistant", "content": ai_response})
        
        if len(context.user_data['history']) > 11:
            context.user_data['history'] = [context.user_data['history'][0]] + context.user_data['history'][-10:]
        
        max_length = 4000
        for i in range(0, len(ai_response), max_length):
            await update.message.reply_text(ai_response[i:i + max_length], parse_mode=None)
    except Exception as e:
        logging.error(f"Photo Error: {e}")
        await update.message.reply_text('Photo එක process කරන්න බැරි උනා මචන් 😭')

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
