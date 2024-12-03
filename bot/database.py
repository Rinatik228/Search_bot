import sqlite3

# Подключение к базе данных SQLite

def get_db_connection():
    """
    Создает и возвращает новое соединение с базой данных.
    Это позволяет избежать конфликта из-за многопоточности.
    """
    return sqlite3.connect('search_bot.db', check_same_thread=False)

# Создание таблиц, если они еще не созданы
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_texts (
        user_id INTEGER,
        text_id INTEGER PRIMARY KEY AUTOINCREMENT,
        text_content TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS search_history (
        user_id INTEGER,
        search_query TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_register (
        user_id INTEGER,
        user_name TEXT,
        name TEXT
    )''')

    # Сохранение изменений и фиксация создания таблиц
    conn.commit()
    conn.close()

# Проверяет, существует ли пользователь в таблице user_register.
def check_user_exists(user_id): 
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_register WHERE user_id=?", (user_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

# Регистрирует нового пользователя, добавляя его данные в таблицу user_register.
def register_user(user_id, user_name, name): 
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_register (user_id, user_name, name) VALUES (?, ?, ?)", (user_id, user_name, name))
        conn.commit()
        conn.close()
        return True
    except Exception as e: # Обработка ошибок при добавлении данных
        print(f"Ошибка при регистрации пользователя: {e}")
        return False

# Добавляет новый текст для пользователя в таблицу user_texts.
def add_user_text(user_id, text_content): 
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_texts (user_id, text_content) VALUES (?, ?)", (user_id, text_content))
        conn.commit()
        conn.close()
        return True
    except Exception as e: # Обработка ошибок при добавлении текста
        print(f"Ошибка при сохранении текста в базу данных: {e}")
        return False

# Возвращает все тексты, сохраненные для указанного пользователя.
def get_user_texts(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT text_content FROM user_texts WHERE user_id=?", (user_id,))
    texts = [row[0] for row in cursor.fetchall() if row[0] is not None]
    conn.close()
    return texts

def update_user_text(user_id, old_text, new_text):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_texts SET text_content = ? WHERE user_id = ? AND text_content = ?", (new_text, user_id, old_text))
    conn.commit()
    conn.close()

# Удаляет все тексты, сохраненные указанным пользователем, из таблицы user_texts.
def delete_user_texts(user_id): 
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_texts WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e: # Обработка ошибок при удалении текстов
        print(f"Ошибка при удалении текстов: {e}")
        return False

# Сохраняет историю поиска для пользователя в таблице search_history.
def save_search_history(user_id, search_query): 
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO search_history (user_id, search_query) VALUES (?, ?)", (user_id, search_query))
        conn.commit()
        conn.close()
    except Exception as e: # Обработка ошибок при сохранении истории поиска
        print(f"Ошибка при сохранении истории поиска: {e}")

# Возвращает историю поиска для указанного пользователя.
def get_search_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT search_query FROM search_history WHERE user_id=?", (user_id,))
    history = [row[0] for row in cursor.fetchall()]
    conn.close()
    return history

# # Проверяет, существует ли текст с указанным text_id для указанного user_id в таблице user_texts.
# def text_exists(user_id, text_id):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT COUNT(*) FROM user_texts WHERE user_id=? AND text_id=?", (user_id, text_id))
#     text = cursor.fetchone()[0] > 0
#     conn.close()
#     return text  # Возвращает True, если текст существует

# # Добавляет нового пользователя в таблицу users.
# def add_user(user_id, username): 
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     with sqlite3.connect('search_bot.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute("INSERT INTO users (user_id, user_name) VALUES (?, ?)", (user_id, username))
#         conn.commit()
#     conn.close()

# # Проверяет, существует ли пользователь в таблице users.
# def check_if_user_exists(user_id):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     with sqlite3.connect('search_bot.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
#         exists = cursor.fetchone() is not None
#     conn.close()
#     return exists

# Очищает историю поиска для указанного пользователя.
def clear_search_history_in_db(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    with sqlite3.connect('search_bot.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM search_history WHERE user_id = ?", (user_id,))
        conn.commit()
    conn.close()
    return True