import logging
import os
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher, types
from database import init_db, add_user, get_user, get_car_price, update_user_balance, log_earning, get_user_balance
from payment_bot import create_payment_link
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Загрузка переменных окружения
load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Обработка команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    try:
        user = await get_user(message.from_user.id)  # Проверяем, есть ли пользователь в БД
        if user:
            # Пользователь найден — приветствие и меню
            await message.reply(f"Привет, {user['username']}! Добро пожаловать обратно!")
        else:
            # Если пользователя нет — просим ввести имя
            await message.reply("Привет! Введите ваше имя, чтобы начать.")
            return  # Выходим, ждем имя пользователя

        # В любом случае показываем меню
        await asyncio.sleep(1)
        await show_main_menu(message)

    except Exception as e:
        logging.error(f"Ошибка при обработке команды /start: {e}")


# Обработка имени пользователя
@dp.message_handler(lambda message: message.text.isalpha())
async def handle_name(message: types.Message):
    try:
        username = message.text
        await add_user(message.from_user.id, username)  # Добавляем нового пользователя в БД
        await message.reply(f"Добро пожаловать, {username}!")
        
        # Показ главного меню
        await asyncio.sleep(1)
        await show_main_menu(message)

    except Exception as e:
        logging.error(f"Ошибка при обработке имени пользователя: {e}")

#######################################################################################################
# # Обработка команды /start
# @dp.message_handler(commands=['start'])
# async def send_welcome(message: types.Message):
#     try:
#         user = await get_user(message.from_user.id)
#         if user:
#             await message.reply(f"Привет, {user['username']}! Добро пожаловать обратно!")
#         else:
#             await message.reply("Привет! Введите ваше имя, чтобы начать.")
#             await asyncio.sleep(2)
#             await bot.send_message(message.from_user.id, "Для начала создайте свой профиль.")
#     except Exception as e:
#         logging.error(f"Ошибка при обработке команды /start: {e}")
#
# # Обработка имени пользователя
# @dp.message_handler(lambda message: message.text.isalpha())
# async def handle_name(message: types.Message):
#     try:
#         username = message.text
#         await add_user(message.from_user.id, username)
#         await message.reply(f"Добро пожаловать, {username}!")
#         await asyncio.sleep(1)
#         await show_main_menu(message)
#     except Exception as e:
#         logging.error(f"Ошибка при обработке имени пользователя: {e}")
######################################################################################################

# Главное меню с новыми кнопками
async def show_main_menu(message: types.Message):
    try:
        markup = InlineKeyboardMarkup()
        promo_code_btn = InlineKeyboardButton("Ввести промокод", callback_data='enter_promo')
        open_app_btn = InlineKeyboardButton("Открыть мини-приложение", url='https://your-minigame-app.com')  # Укажи ссылку на мини-приложение
        markup.add(promo_code_btn, open_app_btn)
        await message.reply("Выберите действие:", reply_markup=markup)
    except Exception as e:
        logging.error(f"Ошибка при отображении главного меню: {e}")

# Обработка нажатия на кнопку "Ввести промокод"
@dp.callback_query_handler(lambda c: c.data == 'enter_promo')
async def process_enter_promo(callback_query: types.CallbackQuery):
    try:
        await bot.send_message(callback_query.from_user.id, "Введите ваш промокод:")
        dp.register_message_handler(handle_promo_code, state=None)  # Ждем промокод
    except Exception as e:
        logging.error(f"Ошибка при запросе промокода: {e}")

# Обработка промокода
async def handle_promo_code(message: types.Message):
    promo_code = message.text
    if promo_code == "HAMSTER2024":  # Пример проверочного кода
        await message.reply("Промокод принят! Вы получили бонус.")
        # Здесь можно добавить логику для начисления бонусов или других действий
    else:
        await message.reply("Неверный промокод. Попробуйте снова.")

# Запуск бота и базы данных
async def main():
    try:
        await init_db()  # Инициализация базы данных
        await dp.start_polling()  # Запуск бота
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")










#)###############################################################################################################################################################
# import logging
# import os
# from dotenv import load_dotenv
# import asyncio
# from aiogram import Bot, Dispatcher, types
# from database import init_db, add_user, get_user, get_car_price, update_user_balance, log_earning, get_user_balance
# from payment_bot import create_payment_link
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# # Загрузка переменных окружения
# load_dotenv()

# )API_TOKEN = os.getenv('API_TOKEN')

