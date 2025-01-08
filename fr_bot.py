# библиотека для  взаимодействия с операционной системой 
import os 
# библиотека для регулярных выражений
import re 
# библиотека Telegram Bot API
import telebot
from telebot import custom_filters
# библиотека для распознования речи
import speech_recognition as sr
#  библиотека для вывода логов событий
import logging
# библиотека для работы с файлом .env в которой содержится TOKEN бота
from dotenv import load_dotenv, dotenv_values


"""Подключение логирования и загрузка данных из файла .env """
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
load_dotenv()
config = dotenv_values('.env')
print(config.get('TOKEN'))
bot = telebot.TeleBot(config.get('TOKEN'), parse_mode=None)



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
    
    formatted_transcriptions = "    ".join(transcriptions) 
    logging.info(f"Найденные транскрипции:{formatted_transcriptions}")#вывод транскрипции в логи
    return "\n".join(transcriptions) if transcriptions else "Транскрипция не найденена в словаре" #ответ пользователю если слово не нашли в словаре

"""Непосредственно блок с командами Telegram бота"""

@bot.message_handler(commands=['start'])
def start_message(message):
    """Функция запуска бота. Отправляет приветственное сообщение и логирует действие пользователя."""
    bot.send_message(message.chat.id, "Привествую, я - Le Petit Assistant. Я могу распознавать и транскрибировать французскую речь! Отправьте мне аудиозапись в формате WAV.")
    logging.info(f"Пользователь {message.from_user.username} активировал бота") #отслеживание запуска бота через логи


@bot.message_handler(text=['Привет','Здравствуйте', 'привет','здравствуйте', 'ghbdtn', 'ПРИВЕТ', 'ЗДРАВСТВУЙТЕ', 'Bonjour', 'bonjour'])
def text_filter(message):
    """Функция приветсвия, которая реагирует на определенные текстовые сообщения с помощью фильтра"""
    bot.send_message(message.chat.id, "Bonjour, {name}!".format(name=message.from_user.first_name)) #отправление приветственного сообщения пользователю
    logging.info(f"Пользователь {message.from_user.username} поздоровался с ботом")


@bot.message_handler(text=['пока','ПОКА', 'Пока','До свидания', 'до свидания', 'прощай', 'Прощай'])
def text_filter(message):
    """Функция прощания, которая реагирует на определенные текстовые сообщения с помощью фильтра"""
    bot.send_message(message.chat.id, "Au revoir, {name}, был рад помочь!".format(name=message.from_user.first_name)) #отправление завершительного сообщения пользователю
    logging.info(f"Пользователь {message.from_user.username} попрощался с ботом")

@bot.message_handler(content_types=['document']) 
def handle_document(message):
    """Функция обработки файла WAV, которая скачавает временный файл транскрибирует его и отправляет пользователю транскрипцию"""
    try:
        logging.info("Получен документ WAV") #лог того, что бот получил файл
        if not message.document.file_name.lower().endswith('.wav'): #проверка формата файла 
             bot.send_message(message.chat.id, "К сожалению, я могу обрабатывать только аудио файлы WAV :(")
             return #если файл отправлен некорректным форматов функция завершается
        file_info = bot.get_file(message.document.file_id) #получение информации о файле 
        input_audio_path = f"{message.document.file_id}.wav" #формируем уникальное имя для скачивания временного файла
        downloaded_file = bot.download_file(file_info.file_path) #скачиваем этот файл
        with open(input_audio_path, "wb") as new_file: #записываем в новый файл
            new_file.write(downloaded_file)
        logging.info(f"Бот получил аудиофайл: {input_audio_path}") #логирования об успешной обработке аудиофайла

        transcribed_text = audio_script(input_audio_path) #вызов фунцкии транскрибирования
        logging.info(f"Транскрибированный текст: {transcribed_text}") #логирование результата

        dictionary = load_dictionary('fr_dict.txt') #подгрузка относительного пути французского словаря 
        transcriptions = g2p_dict(transcribed_text, dictionary) #вызов функции с транскрипуией IPA 
        inf = " ~ слово имеет несколько произношений" #примечания о возможном наличии нескольких транскрипций 
        response = f"Распознанный текст:\n {transcribed_text}\n\nТранскрипции:\n{transcriptions}\n\nПримечание: {inf}" #формирование конечного ответного сообщения пользователю, если всё прошло успешно (транскрипт и транскрипция файла WAV)
        
        bot.send_message(message.chat.id, response)

    except Exception as e: #обработка ошибок при обработке аудио файла 
        logging.error(f"Ошибка обработки аудио: {e}") #логирование для отслеживания ошибки работы бота 
        bot.send_message(message.chat.id, "Произошла ошибка при обработке аудио.") #обратное сообщение об ошибке пользователю
    finally:
        if os.path.exists(input_audio_path):
            os.remove(input_audio_path) #удаление временных файлов
        logging.info("Временные файлы удалены.")

bot.add_custom_filter(custom_filters.TextMatchFilter())
bot.infinity_polling()
