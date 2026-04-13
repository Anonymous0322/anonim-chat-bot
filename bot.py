# anonimbot.py
# aiogram v3 anonymous chat roulette (UZ/RU)
# Requirements: Python 3.10+, aiogram, aiosqlite
# pip install aiogram aiosqlite

import asyncio
import logging
import os
import re
import time
from datetime import datetime
from typing import Optional

import aiosqlite
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

# ========== CONFIG ==========
# ========== CONFIG ==========
API_TOKEN = "8416511999:AAFbwKndsT1S98luxE_jczeCjf0g46pwckA"
ADMIN_ID = 7901013364  # <-- O'ZINGIZNING TELEGRAM ID'INGIZNI QO'YING
DB_PATH = "database.db"
AUTODELETE_DELAY = 60
SUPPORT_USERNAME = "@uletaaay"
USERS_FILE = "users.txt"




# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ensure data dir
os.makedirs("data", exist_ok=True)
os.makedirs("chat_logs", exist_ok=True)

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
        "buy_contact": "💳 Premium sotib olish uchun admin bilan bogʻlaning: {support}",
        "age_updated": "✅ Yosh muvaffaqiyatli yangilandi!",
        "gender_updated": "✅ Jins muvaffaqiyatli yangilandi!",
        "chat_controls": "💬 Chat boshqaruvi:",
        "change_age": "🔁 Yoshni oʻzgartirish",
        "change_gender": "🚻 Jinsni oʻzgartirish",
        "change_lang": "🔤 Tilni oʻzgartirish",
        "back": "⬅️ Orqaga",
        "already_registered": "👋 Xush kelibsiz! Siz allaqachon roʻyxatdan oʻtgansiz.",
        "complete_registration": "Avval roʻyxatdan oʻtishni tugating. /start bosing.",
        "too_many_messages": "⏳ Juda ko‘p xabar yubordingiz. Birozdan keyin urinib ko‘ring.",
        "unsupported": "⚠️ Bu turdagi xabar qo‘llab-quvvatlanmaydi.",
        "broadcast_done": "✅ Xabar {ok} ta foydalanuvchiga yuborildi.\n❌ Yuborilmadi: {fail}",
        "me_text": "🆔 ID: {user_id}\n👤 Username: {username}\n🎂 Yosh: {age}\n🚻 Jins: {gender}\n🌐 Til: {language}\n💎 Premium: {premium}\n⛔ Ban: {banned}",
        "queue_exists": "Siz allaqachon qidiruvdasiz. Biroz kuting.",
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
        "help_text": "ℹ️ Помощь: Нажмите «🔍 Найти собеседника» и начните общение!",
        "gender_m": "Мужчина",
        "gender_f": "Женщина",
        "gender_o": "Другое",
        "profanity": "⚠️ Нецензурная лексика — вы заблокированы.",
        "only_premium": "🔒 Доступно только для Премиум.",
        "buy_contact": "💳 Чтобы купить Premium — свяжитесь с админом: {support}",
        "age_updated": "✅ Возраст обновлён!",
        "gender_updated": "✅ Пол обновлён!",
        "chat_controls": "💬 Управление чатом:",
        "change_age": "🔁 Изменить возраст",
        "change_gender": "🚻 Изменить пол",
        "change_lang": "🔤 Изменить язык",
        "back": "⬅️ Назад",
        "already_registered": "👋 Добро пожаловать! Вы уже зарегистрированы.",
        "complete_registration": "Сначала завершите регистрацию. Нажмите /start.",
        "too_many_messages": "⏳ Вы отправляете слишком много сообщений. Попробуйте позже.",
        "unsupported": "⚠️ Этот тип сообщения не поддерживается.",
        "broadcast_done": "✅ Сообщение отправлено: {ok}\n❌ Не отправлено: {fail}",
        "me_text": "🆔 ID: {user_id}\n👤 Username: {username}\n🎂 Возраст: {age}\n🚻 Пол: {gender}\n🌐 Язык: {language}\n💎 Premium: {premium}\n⛔ Блок: {banned}",
        "queue_exists": "Вы уже в очереди. Подождите немного.",
    }
}

# ========== Profanity & Rate limit ==========
PROFANITY = {"fuck", "bitch", "suka", "blyat", "xaromi", "хуй", "пизд"}
RATE_LIMIT_COUNT = 20
RATE_LIMIT_WINDOW = 60  # seconds
TEMP_BANS: dict[int, float] = {}
MSG_TIMES: dict[int, list[float]] = {}
CHAT_LOGS: dict[int, str] = {}  # user_id -> log_filename
PREMIUM_PACKAGES = [
    "💳 1 oy - 3,000 so'm",
    "💳 3 oy - 7,000 so'm",
    "💳 6 oy - 10,000 so'm",
    "💳 12 oy - 15,000 so'm",
]


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


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


