import re

def find_sentences(text, keyword, case_sensitive=False, fuzzy=False):
    """
    Функция ищет все предложения в тексте, содержащие ключевое слово.
    Возращает список предложений, содержащих искомое слово.
    Какие параметры принимает функция, прописаны ниже

    Параметры:
    - text: Текст, в котором производится поиск
    - keyword: Слово или фраза для поиска
    - case_sensitive: Учитывать ли регистр (по умолчанию False)
    - fuzzy: Неточный поиск с допуском небольших ошибок (по умолчанию False)
    """
    # Разделение текста на предложения, используя регулярное выражение
    # Регулярное выражение ищет окончания предложений ('.', '!', '?') с последующим пробелом.
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Настройка регистра
    if not case_sensitive:
        keyword = keyword.lower()
    
    # Результирующий список для хранения найденных предложений
    result = []
    
    for sentence in sentences:
        # Приведение предложения к нижнему регистру, если поиск нечувствителен к регистру
        search_sentence = sentence if case_sensitive else sentence.lower() 
        
        # Проверка наличия слова в предложении
        if fuzzy:
            # Если степень схожести ключевого слова и части предложения более 80%, то считаем совпадением
            from fuzzywuzzy import fuzz
            if fuzz.partial_ratio(keyword, search_sentence) > 80:
                result.append(sentence)
        else:
            # Если точное совпадение ключевого слова найдено в предложении, добавляем его в результат
            if keyword in search_sentence:
                result.append(sentence)
    
     # Возвращаем список предложений, которые соответствуют условиям поиска
    return result