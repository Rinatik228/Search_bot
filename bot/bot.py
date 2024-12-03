import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from search import *
from database import *
from environs import Env

# Загрузка переменных окружения (токена) для использования с ботом
env = Env()
env.read_env()
token = env('TOKEN')

# Инициализация бота с использованием токена
bot = telebot.TeleBot(token)

# Настройки пользователя
user_settings = {}

# Главное меню с кнопками
def main_menu():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_add_text = KeyboardButton('Добавить текст') # Ктопка для добавления текста
    button_download_file = KeyboardButton('Загрузить файл') # Кнопка для загрузки файла
    button_search = KeyboardButton('Поиск') # Кнопка для поиска
    button_settings = KeyboardButton('Настройки') # Кнопка для настройки поиска
    button_replace_text = KeyboardButton('Замена текста') # Кнопка для замены текста
    button_clear_text = KeyboardButton('Очистить все текста') # Кнопка для очистки текстов
    button_history_search = KeyboardButton('История поиска') # Кнопка для вывода истории поиска 
    button__clear_history_search = KeyboardButton('Очистить историю поиска') # Кнопка дял очистки истории поиска
    markup.add(button_add_text,
                button_download_file,
                button_search,
                button_settings,
                button_replace_text,
                button_clear_text,
                button_history_search,
                button__clear_history_search)
    return markup

# Обработчик команды /start для регистрации и приветствия пользователя
@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.chat.id
    user_name = message.from_user.username
    name = message.from_user.first_name

    # Проверяем, существует ли пользователь в базе данных
    if not check_user_exists(user_id):
        # Если пользователь не существует, регистрируем его
        if not register_user(user_id, user_name, name):
            bot.send_message(user_id, "Ошибка при регистрации пользователя.")
            return
        # Инициализация настроек для нового пользователя
        user_settings[user_id] = {
            "case_sensitive": False,
            "fuzzy_search": False,
            "replace_all": True
        }
        bot.send_message(user_id, f"Добро пожаловать в поисковый бот, {name}! Выберите действие из меню ниже:", reply_markup=main_menu())
    else:
        # Если пользователь уже существует, приветствуем его
        bot.send_message(user_id, f"Привет, {name}! Выберите действие из меню ниже:", reply_markup=main_menu())

# Обработчик кнопки "Добавить текст"
@bot.message_handler(func=lambda message: message.text == 'Добавить текст')
def add_text_prompt(message):
    bot.send_message(message.chat.id, "Отправьте текст, который вы хотите добавить для анализа.")
    bot.register_next_step_handler(message, save_user_text)

def save_user_text(message): # Сохраняет текст в базу данных
    user_id = message.chat.id
    text_content = message.text
    
    # Проверяем, существует ли текст в базе данных
    existing_texts = get_user_texts(user_id)
    if text_content in existing_texts:
        bot.send_message(user_id, "Этот текст уже существует в базе данных.", reply_markup=main_menu())
        return

    # Сохранить содержимое в базу данных
    success = add_user_text(user_id, text_content)
    
    if success: # Проверка на успех добавления текста
        bot.send_message(message.chat.id, "Текст успешно добавлен.", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "Ошибка при добавлении текста. Попробуйте снова.", reply_markup=main_menu())

# Обработчик кнопки "Загрузить файл"
@bot.message_handler(func=lambda message: message.text == 'Загрузить файл')
def prompt_file_upload(message):
    bot.send_message(message.chat.id, "Пожалуйста, загрузите текстовый файл (.txt), который вы хотите добавить.")

# Обработчик загрузки файла
@bot.message_handler(content_types=['document'])
def handle_file(message):
    user_id = message.chat.id
    file_info = bot.get_file(message.document.file_id)
    file_extension = message.document.file_name.split('.')[-1].lower()
    
    if file_extension != 'txt': # Проверка типа файла
        bot.send_message(user_id, "Пожалуйста, загрузите только .txt файлы.", reply_markup=main_menu())
        return

    # Скачивание и декодирование содержимого файла
    downloaded_file = bot.download_file(file_info.file_path)
    text_content = downloaded_file.decode('utf-8')

    # Проверяем, существует ли текст в базе данных
    existing_texts = get_user_texts(user_id)
    if text_content in existing_texts:
        bot.send_message(user_id, "Этот текст уже существует в базе данных.", reply_markup=main_menu())
        return

    # Сохранить содержимое в базу данных
    success = add_user_text(user_id, text_content)
    if success: # Проверка на успех добавления текста
        bot.send_message(user_id, "Текст из файла успешно добавлен.", reply_markup=main_menu())
    else:
        bot.send_message(user_id, "Ошибка при добавлении текста из файла. Попробуйте снова.", reply_markup=main_menu())

# Обработчик кнопки "Поиск"
@bot.message_handler(func=lambda message: message.text == 'Поиск')
def search_prompt(message):
    bot.send_message(message.chat.id, "Введите слово или фразу для поиска:")
    bot.register_next_step_handler(message, search_word)

# Функция для поиска слова в сохраненных текстах пользователя
def search_word(message): 
    user_id = message.chat.id
    keyword = message.text
    texts = get_user_texts(user_id)
    settings = user_settings.get(user_id, {})

    results = []
    for text in texts:
        found_sentences = find_sentences(
            text, keyword,
            case_sensitive=settings.get("case_sensitive", False),
            fuzzy=settings.get("fuzzy_search", False)
        )
        results.extend(found_sentences)
    
    response = "\n".join(results) if results else "Ничего не найдено."
    save_search_history(user_id, keyword)  # Сохраняем историю поиска
    bot.send_message(user_id, response, reply_markup=main_menu())