def normalize_gender_for_display(code: Optional[str], lang: str) -> str:
    t = TEXTS[lang]
    if code == "male":
        return t["gender_m"]
    if code == "female":
        return t["gender_f"]
    return t["gender_o"]


def is_registered_user(user_row: Optional[tuple]) -> bool:
    return bool(user_row and user_row[2] and user_row[3] and user_row[4])


# ========== users.txt helpers ==========
def ensure_users_file_exists():
    if os.path.exists(USERS_FILE):
        return
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        f.write("=== FOYDALANUVCHILAR RO'YXATI ===\n")
        f.write(f"Yaratilgan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 40 + "\n\n")


def _format_users_file_line(user_row: tuple, username_fallback: Optional[str] = None) -> str:
    user_id, username, age, gender, language, premium, banned, _, registered_at = user_row
    username_value = username or username_fallback or "NoUsername"
    display_username = f"@{username_value}" if username_value != "NoUsername" and not str(username_value).startswith("@") else username_value
    gender_map = {"male": "male", "female": "female", "other": "other", None: "-"}
    registered_text = (
        datetime.fromtimestamp(registered_at).strftime("%Y-%m-%d %H:%M:%S")
        if registered_at
        else "-"
    )
    return (
        f"ID: {user_id} | Username: {display_username} | "
        f"Age: {age or '-'} | Gender: {gender_map.get(gender, gender or '-')} | "
        f"Language: {language or '-'} | Premium: {'Yes' if premium else 'No'} | "
        f"Banned: {'Yes' if banned else 'No'} | Registered: {registered_text}\n"
    )


async def sync_user_to_file(user_id: int, username_fallback: Optional[str] = None):
    try:
        ensure_users_file_exists()
        user_row = await get_user_row(user_id)
        if not user_row:
            return

        new_line = _format_users_file_line(user_row, username_fallback=username_fallback)

        with open(USERS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        updated = False
        for i, line in enumerate(lines):
            if line.startswith(f"ID: {user_id} "):
                lines[i] = new_line
                updated = True
                break

        if not updated:
            if lines and not lines[-1].endswith("\n"):
                lines[-1] += "\n"
            lines.append(new_line)

        with open(USERS_FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)

        logger.info("users.txt sync qilindi: %s", user_id)
    except Exception as e:
        logger.error("users.txt sync qilishda xato: %s", e)


async def get_users_txt_count() -> int:
    try:
        if not os.path.exists(USERS_FILE):
            return 0
        count = 0
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("ID:"):
                    count += 1
        return count
    except Exception as e:
        logger.error("users.txt dan o'qishda xato: %s", e)
        return 0


# ========== Chat Log funksiyalari ==========
async def create_chat_log(user1: int, user2: int) -> Optional[str]:
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"chat_logs/chat_{user1}_{user2}_{timestamp}.txt"

        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = (
            "=== CHAT BOSHLANDI ===\n"
            f"Foydalanuvchi 1: {user1}\n"
            f"Foydalanuvchi 2: {user2}\n"
            f"Boshlanish vaqti: {start_time}\n"
            + "=" * 30
            + "\n\n"
        )

        with open(log_filename, "w", encoding="utf-8") as f:
            f.write(log_entry)

        return log_filename
    except Exception as e:
        logger.error("Chat log yaratishda xato: %s", e)
        return None


async def save_message_to_log(log_filename: str, user_id: int, message_text: str, message_type: str = "text"):
    try:
        timestamp = datetime.now().strftime("%H:%M:%S")

        labels = {
            "text": message_text,
            "photo": "[RASM]",
            "sticker": "[STIKER]",
            "voice": "[OVOZLI XABAR]",
            "audio": "[AUDIO]",
            "animation": "[GIF]",
            "video_note": "[VIDEO NOTA]",
            "video": "[VIDEO]",
            "document": "[HUJJAT]",
        }
        content = labels.get(message_type, f"[{message_type.upper()}]")
        log_entry = f"[{timestamp}] User{user_id}: {content}\n"

        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(log_entry)

    except Exception as e:
        logger.error("Chat log ga yozishda xato: %s", e)


async def close_chat_log(log_filename: str):
    try:
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = (
            "\n"
            + "=" * 30
            + f"\n=== CHAT TUGADI ===\nTugash vaqti: {end_time}\n"
        )

        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(log_entry)

    except Exception as e:
        logger.error("Chat log ni yopishda xato: %s", e)


# ========== Database helpers ==========
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                age INTEGER,
                gender TEXT,
                language TEXT DEFAULT 'uz',
                premium INTEGER DEFAULT 0,
                banned INTEGER DEFAULT 0,
                last_active REAL,
                registered_at REAL
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS waiting (
                user_id INTEGER PRIMARY KEY,
                queued_at REAL
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS chats (
                user1 INTEGER,
                user2 INTEGER,
                started_at REAL
            )
            """
        )

        # Eski bazalarda registered_at bo'lmasligi mumkin.
        try:
            await db.execute("ALTER TABLE users ADD COLUMN registered_at REAL")
        except Exception:
            pass

        await db.commit()


async def ensure_user(user: types.User) -> bool:
    """
    True  -> yangi user qo'shildi
    False -> user oldin bazada bor edi
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id FROM users WHERE user_id=?",
            (user.id,),
        ) as cur:
            row = await cur.fetchone()

        if row:
            await db.execute(
                "UPDATE users SET username=?, last_active=? WHERE user_id=?",
                (user.username or "", time.time(), user.id),
            )
            await db.commit()
            return False

        await db.execute(
            """
            INSERT INTO users(user_id, username, age, gender, language, premium, banned, last_active, registered_at)
            VALUES (?, ?, NULL, NULL, NULL, 0, 0, ?, NULL)
            """,
            (user.id, user.username or "", time.time()),
        )
        await db.commit()
        return True


async def get_user_row(user_id: int) -> Optional[tuple]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT user_id, username, age, gender, language, premium, banned, last_active, registered_at
            FROM users
            WHERE user_id=?
            """,
            (user_id,),
        ) as cur:
            return await cur.fetchone()


async def set_user_field(user_id: int, **fields):
    if not fields:
        return
    keys = ", ".join(f"{k}=?" for k in fields.keys())
    vals = list(fields.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {keys} WHERE user_id=?", vals)
        await db.commit()


async def get_total_users_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


async def add_waiting(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO waiting(user_id, queued_at) VALUES (?, ?)",
            (user_id, time.time()),
        )
        await db.commit()


async def remove_waiting(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM waiting WHERE user_id=?", (user_id,))
        await db.commit()


async def is_waiting(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM waiting WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return bool(row)


async def find_candidate(for_user: int) -> Optional[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id FROM waiting WHERE user_id != ? ORDER BY queued_at ASC LIMIT 1",
            (for_user,),
        ) as cur:
            row = await cur.fetchone()
            if row:
                return row[0]
    return None


async def create_chat(a: int, b: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO chats(user1, user2, started_at) VALUES (?, ?, ?)",
            (a, b, time.time()),
        )
        await db.commit()


async def delete_chat(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM chats WHERE user1=? OR user2=?", (user_id, user_id))
        await db.commit()


async def get_partner(user_id: int) -> Optional[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user1, user2 FROM chats WHERE user1=? OR user2=?",
            (user_id, user_id),
        ) as cur:
            row = await cur.fetchone()
            if row:
                u1, u2 = row
                return u2 if u1 == user_id else u1
    return None


async def remove_chat_for_both(user1: int, user2: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            DELETE FROM chats
            WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)
            """,
            (user1, user2, user2, user1),
        )
        await db.commit()


async def get_online_count(window_seconds: int = 300) -> int:
    cutoff = time.time() - window_seconds
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE last_active > ?",
            (cutoff,),
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


async def set_last_active(user_id: int):
    await set_user_field(user_id, last_active=time.time())


async def is_banned(user_id: int) -> bool:
    row = await get_user_row(user_id)
    return bool(row and row[6])


async def get_user_lang(user_id: int, default: str = "uz") -> str:
    user = await get_user_row(user_id)
    if user and user[4] in TEXTS:
        return user[4]
    return default


# ========== FSM states ==========
class Register(StatesGroup):
    choosing_language = State()
    choosing_age = State()
    choosing_gender = State()


class SettingsEdit(StatesGroup):
    choosing_language = State()
    choosing_age = State()
    choosing_gender = State()


# ========== Reply Keyboards ==========
def main_reply_kb(lang: str) -> ReplyKeyboardMarkup:
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["btn_find"])],
            [KeyboardButton(text=t["btn_stop"])],
            [KeyboardButton(text=t["btn_settings"]), KeyboardButton(text=t["btn_help"])],
            [KeyboardButton(text=t["btn_premium"])],
        ],
        resize_keyboard=True,
        persistent=True,
    )


