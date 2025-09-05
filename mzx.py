import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import BadRequest

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

BOT_TOKEN = "8153083108:AAHIMCAdvYiG5zXZ44BhrkvoOW39Mfccoqg"  # вставь свой токен сюда

# Картинки для меню
IMAGES = {
    "welcome": "https://i.imgur.com/bhp1HHi.png",  # добро пожаловать
    "promo": "https://i.imgur.com/mnLWohR.png",    # промокод
    "shop": "https://i.imgur.com/xcSWIey.png",     # магазин
    "support": "https://i.imgur.com/mNEszql.png",  # поддержка
    "guarantee": "https://imgur.com/FTTOKVY.png", # гарантия
    "reviews": "https://i.imgur.com/fHbFAOp.png",  # отзывы
    "channel": "https://i.imgur.com/bhp1HHi.png"   # канал (используем welcome)
}

# Функция для безопасной отправки медиа
async def safe_edit_message_media(query, image_key, text, reply_markup):
    try:
        await query.edit_message_media(
            media=InputMediaPhoto(media=IMAGES[image_key], caption=text),
            reply_markup=reply_markup
        )
    except BadRequest as e:
        logging.error(f"Ошибка при отправке изображения {image_key}: {e}")
        # Отправляем текстовое сообщение как резерв
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )
    except Exception as e:
        logging.error(f"Неожиданная ошибка: {e}")
        await query.answer("❌ Произошла ошибка. Попробуйте позже.", show_alert=True)

# Функция для безопасной отправки первого сообщения
async def safe_reply_photo(message, image_key, text, reply_markup):
    try:
        await message.reply_photo(
            photo=IMAGES[image_key],
            caption=text,
            reply_markup=reply_markup
        )
    except BadRequest as e:
        logging.error(f"Ошибка при отправке изображения {image_key}: {e}")
        # Отправляем текстовое сообщение как резерв
        await message.reply_text(
            text=text,
            reply_markup=reply_markup
        )

# ---------------- Команды ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await back_to_main_menu(update.message)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    routes = {
        "shop": show_shop_menu,
        "promo": show_promo_menu,
        "support": show_support_menu,
        "guarantee": show_guarantee_menu,
        "reviews": show_reviews_menu,
        "channel": show_channel_menu,
        "back_to_main": back_to_main_menu,
        "in_stock": show_in_stock_menu,
        "preorder": show_preorder_menu,
        "catalog": show_catalog_menu,
        "photo_search": show_photo_search_menu,
        "back_to_shop": show_shop_menu,
        "back_to_preorder": show_preorder_menu,
        "check_subscription": lambda q: check_subscription(q, context),
    }

    if query.data in routes:
        await routes[query.data](query)

# ---------------- Меню ----------------

