#Beren Nami Deger Fiddle
import telebot
import os
import subprocess
import sys
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import time
import random

API_KEY = '7691753649:AAFv4nZBg5Pad8bhcZG02m-fzrelmyRIxD4'  # API anahtarınızı buraya ekleyin
bot = telebot.TeleBot(API_KEY)
uploaded_files = {}
running_processes = {}
emojis = ["📩", "🎉", "🪐", "⚡️", "💢", "🧸"]  # random emojiler

def random_emoji():
    return random.choice(emojis)

def create_main_menu_markup():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("⚡Beni Gruba Ekle ⚡", url="https://t.me/BerenFreeVdsBot?startgroup=true")
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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name

    bot.send_message(chat_id, "🌺")
    time.sleep(2)
    welcome_message = (
        f"🌟 Merhaba {user_name} \n\n"
        "🐥 Ben çok gelişmiş bir Telegram python VDS botuyum! \n\n"
        "🎯 Bana bir dosya atın o dosyayı anında hatasız çalıştırırım! \n\n"
        "🎉 Diğer komutlarım ve destek için aşağıdaki butonları kullanabilirsiniz!"
    )

    markup = create_main_menu_markup()
    bot.send_message(chat_id, welcome_message, reply_markup=markup)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id
    file_id = message.document.file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = bot.download_file(file_path)

    file_name = message.document.file_name
    local_file_path = os.path.join(os.getcwd(), file_name)

    if chat_id not in uploaded_files:
        uploaded_files[chat_id] = []

    uploaded_files[chat_id].append(file_name)

    waiting_message = bot.send_message(chat_id, "🔃 Lütfen Bekleyin. !")
    try:
        with open(local_file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # User bot dosyası kontrolü
        with open(local_file_path, 'r') as file:
            first_line = file.readline().strip()
        
        if "from telethon" in first_line:
            # User Bot dosyası
            process = subprocess.Popen(['python', local_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            running_processes[file_name] = process
            bot.edit_message_text(f" 🐉 {file_name} Dosyası Artık Hatasız bir şekilde çalışıyor.", chat_id, waiting_message.message_id)
        else:
            # Normal Python dosyası
            process = subprocess.Popen(['python', local_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            running_processes[file_name] = process
            bot.edit_message_text(f" 🌟 {file_name} Dosyası Artık Hatasız bir şekilde çalışıyor.", chat_id, waiting_message.message_id)

    except subprocess.CalledProcessError as e:
        if "No module named" in str(e.stderr):
            missing_module = str(e.stderr).split("No module named")[1].strip().strip("'")
            bot.edit_message_text(f" ☃️ '{missing_module}' eksik lütfen '/beren pip install {missing_module}' komutu ile yükleyin.", chat_id, waiting_message.message_id)
        else:
            bot.edit_message_text(f"Hata: {e}", chat_id, waiting_message.message_id)

@bot.message_handler(commands=['beren'])
def install_pip_package(message):
    chat_id = message.chat.id
    command_parts = message.text.split(maxsplit=3)

    if len(command_parts) < 4:
        bot.send_message(chat_id, f"{random_emoji()} Lütfen '/beren pip install (pip ismi)' şeklinde bir komut girin.")
        return

    axse_command = command_parts[1].strip()
    pip_command = command_parts[2].strip()
    package_name = command_parts[3].strip()

    if axse_command.lower() == 'pip' and pip_command.lower() == 'install':
        # Paket zaten yüklü mü kontrol et
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "show", package_name])
            bot.send_message(chat_id, f"💱 {package_name} zaten yüklü!")
        except subprocess.CalledProcessError:
            waiting_message = bot.send_message(chat_id, f" 🔃 Lütfen Bekleyin {package_name} yükleniyor.")
            try:
                result = subprocess.run([sys.executable, "-m", "pip", "install", package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode == 0:
                    bot.edit_message_text(f"{random_emoji()} {package_name} başarıyla yüklendi!", chat_id, waiting_message.message_id)
                else:
                    bot.edit_message_text(f"🔎 Böyle Bir pip Bulunamadı!", chat_id, waiting_message.message_id)
            except subprocess.CalledProcessError as e:
                bot.edit_message_text(f"Hata: {e}", chat_id, waiting_message.message_id)
    else:
        bot.send_message(chat_id, f"{random_emoji()} Geçersiz komut. Lütfen '/beren pip install (pip ismi)' şeklinde bir komut girin.")

@bot.message_handler(commands=['dosyalar'])
def list_files(message):
    chat_id = message.chat.id

    if chat_id in uploaded_files and uploaded_files[chat_id]:
        files_list = "\n".join([f"- {file}" for file in uploaded_files[chat_id]])
        files_message = f"💫 İşte Gönderdiğiniz Dosyalar  ! \n\n{files_list}"
    else:
        files_message = "🛰 Hiç dosya yüklemediniz."

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🎀 Kurucu", url="t.me/Berenncik")
    )
    bot.send_message(chat_id, files_message, reply_markup=markup)

@bot.message_handler(commands=['iptal'])
def cancel_file(message):
    chat_id = message.chat.id
    command_parts = message.text.split(maxsplit=1)

    if len(command_parts) < 2:
        bot.send_message(chat_id, "💢 Lütfen iptal etmek istediğiniz dosya adını belirtin.")
        return

    file_name = command_parts[1].strip()

    if file_name in running_processes:
        process = running_processes[file_name]
        process.terminate()
        process.wait()
        del running_processes[file_name]
        bot.send_message(chat_id, f"💢 Dosya  {file_name} çalışması iptal edildi.")
    else:
        bot.send_message(chat_id, f"💢 Dosya '{file_name}' çalışmıyor veya bulunamadı.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    if call.data == "commands":
        commands_message = (
            "💕 Komutlar : \n\n"
            "- /dosyalar: Yüklediğiniz tüm dosyaları bu komutu kullanarak bulabilirsiniz.\n\n"
            "- /iptal (yüklediğiniz dosya adı): Bu komut ile çalıştırdığınız dosyaları iptal edebilirsiniz.\n\n"
            "- /beren pip install (pip ismi): Eksik pip paketlerini yüklemek için bu komutu kullanabilirsiniz."
        )
        markup = create_back_markup()
        bot.edit_message_text(commands_message, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "help":
        help_message = (
            "👾 Beni kullanmak için sadece bir dosya göndermeniz yeterlidir bu dosyayı otomatikman çalıştırırım ve eğer iptal etmek için /iptal (dosya adı) bu komutu kullanabilirsiniz!\n\n"
            "Eksik bir pip paketi varsa, '/beren pip install (pip ismi)' komutunu kullanarak yükleyebilirsiniz."
        )
        markup = create_back_markup()
        bot.edit_message_text(help_message, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "main_menu":
        welcome_message = (
            "🌟 Merhaba\n\n"
            "🐥 Ben çok gelişmiş bir Telegram python VDS botuyum! \n\n"
            "🎯 Bana bir dosya atın o dosyayı anında hatasız çalıştırırım! \n\n"
            "🎉 Diğer komutlarım ve destek için aşağıdaki butonları kullanabilirsiniz!"
        )
        markup = create_main_menu_markup()
        bot.edit_message_text(welcome_message, call.message.chat.id, call.message.message_id, reply_markup=markup)

print('Bot aktif, iyi kullanımalar dilerim')

bot.polling(none_stop=True, timeout=60)