def chat_reply_kb(lang: str) -> ReplyKeyboardMarkup:
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["btn_stop"]), KeyboardButton(text=t["btn_next"])],
        ],
        resize_keyboard=True,
        persistent=True,
    )


def settings_reply_kb(lang: str) -> ReplyKeyboardMarkup:
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["change_age"])],
            [KeyboardButton(text=t["change_gender"])],
            [KeyboardButton(text=t["change_lang"])],
            [KeyboardButton(text=t["back"])],
        ],
        resize_keyboard=True,
        persistent=True,
    )


def premium_reply_kb(lang: str) -> ReplyKeyboardMarkup:
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=package)] for package in PREMIUM_PACKAGES]
        + [[KeyboardButton(text=t["back"])]],
        resize_keyboard=True,
        persistent=True,
    )


# ========== Inline Keyboards helpers ==========
def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 Oʻzbekcha", callback_data="lang_uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            ],
        ]
    )


def settings_lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="settings_lang_uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="settings_lang_ru"),
            ],
        ]
    )


def age_kb(start: int = 12, end: int = 35) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for age in range(start, end + 1):
        row.append(InlineKeyboardButton(text=str(age), callback_data=f"age_{age}"))
        if len(row) == 6:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def gender_kb(lang: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t["gender_m"], callback_data="g_m"),
                InlineKeyboardButton(text=t["gender_f"], callback_data="g_f"),
                InlineKeyboardButton(text=t["gender_o"], callback_data="g_o"),
            ]
        ]
    )


