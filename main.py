import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

def ask_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def telegram_webhook():
    update = request.get_json()
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message']['text']
        reply = ask_groq(text)
        requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',
                      json={'chat_id': chat_id, 'text': reply})
    return 'ok'

@app.route('/')
def home():
    return 'Bot is running!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