# # Настройка логирования
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[
#         logging.FileHandler("bot.log"),
#         logging.StreamHandler()
#     ]
# )

# )bot = Bot(token=API_TOKEN)
# dp = Dispatcher(bot)

# # Обработка команды /start
# @dp.message_handler(commands=['start'])
# async def send_welcome(message: types.Message):
#     try:
#         user = await get_user(message.from_user.id)
#         if user:
#             await message.reply(f"Привет, {user['username']}! Добро пожаловать обратно!")
#         else:
#             await message.reply("Привет! Введите ваше имя, чтобы начать.")
#             await asyncio.sleep(2)
#             await bot.send_message(message.from_user.id, "Для начала создайте свой профиль.")
#     except Exception as e:
#         logging.error(f"Ошибка при обработке команды /start: {e}")

# # Обработка имени пользователя
# @dp.message_handler(lambda message: message.text.isalpha())
# async def handle_name(message: types.Message):
#     try:
#         username = message.text
#         await add_user(message.from_user.id, username)
#         await message.reply(f"Добро пожаловать, {username}!")
#         await asyncio.sleep(1)
#         await show_main_menu(message)
#     except Exception as e:
#         logging.error(f"Ошибка при обработке имени пользователя: {e}")

# # Главное меню
# async def show_main_menu(message: types.Message):
#     try:
#         markup = InlineKeyboardMarkup()
#         buy_car_btn = InlineKeyboardButton("Купить машину", callback_data='buy_car')
#         check_balance_btn = InlineKeyboardButton("Проверить баланс", callback_data='check_balance')
#         markup.add(buy_car_btn, check_balance_btn)
#         await message.reply("Выберите действие:", reply_markup=markup)
#     except Exception as e:
#         logging.error(f"Ошибка при отображении главного меню: {e}")

# # Обработка кнопок меню
# @dp.callback_query_handler(lambda c: c.data == 'buy_car')
# async def process_buy_car(callback_query: types.CallbackQuery):
#     try:
#         price = await get_car_price(1)
#         payment_link = create_payment_link(callback_query.from_user.id, price)
#         await bot.send_message(callback_query.from_user.id, f"Оплатите покупку по ссылке: {payment_link}")
#     except Exception as e:
#         logging.error(f"Ошибка при обработке покупки машины: {e}")

# )@dp.callback_query_handler(lambda c: c.data == 'check_balance')
# async def process_check_balance(callback_query: types.CallbackQuery):
#     try:
#         balance = await get_user_balance(callback_query.from_user.id)
#         await bot.send_message(callback_query.from_user.id, f"Ваш баланс: {balance} монет.")
#     except Exception as e:
#         logging.error(f"Ошибка при проверке баланса: {e}")

# # Проверка оплаты и начисление монет
# async def check_payment_and_credit(user_id, car_id, paid_amount):
#     try:
#         price = await get_car_price(car_id)
#         if paid_amount >= price:
#             await update_user_balance(user_id, paid_amount)
#             await log_earning(user_id, paid_amount)
#             await bot.send_message(user_id, "Платеж успешно завершён. Вы получили машину!")
#         else:
#             await bot.send_message(user_id, "Платеж не был завершен. Попробуйте снова.")
#     except Exception as e:
#         logging.error(f"Ошибка при проверке платежа: {e}")

# # Запуск бота и базы данных
# async def main():
#     try:
#         await init_db()  # Инициализация базы данных
#         await dp.start_polling()  # Запуск бота
#     except Exception as e:
#         logging.error(f"Ошибка при запуске бота: {e}")

# )if __name__ == '__main__':
#     try:
#         asyncio.run(main())
#     except (KeyboardInterrupt, SystemExit):
#         logging.info("Бот остановлен.")
###################################################################################################################################################################




















# )import logging
# import os
# from dotenv import load_dotenv
# import asyncio
# from aiogram import Bot, Dispatcher, types
# from database import init_db, add_user, get_user, get_car_price, update_user_balance, log_earning, get_user_balance
# from payment_bot import create_payment_link
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# load_dotenv()

# )API_TOKEN = os.getenv('API_TOKEN')

# logging.basicConfig(
#     level=logging.INFO,  # Уровень логирования
#     format='%(asctime)s [%(levelname)s] %(message)s',  # Формат сообщения
#     handlers=[
#         logging.FileHandler("bot.log"),  # Лог-файл
#         logging.StreamHandler()  # Вывод в консоль
#     ]
# )

# )bot = Bot(token=API_TOKEN)
# dp = Dispatcher(bot)

# logging.info("Бот в стадии предзапуска")

# # Обработка команды /start
# @dp.message_handler(commands=['start'])
# async def send_welcome(message: types.Message):
#     user = await get_user(message.from_user.id)
#     if user:
#         await message.reply(f"Привет, {user['username']}! Добро пожаловать обратно!")
#     else:
#         await message.reply("Привет! Введите ваше имя, чтобы начать.")
#         await asyncio.sleep(2)
#         await bot.send_message(message.from_user.id, "Для начала создайте свой профиль.")

# logging.info("Бот в стадии запуска /start")

# # Обработка имени пользователя
# @dp.message_handler(lambda message: message.text.isalpha())
# async def handle_name(message: types.Message):
#     username = message.text
#     await add_user(message.from_user.id, username)
#     await message.reply(f"Добро пожаловать, {username}!")
#     await asyncio.sleep(1)
#     await show_main_menu(message)

# logging.info("Бот в стадии Обработка имени пользователя")

# # Главное меню
# async def show_main_menu(message: types.Message):
#     markup = InlineKeyboardMarkup()
#     buy_car_btn = InlineKeyboardButton("Купить машину", callback_data='buy_car')
#     check_balance_btn = InlineKeyboardButton("Проверить баланс", callback_data='check_balance')
#     markup.add(buy_car_btn, check_balance_btn)
#     await message.reply("Выберите действие:", reply_markup=markup)

# logging.info("Бот в стадии запуска кнопок")

# # Обработка кнопок меню
# @dp.callback_query_handler(lambda c: c.data == 'buy_car')
# async def process_buy_car(callback_query: types.CallbackQuery):
#     price = await get_car_price(1)  # Получаем цену машины с ID 1
#     payment_link = create_payment_link(callback_query.from_user.id, price)
#     await bot.send_message(callback_query.from_user.id, f"Оплатите покупку по ссылке: {payment_link}")

#) @dp.callback_query_handler(lambda c: c.data == 'check_balance')
# async def process_check_balance(callback_query: types.CallbackQuery):
#     balance = await get_user_balance(callback_query.from_user.id)
#     await bot.send_message(callback_query.from_user.id, f"Ваш баланс: {balance} монет.")

# logging.info("Бот в стадии обработки кнопок")

# # Проверка оплаты и начисление монет
# async def check_payment_and_credit(user_id, car_id, paid_amount):
#     price = await get_car_price(car_id)
#     if paid_amount >= price:
#         await update_user_balance(user_id, paid_amount)
#         await log_earning(user_id, paid_amount)
#         await bot.send_message(user_id, "Платеж успешно завершён. Вы получили машину!")
#     else:
#         await bot.send_message(user_id, "Платеж не был завершен. Попробуйте снова.")

# logging.info("Бот в стадии проверки оплаты")

# # Запуск бота и базы данных
# async def main():
#     await init_db()  # Инициализация базы данных
#     try:
#         await dp.start_polling()  # Запуск бота
#     finally:
#         await close_database()  # Закрытие базы данных при завершении работы бота

# logging.info("Успешный запуск бота")

#) if __name__ == '__main__':
#     asyncio.run(main())






























# (import logging)
# import os
# from dotenv import load_dotenv
# import asyncio
# from database import init_db
# from aiogram import Bot, Dispatcher, types 
# from database import add_user, get_user, get_car_price, update_user_balance, log_earning, get_user_balance
# from payment_bot import create_payment_link
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# load_dotenv()

# (API_TOKEN = os.getenv('API_TOKEN'))

# logging.basicConfig(level=logging.INFO)

# (bot = Bot(token=API_TOKEN))
# dp = Dispatcher(bot)


# # Обработка команды /start
# @dp.message_handler(commands=['start'])
# async def send_welcome(message: types.Message):
#     user = await get_user(message.from_user.id)  # Добавлен await
#     if user:
#         await message.reply(f"Привет, {user['username']}! Добро пожаловать обратно!")
#     else:
#         await message.reply("Привет! Введите ваше имя, чтобы начать.")
#         await asyncio.sleep(2)
#         await bot.send_message(message.from_user.id, "Для начала создайте свой профиль.")

# # Обработка имени пользователя
# @dp.message_handler(lambda message: message.text.isalpha())
# async def handle_name(message: types.Message):
#     username = message.text
#     await add_user(message.from_user.id, username)  # Добавлен await
#     await message.reply(f"Добро пожаловать, {username}!")
#     await asyncio.sleep(1)
#     await show_main_menu(message)

# # Главное меню
# async def show_main_menu(message: types.Message):
#     markup = InlineKeyboardMarkup()
#     buy_car_btn = InlineKeyboardButton("Купить машину", callback_data='buy_car')
#     check_balance_btn = InlineKeyboardButton("Проверить баланс", callback_data='check_balance')
#     markup.add(buy_car_btn, check_balance_btn)
#     await message.reply("Выберите действие:", reply_markup=markup)

# # Обработка кнопок меню
# @dp.callback_query_handler(lambda c: c.data == 'buy_car')
# async def process_buy_car(callback_query: types.CallbackQuery):
#     price = await get_car_price(1)  # Добавлен await
#     payment_link = create_payment_link(callback_query.from_user.id, price)
    
#     await bot.send_message(callback_query.from_user.id, f"Оплатите покупку по ссылке: {payment_link}")

# (@dp.callback_query_handler(lambda c: c.data == 'check_balance'))
# async def process_check_balance(callback_query: types.CallbackQuery):
#     balance = await get_user_balance(callback_query.from_user.id)  # Добавлен await
#     await bot.send_message(callback_query.from_user.id, f"Ваш баланс: {balance} монет.")

# # Проверка оплаты и начисление монет
# async def check_payment_and_credit(user_id, car_id, paid_amount):
#     price = await get_car_price(car_id)  # Добавлен await
#     if paid_amount >= price:
#         await update_user_balance(user_id, paid_amount)  # Добавлен await
#         await log_earning(user_id, paid_amount)  # Добавлен await
#         await bot.send_message(user_id, "Платеж успешно завершён. Вы получили машину!")
#     else:
#         await bot.send_message(user_id, "Платеж не был завершен. Попробуйте снова.")

# (async def run_bot():)
#     await init_db()  # Инициализация базы данных
#     await dp.start_polling()

# (if __name__ == '__main__':)
#     asyncio.run(run_bot())















# (import logging)
# import os
# from dotenv import load_dotenv
# import asyncio
# from database import init_db
# from aiogram import Bot, Dispatcher, types 
# from database import add_user, get_user, get_car_price, update_user_balance, log_earning, get_user_balance
# from payment_bot import create_payment_link
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# # Расшифровка файла .env
# #from decrypt_env import decrypt_env_gpg
# #decrypt_env_gpg()

# load_dotenv()

# (API_TOKEN = os.getenv('API_TOKEN'))

# logging.basicConfig(level=logging.INFO)

# (bot = Bot(token=API_TOKEN))
# dp = Dispatcher(bot)


# # Обработка команды /start
# @dp.message_handler(commands=['start'])
# async def send_welcome(message: types.Message):
#     user = get_user(message.from_user.id)
#     if user:
#         await message.reply(f"Привет, {user['username']}! Добро пожаловать обратно!")
#     else:
#         await message.reply("Привет! Введите ваше имя, чтобы начать.")
#         await asyncio.sleep(2)
#         await bot.send_message(message.from_user.id, "Для начала создайте свой профиль.")

# # Обработка имени пользователя
# @dp.message_handler(lambda message: message.text.isalpha())
# async def handle_name(message: types.Message):
#     username = message.text
#     add_user(message.from_user.id, username)
#     await message.reply(f"Добро пожаловать, {username}!")
#     await asyncio.sleep(1)
#     await show_main_menu(message)

# # Главное меню
# async def show_main_menu(message: types.Message):
#     markup = InlineKeyboardMarkup()
#     buy_car_btn = InlineKeyboardButton("Купить машину", callback_data='buy_car')
#     check_balance_btn = InlineKeyboardButton("Проверить баланс", callback_data='check_balance')
#     markup.add(buy_car_btn, check_balance_btn)
#     await message.reply("Выберите действие:", reply_markup=markup)

# # Обработка кнопок меню
# @dp.callback_query_handler(lambda c: c.data == 'buy_car')
# async def process_buy_car(callback_query: types.CallbackQuery):
#     # Сгенерировать ссылку на оплату машины
#     price = get_car_price(1)  # ID машины
#     payment_link = create_payment_link(callback_query.from_user.id, price)
    
#     await bot.send_message(callback_query.from_user.id, f"Оплатите покупку по ссылке: {payment_link}")

# (@dp.callback_query_handler(lambda c: c.data == 'check_balance'))
# async def process_check_balance(callback_query: types.CallbackQuery):
#     balance = get_user_balance(callback_query.from_user.id)
#     await bot.send_message(callback_query.from_user.id, f"Ваш баланс: {balance} монет.")

# # Проверка оплаты и начисление монет
# async def check_payment_and_credit(user_id, car_id, paid_amount):
#     price = get_car_price(car_id)
#     if paid_amount >= price:
#         update_user_balance(user_id, paid_amount)
#         log_earning(user_id, paid_amount)
#         await bot.send_message(user_id, "Платеж успешно завершён. Вы получили машину!")
#     else:
#         await bot.send_message(user_id, "Платеж не был завершен. Попробуйте снова.")

# (async def run_bot():)
#     # Запускаем бота
#     await dp.start_polling()

# (if __name__ == '__main__':)
#      init_db()
#      asyncio.run(run_bot())

#    # (from) aiogram import asyncio
#     #asyncio.run(dp.start_polling(skip_updates=True))