async def back_to_main_menu(obj) -> None:
    text = """💙MZ MARKET — поможет с покупкой лучшей одежды из Китая.

Для получения скидки 2️⃣0️⃣% нажмите на «Промокод»"""
    keyboard = [
        [InlineKeyboardButton("🛒МАГАЗИН", callback_data="shop"),
         InlineKeyboardButton("👑ПРОМОКОД", callback_data="promo")],
        [InlineKeyboardButton("🫶🏻ПОДДЕРЖКА", callback_data="support"),
         InlineKeyboardButton("🛡ГАРАНТИЯ", callback_data="guarantee")],
        [InlineKeyboardButton("😎ОТЗЫВЫ", callback_data="reviews"),
         InlineKeyboardButton("🏠НАШ КАНАЛ", callback_data="channel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if hasattr(obj, "reply_photo"):
        await safe_reply_photo(obj, "welcome", text, reply_markup)
    else:
        await safe_edit_message_media(obj, "welcome", text, reply_markup)

async def show_shop_menu(query) -> None:
    text = "Выберите услугу:"
    keyboard = [
        [InlineKeyboardButton("В НАЛИЧИИ🛒", callback_data="in_stock")],
        [InlineKeyboardButton("ПОД ЗАКАЗ🚚", callback_data="preorder")],
        [InlineKeyboardButton("⬅️ НАЗАД", callback_data="back_to_main")]
    ]
    await safe_edit_message_media(query, "shop", text, InlineKeyboardMarkup(keyboard))

async def show_promo_menu(query) -> None:
    text = 'Для получения ПРОМОКОДА подпишись на основной канал 📢'
    keyboard = [
        [InlineKeyboardButton("📢 Подписаться на канал", url="https://t.me/MZMARKET1")],
        [InlineKeyboardButton("✅ ПРОВЕРИТЬ", callback_data="check_subscription")],
        [InlineKeyboardButton("⬅️ НАЗАД", callback_data="back_to_main")]
    ]
    await safe_edit_message_media(query, "promo", text, InlineKeyboardMarkup(keyboard))

async def show_support_menu(query) -> None:
    text = "Связаться с нашим менеджером:"
    keyboard = [
        [InlineKeyboardButton("👨‍💼 Связаться с менеджером", url="https://t.me/MZmanager")],
        [InlineKeyboardButton("⬅️ НАЗАД", callback_data="back_to_main")]
    ]
    await safe_edit_message_media(query, "support", text, InlineKeyboardMarkup(keyboard))

async def show_guarantee_menu(query) -> None:
    text = """🛡Наша деятельность легальна и надежна.

🧐Ознакомиться с гарантией: https://telegra.ph/GARANTIYA-08-18"""
    keyboard = [[InlineKeyboardButton("⬅️ НАЗАД", callback_data="back_to_main")]]
    await safe_edit_message_media(query, "guarantee", text, InlineKeyboardMarkup(keyboard))

async def show_reviews_menu(query) -> None:
    text = "Наши отзывы находятся в отдельном канале ⭐️"
    keyboard = [
        [InlineKeyboardButton("⭐️ОТЗЫВЫ", url="https://t.me/+PUEqE_tmfzNkZDFi")],
        [InlineKeyboardButton("⬅️ НАЗАД", callback_data="back_to_main")]
    ]
    await safe_edit_message_media(query, "reviews", text, InlineKeyboardMarkup(keyboard))

async def show_channel_menu(query) -> None:
    text = "📢 Подписывайтесь на наш официальный канал!"
    keyboard = [
        [InlineKeyboardButton("Перейти на канал", url="https://t.me/MZMARKET1")],
        [InlineKeyboardButton("⬅️ НАЗАД", callback_data="back_to_main")]
    ]
    await safe_edit_message_media(query, "channel", text, InlineKeyboardMarkup(keyboard))

async def show_in_stock_menu(query) -> None:
    text = "Перейти к товарам в наличии:"
    keyboard = [
        [InlineKeyboardButton("🛒 Перейти в магазин", url="https://t.me/mzassortiment")],
        [InlineKeyboardButton("⬅️ НАЗАД", callback_data="back_to_shop")]
    ]
    await safe_edit_message_media(query, "shop", text, InlineKeyboardMarkup(keyboard))

async def show_preorder_menu(query) -> None:
    text = """Вы можете ознакомиться🔍
КАК РАБОТАЕТ УСЛУГА ПОД ЗАКАЗ❓
https://telegra.ph/KAK-RABOTAET-USLUGA-POD-ZAKAZ-08-18
Выберите вариант:"""
    keyboard = [
        [InlineKeyboardButton("КАТАЛОГ📱", callback_data="catalog")],
        [InlineKeyboardButton("ПОИСК ПО ФОТО📸", callback_data="photo_search")],
        [InlineKeyboardButton("⬅️ НАЗАД", callback_data="back_to_shop")]
    ]
    await safe_edit_message_media(query, "shop", text, InlineKeyboardMarkup(keyboard))

async def show_catalog_menu(query) -> None:
    text = "Перейти в каталог:"
    keyboard = [
        [InlineKeyboardButton("📱 Открыть каталог", url="https://t.me/mzcatalog")],
        [InlineKeyboardButton("⬅️ НАЗАД", callback_data="back_to_preorder")]
    ]
    await safe_edit_message_media(query, "shop", text, InlineKeyboardMarkup(keyboard))

async def show_photo_search_menu(query) -> None:
    text = "Отправьте фото нашему менеджеру:"
    keyboard = [
        [InlineKeyboardButton("📸 Отправить фото", url="https://t.me/MZmanager")],
        [InlineKeyboardButton("⬅️ НАЗАД", callback_data="back_to_preorder")]
    ]
    await safe_edit_message_media(query, "shop", text, InlineKeyboardMarkup(keyboard))

# ---------------- Проверка подписки ----------------

async def check_subscription(query, context) -> None:
    user_id = query.from_user.id
    chat_id = "@MZMARKET1"
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status in ["member", "administrator", "creator"]:
            text = """🎉 ВАШ ПРОМОКОД: TRY MZ

Как использовать промокод? 🧐
1. Выберите услугу или товар 🤔
2. Напишите @MZmanager 📝
3. Перешлите это сообщение менеджеру ✅

🎁 Скидка 20% действует на все товары!"""
            keyboard = [[InlineKeyboardButton("⬅️ НАЗАД", callback_data="back_to_main")]]
            await safe_edit_message_media(query, "promo", text, InlineKeyboardMarkup(keyboard))
        else:
            await query.answer("❌ Вы не подписаны на канал! Подпишитесь и попробуйте снова.", show_alert=True)
    except Exception as e:
        await query.answer("❌ Ошибка проверки подписки. Попробуйте позже.", show_alert=True)
        logging.error(f"Ошибка при проверке подписки: {e}")

# ---------------- Запуск ----------------

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()