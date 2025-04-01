import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient, events
import openai
import random
import time
import asyncio

# Загрузка конфигурации
load_dotenv()

class Config:
    TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID"))
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
    TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    ALLOWED_CHAT_IDS = [int(x.strip()) for x in os.getenv("ALLOWED_CHAT_IDS").split(",")]
    MIN_DELAY = int(os.getenv("MIN_DELAY_SECONDS"))
    MAX_REPLIES = int(os.getenv("MAX_REPLIES_PER_HOUR"))

# Настройка DeepSeek (старая версия API)
openai.api_key = Config.DEEPSEEK_API_KEY
openai.api_base = "https://api.deepseek.com/v1"

# Инициализация Telegram
client = TelegramClient('timi_session', Config.TELEGRAM_API_ID, Config.TELEGRAM_API_HASH)
chat_stats = {}

async def generate_reply(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Ты дружелюбная девушка. Отвечай доброжелательно, ответ не должен быть более 20 слов."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"DeepSeek error: {e}")
        return None

@client.on(events.NewMessage(chats=Config.ALLOWED_CHAT_IDS))
async def handler(event):
    chat_id = event.chat_id
    now = time.time()
    
    if chat_id not in chat_stats:
        chat_stats[chat_id] = {'last_reply': 0, 'count': 0}
    
    stats = chat_stats[chat_id]
    
    if (now - stats['last_reply'] < Config.MIN_DELAY) or (stats['count'] >= Config.MAX_REPLIES):
        return
    
    if random.random() > 0.5:
        return
    
    user = await event.get_sender()
    mention = f"@{user.username}" if user.username else user.first_name
    
    reply = await generate_reply(f"Ответь на '{event.text}'. Упомяни {mention}")
    if reply:
        await asyncio.sleep(random.uniform(1, 3))
        await event.reply(reply)
        stats['last_reply'] = now
        stats['count'] += 1

if __name__ == "__main__":
    print("Тими запущен!")
    client.start(phone=Config.TELEGRAM_PHONE)
    client.run_until_disconnected()