# ========== Helpers ==========
async def delete_after(msg: types.Message | types.CallbackQuery | None, delay: int = AUTODELETE_DELAY):
    if msg is None:
        return
    message = msg.message if isinstance(msg, CallbackQuery) else msg
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass


async def show_panel_for_user(user_id: int):
    row = await get_user_row(user_id)
    lang = row[4] if row and row[4] in TEXTS else "uz"
    online = await get_online_count()
    panel_text = TEXTS[lang]["panel_title"].format(online=online)
    try:
        await bot.send_message(user_id, panel_text, reply_markup=main_reply_kb(lang))
    except Exception:
        pass


async def send_match_messages(user1: int, user2: int):
    me = await get_user_row(user1)
    pa = await get_user_row(user2)

    my_lang = me[4] if me and me[4] in TEXTS else "uz"
    pa_lang = pa[4] if pa and pa[4] in TEXTS else "uz"

    my_gender_for_partner = normalize_gender_for_display(me[3] if me else None, pa_lang)
    partner_gender_for_me = normalize_gender_for_display(pa[3] if pa else None, my_lang)

    try:
        await bot.send_message(
            user2,
            TEXTS[pa_lang]["matched"].format(gender=my_gender_for_partner, age=me[2] if me else "-"),
            reply_markup=chat_reply_kb(pa_lang),
        )
    except Exception:
        pass

    try:
        await bot.send_message(
            user1,
            TEXTS[my_lang]["matched"].format(gender=partner_gender_for_me, age=pa[2] if pa else "-"),
            reply_markup=chat_reply_kb(my_lang),
        )
    except Exception:
        pass


async def stop_current_chat(user_id: int, notify_partner: bool = True, show_panel: bool = True):
    partner = await get_partner(user_id)

    if user_id in CHAT_LOGS:
        log_filename = CHAT_LOGS[user_id]
        await close_chat_log(log_filename)
        CHAT_LOGS.pop(user_id, None)
        if partner:
            CHAT_LOGS.pop(partner, None)

    await delete_chat(user_id)
    await remove_waiting(user_id)

    if partner:
        await remove_chat_for_both(user_id, partner)
        if notify_partner:
            p = await get_user_row(partner)
            p_lang = p[4] if p and p[4] in TEXTS else "uz"
            try:
                await bot.send_message(partner, TEXTS[p_lang]["partner_left"], reply_markup=main_reply_kb(p_lang))
            except Exception:
                pass

    if show_panel:
        await show_panel_for_user(user_id)