# Обработчик кнопки "Настройки" для изменения конфигураций поиска
@bot.message_handler(func=lambda message: message.text == 'Настройки')
def show_settings(message):
    user_id = message.chat.id
    # Проверяем, инициализированы ли настройки
    if user_id not in user_settings:
        user_settings[user_id] = {
            "case_sensitive": False,
            "fuzzy_search": False,
            "replace_all": True
        }
    
    # Создание кнопок для изменения настроек
    markup = InlineKeyboardMarkup(row_width=2)
    case_btn = InlineKeyboardButton(f"Учитывать регистр: {'Да' if user_settings[user_id]['case_sensitive'] else 'Нет'}", callback_data="toggle_case")
    fuzzy_btn = InlineKeyboardButton(f"Неточный поиск: {'Да' if user_settings[user_id]['fuzzy_search'] else 'Нет'}", callback_data="toggle_fuzzy")
    replace_btn = InlineKeyboardButton(f"Замена всех: {'Да' if user_settings[user_id]['replace_all'] else 'Нет'}", callback_data="toggle_replace_all")

    markup.add(case_btn, fuzzy_btn, replace_btn)
    bot.send_message(message.chat.id, "Настройки поиска:", reply_markup=markup)

# Обработчик для изменения настроек через callback
@bot.callback_query_handler(func=lambda call: call.data in ["toggle_case", "toggle_fuzzy", "toggle_replace_all"])
def change_settings(call):
    user_id = call.message.chat.id
    # Логика переключения настроек
    if call.data == "toggle_case":
        current_setting = user_settings[user_id]["case_sensitive"]
        user_settings[user_id]["case_sensitive"] = not current_setting
    elif call.data == "toggle_fuzzy":
        current_setting = user_settings[user_id]["fuzzy_search"]
        user_settings[user_id]["fuzzy_search"] = not current_setting
    elif call.data == "toggle_replace_all":
        current_setting = user_settings[user_id]["replace_all"]
        user_settings[user_id]["replace_all"] = not current_setting
    
    bot.answer_callback_query(call.id, "Настройка обновлена!")
    show_settings(call.message)

# Обработчик кнопки "Очистить текст" для удаления всех текстов
@bot.message_handler(func=lambda message: message.text == 'Очистить все текста')
def clear_user_texts(message):
    user_id = message.chat.id
    # Удаление всех текстов из базы данных
    if delete_user_texts(user_id):
        bot.send_message(user_id, "Все загруженные тексты успешно удалены.", reply_markup=main_menu())
    else:
        bot.send_message(user_id, "Ошибка при удалении текстов. Попробуйте снова.", reply_markup=main_menu())

# Обработчик кнопки "История поиска"
@bot.message_handler(func=lambda message: message.text == 'История поиска')
def show_search_history(message):
    user_id = message.chat.id
    history = get_search_history(user_id)
    
    if history:
        response = "История поиска:\n" + "\n".join(history)
    else:
        response = "История поиска пуста."
    
    bot.send_message(user_id, response, reply_markup=main_menu())

# Обработчик кнопки "Очистить историю поиска"
@bot.message_handler(func=lambda message: message.text == 'Очистить историю поиска')
def clear_search_history(message):
    user_id = message.chat.id
    # Удаление истории поиска пользователя
    if clear_search_history_in_db(user_id):
        bot.send_message(user_id, "История поиска успешно очищена.", reply_markup=main_menu())
    else:
        bot.send_message(user_id, "Ошибка при очистке истории поиска. Попробуйте снова.", reply_markup=main_menu())

# Обработчик команды для замены текста. Сначала запрашивает у пользователя текст для замены.    
@bot.message_handler(func=lambda message: message.text == 'Замена текста')
def replacement_prompt(message):
    bot.send_message(message.chat.id, "Введите текст, который вы хотите заменить:")
    bot.register_next_step_handler(message, get_replacement_text)

def get_replacement_text(message):
    user_id = message.chat.id
    old_text = message.text
    bot.send_message(user_id, "Введите новый текст:")
    bot.register_next_step_handler(message, lambda msg: replace_text(user_id, old_text, msg.text))

# Выполняет замену старого текста на новый в базе данных.
def replace_text(user_id, old_text, new_text):
    texts = get_user_texts(user_id)
    settings = user_settings.get(user_id, {})
    replace_all = settings.get("replace_all", True)

    # Замена текста
    for text in texts:
        if isinstance(text, str) and isinstance(old_text, str) and old_text in text:
            if replace_all:
                new_text_content = text.replace(old_text, new_text)
            else:
                new_text_content = text.replace(old_text, new_text, 1)  # Заменить только первое вхождение
            
            # Обновляем текст в базе данных
            update_user_text(user_id, old_text, new_text)

    bot.send_message(user_id, "Замена текста выполнена.", reply_markup=main_menu())

def find_sentences(text, keyword, case_sensitive=False, fuzzy=False): 
    """
    Функция поиска предложений в тексте
    text: Исходный текст, в котором происходит поиск.
    keyword: Слово или фраза для поиска.
    case_sensitive: Если False, игнорирует регистр символов.
    fuzzy: Если True, позволяет выполнять неточный поиск.
    """
    if case_sensitive: # Если поиск чувствителен к регистру
        return [sentence for sentence in text.split('.') if keyword in sentence]
    else: # Если поиск не чувствителен к регистру
        return [sentence for sentence in text.split('.') if keyword.lower() in sentence.lower()]

# Запуск бота с использованием бесконечного поллинга
bot.infinity_polling(timeout=123, long_polling_timeout = 5)
