#  библиотека для вывода логов событий
import logging 
# библиотека для распознования речи
import speech_recognition as sr
# библиотека для регулярных выражений
import re 

'''Блок функций для корректной работы бота'''

def load_dictionary(filepath):
    """Загружает словарь из файла fr_dict.txt, где каждая строка состоит из "слово | транскрипция" (IPA)"""
    dictionary = {} #создаем словарь для хранения слова и его транскрипции 
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip() #очистка от лишнего в начале и конце строки
            if not line: #проверка на пустоту строки если такие есть пропускаем
                continue
            parts = line.split(' | ') #так как в нашем словаре разделитель " | " делим по нему на две части (слово транскрипция)
            if len(parts) == 2:
                word, transcription = parts
                dictionary[word.strip()] = transcription.strip() #добавляем слово и его транскрипцию в словарь
    return dictionary #возвращаем результат со словарём

def audio_script(audio_file_path):
    """Данная функция распознает аудио файл c помощью SpeechRecognotion и ранскрибирует его на французском языке"""
    recognize = sr.Recognizer() #вводим переменуб с распознователем речи от Google
    try:
        with sr.AudioFile(audio_file_path) as source: #чтение аудио файла из сообщения
            audio = recognize.record(source)
        text = recognize.recognize_google(audio, language="fr-FR") #разпознаем речь указав язык распознования fr (французский)
        return text #возвращаем транскрипт аудио файла 
    except sr.UnknownValueError: #обработка ошибки 
        logging.error(f"Не удалось распознать речь") #вывод лога ошибки с причиной
        return "Не удалось распознать речь" #возвратное сообщение к пользователю 

def g2p_dict(text, dictionary):
    """Находит транскрипции для слов в тексте."""
    words = re.findall(r'\b\w+\b', text) #регулярное выраженние для нахождения слов в получившемся транскрипте
    transcriptions = [] #список для хранения транскрипций
    for word in words:
        if word in dictionary: #итерация с поиском подходящего слова в словаре 
            transcriptions.append(f"{word}: {dictionary[word]}") #подобранная транскрипция добавляется в список вместе со словом
        else:
            transcriptions.append(f"{word}: Слово не найдено в словаре") #добавление условия если в словаре не нашлось нужное слово
    
    formatted_transcriptions = "    ".join(transcriptions) 
    logging.info(f"Найденные транскрипции {formatted_transcriptions}") #вывод транскрипции в логи
    return "\n".join(transcriptions)  