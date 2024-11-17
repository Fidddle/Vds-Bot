import logging
from telegram import Update, Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler
import os
import subprocess
import sys
import time
import random

# Tek bir bot token kullanıyoruz.
bot_token = "7691753649:AAFv4nZBg5Pad8bhcZG02m-fzrelmyRIxD4"  # Buraya bot tokenınızı ekleyin
channel_username = "@KalbiTemizler"  # Kanal kullanıcı adı
non_member_message = "Kanala katılmadan botu kullanamazsınız."
bot = Bot(token=bot_token)

uploaded_files = {}
running_processes = {}
emojis = ["📩", "🎉", "🪐", "⚡️", "💢", "🧸"]  # Rastgele emojiler

# Rastgele emoji seç
def random_emoji():
    return random.choice(emojis)

# Ana Menü Butonları
def create_main_menu_markup():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("⚡ Beni Gruba Ekle ⚡", url=f"https://t.me/{bot.username}?startgroup=true")
    )
    markup.add(
        InlineKeyboardButton("💞 Komutlar", callback_data="commands"),
    )
    markup.add(
        InlineKeyboardButton("🌿 Sahibim", url="https://t.me/Berenncik"),
        InlineKeyboardButton("💱 Yardım", callback_data="help")
    )
    return markup

def create_back_markup():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🔙 Geri", callback_data="main_menu")
    )
    return markup

# Üye Kontrol Fonksiyonu
def check_membership(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    try:
        member_status = context.bot.get_chat_member(channel_username, user_id).status
        return member_status not in ['left', 'kicked']
    except Exception as e:
        update.message.reply_text('Bir hata oluştu: ' + str(e))
        return False

# /start Komutu
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name

    if not check_membership(update, context):
        keyboard = [[InlineKeyboardButton("Kanala Katıl", url=f'https://t.me/{channel_username.strip("@")}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(non_member_message, reply_markup=reply_markup)
        return

    welcome_message = (
        f"🌟 Merhaba {user_name} \n\n"
        "🐥 Ben çok gelişmiş bir Telegram python VDS botuyum! \n\n"
        "🎯 Bana bir dosya atın o dosyayı anında hatasız çalıştırırım! \n\n"
        "🎉 Diğer komutlarım ve destek için aşağıdaki butonları kullanabilirsiniz!"
    )
    markup = create_main_menu_markup()
    update.message.reply_text(welcome_message, reply_markup=markup)

# Dosya İşleme
def handle_document(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    document = update.message.document
    file_name = document.file_name
    file_id = document.file_id

    if chat_id not in uploaded_files:
        uploaded_files[chat_id] = []
    uploaded_files[chat_id].append(file_name)

    file_path = context.bot.get_file(file_id).file_path
    local_file_path = os.path.join(os.getcwd(), file_name)
    downloaded_file = context.bot.download_file(file_path)

    with open(local_file_path, 'wb') as f:
        f.write(downloaded_file)

    process = subprocess.Popen(['python', local_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    running_processes[file_name] = process
    update.message.reply_text(f"🌟 {file_name} başarıyla çalıştırıldı!")

# /dosyalar Komutu
def list_files(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id in uploaded_files and uploaded_files[chat_id]:
        files_list = "\n".join([f"- {file}" for file in uploaded_files[chat_id]])
        files_message = f"💫 İşte Gönderdiğiniz Dosyalar  ! \n\n{files_list}"
    else:
        files_message = "🛰 Hiç dosya yüklemediniz."
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("🎀 Kurucu", url="t.me/Berenncik")]])
    context.bot.send_message(chat_id, files_message, reply_markup=markup)

# /iptal Komutu
def cancel_file(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    command_parts = update.message.text.split(maxsplit=1)

    if len(command_parts) < 2:
        update.message.reply_text("💢 Lütfen iptal etmek istediğiniz dosya adını belirtin.")
        return

    file_name = command_parts[1].strip()
    if file_name in running_processes:
        process = running_processes[file_name]
        process.terminate()
        process.wait()
        del running_processes[file_name]
        update.message.reply_text(f"💢 Dosya '{file_name}' çalışması iptal edildi.")
    else:
        update.message.reply_text(f"💢 Dosya '{file_name}' çalışmıyor veya bulunamadı.")

# /beren pip install Komutu
def install_pip_package(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    command_parts = update.message.text.split(maxsplit=3)

    if len(command_parts) < 4:
        update.message.reply_text(f"{random_emoji()} Lütfen '/beren pip install (pip ismi)' şeklinde bir komut girin.")
        return

    package_name = command_parts[3].strip()

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "show", package_name])
        update.message.reply_text(f"💱 {package_name} zaten yüklü!")
    except subprocess.CalledProcessError:
        waiting_message = update.message.reply_text(f" 🔃 Lütfen Bekleyin {package_name} yükleniyor.")
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "install", package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                context.bot.edit_message_text(f"{random_emoji()} {package_name} başarıyla yüklendi!", chat_id, waiting_message.message_id)
            else:
                context.bot.edit_message_text(f"🔎 Böyle Bir pip Bulunamadı!", chat_id, waiting_message.message_id)
        except subprocess.CalledProcessError as e:
            context.bot.edit_message_text(f"Hata: {e}", chat_id, waiting_message.message_id)

# Bot Başlatma
def main():
    updater = Updater(token=bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("dosyalar", list_files))
    dp.add_handler(CommandHandler("iptal", cancel_file))
    dp.add_handler(CommandHandler("beren", install_pip_package))
    dp.add_handler(MessageHandler(Filters.document, handle_document))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
