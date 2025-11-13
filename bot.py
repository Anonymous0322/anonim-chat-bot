# anonimbot.py
# aiogram v3 anonymous chat roulette (UZ/RU)
# Requirements: Python 3.10+, aiogram, aiosqlite
# pip install aiogram aiosqlite

import asyncio
import logging
import os
import re
import time
import datetime
from datetime import datetime, timezone
from typing import Optional

import aiosqlite
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup

# ========== CONFIG ==========
API_TOKEN = "8416511999:AAFbwKndsT1S98luxE_jczeCjf0g46pwckA"
ADMIN_ID = 7901013364  # <-- O'ZINGIZNING TELEGRAM ID'INGIZNI QO'YING
DB_PATH = "database.db"
AUTODELETE_DELAY = 60

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ensure data dir
os.makedirs("data", exist_ok=True)
os.makedirs("chat_logs", exist_ok=True)  # Chat loglari uchun papka

# Bot va dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ========== TEXTS ==========
TEXTS = {
    "uz": {
        "ask_lang": "🌐 Tilni tanlang:",
        "ask_age": "🗓 Yoshingiz nechida? (12–35):",
        "ask_gender": "🚻 Jinsingizni tanlang:",
        "registered": "✅ Roʻyxatdan oʻtdingiz! Quyidagi tugmalar orqali boshqarishingiz mumkin.",
        "panel_title": "⚡ Asosiy panel — Online: {online}",
        "btn_find": "🔍 Juft qidirish",
        "btn_stop": "❌ Toʻxtatish",
        "btn_next": "➡️ Keyingisi",
        "btn_settings": "⚙️ Sozlamalar",
        "btn_help": "ℹ️ Yordam",
        "btn_premium": "💎 Premium",
        "searching": "🔎 Juft qidirilmoqda...",
        "matched": "✅ Suhbatdosh topildi!\n👤 Jinsi: {gender}\n🎂 Yoshi: {age}\nYozishni boshlang.",
        "not_in_chat": "Siz hozir chatda emassiz. '🔍 Juft qidirish' ni bosing.",
        "stopped": "❌ Chat toʻxtatildi.",
        "partner_left": "ℹ️ Suhbatdosh chatdan chiqdi.",
        "settings": "⚙️ Sozlamalar",
        "choose_lang": "🔤 Tilni tanlang:",
        "changed_lang": "✅ Til oʻzgartirildi.",
        "help_text": "ℹ️ Yordam: 🔍 Juft qidirish tugmasini bosing va suhbatni boshlang!",
        "gender_m": "Erkak",
        "gender_f": "Ayol",
        "gender_o": "Boshqa",
        "profanity": "⚠️ Nojoʻya soʻzlar uchun bloklandingiz.",
        "only_premium": "🔒 Bu xabarni faqat Premium foydalanuvchilar yuborishi mumkin.",
        "buy_contact": "💳 Premium sotib olish uchun admin bilan bogʻlaning: @uletaaay",
        "age_updated": "✅ Yosh muvaffaqiyatli yangilandi!",
        "gender_updated": "✅ Jins muvaffaqiyatli yangilandi!",
        "chat_controls": "💬 Chat boshqaruvi:",
        "change_age": "🔁 Yoshni oʻzgartirish",
        "change_gender": "🚻 Jinsni oʻzgartirish",
        "change_lang": "🔤 Tilni oʻzgartirish",
        "back": "⬅️ Orqaga",
    },
    "ru": {
        "ask_lang": "🌐 Выберите язык:",
        "ask_age": "🗓 Сколько вам лет? (12–35):",
        "ask_gender": "🚻 Выберите пол:",
        "registered": "✅ Вы зарегистрированы! Используйте меню ниже.",
        "panel_title": "⚡ Главное меню — Онлайн: {online}",
        "btn_find": "🔍 Найти собеседника",
        "btn_stop": "❌ Остановить",
        "btn_next": "➡️ Следующий",
        "btn_settings": "⚙️ Настройки",
        "btn_help": "ℹ️ Помощь",
        "btn_premium": "💎 Премиум",
        "searching": "🔎 Идёт поиск...",
        "matched": "✅ Собеседник найден!\n👤 Пол: {gender}\n🎂 Возраст: {age}\nНачинайте переписку.",
        "not_in_chat": "Вы сейчас не в чате. Нажмите '🔍 Найти собеседника'.",
        "stopped": "❌ Чат остановлен.",
        "partner_left": "ℹ️ Собеседник покинул чат.",
        "settings": "⚙️ Настройки",
        "choose_lang": "🔤 Выберите язык:",
        "changed_lang": "✅ Язык изменён.",
        "help_text": "ℹ️ Помощь: Нажмите «🔍Найти собеседника» и начните общение!",
        "gender_m": "Мужчина",
        "gender_f": "Женщина",
        "gender_o": "Другое",
        "profanity": "⚠️ Нецензурная лексика — вы заблокированы.",
        "only_premium": "🔒 Доступно только для Премиум.",
        "buy_contact": "💳 Чтобы купить Premium — свяжитесь с админом: @uletaaay",
        "age_updated": "✅ Возраст обновлён!",
        "gender_updated": "✅ Пол обновлён!",
        "chat_controls": "💬 Управление чатом:",
        "change_age": "🔁 Изменить возраст",
        "change_gender": "🚻 Изменить пол",
        "change_lang": "🔤 Изменить язык",
        "back": "⬅️ Назад",
    }
}

