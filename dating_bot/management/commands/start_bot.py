from django.core.management.base import BaseCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from dating_bot.views import start, register, handle_gender_choice, handle_registration, show_profile, \
    handle_like_dislike


class Command(BaseCommand):
    help = 'Запускает телеграм-бота'

    def handle(self, *args, **kwargs):
        application = Application.builder().token('8033383316:AAGXUQwEwSjCysHSqY51Ip7Pm8Z9tdmo8-k').build()

        # Регистрируем команды
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('register', register))

        # Обрабатываем текстовые сообщения
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_registration))

        # Обрабатываем кнопки
        application.add_handler(CallbackQueryHandler(handle_gender_choice, pattern="^gender_"))

        application.add_handler(CommandHandler('show_profiles', show_profile))
        application.add_handler(CallbackQueryHandler(handle_like_dislike, pattern="^(like|dislike)_"))

        # Запускаем бота
        application.run_polling()
