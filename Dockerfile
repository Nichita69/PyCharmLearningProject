# Используйте официальный образ Python как базовый
FROM python:3.10-slim

# Установите рабочую директорию в контейнере
WORKDIR /app

# Скопируйте файл requirements.txt в рабочую директорию
COPY requirements.txt ./

# Установите зависимости из файла requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Скопируйте содержимое локальной директории src в рабочую директорию контейнера
COPY . .

# Определите переменную окружения для Flask
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Укажите порт, на котором будет работать приложение
EXPOSE 5000

# Запустите приложение
CMD ["flask", "run"]
