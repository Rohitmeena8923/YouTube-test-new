import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

from downloader import get_streams, download_video
from utils import is_admin

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

logging.basicConfig(level=logging.INFO)

user_video_url = {}
stream_map_cache = {}

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_admin(user_id, ADMIN_IDS):
        return update.message.reply_text("Access Denied. Admins only.")
    update.message.reply_text("Send a YouTube URL (video or playlist).")

def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_admin(user_id, ADMIN_IDS):
        return update.message.reply_text("Admins only.")

    url = update.message.text.strip()
    update.message.reply_text("Fetching qualities...")

    buttons, stream_map = get_streams(url)
    user_video_url[user_id] = url
    stream_map_cache[user_id] = stream_map

    update.message.reply_text("Choose quality:", reply_markup=InlineKeyboardMarkup(buttons))

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()

    itag = query.data
    url = user_video_url.get(user_id)
    stream_map = stream_map_cache.get(user_id)

    if not url or itag not in stream_map:
        return query.edit_message_text("Something went wrong. Try again.")

    query.edit_message_text("Downloading...")

    for msg in download_video(url, itag):
        context.bot.send_message(chat_id=user_id, text=msg)

    context.bot.send_video(chat_id=user_id, video=open("video.mp4", "rb"))
    os.remove("video.mp4")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()