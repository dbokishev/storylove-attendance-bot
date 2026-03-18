import os
import json
import logging
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import gspread
from google.oauth2.service_account import Credentials

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TIMEZONE = pytz.timezone('Asia/Almaty')
WORK_START_TIME = datetime.strptime("11:00", "%H:%M").time()

def init_google_sheets():
    """Инициализация подключения к Google Sheets"""
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]

        creds_json = os.getenv('GOOGLE_CREDENTIALS')

        if creds_json:
            creds_dict = json.loads(creds_json)
            creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        else:
            creds = Credentials.from_service_account_file(
                'credentials.json',
                scopes=scope
            )

        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(os.getenv('SPREADSHEET_ID'))

        return spreadsheet
    except Exception as e:
        logger.error(f"Ошибка при подключении к Google Sheets: {e}")
        return None

spreadsheet = None

def get_current_datetime():
    """Получить текущие дату и время в нужном часовом поясе"""
    return datetime.now(TIMEZONE)

def get_user_info(update: Update):
    """Получить информацию о пользователе"""
    user = update.effective_user
    return {
        'user_id': user.id,
        'name': user.first_name or user.username or 'Unknown',
        'username': user.username or ''
    }

def ensure_user_exists(user_info):
    """Добавить пользователя в таблицу Users, если его там нет"""
    try:
        users_sheet = spreadsheet.worksheet('Users')

        cell = users_sheet.find(str(user_info['user_id']), in_column=1)

        if not cell:
            users_sheet.append_row([
                user_info['user_id'],
                user_info['name'],
                user_info['username']
            ])
            logger.info(f"Добавлен новый пользователь: {user_info['name']}")
    except Exception as e:
        logger.error(f"Ошибка при добавлении пользователя: {e}")

def get_today_records(user_id):
    """Получить записи пользователя за сегодня"""
    try:
        logs_sheet = spreadsheet.worksheet('Logs')
        today = get_current_datetime().strftime('%Y-%m-%d')

        records = logs_sheet.get_all_records()

        today_records = [
            r for r in records
            if str(r.get('user_id')) == str(user_id) and r.get('date') == today
        ]

        return today_records
    except Exception as e:
        logger.error(f"Ошибка при получении записей: {e}")
        return []

def has_check_in_today(user_id):
    """Проверить, есть ли уже отметка прихода сегодня"""
    records = get_today_records(user_id)
    return any(r.get('action') == 'check-in' for r in records)

def has_check_out_today(user_id):
    """Проверить, есть ли уже отметка ухода сегодня"""
    records = get_today_records(user_id)
    return any(r.get('action') == 'check-out' for r in records)

def add_log_entry(user_info, action):
    """Добавить запись в таблицу Logs"""
    try:
        logs_sheet = spreadsheet.worksheet('Logs')

        now = get_current_datetime()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')

        check_in = time_str if action == 'check-in' else ''
        check_out = time_str if action == 'check-out' else ''

        logs_sheet.append_row([
            date_str,
            user_info['user_id'],
            user_info['name'],
            check_in,
            check_out,
            time_str,
            action
        ])

        logger.info(f"Добавлена запись: {user_info['name']} - {action} в {time_str}")
        return True, time_str
    except Exception as e:
        logger.error(f"Ошибка при добавлении записи: {e}")
        return False, None

