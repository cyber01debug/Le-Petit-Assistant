# библиотека для  взаимодействия с операционной системой 
import os 
# библиотека Telegram Bot API
import telebot
from telebot import custom_filters
#  библиотека для вывода логов событий
import logging
# библиотека для работы с файлом .env в которой содержится TOKEN бота
from dotenv import load_dotenv, dotenv_values
# привящка файла с функциями
import functions


"""Подключение логирования и загрузка данных из файла .env """
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
load_dotenv()
config = dotenv_values('.env')
print(config.get('TOKEN'))
bot = telebot.TeleBot(config.get('TOKEN'), parse_mode=None)


"""Непосредственно блок с командами Telegram бота"""

@bot.message_handler(commands=['start'])
def start_message(message):
    """Функция запуска бота. Отправляет приветственное сообщение и логирует действие пользователя."""
    bot.send_message(message.chat.id, "Привествую, я - Le Petit Assistant. Я могу распознавать и транскрибировать французскую речь! Отправьте мне аудиозапись в формате WAV.")
    logging.info(f"Пользователь {message.from_user.username} активировал бота") #отслеживание запуска бота через логи


@bot.message_handler(func=lambda message: message.text and message.text.lower() in ['привет', 'здравствуйте', 'ghbdtn', 'bonjour']) #приведение к нижнему регистру входного сообщения пользователя
def text_filter(message):
    """Функция приветсвия, которая реагирует на определенные текстовые сообщения с помощью фильтра"""
    bot.send_message(message.chat.id, "Bonjour, {name}!".format(name=message.from_user.first_name)) #отправление приветственного сообщения пользователю
    logging.info(f"Пользователь {message.from_user.username} поздоровался с ботом")


@bot.message_handler(func=lambda message: message.text and message.text.lower() in ['пока', 'прощай', 'до свидания', 'gjrf']) 
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

        transcribed_text = functions.audio_script(input_audio_path) #вызов фунцкии транскрибирования
        logging.info(f"Транскрибированный текст: {transcribed_text}") #логирование результата

        dictionary = functions.load_dictionary('fr_dict.txt') #подгрузка относительного пути французского словаря 
        transcriptions = functions.g2p_dict(transcribed_text, dictionary) #вызов функции с транскрипуией IPA 
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
