import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8014266071:AAGuYgdEhr5-sKCp1uq0HNt02de7Skj6ATw"

# Главное меню
def main_menu_keyboard(lang='ru'):
    if lang == 'en':
        return [
            [InlineKeyboardButton("🎨 Portfolio", callback_data='portfolio')],
            [InlineKeyboardButton("📦 Ready 3D Models", callback_data='models')],
            [InlineKeyboardButton("🛒 Order 3D Model", callback_data='order')],
            [InlineKeyboardButton("🌐 Language", callback_data='language')]
        ]
    else:
        return [
            [InlineKeyboardButton("🎨 Моё портфолио", callback_data='portfolio')],
            [InlineKeyboardButton("📦 Готовые 3D модели", callback_data='models')],
            [InlineKeyboardButton("🛒 Заказать 3D модель", callback_data='order')],
            [InlineKeyboardButton("🌐 Язык", callback_data='language')]
        ]

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'ru')
    keyboard = InlineKeyboardMarkup(main_menu_keyboard(lang))
    if lang == 'en':
        await update.message.reply_text("Welcome! Choose an option:", reply_markup=keyboard)
    else:
        await update.message.reply_text("Привет! Добро пожаловать. Выберите раздел:", reply_markup=keyboard)

# Кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    lang = context.user_data.get('lang', 'ru')

    if data == 'menu':
        keyboard = InlineKeyboardMarkup(main_menu_keyboard(lang))
        text = "Выберите раздел:" if lang == 'ru' else "Choose an option:"
        await query.edit_message_text(text, reply_markup=keyboard)

    elif data == 'portfolio':
        title = "🎨 Моё портфолио:" if lang == 'ru' else "🎨 My Portfolio:"
        await send_images(query, folder='portfolio', title=title, lang=lang)

    elif data == 'models':
        title = "📦 Готовые 3D модели:" if lang == 'ru' else "📦 Ready 3D Models:"
        await send_images(query, folder='models', title=title, lang=lang, with_order=True)

    elif data == 'order':
        msg = "✏️ Как заказать 3D модель:\n\nНапиши, что тебе нужно + прикрепи пример (если есть).\n📩 Мой Telegram: @ArtMudry3Ddizayn"
        if lang == 'en':
            msg = "✏️ How to order a 3D model:\n\nDescribe what you need and attach an example if you have one.\n📩 My Telegram: @ArtMudry3Ddizayn"
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад" if lang == 'ru' else "🔙 Back", callback_data='menu')]]))

    elif data == 'language':
        await query.edit_message_text(
            "Выберите язык / Choose a language:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🇷🇺 Русский", callback_data='set_lang_ru')],
                [InlineKeyboardButton("🇬🇧 English", callback_data='set_lang_en')],
                [InlineKeyboardButton("🔙 Назад", callback_data='menu')]
            ])
        )

    elif data == 'set_lang_ru':
        context.user_data['lang'] = 'ru'
        await query.edit_message_text("Язык установлен: Русский 🇷🇺", reply_markup=InlineKeyboardMarkup(main_menu_keyboard('ru')))

    elif data == 'set_lang_en':
        context.user_data['lang'] = 'en'
        await query.edit_message_text("Language set: English 🇬🇧", reply_markup=InlineKeyboardMarkup(main_menu_keyboard('en')))

# Отправка изображений из папки
async def send_images(query, folder, title, lang='ru', with_order=False):
    files = os.listdir(folder)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    await query.edit_message_text(title)
    await query.message.reply_text("📂 Смотри примеры ниже:" if lang == 'ru' else "📂 See the examples below:")

    if not image_files:
        await query.message.reply_text("Пока ничего нет 😢" if lang == 'ru' else "Nothing here yet 😢")
        return

    for image in image_files:
        path = os.path.join(folder, image)
        size = os.path.getsize(path)
        with open(path, 'rb') as img:
            if size <= 10 * 1024 * 1024:
                await query.message.reply_photo(photo=img)
            else:
                await query.message.reply_document(document=img)

    buttons = [[InlineKeyboardButton("🔙 Вернуться в меню" if lang == 'ru' else "🔙 Back to menu", callback_data='menu')]]
    if with_order:
        buttons.insert(0, [InlineKeyboardButton("📩 Заказать" if lang == 'ru' else "📩 Order", callback_data='order')])
    await query.message.reply_text("Что дальше?" if lang == 'ru' else "What next?", reply_markup=InlineKeyboardMarkup(buttons))

# Запуск
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()

if __name__ == '__main__':
    main()