def get_keyboard():
    """Создать клавиатуру с кнопками"""
    keyboard = [
        [KeyboardButton("✅ Я пришел")],
        [KeyboardButton("🚪 Я ушел")],
        [KeyboardButton("📊 Моя статистика")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_info = get_user_info(update)

    ensure_user_exists(user_info)

    welcome_message = (
        f"Привет, {user_info['name']}! 👋\n\n"
        "Я помогу тебе отмечать рабочее время.\n\n"
        "Используй кнопки ниже:\n"
        "✅ Я пришел - отметить приход\n"
        "🚪 Я ушел - отметить уход\n"
        "📊 Моя статистика - посмотреть свои отметки"
    )

    await update.message.reply_text(
        welcome_message,
        reply_markup=get_keyboard()
    )

async def handle_check_in(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отметки прихода"""
    user_info = get_user_info(update)

    if has_check_in_today(user_info['user_id']):
        await update.message.reply_text(
            "❌ Ты уже отметил приход сегодня!",
            reply_markup=get_keyboard()
        )
        return

    success, time_str = add_log_entry(user_info, 'check-in')

    if success:
        current_time = get_current_datetime().time()
        late_emoji = "⏰" if current_time > WORK_START_TIME else "✅"

        message = f"{late_emoji} Отметка прихода зафиксирована в {time_str[:5]}"

        if current_time > WORK_START_TIME:
            message += "\n\n⚠️ Ты опоздал! Начало работы в 11:00"

        await update.message.reply_text(message, reply_markup=get_keyboard())
    else:
        await update.message.reply_text(
            "❌ Ошибка при записи. Попробуй позже.",
            reply_markup=get_keyboard()
        )

async def handle_check_out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отметки ухода"""
    user_info = get_user_info(update)

    if not has_check_in_today(user_info['user_id']):
        await update.message.reply_text(
            "❌ Сначала отметь приход!",
            reply_markup=get_keyboard()
        )
        return

    if has_check_out_today(user_info['user_id']):
        await update.message.reply_text(
            "❌ Ты уже отметил уход сегодня!",
            reply_markup=get_keyboard()
        )
        return

    success, time_str = add_log_entry(user_info, 'check-out')

    if success:
        await update.message.reply_text(
            f"🚪 Отметка ухода зафиксирована в {time_str[:5]}\n\n"
            "Хорошего вечера! 👋",
            reply_markup=get_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Ошибка при записи. Попробуй позже.",
            reply_markup=get_keyboard()
        )

async def handle_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику пользователя"""
    user_info = get_user_info(update)
    records = get_today_records(user_info['user_id'])

    if not records:
        await update.message.reply_text(
            "📊 У тебя пока нет отметок сегодня.",
            reply_markup=get_keyboard()
        )
        return

    message = "📊 Твои отметки сегодня:\n\n"

    check_in_time = None
    check_out_time = None

    for record in records:
        if record.get('action') == 'check-in':
            check_in_time = record.get('check_in') or record.get('raw_timestamp')
            message += f"✅ Пришел: {check_in_time[:5]}\n"
        elif record.get('action') == 'check-out':
            check_out_time = record.get('check_out') or record.get('raw_timestamp')
            message += f"🚪 Ушел: {check_out_time[:5]}\n"

    if check_in_time and check_out_time:
        try:
            check_in_dt = datetime.strptime(check_in_time, '%H:%M:%S')
            check_out_dt = datetime.strptime(check_out_time, '%H:%M:%S')
            worked = check_out_dt - check_in_dt
            hours = worked.seconds // 3600
            minutes = (worked.seconds % 3600) // 60
            message += f"\n⏱ Отработано: {hours}ч {minutes}мин"
        except:
            pass

    await update.message.reply_text(message, reply_markup=get_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    text = update.message.text

    if text == "✅ Я пришел":
        await handle_check_in(update, context)
    elif text == "🚪 Я ушел":
        await handle_check_out(update, context)
    elif text == "📊 Моя статистика":
        await handle_stats(update, context)
    else:
        await update.message.reply_text(
            "Используй кнопки ниже для управления ⬇️",
            reply_markup=get_keyboard()
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Запуск бота"""
    global spreadsheet

    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        return

    spreadsheet = init_google_sheets()
    if not spreadsheet:
        logger.error("Не удалось подключиться к Google Sheets!")
        return

    logger.info("Бот запущен и подключен к Google Sheets")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    import asyncio
    try:
        asyncio.run(application.run_polling(allowed_updates=Update.ALL_TYPES))
    except RuntimeError:
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
