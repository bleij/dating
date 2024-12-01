from django.db import models
from django.conf import settings
import os
from .models import User
from django.db.models.query import sync_to_async
from telegram import Update

import os

if not os.access('media', os.W_OK):
    print("Нет прав на запись в директорию media!")
else:
    print("Директория media доступна для записи!")

# Функция для регистрации
async def register(update: Update, context):
    await update.message.reply_text("Добро пожаловать! Давайте начнем с регистрации.\nВведите ваше имя:")
    context.user_data['step'] = 1


# Обработчик имени и других данных
async def handle_name(update: Update, context):
    step = context.user_data.get('step')

    if step == 1:
        context.user_data['first_name'] = update.message.text
        await update.message.reply_text("Теперь введите ваш город:")
        context.user_data['step'] = 2
    elif step == 2:
        context.user_data['city'] = update.message.text
        await update.message.reply_text("Введите ваш возраст:")
        context.user_data['step'] = 3
    elif step == 3:
        context.user_data['age'] = update.message.text
        await update.message.reply_text("Теперь выберите ваш гендер (М/Ж):")
        context.user_data['step'] = 4
    elif step == 4:
        context.user_data['gender'] = update.message.text
        await update.message.reply_text("Добавьте описание вашего профиля:")
        context.user_data['step'] = 5
    elif step == 5:
        context.user_data['description'] = update.message.text
        await update.message.reply_text("Отправьте ваше фото (только файл):")
        context.user_data['step'] = 6
    elif step == 6:
        print("Шаг 6: обработка фото")
        # Проверка, что фото было получено
        if update.message.photo:
            print(f"Получена фотография: {update.message.photo[-1]}")
            # Получаем файл с помощью update.bot.get_file()
            try:
                photo_file = await update.bot.get_file(update.message.photo[-1].file_id)
                print(f"Получен файл с ID: {photo_file.file_id}")

                # Загружаем фото
                photo_path = f"media/{photo_file.file_unique_id}.jpg"
                await photo_file.download(photo_path)  # Сохраняем файл на диск
                print(f"Фото сохранено по пути {photo_path}")

                # Присваиваем фото путь к файлу
                photo_url = photo_path

            except Exception as e:
                print(f"Ошибка при получении файла: {e}")
                await update.message.reply_text("Произошла ошибка при получении фотографии.")
                return
        else:
            await update.message.reply_text("Пожалуйста, отправьте файл фотографии.")
            return

        # Сохранение данных в БД
        print("Создание пользователя с данными:", context.user_data)
        await create_user(
            telegram_id=update.message.from_user.id,
            first_name=context.user_data['first_name'],
            last_name=update.message.from_user.last_name,
            username=update.message.from_user.username,
            city=context.user_data['city'],
            age=context.user_data['age'],
            gender=context.user_data['gender'],
            description=context.user_data['description'],
            photo_url=photo_url
        )

        # Ответ с подтверждением
        await update.message.reply_text(f"Регистрация прошла успешно! Ваш профиль:\n"
                                        f"Имя: {context.user_data['first_name']}\n"
                                        f"Город: {context.user_data['city']}\n"
                                        f"Возраст: {context.user_data['age']}\n"
                                        f"Гендер: {context.user_data['gender']}\n"
                                        f"Описание: {context.user_data['description']}")

        # Очистка данных после регистрации
        context.user_data.clear()


# Асинхронная функция для создания пользователя
@sync_to_async
def create_user(telegram_id, first_name, last_name, username, city, age, gender, description, photo_url):
    print(
        f"Создание пользователя с данными: {first_name} {last_name}, {city}, {age}, {gender}, {description}, {photo_url}")
    user = User.objects.create(
        telegram_id=telegram_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
        city=city,
        age=age,
        gender=gender,
        description=description,
        photo=photo_url
    )
    print(f"Пользователь {first_name} {last_name} создан!")
    return user


# Функция для старта
async def start(update: Update, context):
    await update.message.reply_text("Привет! Для регистрации введите команду /register.")