async def start_search(user_id: int):
    user = await get_user_row(user_id)
    lang = user[4] if user and user[4] in TEXTS else "uz"

    if not is_registered_user(user):
        await bot.send_message(user_id, TEXTS[lang]["complete_registration"])
        return

    if await is_waiting(user_id):
        await bot.send_message(user_id, TEXTS[lang]["queue_exists"])
        return

    await delete_chat(user_id)
    await add_waiting(user_id)
    loading_msg = await bot.send_message(user_id, TEXTS[lang]["searching"])

    partner = await find_candidate(user_id)
    if partner:
        await create_chat(user_id, partner)
        await remove_waiting(user_id)
        await remove_waiting(partner)

        log_filename = await create_chat_log(user_id, partner)
        if log_filename:
            CHAT_LOGS[user_id] = log_filename
            CHAT_LOGS[partner] = log_filename

        await send_match_messages(user_id, partner)
    else:
        await show_panel_for_user(user_id)

    try:
        await loading_msg.delete()
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
        await sync_user_to_file(user_id)
        await stop_current_chat(user_id, notify_partner=True, show_panel=False)
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
        await sync_user_to_file(user_id)
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
        await sync_user_to_file(user_id)
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
        await sync_user_to_file(user_id)
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
        async with db.execute("SELECT COUNT(*) FROM waiting") as cur:
            waiting = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM chats") as cur:
            chats = (await cur.fetchone())[0]

    txt_users_count = await get_users_txt_count()

    stats_text = (
        "📊 Bot statistikasi\n\n"
        f"👥 Jami foydalanuvchilar: {total}\n"
        f"📝 users.txt dagi foydalanuvchilar: {txt_users_count}\n"
        f"💎 Premium foydalanuvchilar: {premium}\n"
        f"⛔ Bloklangan foydalanuvchilar: {banned}\n"
        f"⏳ Navbatdagilar: {waiting}\n"
        f"💬 Aktiv chatlar: {chats}"
    )
    await m.answer(stats_text)


@dp.message(Command("users"))
async def show_users_list(m: Message):
    if not is_admin(m.from_user.id):
        return

    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                """
                SELECT user_id, username, language, age, gender, last_active
                FROM users
                ORDER BY COALESCE(last_active, 0) DESC
                LIMIT 10
                """
            ) as cur:
                rows = await cur.fetchall()

        if not rows:
            await m.answer("📝 Hozircha foydalanuvchilar yo'q")
            return

        text = "📝 Oxirgi 10 ta foydalanuvchi:\n\n"
        for user_id, username, language, age, gender, last_active in rows:
            dt = datetime.fromtimestamp(last_active).strftime("%Y-%m-%d %H:%M:%S") if last_active else "-"
            text += (
                f"ID: {user_id}\n"
                f"Username: @{username if username else 'NoUsername'}\n"
                f"Til: {language or '-'} | Yosh: {age or '-'} | Jins: {gender or '-'}\n"
                f"Last active: {dt}\n\n"
            )

        text += f"📊 Jami foydalanuvchilar: {await get_total_users_count()}"
        await m.answer(text)
    except Exception as e:
        logger.error("Users ro'yxatini o'qishda xato: %s", e)
        await m.answer("❌ Foydalanuvchilar ro'yxatini o'qishda xato")


@dp.message(Command("export_users"))
async def export_users_file(m: Message):
    if not is_admin(m.from_user.id):
        return

    try:
        if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
            await m.answer("❌ Foydalanuvchilar ro'yxati fayli bo'sh yoki mavjud emas")
            return

        await m.answer_document(
            FSInputFile(USERS_FILE, filename="users_list.txt"),
            caption=f"📊 Foydalanuvchilar ro'yxati\nJami: {await get_users_txt_count()} ta",
        )
    except FileNotFoundError:
        await m.answer("❌ Foydalanuvchilar ro'yxati fayli topilmadi")
    except Exception as e:
        logger.error("Faylni yuborishda xato: %s", e)
        await m.answer("❌ Faylni yuborishda xato.")


@dp.message(Command("me"))
async def cmd_me(m: Message):
    user = await get_user_row(m.from_user.id)
    if not user:
        await m.answer("Siz hali ro'yxatdan o'tmagansiz. /start bosing.")
        return

    lang = user[4] if user[4] in TEXTS else "uz"
    text = TEXTS[lang]["me_text"].format(
        user_id=user[0],
        username=f"@{user[1]}" if user[1] else "NoUsername",
        age=user[2] or "-",
        gender=normalize_gender_for_display(user[3], lang),
        language=user[4] or "-",
        premium="Ha" if user[5] else "Yo‘q" if lang == "uz" else ("Да" if user[5] else "Нет"),
        banned="Ha" if user[6] else "Yo‘q" if lang == "uz" else ("Да" if user[6] else "Нет"),
    )
    await m.answer(text)


