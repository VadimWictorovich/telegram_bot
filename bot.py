from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Пишем функцию для команды /start
def start(update: Update, context: CallbackContext) -> None:
    # Приветственное сообщение при нажатии старта
    update.message.reply_text('Приветствую, данный бот поможет в сборе информации по МП')

# Основная функция для запуска бота
def main(): 
    # Тут расположен ваш токен
    updater = Updater("7440834305:AAFy-1Gtx9-kRN0cn87dLyOpkJ8Rh3DKTG0")
        
    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Регистрируем обработчик для команды /start
    dp.add_handler(CommandHandler("start", start))

    # Запуск бота
    updater.start_polling()
        
    # Ожидание завершения (бот работает, пока не будет остановлен вручную)
    updater.idle()

# Проверяем, является ли данный файл основным модулем
if __name__ == '__main__':
    main()  # Убедитесь, что здесь 4 пробела или 1 табуляция