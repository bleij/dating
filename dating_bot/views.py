from .models import User, Interaction, Match
from django.db.models.query import sync_to_async
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext


# Функция для старта
async def start(update: Update, context):
    await update.message.reply_text("Для создания анкеты введите команду /register.")


# Функция для регистрации
async def register(update: Update, context):
    await update.message.reply_text("Введите ваше имя:")
    context.user_data.clear()  # Сбрасываем временные данные
    context.user_data['step'] = 1


async def handle_registration(update: Update, context: CallbackContext):
    step = context.user_data.get('step')

    if step == 1:
        context.user_data['name'] = update.message.text
        await update.message.reply_text("Теперь введите ваш город:")
        context.user_data['step'] = 2

    elif step == 2:
        context.user_data['city'] = update.message.text
        await update.message.reply_text("Введите ваш возраст:")
        context.user_data['step'] = 3

    elif step == 3:
        context.user_data['age'] = update.message.text
        # Переходим к выбору пола с кнопками
        keyboard = [
            [
                InlineKeyboardButton("Парень", callback_data="gender_M"),
                InlineKeyboardButton("Девушка", callback_data="gender_F"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Теперь выберите ваш пол:", reply_markup=reply_markup)
        context.user_data['step'] = 4

    elif step == 5:
        context.user_data['description'] = update.message.text

        # Сохранение данных в БД
        await create_or_update_user(
            telegram_id=update.message.from_user.id,
            name=context.user_data['name'],
            username=update.message.from_user.username,
            city=context.user_data['city'],
            age=context.user_data['age'],
            gender=context.user_data['gender'],
            description=context.user_data['description'],
        )

        # Подтверждение и очистка данных
        await update.message.reply_text(f"Ваша анкета:\n"
                                        f"Имя: {context.user_data['name']}\n"
                                        f"Город: {context.user_data['city']}\n"
                                        f"Возраст: {context.user_data['age']}\n"
                                        f"Пол: {'Парень' if context.user_data['gender'] == 'M' else 'Девушка'}\n"
                                        f"Описание: {context.user_data['description']}")
        context.user_data.clear()


# Обработчик выбора пола
async def handle_gender_choice(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Подтверждаем нажатие

    # Сохраняем пол в user_data
    gender = query.data.split("_")[1]  # gender_M -> M
    context.user_data['gender'] = gender

    # Переход к следующему шагу
    await query.edit_message_text(f"Вы выбрали: {'Парень' if gender == 'M' else 'Девушка'}")
    await query.message.reply_text("Добавьте описание вашего профиля:")
    context.user_data['step'] = 5


# Асинхронная функция для создания пользователя
@sync_to_async
def create_or_update_user(telegram_id, name, username, city, age, gender, description):
    user, created = User.objects.update_or_create(
        telegram_id=telegram_id,
        defaults={
            'name': name,
            'username': username,
            'city': city,
            'age': age,
            'gender': gender,
            'description': description,
        }
    )
    if created:
        print(f"Создан новый пользователь: {name}")
    else:
        print(f"Обновлён профиль пользователя: {name}")
    return user


@sync_to_async
def get_next_profile(current_user_id):
    print(f"Ищем для пользователя telegram_id {current_user_id}")
    user = User.objects.exclude(telegram_id=current_user_id).first()
    print(f"Найден пользователь: {user}")
    return user


async def show_profile(update, context):
    print("Команда /browse вызвана")  # Отладка
    await update.message.reply_text("Ищу анкету...")  # Простое сообщение

    user = await get_next_profile(update.message.from_user.id)
    if not user:
        await update.message.reply_text("Анкеты закончились! Попробуйте позже.")
        return

    # Создаем кнопки "Лайк" и "Дизлайк"
    keyboard = [
        [
            InlineKeyboardButton("👍 Лайк", callback_data=f"like_{user.telegram_id}"),
            InlineKeyboardButton("👎 Дизлайк", callback_data=f"dislike_{user.telegram_id}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем анкету
    await update.message.reply_text(
        f"Имя: {user.name}\nГород: {user.city}\nВозраст: {user.age}\nОписание: {user.description}",
        reply_markup=reply_markup
    )


@sync_to_async
def save_interaction(from_user_id, to_user_id, is_like):
    # Получаем объекты пользователей
    try:
        from_user = User.objects.get(telegram_id=from_user_id)
        to_user = User.objects.get(telegram_id=to_user_id)
    except User.DoesNotExist as e:
        raise ValueError(f"Ошибка: {e}")

    # Создаём или обновляем взаимодействие
    interaction, created = Interaction.objects.get_or_create(
        from_user=from_user,
        to_user=to_user,
        defaults={'is_like': is_like}
    )
    if not created:
        interaction.is_like = is_like
        interaction.save()

    # Проверяем взаимный лайк
    if is_like:
        reverse_interaction = Interaction.objects.filter(
            from_user=to_user,
            to_user=from_user,
            is_like=True
        ).exists()
        if reverse_interaction:
            Match.objects.get_or_create(
                user1=min(from_user, to_user, key=lambda u: u.id),
                user2=max(from_user, to_user, key=lambda u: u.id)
            )



async def handle_like_dislike(update, context):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    action = data[0]  # "like" или "dislike"
    to_user_id = int(data[1])
    from_user_id = query.from_user.id

    print(f"Обрабатываем {action} от {from_user_id} к {to_user_id}")

    try:
        await save_interaction(from_user_id, to_user_id, action == "like")
        await query.edit_message_text("Ваш выбор сохранён!")
        await show_profile(update, context)  # Переход к следующей анкете
    except ValueError as e:
        await query.edit_message_text(f"Ошибка: {e}")