@dp.message(Command("broadcast"))
async def cmd_broadcast(m: Message):
    if not is_admin(m.from_user.id):
        return

    parts = m.text.split(maxsplit=1)
    if len(parts) != 2:
        await m.answer("Ishlatish: /broadcast xabar")
        return

    text_to_send = parts[1]
    ok = 0
    fail = 0

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cur:
            rows = await cur.fetchall()

    for (user_id,) in rows:
        try:
            await bot.send_message(user_id, text_to_send)
            ok += 1
        except Exception:
            fail += 1

    lang = "uz"
    await m.answer(TEXTS[lang]["broadcast_done"].format(ok=ok, fail=fail))


# ========== Handlers ==========
@dp.message(Command("start"))
async def cmd_start(m: Message, state: FSMContext):
    await ensure_user(m.from_user)
    await set_last_active(m.from_user.id)
    await sync_user_to_file(m.from_user.id, m.from_user.username)

    if is_admin(m.from_user.id):
        users_count = await get_total_users_count()
        await state.clear()
        await m.answer(
            "👨‍💻 Siz admin sifatida kirdingiz!\n"
            f"📊 Jami foydalanuvchilar: {users_count}\n\n"
            "Admin buyruqlari:\n"
            "/ban <id>\n"
            "/unban <id>\n"
            "/premium <id>\n"
            "/unpremium <id>\n"
            "/stats\n"
            "/users\n"
            "/export_users\n"
            "/broadcast <xabar>"
        )

    user = await get_user_row(m.from_user.id)
    if is_registered_user(user):
        lang = user[4] if user[4] in TEXTS else "uz"
        online = await get_online_count()
        panel_text = TEXTS[lang]["panel_title"].format(online=online)
        await state.clear()
        await m.answer(TEXTS[lang]["already_registered"])
        await m.answer(panel_text, reply_markup=main_reply_kb(lang))
        return

    msg = await m.answer(TEXTS["uz"]["ask_lang"], reply_markup=lang_kb())
    await state.set_state(Register.choosing_language)
    asyncio.create_task(delete_after(msg, AUTODELETE_DELAY))


# language selection (during registration)
@dp.callback_query(Register.choosing_language, F.data.in_({"lang_uz", "lang_ru"}))
async def cb_choose_lang(c: CallbackQuery, state: FSMContext):
    lang_code = "uz" if c.data == "lang_uz" else "ru"
    await set_user_field(c.from_user.id, language=lang_code)
    await sync_user_to_file(c.from_user.id, c.from_user.username)
    try:
        await c.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await state.set_state(Register.choosing_age)
    t = TEXTS[lang_code]
    msg = await c.message.answer(t["ask_age"], reply_markup=age_kb(12, 35))
    asyncio.create_task(delete_after(msg, AUTODELETE_DELAY))
    await c.answer()


# age selection (during registration)
@dp.callback_query(Register.choosing_age, F.data.startswith("age_"))
async def cb_choose_age(c: CallbackQuery, state: FSMContext):
    try:
        age = int(c.data.split("_", 1)[1])
    except Exception:
        await c.answer()
        return
    await set_user_field(c.from_user.id, age=age)
    await sync_user_to_file(c.from_user.id, c.from_user.username)
    try:
        await c.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    user = await get_user_row(c.from_user.id)
    lang = user[4] if user and user[4] in TEXTS else "uz"
    await state.set_state(Register.choosing_gender)
    msg = await c.message.answer(TEXTS[lang]["ask_gender"], reply_markup=gender_kb(lang))
    asyncio.create_task(delete_after(msg, AUTODELETE_DELAY))
    await c.answer()


# gender selection (during registration)
@dp.callback_query(Register.choosing_gender, F.data.in_({"g_m", "g_f", "g_o"}))
async def cb_choose_gender(c: CallbackQuery, state: FSMContext):
    mapping = {"g_m": "male", "g_f": "female", "g_o": "other"}
    code = mapping.get(c.data, "other")
    await set_user_field(c.from_user.id, gender=code, registered_at=time.time())
    await sync_user_to_file(c.from_user.id, c.from_user.username)
    try:
        await c.message.edit_reply_markup(reply_markup=None)
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
    user = await get_user_row(uid)
    lang = user[4] if user and user[4] in TEXTS else "uz"

    if not is_registered_user(user):
        await m.answer(TEXTS[lang]["complete_registration"])
        return

    if await is_banned(uid) or is_temp_banned(uid):
        await m.answer(TEXTS[lang]["profanity"])
        return

    await start_search(uid)


