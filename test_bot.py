import json
import random
import time
import telebot
from telebot import types

TOKEN = '8256379069:AAEkcTIEEjfIy2D9ZL9M6weTOPlvGxuhoFY'
bot = telebot.TeleBot(TOKEN)

LINK_FILE = 'pending_links.json'
ACCOUNTS_FILE = 'accounts.json'

# ====== ФУНКЦИИ ДЛЯ ФАЙЛОВ ======
def load_json(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def save_link_code(user_id, code):
    data = load_json(LINK_FILE)
    data[str(user_id)] = {"code": code, "ts": int(time.time())}
    save_json(LINK_FILE, data)

def link_account_to_username(user_id, username):
    data = load_json(ACCOUNTS_FILE)
    data[str(user_id)] = {"username": username, "2fa": False, "blocked": False}
    save_json(ACCOUNTS_FILE, data)

def is_user_linked(user_id):
    data = load_json(ACCOUNTS_FILE)
    return str(user_id) in data

# ====== МЕНЮ ======
def basic_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('🆘 Помощь', '🔗 Привязать аккаунт')
    return markup

def full_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('👤 Мой аккаунт', '🔐 Включить 2FA')
    markup.row('🔑 Новый пароль', '👟 Кикнуть себя')
    markup.row('⛔ Заблокировать аккаунт', '❌ Отвязать аккаунт')
    markup.row('🆔 Показать user ID')
    return markup

# ====== ОБРАБОТЧИКИ КОМАНД ======
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    if is_user_linked(user_id):
        bot.send_message(
            message.chat.id,
            f"👋 Привет, {message.from_user.first_name}!\nДобро пожаловать обратно!",
            reply_markup=full_menu()
        )
    else:
        bot.send_message(
            message.chat.id,
            f"👋 Привет, {message.from_user.first_name}!\nЧтобы начать, привяжите аккаунт.",
            reply_markup=basic_menu()
        )

# ====== ОСНОВНЫЕ КОМАНДЫ ======
@bot.message_handler(func=lambda m: m.text == '🆘 Помощь')
def help_cmd(message):
    bot.send_message(message.chat.id, "📋 Доступные команды:\n- Привязать аккаунт\n- Мой аккаунт\n- Включить 2FA и т.д.")

@bot.message_handler(func=lambda m: m.text == '🔗 Привязать аккаунт')
def link_cmd(message):
    user_id = message.from_user.id
    code = random.randint(100000, 999999)
    save_link_code(user_id, code)
    bot.send_message(message.chat.id, f"🔐 Ваш код привязки: *{code}*\nВведите его в Minecraft: `/link {code}`", parse_mode='Markdown')

@bot.message_handler(commands=['link'])
def confirm_link(message):
    user_id = str(message.from_user.id)
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "⚠️ Использование: /link <код>")
        return

    code = parts[1]
    pending = load_json(LINK_FILE)
    if user_id in pending and str(pending[user_id]["code"]) == code:
        username = f"user_{user_id}"  # можно заменить на ввод ника
        link_account_to_username(user_id, username)
        del pending[user_id]
        save_json(LINK_FILE, pending)
        bot.send_message(message.chat.id, f"✅ Аккаунт {username} привязан!", reply_markup=full_menu())
    else:
        bot.send_message(message.chat.id, "❌ Неверный или просроченный код.")

# Остальные команды (если привязан)
@bot.message_handler(func=lambda m: m.text == '👤 Мой аккаунт')
def my_account(message):
    user_id = str(message.from_user.id)
    data = load_json(ACCOUNTS_FILE)
    if user_id in data:
        acc = data[user_id]
        bot.send_message(message.chat.id, f"👤 Ник: {acc['username']}\n2FA: {'✅' if acc['2fa'] else '❌'}\nБлок: {'⛔' if acc['blocked'] else '✅'}")
    else:
        bot.send_message(message.chat.id, "❗ Аккаунт не найден.")

@bot.message_handler(func=lambda m: m.text == '🔐 Включить 2FA')
def enable_2fa(message):
    user_id = str(message.from_user.id)
    data = load_json(ACCOUNTS_FILE)
    if user_id in data:
        data[user_id]['2fa'] = True
        save_json(ACCOUNTS_FILE, data)
        bot.send_message(message.chat.id, "🔐 2FA включена.")
    else:
        bot.send_message(message.chat.id, "❗ Привяжите аккаунт.")

@bot.message_handler(func=lambda m: m.text == '🔑 Новый пароль')
def new_pass(message):
    password = ''.join(random.choices('abcdefghjkmnpqrstuvwxyz23456789', k=8))
    bot.send_message(message.chat.id, f"🔑 Новый пароль: `{password}`", parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == '👟 Кикнуть себя')
def kick_self(message):
    bot.send_message(message.chat.id, "👟 Вы были кикнуты (реализуй на сервере Minecraft).")

@bot.message_handler(func=lambda m: m.text == '⛔ Заблокировать аккаунт')
def block_account(message):
    user_id = str(message.from_user.id)
    data = load_json(ACCOUNTS_FILE)
    if user_id in data:
        data[user_id]['blocked'] = True
        save_json(ACCOUNTS_FILE, data)
        bot.send_message(message.chat.id, "⛔ Аккаунт заблокирован.")
    else:
        bot.send_message(message.chat.id, "❗ Привяжите аккаунт.")

@bot.message_handler(func=lambda m: m.text == '❌ Отвязать аккаунт')
def unlink(message):
    user_id = str(message.from_user.id)
    data = load_json(ACCOUNTS_FILE)
    if user_id in data:
        del data[user_id]
        save_json(ACCOUNTS_FILE, data)
        bot.send_message(message.chat.id, "🗑 Аккаунт отвязан.", reply_markup=basic_menu())
    else:
        bot.send_message(message.chat.id, "❗ Аккаунт не найден.")

@bot.message_handler(func=lambda m: m.text == '🆔 Показать user ID')
def show_id(message):
    bot.send_message(message.chat.id, f"🆔 Ваш Telegram ID: {message.from_user.id}")

# ====== Запуск бота ======
bot.infinity_polling()
