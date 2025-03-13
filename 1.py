import PyPDF2

# Открытие PDF-файла

with open('ex.pdf', 'rb') as file:

# Создание объекта для работы с PDF

    pdf_reader = PyPDF2.PdfReader(file)

# Получение количества страниц в документе

    num_pages = len(pdf_reader.pages)

# Извлечение текста со всех страниц

    text = ""

    for page_num in range(num_pages):

        page = pdf_reader.pages[page_num]

        text += page.extract_text()

# Вывод извлеченного текста

print(text)