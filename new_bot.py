from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Словарь для хранения информации от пользователей
user_data = {}

# Список районов Могилевской области
regions = [
    "Бобруйский", "Быховский", "Глусский", "Горецкий",
    "Дрибинский", "Кировский", "Климовичский", "Кличевский",
    "Костюковичский", "Краснопольский", "Кричевский", "Круглянский",
    "Могилевский", "Мстиславский", "Осиповичский", "Славгородский",
    "Хотимский", "Чаусский", "Чериковский", "Шкловский",
    "Ленинский (Могилева)", "Октябрьский (Могилева)", "г. Бобруйск"
]

# Функция для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton(region, callback_data=region)] for region in regions]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Выберите ваш район:', reply_markup=reply_markup)

# Обработчик для выбора района
async def region_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Получаем выбранный район
    region = query.data
    user_id = query.from_user.id

    # Сохраняем район в словарь, но не подтверждаем сразу
    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]['region'] = region

    # Кнопки для подтверждения района
    keyboard = [
        [InlineKeyboardButton("Да", callback_data="confirm_yes"),
         InlineKeyboardButton("Нет", callback_data="confirm_no")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Запрашиваем подтверждение у пользователя
    await query.edit_message_text(f"Вы выбрали {region}. Подтверждаете?", reply_markup=reply_markup)

# Обработчик для подтверждения выбора региона
async def confirm_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Если пользователь подтвердил выбор
    if query.data == "confirm_yes":
        await query.edit_message_text(f"{user_data[user_id]['region']} район подтвержден. Введите количество МП находящихся в производстве (в том числе приостановленных):")
        user_data[user_id]['step'] = 'mp_in_production'
    
    # Если пользователь отказался и хочет выбрать район заново
    elif query.data == "confirm_no":
        keyboard = [[InlineKeyboardButton(region, callback_data=region)] for region in regions]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text('Выберите ваш район еще раз:', reply_markup=reply_markup)

# Обработчик для обработки числовых ответов
async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    text = update.message.text

    # Проверка на то, ввел ли пользователь число
    if not text.isdigit():
        await update.message.reply_text('Пожалуйста, введите числовое значение.')
        return
    
    # Преобразуем текст в число
    number = int(text)

    # Проверяем, на каком шаге находится пользователь
    step = user_data[user_id].get('step')

    if step == 'mp_in_production':
        user_data[user_id]['mp_in_production'] = number
        user_data[user_id]['step'] = 'mp_suspended'
        await update.message.reply_text('Сколько из них приостановлено?')

    elif step == 'mp_suspended':
        user_data[user_id]['mp_suspended'] = number
        user_data[user_id]['step'] = 'mp_transferred'
        await update.message.reply_text('Сколько МП передано в следственные подразделения?')

    elif step == 'mp_transferred':
        user_data[user_id]['mp_transferred'] = number
        user_data[user_id]['step'] = None  # Завершаем сбор данных
        
        # Собранные данные
        mp_in_production = user_data[user_id].get('mp_in_production', 0)
        mp_suspended = user_data[user_id].get('mp_suspended', 0)
        mp_transferred = user_data[user_id].get('mp_transferred', 0)

        await update.message.reply_text(f"Спасибо! Вот собранная информация:\n"
                                        f"МП в производстве: {mp_in_production}\n"
                                        f"Из них приостановлено: {mp_suspended}\n"
                                        f"Передано в следствие: {mp_transferred}")
    
# Функция для команды /show_info
async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if user_data:
        info_message = "Собранная информация:\n"
        for user_id, data in user_data.items():
            region = data.get('region', 'Не выбран')
            mp_in_production = data.get('mp_in_production', 'Не указано')
            mp_suspended = data.get('mp_suspended', 'Не указано')
            mp_transferred = data.get('mp_transferred', 'Не указано')
            info_message += (f"Пользователь {user_id} - Район: {region}, "
                             f"МП в производстве: {mp_in_production}, "
                             f"Приостановлено: {mp_suspended}, "
                             f"Передано в следствие: {mp_transferred}\n")
        await update.message.reply_text(info_message)
    else:
        await update.message.reply_text('Нет сохраненной информации.')

# Основная функция для запуска бота
def main(): 
    application = ApplicationBuilder().token("7440834305:AAFy-1Gtx9-kRN0cn87dLyOpkJ8Rh3DKTG0").build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(region_choice, pattern="^((?!confirm_).)*$"))  # Обработчик для выбора региона
    application.add_handler(CallbackQueryHandler(confirm_choice, pattern="^confirm_"))  # Обработчик для подтверждения выбора
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))  # Обработчик для ввода данных
    application.add_handler(CommandHandler("show_info", show_info))  # Обработчик для отображения информации

    application.run_polling()

if __name__ == '__main__':
    main()