@dp.message(F.text.in_([TEXTS["uz"]["btn_stop"], TEXTS["ru"]["btn_stop"]]))
async def handle_stop_button(m: Message):
    uid = m.from_user.id
    user = await get_user_row(uid)
    lang = user[4] if user and user[4] in TEXTS else "uz"

    await stop_current_chat(uid, notify_partner=True, show_panel=False)
    await m.answer(TEXTS[lang]["stopped"], reply_markup=main_reply_kb(lang))
    await show_panel_for_user(uid)


@dp.message(F.text.in_([TEXTS["uz"]["btn_next"], TEXTS["ru"]["btn_next"]]))
async def handle_next_button(m: Message):
    uid = m.from_user.id
    await stop_current_chat(uid, notify_partner=True, show_panel=False)
    await start_search(uid)


@dp.message(F.text.in_([TEXTS["uz"]["btn_settings"], TEXTS["ru"]["btn_settings"]]))
async def handle_settings_button(m: Message, state: FSMContext):
    await state.clear()
    lang = await get_user_lang(m.from_user.id)
    await m.answer(TEXTS[lang]["settings"], reply_markup=settings_reply_kb(lang))


@dp.message(F.text.in_([TEXTS["uz"]["btn_help"], TEXTS["ru"]["btn_help"]]))
async def handle_help_button(m: Message):
    lang = await get_user_lang(m.from_user.id)
    await m.answer(TEXTS[lang]["help_text"])


@dp.message(
    F.text.in_([TEXTS["uz"]["btn_premium"], TEXTS["ru"]["btn_premium"], "Premium", "Премиум"])
)
async def handle_premium_button(m: Message):
    lang = await get_user_lang(m.from_user.id)
    prompt = "Premium paketni tanlang:" if lang == "uz" else "Выберите Premium пакет:"
    await m.answer(prompt, reply_markup=premium_reply_kb(lang))


@dp.message(F.text.in_([TEXTS["uz"]["change_age"], TEXTS["ru"]["change_age"]]))
async def handle_change_age(m: Message, state: FSMContext):
    lang = await get_user_lang(m.from_user.id)
    await state.set_state(SettingsEdit.choosing_age)
    await m.answer(TEXTS[lang]["ask_age"], reply_markup=age_kb(12, 80))


@dp.message(F.text.in_([TEXTS["uz"]["change_gender"], TEXTS["ru"]["change_gender"]]))
async def handle_change_gender(m: Message, state: FSMContext):
    lang = await get_user_lang(m.from_user.id)
    await state.set_state(SettingsEdit.choosing_gender)
    await m.answer(TEXTS[lang]["ask_gender"], reply_markup=gender_kb(lang))


@dp.message(F.text.in_([TEXTS["uz"]["change_lang"], TEXTS["ru"]["change_lang"]]))
async def handle_change_lang(m: Message, state: FSMContext):
    lang = await get_user_lang(m.from_user.id)
    await state.set_state(SettingsEdit.choosing_language)
    await m.answer(TEXTS[lang]["choose_lang"], reply_markup=settings_lang_kb())


@dp.message(F.text.in_(PREMIUM_PACKAGES))
async def handle_premium_package(m: Message):
    lang = await get_user_lang(m.from_user.id)
    await m.answer(TEXTS[lang]["buy_contact"].format(support=SUPPORT_USERNAME), reply_markup=premium_reply_kb(lang))


@dp.message(F.text.in_([TEXTS["uz"]["back"], TEXTS["ru"]["back"]]))
async def handle_back_button(m: Message, state: FSMContext):
    await state.clear()
    lang = await get_user_lang(m.from_user.id)
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


@dp.callback_query(SettingsEdit.choosing_language, F.data.in_({"settings_lang_uz", "settings_lang_ru"}))
async def cb_change_lang(c: CallbackQuery, state: FSMContext):
    lang_code = "uz" if c.data == "settings_lang_uz" else "ru"
    await set_user_field(c.from_user.id, language=lang_code)
    await sync_user_to_file(c.from_user.id, c.from_user.username)
    await state.clear()
    try:
        await c.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await c.message.answer(TEXTS[lang_code]["changed_lang"], reply_markup=settings_reply_kb(lang_code))
    await c.answer()