# ========== Profanity & Rate limit ==========
PROFANITY = {"fuck", "bitch", "suka", "blyat", "xaromi", "хуй", "пизд"}
RATE_LIMIT_COUNT = 20
RATE_LIMIT_WINDOW = 60  # seconds
TEMP_BANS: dict[int, float] = {}
MSG_TIMES: dict[int, list[float]] = {}

def contains_profanity(text: str) -> bool:
    if not text:
        return False
    s = re.sub(r"\W+", " ", text).lower()
    return any(bad in s for bad in PROFANITY)

def check_rate_limit(user_id: int) -> bool:
    now = time.time()
    arr = [t for t in MSG_TIMES.get(user_id, []) if t > now - RATE_LIMIT_WINDOW]
    arr.append(now)
    MSG_TIMES[user_id] = arr
    if len(arr) > RATE_LIMIT_COUNT:
        TEMP_BANS[user_id] = now + 300
        return False
    return True

def is_temp_banned(user_id: int) -> bool:
    t = TEMP_BANS.get(user_id)
    if not t:
        return False
    if time.time() > t:
        TEMP_BANS.pop(user_id, None)
        return False
    return True

# ========== Admin helpers ==========
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

# ========== Users.txt saqlash funksiyasi ==========
USERS_FILE = "users.txt"

async def save_user_to_file(user_id: int, username: str):
    """Foydalanuvchini users.txt fayliga saqlash"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Tuzatildi
        
        # Username bo'sh bo'lsa, "NoUsername" deb yozish
        display_username = f"@{username}" if username else "NoUsername"
        
        user_entry = f"ID: {user_id} | Username: {display_username} | Qo'shilgan: {timestamp}\n"
        
        # Fayl mavjudligini tekshirish va yangi foydalanuvchini qo'shish
        with open(USERS_FILE, "a", encoding="utf-8") as f:
            f.write(user_entry)
            
        logger.info(f"Foydalanuvchi users.txt ga saqlandi: {user_id} | {display_username}")
        
    except Exception as e:
        logger.error(f"users.txt ga yozishda xato: {e}")

async def get_users_count():
    """users.txt faylidagi foydalanuvchilar sonini olish"""
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return len(lines)
    except FileNotFoundError:
        return 0
    except Exception as e:
        logger.error(f"users.txt dan o'qishda xato: {e}")
        return 0

# ========== Chat Log funksiyalari ==========
async def create_chat_log(user1: int, user2: int):
    """Yangi chat log fayli yaratish"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Tuzatildi
        
        log_filename = f"chat_logs/chat_{user1}_{user2}_{timestamp}.txt"
        
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Tuzatildi
        log_entry = f"=== CHAT BOSHLANDI ===\n"
        log_entry += f"Foydalanuvchi 1: {user1}\n"
        log_entry += f"Foydalanuvchi 2: {user2}\n"
        log_entry += f"Boshlanish vaqti: {start_time}\n"
        log_entry += "=" * 30 + "\n\n"
        
        with open(log_filename, "w", encoding="utf-8") as f:
            f.write(log_entry)
            
        return log_filename
    except Exception as e:
        logger.error(f"Chat log yaratishda xato: {e}")
        return None

async def save_message_to_log(log_filename: str, user_id: int, message_text: str, message_type: str = "text"):
    """Xabarni chat log ga saqlash"""
    try:
        timestamp = datetime.now().strftime("%H:%M:%S")  # Tuzatildi
        
        if message_type == "text":
            log_entry = f"[{timestamp}] User{user_id}: {message_text}\n"
        elif message_type == "photo":
            log_entry = f"[{timestamp}] User{user_id}: [RASM]\n"
        elif message_type == "sticker":
            log_entry = f"[{timestamp}] User{user_id}: [STIKER]\n"
        elif message_type == "voice":
            log_entry = f"[{timestamp}] User{user_id}: [OVOZLI XABAR]\n"
        elif message_type == "audio":
            log_entry = f"[{timestamp}] User{user_id}: [AUDIO]\n"
        elif message_type == "animation":
            log_entry = f"[{timestamp}] User{user_id}: [GIF]\n"
        elif message_type == "video_note":
            log_entry = f"[{timestamp}] User{user_id}: [VIDEO NOTA]\n"
        else:
            log_entry = f"[{timestamp}] User{user_id}: [{message_type.upper()}]\n"
        
        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(log_entry)
            
    except Exception as e:
        logger.error(f"Chat log ga yozishda xato: {e}")

async def close_chat_log(log_filename: str):
    """Chat log ni yopish (chat tugaganda)"""
    try:
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Tuzatildi
        log_entry = f"\n" + "=" * 30 + f"\n=== CHAT TUGADI ===\nTugash vaqti: {end_time}\n"
        
        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(log_entry)
            
    except Exception as e:
        logger.error(f"Chat log ni yopishda xato: {e}")

async def close_chat_log(log_filename: str):
    """Chat log ni yopish (chat tugaganda)"""
    try:
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # datetime.datetime -> datetime
        log_entry = f"\n" + "=" * 30 + f"\n=== CHAT TUGADI ===\nTugash vaqti: {end_time}\n"
        
        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(log_entry)
            
    except Exception as e:
        logger.error(f"Chat log ni yopishda xato: {e}")

