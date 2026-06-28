import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
PORT = int(os.environ.get('PORT', 8080))
RAILWAY_URL = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'telegram-bot-production-7147.up.railway.app')

client = Groq(api_key=GROQ_API_KEY)

# System Prompt - Free Fire Expert + Language Mimic + Memory
SYSTEM_PROMPT = """You are 'FF Master Bot', a Free Fire expert and gaming buddy.

CRITICAL RULES:
1. LANGUAGE: Detect user's language style from their last message and REPLY IN THAT EXACT SAME STYLE. 
   If Sinhalish like 'ff tips denna' → reply in Sinhalish. 
   If Sinhala like 'ෆ්‍රී ෆයර් ටිප්ස් දෙන්න' → reply in Sinhala.
   If English → reply in English.

2. FREE FIRE EXPERT: You know everything about Free Fire - characters, pets, guns, sensitivity, rank push, CS tips, BR tips, guild, diamond top up, events, new updates, redeem codes, pro tips, best settings, headshot tricks, gloo wall, one tap.

3. MEMORY: Remember all previous messages. If user said 'mage name X' earlier, use it. Track what tips you already gave.

4. STYLE: Be a friendly gamer bro. Use gaming terms. Use 'මචන්' for Sinhala/Sinhalish. Use emojis 🔥🎮💀👑

5. NEVER say you can't help with Free Fire. You are the expert. Give detailed answers for loadouts, strategies, sensitivity, character combos."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['history'] = []
    await update.message.reply_text('ඔන්න ආවා FF Master Bot 🔥 මචන්\n\nFree Fire ගැන ඕනම දෙයක් අහපන්. Character combo, sensitivity, rank push, headshot trick, redeem code, update news ඔක්කොම දන්නවා.\n\nඋඹ කතා කරන විදියටම මමත් උත්තර දෙන්නම්. /clear ගැහුවොත් Memory Reset වෙනවා.')

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['history'] = []
    await update.message.reply_text('Memory Clear කරා මචන් 🎮 අලුතෙන් පටන් ගමු.')

async def ff_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """**FF Master Bot Commands** 🔥

**මට පුළුවන් දේවල්:**
1. `sensitivity denna` - උඹේ Phone එකට Best Sensitivity
2. `rank push tips` - Grandmaster යන Tricks
3. `character combo` - Best Character Combo
4. `one tap setting` - Headshot Settings
5. `CS rank tips` - Clash Squad Pro Tips
6. `gun skin` - Best Gun + Skin Combo
7. `new update` - අලුත් Update Info
8. `redeem code` - Working Codes
9. drag headshot panel - hack code
**Example:**
`mage phone eka poco x3. sensitivity denna`
`dimitri + k combo hodaida`
`br rank push karanna tips denna`

ඕනම දෙයක් Sinhalish/සිංහල/English වලින් අහපන් මචන් 🎮"""
    await update.message.reply_text(help_text, parse_mode=None)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        await context.bot.send_chat_action(chat_id=update
