from pptxtopdf import convert #Для конвертации pptx в pdf
import telebot #Для управления ботом
from mistralai.models import OCRResponse #Для получения ответа от OCR
from pathlib import Path #Для открытия файлов
from mistralai import DocumentURLChunk, Mistral #Для инициализации самой модели
import markdown #Для преобразования разметки в html
import requests #Для отправки файлов
import os


def pdf_to_json(pdf_path):#Получаем json с информацией из pdf при помощи Mistral
    # Считываем pdf файл
    pdf_file = Path(pdf_path)
    assert pdf_file.is_file() #Проверяем, что это файл
    # Загружаем PDF файл в Mistral OCR
    uploaded_file = client.files.upload(
        file={
            "file_name": pdf_file.stem,
            "content": pdf_file.read_bytes(),
        },
        purpose="ocr",
    )
    #Получаем ссылку на загруженный файл
    signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
    #Обрабатываем файл с помощью OCR 
    pdf_response = client.ocr.process(
        document=DocumentURLChunk(document_url=signed_url.url),
        model="mistral-ocr-latest",
        include_image_base64=True,
    )
    #Конвертируем ответ в json формат
    #response_dict = json.loads(pdf_response.model_dump_json())
    return pdf_response
def replace_images_in_markdown(markdown_str: str, images_dict: dict) -> str:#Заменяет обозначения изображений в json на base64-encoded изображения
    for img_name, base64_str in images_dict.items():
        markdown_str = markdown_str.replace(
            f"![{img_name}]({img_name})", f"![{img_name}]({base64_str})"
        )
    return markdown_str
def get_combined_markdown(ocr_response: OCRResponse) -> str:#Получаем полноценный вывод
    markdowns: list[str] = []
    # Выделяем картинки на странице
    for page in ocr_response.pages:
        image_data = {}
        for img in page.images:
            image_data[img.id] = img.image_base64
        # Заменяем id изображений на них намих в кодировке base64
        markdowns.append(replace_images_in_markdown(page.markdown, image_data))

    return "\n\n".join(markdowns)
def convert_markdown_to_html(inp):
    extensions = [
        'tables',
        'pymdownx.superfences',
        'pymdownx.highlight',
        'pymdownx.arithmatex',
        'pymdownx.inlinehilite'
    ]

    extension_configs = {
        "pymdownx.highlight": {
            "linenums": True
        },
        'pymdownx.arithmatex': {
            'generic': True
        }
    }
    md = markdown.markdown(inp, extensions=extensions, extension_configs=extension_configs)
    return md
def send_file(chat_id, file):
    files = {'document': open(file, 'rb')}
    requests.post(f'{URL}{api_telegram}/sendDocument?chat_id={chat_id}', files=files)
def pdf_conv(id, curr_path, res_path): #Обработка и отправка pdf файла
    res = get_combined_markdown(pdf_to_json(curr_path))
    res = convert_markdown_to_html(res)
    res = res.replace("<img ", '<img style="display:block" ')
    with open(res_path ,'w') as new_file:
        md_ext = """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/default.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script> <script>hljs.highlightAll();</script>
        <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
        <
        \n
        """
        new_file.write(md_ext+res)
    send_file(id, res_path)

#Инициализируем модель
with open("C:/API_keys/api_mistral.txt") as source:
    api_mistral = source.readline()
client = Mistral(api_key=api_mistral)

URL = 'https://api.telegram.org/bot'
#Устанавливаем связь с ботом
with open("C:/API_keys/api_telegram.txt") as source:
    api_telegram = source.readline()
bot = telebot.TeleBot(api_telegram)

@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAENvqhn4UifnO5eou6eq_JsrjT9fNEyvQAC-l0AAlAW-EogFbdaX1UZijYE')
    bot.reply_to(message, """Привет! Это бот для конвертации презентаций в текстовый конспект
                 Боту можно отправлять файлы в формате PDF и PPTX
                 Для подробной информации смотри команду /info""")

@bot.message_handler(commands=['info'])
def info(message):
     bot.reply_to(message, "Данный бот позволяет конвертировать файлы презентаций в формате PDF и PPTX в текстовые конспекты, сохраняя структуру документа, все картинки, таблицы и формулы. Для этого используется модель Mistral OCR (подробнее с кодом можно ознакомиться по ссылке:https://github.com/DillFennel/PPTX_PDF_text_bot)")

@bot.message_handler(content_types=['document'])
def send_welcome(message):
    try:
        #Получаем объект файла
        file = bot.get_file(message.document.file_id)
        #Скачиваем файл
        downloaded_file = bot.download_file(file.file_path)
        #Записываем файл
        res_path = 'C:/Users/julea.DESKTOP-14BO1U3/OneDrive/Рабочий стол/Курсовая/PPTX_PDF_text_bot/data/user/'+str(message.chat.id)+'_res.html'
        #Считываем тип файла
        mime_type = message.document.mime_type
        match mime_type:
            case "application/pdf": #Формат PDF
                curr_path = 'data/user/'+str(message.chat.id)+'_download.pdf'
                with open(curr_path,'wb') as new_file:
                    new_file.write(downloaded_file)
                pdf_conv(message.chat.id, curr_path, res_path)
                bot.reply_to(message, "Работа с pdf файлом выполнена")
            case "application/vnd.openxmlformats-officedocument.presentationml.presentation": #Формат PPTX
                path_pptx = 'data/user/'+str(message.chat.id)+'_download.pptx'
                path_pdf = 'data/user/'+str(message.chat.id)+'_download.pdf'
                with open(path_pptx,'wb') as new_file:
                    new_file.write(downloaded_file)
                if os.path.exists(path_pdf):
                    # Удаляем файл
                    os.remove(path_pdf)
                #Конвертируем файл в PDF
                convert(path_pptx, path_pdf)
                pdf_conv(message.chat.id, path_pdf, res_path)
                bot.reply_to(message, "Работа с pptx файлом выполнена")
            case _: #Другой формат
                bot.reply_to(message, "Такой формат не поддерживается")
    except:
        bot.reply_to(message, "Возникла ошибка")
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAENvp5n4Uc-s-5qUy8NBxKjPu0w_xQ7HgACOFoAAt_O-EpiJOIYOK5tdDYE')

@bot.message_handler(func=lambda message:True)
def echo_all(message):
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAENwZ5n4Z5EniqOQsUlqr1-tGHDZ11mygACa1wAAuvM-EqDZD8iaJG5YjYE')
    bot.send_message(message.chat.id, "<em><u>Бип буп бип бип буп</u></em>", parse_mode='html')

# Запуск бота
bot.infinity_polling()