async def close_chat_log(log_filename: str):
    """Chat log ni yopish (chat tugaganda)"""
    try:
        end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"\n" + "=" * 30 + f"\n=== CHAT TUGADI ===\nTugash vaqti: {end_time}\n"
        
        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(log_entry)
            
    except Exception as e:
        logger.error(f"Chat log ni yopishda xato: {e}")

# Chat log fayllarini saqlash uchun dictionary
CHAT_LOGS: dict[int, str] = {}  # user_id -> log_filename

# ========== Database helpers ==========
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                age INTEGER,
                gender TEXT,
                language TEXT DEFAULT 'uz',
                premium INTEGER DEFAULT 0,
                banned INTEGER DEFAULT 0,
                last_active REAL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS waiting (
                user_id INTEGER PRIMARY KEY,
                queued_at REAL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                user1 INTEGER,
                user2 INTEGER,
                started_at REAL
            )
        """)
        await db.commit()

async def ensure_user(user: types.User):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users WHERE user_id=?", (user.id,)) as cur:
            r = await cur.fetchone()
        if not r:
            await db.execute("INSERT INTO users(user_id, username, last_active) VALUES (?, ?, ?)",
                             (user.id, user.username or "", time.time()))
            await db.commit()

async def get_user_row(user_id: int) -> Optional[tuple]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id, username, age, gender, language, premium, banned, last_active FROM users WHERE user_id=?", (user_id,)) as cur:
            return await cur.fetchone()

async def set_user_field(user_id: int, **fields):
    if not fields:
        return
    keys = ", ".join(f"{k}=?" for k in fields.keys())
    vals = list(fields.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {keys} WHERE user_id=?", vals)
        await db.commit()

async def add_waiting(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO waiting(user_id, queued_at) VALUES (?, ?)", (user_id, time.time()))
        await db.commit()

async def remove_waiting(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM waiting WHERE user_id=?", (user_id,))
        await db.commit()

async def find_candidate(for_user: int) -> Optional[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM waiting WHERE user_id != ? LIMIT 1", (for_user,)) as cur:
            row = await cur.fetchone()
            if row:
                return row[0]
    return None

async def create_chat(a: int, b: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO chats(user1, user2, started_at) VALUES (?, ?, ?)", (a, b, time.time()))
        await db.commit()

async def delete_chat(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM chats WHERE user1=? OR user2=?", (user_id, user_id))
        await db.commit()

async def get_partner(user_id: int) -> Optional[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user1, user2 FROM chats WHERE user1=? OR user2=?", (user_id, user_id)) as cur:
            row = await cur.fetchone()
            if row:
                u1, u2 = row
                return u2 if u1 == user_id else u1
    return None

async def remove_chat_for_both(user1: int, user2: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM chats WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)", (user1, user2, user2, user1))
        await db.commit()

async def get_online_count(window_seconds: int = 300) -> int:
    cutoff = time.time() - window_seconds
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users WHERE last_active > ?", (cutoff,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0

async def set_last_active(user_id: int):
    await set_user_field(user_id, last_active=time.time())

async def is_banned(user_id: int) -> bool:
    row = await get_user_row(user_id)
    return bool(row and row[6])

# ========== FSM states ==========
class Register(StatesGroup):
    choosing_language = State()
    choosing_age = State()
    choosing_gender = State()

# ========== Reply Keyboards ==========
def main_reply_kb(lang: str) -> ReplyKeyboardMarkup:
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["btn_find"])], [KeyboardButton(text=t["btn_stop"])],
            [KeyboardButton(text=t["btn_settings"]), KeyboardButton(text=t["btn_help"])],
            [KeyboardButton(text=t["btn_premium"])]
        ],
        resize_keyboard=True,
        persistent=True
    )

def chat_reply_kb(lang: str) -> ReplyKeyboardMarkup:
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["btn_stop"]), KeyboardButton(text=t["btn_next"])]
        ],
        resize_keyboard=True,
        persistent=True
    )

def settings_reply_kb(lang: str) -> ReplyKeyboardMarkup:
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["change_age"])],
            [KeyboardButton(text=t["change_gender"])],
            [KeyboardButton(text=t["change_lang"])],
            [KeyboardButton(text=t["back"])]
        ],
        resize_keyboard=True,
        persistent=True
    )

def premium_reply_kb(lang: str) -> ReplyKeyboardMarkup:
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💳 1 oy - 3,000 so'm")],
            [KeyboardButton(text="💳 3 oy - 7,000 so'm")],
            [KeyboardButton(text="💳 6 oy - 10,000 so'm")],
            [KeyboardButton(text="💳 12 oy - 15,000 so'm")],
            [KeyboardButton(text=t["back"])]
        ],
        resize_keyboard=True,
        persistent=True
    )

# ========== Inline Keyboards helpers ==========
def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 Oʻzbekcha", callback_data="lang_uz"),
         InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
    ])

def age_kb(start: int = 12, end: int = 35) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for a in range(start, end + 1):
        row.append(InlineKeyboardButton(text=str(a), callback_data=f"age_{a}"))
        if len(row) == 6:
            buttons.append(row); row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def gender_kb(lang: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t["gender_m"], callback_data="g_m"),
            InlineKeyboardButton(text=t["gender_f"], callback_data="g_f"),
            InlineKeyboardButton(text=t["gender_o"], callback_data="g_o"),
        ]
    ])

# ========== Helpers ==========
async def delete_after(msg: types.Message | types.CallbackQuery | None, delay: int = AUTODELETE_DELAY):
    if msg is None:
        return
    m = msg.message if isinstance(msg, CallbackQuery) else msg
    await asyncio.sleep(delay)
    try:
        await m.delete()
    except Exception:
        pass

# ========== Admin commands ==========
@dp.message(Command("ban"))
async def ban_user(m: Message):
    if not is_admin(m.from_user.id):
        return
    
    parts = m.text.split()
    if len(parts) != 2:
        await m.answer("Ishlatish: /ban <user_id>")
        return
    
    try:
        user_id = int(parts[1])
        await set_user_field(user_id, banned=1)
        await delete_chat(user_id)
        await remove_waiting(user_id)
        await m.answer(f"✅ User {user_id} bloklandi")
    except ValueError:
        await m.answer("Noto'g'ri user_id")

@dp.message(Command("unban"))
async def unban_user(m: Message):
    if not is_admin(m.from_user.id):
        return
    
    parts = m.text.split()
    if len(parts) != 2:
        await m.answer("Ishlatish: /unban <user_id>")
        return
    
    try:
        user_id = int(parts[1])
        await set_user_field(user_id, banned=0)
        await m.answer(f"✅ User {user_id} blokdan chiqarildi")
    except ValueError:
        await m.answer("Noto'g'ri user_id")

@dp.message(Command("premium"))
async def give_premium(m: Message):
    if not is_admin(m.from_user.id):
        return
    
    parts = m.text.split()
    if len(parts) != 2:
        await m.answer("Ishlatish: /premium <user_id>")
        return
    
    try:
        user_id = int(parts[1])
        await set_user_field(user_id, premium=1)
        await m.answer(f"✅ User {user_id} ga premium berildi")
    except ValueError:
        await m.answer("Noto'g'ri user_id")

@dp.message(Command("unpremium"))
async def remove_premium(m: Message):
    if not is_admin(m.from_user.id):
        return
    
    parts = m.text.split()
    if len(parts) != 2:
        await m.answer("Ishlatish: /unpremium <user_id>")
        return
    
    try:
        user_id = int(parts[1])
        await set_user_field(user_id, premium=0)
        await m.answer(f"✅ User {user_id} dan premium olib tashlandi")
    except ValueError:
        await m.answer("Noto'g'ri user_id")

@dp.message(Command("stats"))
async def show_stats(m: Message):
    if not is_admin(m.from_user.id):
        return
    
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            total = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM users WHERE premium=1") as cur:
            premium = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM users WHERE banned=1") as cur:
            banned = (await cur.fetchone())[0]
    
    txt_users_count = await get_users_count()
    
    stats_text = f"""
