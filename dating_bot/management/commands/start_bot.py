from django.core.management.base import BaseCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dating_bot.views import start, register, handle_name


class Command(BaseCommand):
    help = 'Запускает телеграм-бота'

    def handle(self, *args, **kwargs):
        application = Application.builder().token('8033383316:AAGXUQwEwSjCysHSqY51Ip7Pm8Z9tdmo8-k').build()

        # Регистрируем команды
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('register', register))

        # Обрабатываем текстовые сообщения
        application.add_handler(MessageHandler(filters.TEXT, handle_name))

        # Запускаем бота
        application.run_polling()