@dp.callback_query(SettingsEdit.choosing_age, F.data.startswith("age_"))
async def cb_change_age(c: CallbackQuery, state: FSMContext):
    try:
        age = int(c.data.split("_", 1)[1])
    except Exception:
        await c.answer()
        return
    await set_user_field(c.from_user.id, age=age)
    await sync_user_to_file(c.from_user.id, c.from_user.username)
    await sync_user_to_file(c.from_user.id, c.from_user.username)
    await state.clear()
    try:
        await c.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    lang = await get_user_lang(c.from_user.id)
    await c.message.answer(TEXTS[lang]["age_updated"], reply_markup=settings_reply_kb(lang))
    await c.answer()


@dp.callback_query(SettingsEdit.choosing_gender, F.data.in_({"g_m", "g_f", "g_o"}))
async def cb_change_gender(c: CallbackQuery, state: FSMContext):
    mapping = {"g_m": "male", "g_f": "female", "g_o": "other"}
    code = mapping.get(c.data, "other")
    await set_user_field(c.from_user.id, gender=code)
    await sync_user_to_file(c.from_user.id, c.from_user.username)
    await state.clear()
    try:
        await c.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    lang = await get_user_lang(c.from_user.id)
    await c.message.answer(TEXTS[lang]["gender_updated"], reply_markup=settings_reply_kb(lang))
    await c.answer()


# ========== Relaying messages between partners ==========
@dp.message()
async def relay_messages(m: Message):
    if m.text and m.text.startswith("/"):
        return

    uid = m.from_user.id
    await set_last_active(uid)

    user = await get_user_row(uid)
    lang = user[4] if user and user[4] in TEXTS else "uz"

    if await is_banned(uid) or is_temp_banned(uid):
        await m.answer(TEXTS[lang]["profanity"])
        return

    if not check_rate_limit(uid):
        await m.answer(TEXTS[lang]["too_many_messages"])
        return

    partner = await get_partner(uid)
    if not partner:
        await m.answer(TEXTS[lang]["not_in_chat"], reply_markup=main_reply_kb(lang))
        return

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
        elif m.video:
            message_type = "video"
        elif m.document:
            message_type = "document"

        await save_message_to_log(log_filename, uid, message_text, message_type)

    txt = m.text or m.caption or ""
    if contains_profanity(txt):
        await m.answer(TEXTS[lang]["profanity"])
        await set_user_field(uid, banned=1)
        await sync_user_to_file(uid, m.from_user.username)
        await stop_current_chat(uid, notify_partner=True, show_panel=False)
        return

    if is_admin(uid):
        is_premium = True
    else:
        me = await get_user_row(uid)
        is_premium = bool(me and me[5])

    try:
        if m.text:
            await bot.send_message(partner, m.text)
        elif m.photo:
            if not is_premium:
                await m.reply(TEXTS[lang]["only_premium"])
                return
            await bot.send_photo(partner, m.photo[-1].file_id, caption=m.caption or "")
        elif m.sticker:
            if not is_premium:
                await m.reply(TEXTS[lang]["only_premium"])
                return
            await bot.send_sticker(partner, m.sticker.file_id)
        elif m.voice:
            if not is_premium:
                await m.reply(TEXTS[lang]["only_premium"])
                return
            await bot.send_voice(partner, m.voice.file_id)
        elif m.audio:
            if not is_premium:
                await m.reply(TEXTS[lang]["only_premium"])
                return
            await bot.send_audio(partner, m.audio.file_id)
        elif m.animation:
            if not is_premium:
                await m.reply(TEXTS[lang]["only_premium"])
                return
            await bot.send_animation(partner, m.animation.file_id)
        elif m.video_note:
            if not is_premium:
                await m.reply(TEXTS[lang]["only_premium"])
                return
            await bot.send_video_note(partner, m.video_note.file_id)
        elif m.video:
            if not is_premium:
                await m.reply(TEXTS[lang]["only_premium"])
                return
            await bot.send_video(partner, m.video.file_id, caption=m.caption or "")
        elif m.document:
            if not is_premium:
                await m.reply(TEXTS[lang]["only_premium"])
                return
            await bot.send_document(partner, m.document.file_id, caption=m.caption or "")
        else:
            await m.answer(TEXTS[lang]["unsupported"])
    except Exception as e:
        logger.exception("Forward error: %s", e)
        await m.answer("⚠️ Xato: xabar yuborilmadi.")


# ========== Startup ==========
async def on_startup():
    os.makedirs("data", exist_ok=True)
    os.makedirs("chat_logs", exist_ok=True)
    ensure_users_file_exists()

    await init_db()
    logger.info("Bot ishga tushdi. DB: %s", DB_PATH)


async def main():
    await on_startup()
    logger.info("Bot polling ni boshladi...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error("Xato: %s", e)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
