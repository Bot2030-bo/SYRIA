import asyncio
import os
import re
import time
from datetime import datetime, timezone

from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from telethon.tl.functions.channels import JoinChannelRequest

# =========================
# قراءة البيانات من متغيرات البيئة
# =========================
API_ID = int(os.environ.get('API_ID', 38285947))
API_HASH = os.environ.get('API_HASH', '3656d9d6dfac023a86a9677436e9a418')
PHONE_NUMBER = os.environ.get('PHONE_NUMBER', '+963992069880')
OWNER_ID = int(os.environ.get('OWNER_ID', 8787194614))
SESSION_NAME = 'hunter_session'

CHANNELS = [
    {'id': -1003944166760, 'name': 'Kingrodai', 'bot': '@Ichancy990_bot', 'keywords': ['كود', 'أكواد', 'جائزة', 'جوائز']},
    {'id': -1003516729119, 'name': 'Shelby Robert', 'bot': '@shelby_ichancy_bot', 'keywords': ['كود', 'استرداد', 'هدية']},
    {'id': -1002919977260, 'name': 'Ichancy', 'bot': '@IchancyBlack1_Bot', 'keywords': ['كود', 'أكواد', 'جوائز']},
    {'id': -1002690845884, 'name': 'Chanzo', 'bot': '@chanzo_ichancy_bot', 'keywords': ['كود', 'هدية', 'أكواد']},
    {'id': -1002310273404, 'name': 'القناة الخامسة', 'bot': '8049991519', 'keywords': ['كود', 'أكواد', 'جائزة', 'هدية']},
]

SEND_DELAY = 3
WIN_KEYWORDS = ['مبروك', 'ربحت', '🎉', 'تهانينا', 'success', 'valid', 'نجحت']

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
sent_codes = set()
last_button_click = {}

def extract_codes(text: str):
    if not text: return []
    text = re.sub(r'https?://\S+', '', text.replace("\n", " "))
    codes = []
    patterns = [r'[A-Za-z0-9_]{8,32}', r'[A-Fa-f0-9]{16,32}']
    for pattern in patterns:
        for match in re.findall(pattern, text):
            if not re.search(r'[\u0600-\u06FF]', match) and not match.startswith("@") and not match.isdigit() and 8 <= len(match) <= 32:
                codes.append(match)
    return list(set(codes))

async def find_and_click_button(bot, keywords_list):
    try:
        async for msg in client.iter_messages(bot, limit=25):
            if not msg.buttons: continue
            for row in msg.buttons:
                for btn in row:
                    if any(k.lower() in (btn.text or "").lower() for k in keywords_list):
                        last = last_button_click.get(bot)
                        if last and time.time() - last < 4: return True
                        last_button_click[bot] = time.time()
                        await btn.click()
                        await asyncio.sleep(2.5)
                        return True
        return False
    except: return False

async def send_code(code, bot_name, keywords_list):
    try:
        bot = await client.get_entity(bot_name)
        await client.send_message(bot, "/start")
        await asyncio.sleep(2.5)
        await find_and_click_button(bot, keywords_list)
        await client.send_message(bot, code.strip())
        await asyncio.sleep(3)
        async for msg in client.iter_messages(bot, limit=2):
            if msg.from_id and getattr(msg.from_id, "user_id", None) == bot.id:
                reply = (msg.text or "").lower()
                if any(w in reply for w in WIN_KEYWORDS):
                    print(f"[✓] نجح {code}")
                    return True
                print(f"[✗] فشل {code}")
                return False
        print(f"[?] لا رد {code}")
        return False
    except FloodWaitError as e:
        print(f"انتظر {e.seconds}s")
        await asyncio.sleep(e.seconds)
        return False
    except Exception as e:
        print(f"خطأ: {e}")
        return False

@client.on(events.NewMessage(chats=[ch['id'] for ch in CHANNELS]))
async def watcher(event):
    channel = next((c for c in CHANNELS if c['id'] == event.chat_id), None)
    if not channel: return
    for code in extract_codes(event.message.text or ""):
        if code not in sent_codes:
            sent_codes.add(code)
            print(f"🎯 {code} من {channel['name']}")
            await send_code(code, channel['bot'], channel['keywords'])
            await asyncio.sleep(SEND_DELAY)

async def main():
    print("🚀 تشغيل البوت على السحابة...")
    await client.start(phone=PHONE_NUMBER)
    for ch in CHANNELS:
        try:
            await client(JoinChannelRequest(ch['id']))
            print(f"✅ انضم إلى {ch['name']}")
        except: pass
    print("✅ البوت جاهز!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())