📊 **Bot Statistikasi:**

👥 Jami foydalanuvchilar: {total}
📝 users.txt dagi foydalanuvchilar: {txt_users_count}
💎 Premium foydalanuvchilar: {premium}
⛔ Bloklangan foydalanuvchilar: {banned}
"""
    await m.answer(stats_text)

# ========== Yangi admin buyrug'i - /users ==========
@dp.message(Command("users"))
async def show_users_list(m: Message):
    if not is_admin(m.from_user.id):
        return
    
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = f.readlines()
        
        if not users:
            await m.answer("📝 Hozircha foydalanuvchilar ro'yxati bo'sh")
            return
        
        # Oxirgi 10 ta foydalanuvchini ko'rsatish
        recent_users = users[-10:]  # Oxirgi 10 ta
        users_text = "📝 **Oxirgi 10 ta foydalanuvchi:**\n\n"
        
        for user in recent_users:
            users_text += f"• {user.strip()}\n"
        
        users_text += f"\n📊 Jami foydalanuvchilar: {len(users)}"
        
        await m.answer(users_text)
        
    except FileNotFoundError:
        await m.answer("📝 Hozircha foydalanuvchilar ro'yxati mavjud emas")
    except Exception as e:
        logger.error(f"users.txt ni o'qishda xato: {e}")
        await m.answer("❌ Foydalanuvchilar ro'yxatini o'qishda xato")

# ========== Yangi admin buyrug'i - /export_users ==========
@dp.message(Command("export_users"))
async def export_users_file(m: Message):
    if not is_admin(m.from_user.id):
        return
    
    try:
        # users.txt fayli mavjudligini va bo'sh emasligini tekshirish
        if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
            await m.answer("❌ Foydalanuvchilar ro'yxati fayli bo'sh yoki mavjud emas")
            return
            
        with open(USERS_FILE, "rb") as f:
            await m.answer_document(
                types.FSInputFile(USERS_FILE, filename="users_list.txt"),
                caption=f"📊 Foydalanuvchilar ro'yxati\nJami: {await get_users_count()} ta"
            )
    except FileNotFoundError:
        await m.answer("❌ Foydalanuvchilar ro'yxati fayli topilmadi")
    except Exception as e:
        logger.error(f"Faylni yuborishda xato: {e}")
        await m.answer("❌ Faylni yuborishda xato. Fayl bo'sh bo'lishi mumkin.")

# ========== Handlers ==========

# /start
@dp.message(Command("start"))
async def cmd_start(m: Message, state: FSMContext):
    await ensure_user(m.from_user)
    await set_last_active(m.from_user.id)
    
    # Yangi foydalanuvchini users.txt ga saqlash
    await save_user_to_file(m.from_user.id, m.from_user.username)
    
    # Agar admin bo'lsa, admin xabarini ko'rsatish
    if is_admin(m.from_user.id):
        users_count = await get_users_count()
        await m.answer(f"👨‍💻 Siz admin sifatida kirdingiz!\n📊 Jami foydalanuvchilar: {users_count}\n\nAdmin buyruqlari:\n/ban <id>\n/unban <id>\n/premium <id>\n/unpremium <id>\n/stats\n/users\n/export_users")
    
    # ask language
    msg = await m.answer(TEXTS["uz"]["ask_lang"], reply_markup=lang_kb())
    await state.set_state(Register.choosing_language)
    asyncio.create_task(delete_after(msg, AUTODELETE_DELAY))

# language selection (during registration)
@dp.callback_query(Register.choosing_language, F.data.in_({"lang_uz", "lang_ru"}))
async def cb_choose_lang(c: CallbackQuery, state: FSMContext):
    lang_code = "uz" if c.data == "lang_uz" else "ru"
    await set_user_field(c.from_user.id, language=lang_code)
    try:
        await c.message.edit_reply_markup(None)
    except Exception:
        pass
    await state.set_state(Register.choosing_age)
    t = TEXTS[lang_code]
    msg = await c.message.answer(t["ask_age"], reply_markup=age_kb(12,35))
    asyncio.create_task(delete_after(msg, AUTODELETE_DELAY))
    await c.answer()

# age selection (during registration) 12-35
@dp.callback_query(Register.choosing_age, F.data.startswith("age_"))
async def cb_choose_age(c: CallbackQuery, state: FSMContext):
    try:
        age = int(c.data.split("_",1)[1])
    except Exception:
        await c.answer()
        return
    await set_user_field(c.from_user.id, age=age)
    try:
        await c.message.edit_reply_markup(None)
    except Exception:
        pass
    user = await get_user_row(c.from_user.id)
    lang = user[4] if user and user[4] in TEXTS else "uz"
    await state.set_state(Register.choosing_gender)
    msg = await c.message.answer(TEXTS[lang]["ask_gender"], reply_markup=gender_kb(lang))
    asyncio.create_task(delete_after(msg, AUTODELETE_DELAY))
    await c.answer()

# gender selection
@dp.callback_query(Register.choosing_gender, F.data.in_({"g_m","g_f","g_o"}))
async def cb_choose_gender(c: CallbackQuery, state: FSMContext):
    mapping = {"g_m":"male","g_f":"female","g_o":"other"}
    code = mapping.get(c.data, "other")
    await set_user_field(c.from_user.id, gender=code)
    try:
        await c.message.edit_reply_markup(None)
    except Exception:
        pass
    user = await get_user_row(c.from_user.id)
    lang = user[4] if user and user[4] in TEXTS else "uz"
    await state.clear()
    online = await get_online_count()
    panel_text = TEXTS[lang]["panel_title"].format(online=online)
    await c.message.answer(TEXTS[lang]["registered"])
    await c.message.answer(panel_text, reply_markup=main_reply_kb(lang))
    await c.answer()

# ========== Reply Keyboard Handlers ==========
@dp.message(F.text.in_([TEXTS["uz"]["btn_find"], TEXTS["ru"]["btn_find"]]))
async def handle_find_button(m: Message):
    await ensure_user(m.from_user)
    await set_last_active(m.from_user.id)
    
    uid = m.from_user.id
    if await is_banned(uid):
        user = await get_user_row(uid)
        lang = user[4] if user and user[4] in TEXTS else "uz"
        await m.answer(TEXTS[lang]["profanity"])
        return
    if is_temp_banned(uid):
        user = await get_user_row(uid)
        lang = user[4] if user and user[4] in TEXTS else "uz"
        await m.answer(TEXTS[lang]["profanity"])
        return

    await delete_chat(uid)
    await add_waiting(uid)
    user = await get_user_row(uid)
    lang = user[4] if user and user[4] in TEXTS else "uz"
    loading_msg = await bot.send_message(uid, TEXTS[lang]["searching"])
    
    partner = await find_candidate(uid)
    if partner:
        await create_chat(uid, partner)
        await remove_waiting(uid)
        await remove_waiting(partner)
        
        # Chat log yaratish
        log_filename = await create_chat_log(uid, partner)
        if log_filename:
            CHAT_LOGS[uid] = log_filename
            CHAT_LOGS[partner] = log_filename
        
        me = await get_user_row(uid)
        pa = await get_user_row(partner)
        pa_lang = pa[4] if pa and pa[4] in TEXTS else "uz"
        me_gender_label = TEXTS[pa_lang]["gender_m"] if me and me[3] == "male" else \
                          TEXTS[pa_lang]["gender_f"] if me and me[3] == "female" else \
                          TEXTS[pa_lang]["gender_o"]
        
        try:
            await bot.send_message(
                partner, 
                TEXTS[pa_lang]["matched"].format(gender=me_gender_label, age=me[2]),
                reply_markup=chat_reply_kb(pa_lang)
            )
        except Exception:
            pass

        my_lang = me[4] if me and me[4] in TEXTS else "uz"
        pa_gender_label = TEXTS[my_lang]["gender_m"] if pa and pa[3] == "male" else \
                          TEXTS[my_lang]["gender_f"] if pa and pa[3] == "female" else \
                          TEXTS[my_lang]["gender_o"]
        
        try:
            await bot.send_message(
                uid, 
                TEXTS[my_lang]["matched"].format(gender=pa_gender_label, age=pa[2]),
                reply_markup=chat_reply_kb(my_lang)
            )
        except Exception:
            pass
    else:
        await show_panel_for_user(uid)
    
    try:
        await loading_msg.delete()
    except Exception:
        pass

@dp.message(F.text.in_([TEXTS["uz"]["btn_stop"], TEXTS["ru"]["btn_stop"]]))
async def handle_stop_button(m: Message):
    uid = m.from_user.id
    partner = await get_partner(uid)
    
    # Chat log ni yopish
    if uid in CHAT_LOGS:
        log_filename = CHAT_LOGS[uid]
        await close_chat_log(log_filename)
        # Log fayllarini tozalash
        if partner and partner in CHAT_LOGS:
            del CHAT_LOGS[partner]
        del CHAT_LOGS[uid]
    
    await delete_chat(uid)
    await remove_waiting(uid)
    user = await get_user_row(uid)
    lang = user[4] if user and user[4] in TEXTS else "uz"
    
    await m.answer(TEXTS[lang]["stopped"], reply_markup=main_reply_kb(lang))
    
    if partner:
        p = await get_user_row(partner)
        p_lang = p[4] if p and p[4] in TEXTS else "uz"
        try:
            await bot.send_message(partner, TEXTS[p_lang]["partner_left"], reply_markup=main_reply_kb(p_lang))
        except Exception:
            pass
        await remove_chat_for_both(uid, partner)
    
    await show_panel_for_user(uid)

@dp.message(F.text.in_([TEXTS["uz"]["btn_next"], TEXTS["ru"]["btn_next"]]))
async def handle_next_button(m: Message):
    uid = m.from_user.id
    partner = await get_partner(uid)
    
    # Oldingi chat log ni yopish
    if uid in CHAT_LOGS:
        log_filename = CHAT_LOGS[uid]
        await close_chat_log(log_filename)
        # Log fayllarini tozalash
        if partner and partner in CHAT_LOGS:
            del CHAT_LOGS[partner]
        del CHAT_LOGS[uid]
    
    await delete_chat(uid)
    await remove_waiting(uid)
    
    user = await get_user_row(uid)
    lang = user[4] if user and user[4] in TEXTS else "uz"
    
    if partner:
        p = await get_user_row(partner)
        p_lang = p[4] if p and p[4] in TEXTS else "uz"
        try:
            await bot.send_message(partner, TEXTS[p_lang]["partner_left"], reply_markup=main_reply_kb(p_lang))
        except Exception:
            pass
        await remove_chat_for_both(uid, partner)
    
    await add_waiting(uid)
    loading_msg = await bot.send_message(uid, TEXTS[lang]["searching"])
    
    new_partner = await find_candidate(uid)
    if new_partner:
        await create_chat(uid, new_partner)
        await remove_waiting(uid)
        await remove_waiting(new_partner)
        
        # Yangi chat log yaratish
        log_filename = await create_chat_log(uid, new_partner)
        if log_filename:
            CHAT_LOGS[uid] = log_filename
            CHAT_LOGS[new_partner] = log_filename
        
        me = await get_user_row(uid)
        pa = await get_user_row(new_partner)
        pa_lang = pa[4] if pa and pa[4] in TEXTS else "uz"
        me_gender_label = TEXTS[pa_lang]["gender_m"] if me and me[3] == "male" else \
                          TEXTS[pa_lang]["gender_f"] if me and me[3] == "female" else \
                          TEXTS[pa_lang]["gender_o"]
        
        try:
            await bot.send_message(
                new_partner, 
                TEXTS[pa_lang]["matched"].format(gender=me_gender_label, age=me[2]),
                reply_markup=chat_reply_kb(pa_lang)
            )
        except Exception:
            pass

        my_lang = me[4] if me and me[4] in TEXTS else "uz"
        pa_gender_label = TEXTS[my_lang]["gender_m"] if pa and pa[3] == "male" else \
                          TEXTS[my_lang]["gender_f"] if pa and pa[3] == "female" else \
                          TEXTS[my_lang]["gender_o"]
        
        try:
            await bot.send_message(
                uid, 
                TEXTS[my_lang]["matched"].format(gender=pa_gender_label, age=pa[2]),
                reply_markup=chat_reply_kb(my_lang)
            )
        except Exception:
            pass
    else:
        await show_panel_for_user(uid)
    
    try:
        await loading_msg.delete()
    except Exception:
        pass

# Settings, Help, Premium reply buttons
@dp.message(F.text.in_([TEXTS["uz"]["btn_settings"], TEXTS["ru"]["btn_settings"]]))
async def handle_settings_button(m: Message):
    user = await get_user_row(m.from_user.id)
    lang = user[4] if user and user[4] in TEXTS else "uz"
    await m.answer(TEXTS[lang]["settings"], reply_markup=settings_reply_kb(lang))

@dp.message(F.text.in_([TEXTS["uz"]["btn_help"], TEXTS["ru"]["btn_help"]]))
async def handle_help_button(m: Message):
    user = await get_user_row(m.from_user.id)
    lang = user[4] if user and user[4] in TEXTS else "uz"
    await m.answer(TEXTS[lang]["help_text"])

@dp.message(F.text.in_([TEXTS["uz"]["btn_premium"], TEXTS["ru"]["btn_premium"]]))
async def handle_premium_button(m: Message):
    user = await get_user_row(m.from_user.id)
    lang = user[4] if user and user[4] in TEXTS else "uz"
    await m.answer("💎 Premium paketlarni tanlang:", reply_markup=premium_reply_kb(lang))

# Settings reply buttons
@dp.message(F.text.in_([TEXTS["uz"]["change_age"], TEXTS["ru"]["change_age"]]))
async def handle_change_age(m: Message):
    user = await get_user_row(m.from_user.id)
    lang = user[4] if user and user[4] in TEXTS else "uz"
    await m.answer(TEXTS[lang]["ask_age"], reply_markup=age_kb(12, 80))

@dp.message(F.text.in_([TEXTS["uz"]["change_gender"], TEXTS["ru"]["change_gender"]]))
async def handle_change_gender(m: Message):
    user = await get_user_row(m.from_user.id)
    lang = user[4] if user and user[4] in TEXTS else "uz"
    await m.answer(TEXTS[lang]["ask_gender"], reply_markup=gender_kb(lang))

@dp.message(F.text.in_([TEXTS["uz"]["change_lang"], TEXTS["ru"]["change_lang"]]))
async def handle_change_lang(m: Message):
    await m.answer("🔤 Tilni tanlang:", reply_markup=lang_kb())

# Premium package buttons
@dp.message(F.text.in_([
    "💳 1 oy - 3,000 so'm", 
    "💳 3 oy - 7,000 so'm", 
    "💳 6 oy - 10,000 so'm", 
    "💳 12 oy - 15,000 so'm"
]))
async def handle_premium_package(m: Message):
    user = await get_user_row(m.from_user.id)
    lang = user[4] if user and user[4] in TEXTS else "uz"
    
    await m.answer(TEXTS[lang]["buy_contact"], reply_markup=premium_reply_kb(lang))

# Back button handler
@dp.message(F.text.in_([TEXTS["uz"]["back"], TEXTS["ru"]["back"]]))
async def handle_back_button(m: Message):
    user = await get_user_row(m.from_user.id)
    lang = user[4] if user and user[4] in TEXTS else "uz"
    online = await get_online_count()
    panel_text = TEXTS[lang]["panel_title"].format(online=online)
    await m.answer(panel_text, reply_markup=main_reply_kb(lang))

# ========== Inline Callbacks ==========
@dp.callback_query(F.data == "help")
async def cb_help(c: CallbackQuery):
    user = await get_user_row(c.from_user.id)
    lang = user[4] if user and user[4] in TEXTS else "uz"
    await c.message.answer(TEXTS[lang]["help_text"])
    await c.answer()

# Language change callback
@dp.callback_query(F.data.in_({"lang_uz", "lang_ru"}))
async def cb_change_lang(c: CallbackQuery):
    lang_code = "uz" if c.data == "lang_uz" else "ru"
    await set_user_field(c.from_user.id, language=lang_code)
    try:
        await c.message.edit_reply_markup(None)
    except Exception:
        pass
    t = TEXTS[lang_code]
    await c.message.answer(t["changed_lang"], reply_markup=settings_reply_kb(lang_code))
    await c.answer()

# Age change callback
@dp.callback_query(F.data.startswith("age_"))
async def cb_change_age(c: CallbackQuery):
    try:
        age = int(c.data.split("_",1)[1])
    except Exception:
        await c.answer()
        return
    await set_user_field(c.from_user.id, age=age)
    try:
        await c.message.edit_reply_markup(None)
    except Exception:
        pass
    user = await get_user_row(c.from_user.id)
    lang = user[4] if user and user[4] in TEXTS else "uz"
    await c.message.answer(TEXTS[lang]["age_updated"], reply_markup=settings_reply_kb(lang))
    await c.answer()

# Gender change callback
@dp.callback_query(F.data.in_({"g_m","g_f","g_o"}))
async def cb_change_gender(c: CallbackQuery):
    mapping = {"g_m":"male","g_f":"female","g_o":"other"}
    code = mapping.get(c.data, "other")
    await set_user_field(c.from_user.id, gender=code)
    try:
        await c.message.edit_reply_markup(None)
    except Exception:
        pass
    user = await get_user_row(c.from_user.id)
    lang = user[4] if user and user[4] in TEXTS else "uz"
    await c.message.answer(TEXTS[lang]["gender_updated"], reply_markup=settings_reply_kb(lang))
    await c.answer()

# ========== Relaying messages between partners ==========
@dp.message()
async def relay_messages(m: Message):
    # ignore commands handled separately
    if m.text and m.text.startswith("/"):
        return
    uid = m.from_user.id
    await set_last_active(uid)

    # check banned & temp banned
    if await is_banned(uid):
        user = await get_user_row(uid)
        lang = user[4] if user and user[4] in TEXTS else "uz"
        await m.answer(TEXTS[lang]["profanity"])
        return
    if is_temp_banned(uid):
        user = await get_user_row(uid)
        lang = user[4] if user and user[4] in TEXTS else "uz"
        await m.answer(TEXTS[lang]["profanity"])
        return

    if not check_rate_limit(uid):
        await m.answer("Too many messages. Try later.")
        return

    partner = await get_partner(uid)
    if not partner:
        user = await get_user_row(uid)
        lang = user[4] if user and user[4] in TEXTS else "uz"
        await m.answer(TEXTS[lang]["not_in_chat"], reply_markup=main_reply_kb(lang))
        return

    # Chat log ga xabarni saqlash
    if uid in CHAT_LOGS:
        log_filename = CHAT_LOGS[uid]
        message_text = m.text or m.caption or ""
        message_type = "text"
        
        if m.photo:
            message_type = "photo"
        elif m.sticker:
            message_type = "sticker"
        elif m.voice:
            message_type = "voice"
        elif m.audio:
            message_type = "audio"
        elif m.animation:
            message_type = "animation"
        elif m.video_note:
            message_type = "video_note"
        
        await save_message_to_log(log_filename, uid, message_text, message_type)

    # profanity check
    txt = m.text or m.caption or ""
    if contains_profanity(txt):
        user = await get_user_row(uid)
        lang = user[4] if user and user[4] in TEXTS else "uz"
        await m.answer(TEXTS[lang]["profanity"])
        await set_user_field(uid, banned=1)
        p = await get_user_row(partner)
        p_lang = p[4] if p and p[4] in TEXTS else "uz"
        try:
            await bot.send_message(partner, TEXTS[p_lang]["partner_left"], reply_markup=main_reply_kb(p_lang))
        except Exception:
            pass
        await remove_chat_for_both(uid, partner)
        await show_panel_for_user(partner)
        return

    # Agar admin bo'lsa, premium tekshirishdan o'tkazma
    if is_admin(uid):
        is_premium = True  # Admin har doim premium hisoblanadi
    else:
        me = await get_user_row(uid)
        is_premium = bool(me and me[5])
    
    # handle different content types
    try:
        if m.text:
            await bot.send_message(partner, m.text)
        elif m.photo:
            if not is_premium:
                lang = me[4] if me and me[4] in TEXTS else "uz"
                await m.reply(TEXTS[lang]["only_premium"])
                return
            await bot.send_photo(partner, m.photo[-1].file_id, caption=m.caption or "")
        elif m.sticker:
            if not is_premium:
                lang = me[4] if me and me[4] in TEXTS else "uz"
                await m.reply(TEXTS[lang]["only_premium"])
                return
            await bot.send_sticker(partner, m.sticker.file_id)
        elif m.voice:
            if not is_premium:
                lang = me[4] if me and me[4] in TEXTS else "uz"
                await m.reply(TEXTS[lang]["only_premium"])
                return
            await bot.send_voice(partner, m.voice.file_id)
        elif m.audio:
            if not is_premium:
                lang = me[4] if me and me[4] in TEXTS else "uz"
                await m.reply(TEXTS[lang]["only_premium"])
                return
            await bot.send_audio(partner, m.audio.file_id)
        elif m.animation:
            if not is_premium:
                lang = me[4] if me and me[4] in TEXTS else "uz"
                await m.reply(TEXTS[lang]["only_premium"])
                return
            await bot.send_animation(partner, m.animation.file_id)
        elif m.video_note:
            if not is_premium:
                lang = me[4] if me and me[4] in TEXTS else "uz"
                await m.reply(TEXTS[lang]["only_premium"])
                return
            await bot.send_video_note(partner, m.video_note.file_id)
        else:
            await m.answer("Unsupported message type.")
    except Exception as e:
        logger.exception("Forward error: %s", e)
        await m.answer("⚠️ Xato: xabar yuborilmadi.")

# helper: show panel with online count
async def show_panel_for_user(user_id: int):
    row = await get_user_row(user_id)
    lang = row[4] if row and row[4] in TEXTS else "uz"
    online = await get_online_count()
    panel_text = TEXTS[lang]["panel_title"].format(online=online)
    try:
        await bot.send_message(user_id, panel_text, reply_markup=main_reply_kb(lang))
    except Exception:
        pass

# ========== Startup ==========
async def on_startup():
    # Papkalarni yaratish
    os.makedirs("data", exist_ok=True)
    os.makedirs("chat_logs", exist_ok=True)
    
    # users.txt faylini yaratish agar mavjud bo'lmasa
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            f.write("=== FOYDALANUVCHILAR RO'YXATI ===\n")
            f.write(f"Yaratilgan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")  # Tuzatildi
            f.write("=" * 40 + "\n\n")
    
    await init_db()
    logger.info("Bot ishga tushdi. DB: %s", DB_PATH)

async def main():
    await on_startup()
    logger.info("Bot polling ni boshladi...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Xato: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
