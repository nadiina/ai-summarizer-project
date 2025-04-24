import asyncio
import os
import logging
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Document
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)

from libs.utils_shared import get_upload_folder, allowed_file

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не знайдено в .env файлі")

UPLOAD_FOLDER = get_upload_folder()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
API_BASE_URL = "http://localhost:5000/api/v1"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

user_files = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Chat {update.effective_chat.id}: викликано /start")
    await update.message.reply_text("👋 Надішли мені .txt файл, і я згенерую зміст або підсумок!")


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc: Document = update.message.document
    chat_id = update.effective_chat.id
    logger.info(f"Chat {chat_id}: отримано файл {doc.file_name}")

    if not allowed_file(doc.file_name):
        logger.warning(f"Chat {chat_id}: невірний формат файлу {doc.file_name}")
        await update.message.reply_text("Будь ласка, надішліть файл з розширенням .txt")
        return

    file_path = os.path.join(UPLOAD_FOLDER, doc.file_name)
    new_file = await doc.get_file()
    await new_file.download_to_drive(file_path)
    logger.info(f"Chat {chat_id}: файл збережено за шляхом {file_path}")

    user_files[chat_id] = {
        "path": file_path,
        "filename": doc.file_name
    }

    keyboard = [
        [InlineKeyboardButton("📋 Зміст", callback_data="get_contents")],
        [InlineKeyboardButton("🧠 Підсумок", callback_data="get_summary")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Що ви хочете зробити з файлом?", reply_markup=reply_markup)


async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    action = query.data
    logger.info(f"Chat {chat_id}: обрано дію {action}")

    file_info = user_files.get(chat_id)
    if not file_info:
        logger.error(f"Chat {chat_id}: файл не знайдено для дії {action}")
        await query.edit_message_text("Файл не знайдено. Надішліть його спочатку.")
        return

    await context.bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=query.message.message_id,
        reply_markup=None
    )

    processing_msg = await context.bot.send_message(chat_id=chat_id, text="⏳ Обробка файлу...")
    logger.info(f"Chat {chat_id}: відправлено повідомлення про обробку (msg_id={processing_msg.message_id})")

    await asyncio.sleep(0.2)

    try:
        with open(file_info["path"], 'rb') as f:
            files = {'file': (file_info["filename"], f, 'text/plain')}
            url = f"{API_BASE_URL}/{action}"
            logger.info(f"Chat {chat_id}: надсилаю POST на {url}")
            response = requests.post(url, files=files)
            logger.info(f"Chat {chat_id}: отримано відповідь API {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            result_key = "summary" if action == "get_summary" else "contents"
            result = data.get(result_key, "Результат порожній.")
            logger.info(f"Chat {chat_id}: успішно отримано результат для {action}")

            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=processing_msg.message_id,
                text=f"✅ Результат аналізу:\n\n{result[:4000]}"
            )
        else:
            logger.error(f"Chat {chat_id}: API повернув помилку {response.status_code} - {response.text}")
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=processing_msg.message_id,
                text=f"❌ Помилка API: {response.text}"
            )

        await context.bot.send_message(chat_id=chat_id, text="📤 Ви можете надіслати ще один .txt файл для аналізу.")

    except Exception as e:
        logger.exception(f"Chat {chat_id}: помилка під час обробки")
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=processing_msg.message_id,
            text=f"❌ Виникла помилка: {str(e)}"
        )


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(CallbackQueryHandler(handle_choice))

    logger.info("✅ Бот запущено... (polling)")
    app.run_polling()


if __name__ == '__main__':
    main()
