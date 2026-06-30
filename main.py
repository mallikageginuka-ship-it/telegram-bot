import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# Logging - Error එකක් ආවොත් Railway logs වල පේන්න
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# Environment Variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
PORT = int(os.environ.get('PORT', 8080))
RAILWAY_URL = os.environ.get('RAILWAY_PUBLIC_DOMAIN')

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise ValueError("TELEGRAM_TOKEN or GROQ_API_KEY not found")

if not RAILWAY_URL:
    raise ValueError("RAILWAY_PUBLIC_DOMAIN not found. Add it in Railway Variables")

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are 'FF Master Bot', a Free Fire expert and gaming buddy.

CRITICAL RULES:
1. LANGUAGE: Detect user's language style and REPLY IN THAT EXACT SAME STYLE. Sinhalish, Sinhala, or English.
2. FREE FIRE EXPERT: You know everything about Free Fire - characters, pets, guns, sensitivity, rank push, CS tips, BR tips, guild, diamond top up, events, new updates, redeem codes, pro tips, best settings, headshot tricks, gloo wall, one tap.
3. MEMORY: Remember all previous messages and use context.
4. STYLE: Be a friendly gamer bro. Use 'මචන්' for Sinhala/Sinhalish. Use emojis 🔥🎮💀👑"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['history'] = []
    await update.message.reply_text(
        'ඔන්න ආවා FF Master Bot 🔥 මචන්\n'
        'Free Fire ගැන ඕනම දෙයක් අහපන්. Photo එකක් එක්ක උනත් අහන්න පුලුවන් 📸\n'
        '/ff ගහලා Commands බලපන්.'
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['history'] = []
    await update.message.reply_text('Memory Clear කරා මචන් 🎮 අලුතෙන් පටන් ගමු.')

async def ff_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """**FF Master Bot** 🔥

`sensitivity denna` - Best Sensitivity
`rank push tips` - Grandmaster යන Tricks
`character combo` - Best Combo
`one tap setting` - Headshot Settings
`new update` - අලුත් Update Info

**Photo එකක් එක්කත් අහන්න පුලුවන්** 📸
උදා: Screenshot එකක් එක්ක `mage sensitivity hari da` කියලා

උදා: `mage phone eka poco x3. sensitivity denna`

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

        try:
            chat_completion = client.chat.completions.create(
                messages=context.user_data['history'],
                model="llama-3.1-8b-instant",
                temperature=0.8,
                max_tokens=1024
