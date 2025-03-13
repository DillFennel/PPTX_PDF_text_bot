import telebot
import random
with open("/home/julea/Курсовая/api_token.txt") as source:
    api_token = source.readline()
bot = telebot.TeleBot(api_token)

@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.reply_to(message, "Привет!")

@bot.message_handler(commands=['info'])
def send_welcome(message):
    bot.reply_to(message, message)

@bot.message_handler(content_types=['document'])
def send_welcome(message):
    file = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file.file_path)
    with open('data/user/download.pdf','wb') as new_file:
        new_file.write(downloaded_file)
    bot.reply_to(message, 'Файл скачан')

@bot.message_handler(content_types=['sticker'])
def send_welcome(message):
    bot.reply_to(message, 'Это стикер')

@bot.message_handler(regexp="кот")
def cats(message):
    rand_n = random.randint(1, 15)
    with open('data/cats/cat'+str(rand_n)+'.jpg', 'rb') as img:
        bot.send_photo(message.chat.id, img)
    with open('data/audio/audio1.ogg', 'rb') as song:
        bot.send_voice(message.chat.id, song, "<b>Нейро кот</b>", parse_mode='html')
    #bot.reply_to(message, "<b>Толстый кот</b>", parse_mode='html')

@bot.message_handler(regexp="Кактус")
def cats(message):
    with open('data/Сумерки/video0.mp4', 'rb') as video:
        bot.send_video(message.chat.id, video)

    with open('data/Сумерки/audio0.ogg', 'rb') as song:
        bot.send_voice(message.chat.id, song)

@bot.message_handler(func=lambda message:True)
def echo_all(message):
    bot.reply_to(message, "<em><u>Бип буп бип бип буп</u></em>", parse_mode='html')

bot.infinity_polling()