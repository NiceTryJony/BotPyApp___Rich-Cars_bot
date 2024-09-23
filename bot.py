import logging
import aiosqlite
import os
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher, types
from database import init_db , add_user, get_user, update_user_balance, check_tables, get_user_balance
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberStatus
from datetime import datetime, timedelta

# Загрузка переменных окружения
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
DB_NAME = os.getenv('DB_NAME')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Генерация промокодов
async def insert_promo_codes():
    promo_codes = [
        ('CODE1', 'normal', 10),
        ('CODE2', 'normal', 10),
        ('CODE3', 'normal', 10),
        ('CODE4', 'normal', 30),
        ('CODE5', 'normal', 30),
        ('CODE6', 'normal', 50),
        ('SPECIAL1', 'special', 100),
        ('SPECIAL2', 'special', 150),
        ('SPECIAL3', 'special', 200),
        ('ADVANCED1', 'advanced', 350),
        ('ADVANCED2', 'advanced', 400),
        ('ADVANCED3', 'advanced', 450),
    ]

    expiration_time = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    try:
        async with aiosqlite.connect(DB_NAME) as conn:
            logging.info("Вставка заранее подготовленных промокодов в базу данных..........................................................................................................")
            await conn.execute('DELETE FROM promo_codes')  # Очистка таблицы перед вставкой новых данных
            for code, category, reward in promo_codes:
                logging.info(f"Добавляем промокод: {code}, категория: {category}, награда: {reward}")
                await conn.execute(
                    'INSERT INTO promo_codes (code, category, reward, expiration_time) VALUES (?, ?, ?, ?)',
                    (code, category, reward, expiration_time)
                )
            await conn.commit()
            logging.info("Промокоды успешно вставлены в базу данных.................................................................................................................")
    except Exception as e:
        logging.error(f"Ошибка при вставке промокодов: {e}")



# Обработка команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("TESTiiii")
    try:
        user_id = message.from_user.id
        username = message.from_user.username

        user = await get_user(user_id)
        if user:
            await message.reply(f"Привет, {user['username']}! Добро пожаловать обратно!")
        else:
            await add_user(user_id, username)
            await message.reply("Привет! Вы новый пользователь. Введите ваше имя, чтобы начать.")
            return

        if await check_subscription(user_id, bot):
            await message.reply("Вы подписаны на оба канала! Добро пожаловать!")
            await show_main_menu(message)
        else:
            await message.reply("Пожалуйста, подпишитесь на оба канала, чтобы продолжить:")
            await message.reply(f"1. {CHANNEL_ID_1}\n2. {CHANNEL_ID_2}")

            # Создаем только кнопку "Проверить подписку"
            markup = InlineKeyboardMarkup()
            check_btn = InlineKeyboardButton("Проверить подписку", callback_data='restart')  # Используем callback 'restart'
            markup.add(check_btn)
            await message.reply("После подписки нажмите кнопку ниже для проверки:", reply_markup=markup)

    except Exception as e:
        logging.error(f"Ошибка при обработке команды /start: {e}")

# Обработчик нажатия на кнопку "Проверить подписку"
@dp.callback_query_handler(lambda c: c.data == 'restart')
async def process_restart_callback(callback_query: types.CallbackQuery):
    # Имитируем действие команды /start
    await send_welcome(callback_query.message)

    # Закрываем всплывающее уведомление о нажатии на кнопку
    await bot.answer_callback_query(callback_query.id)



# # Обработка команды /start
# @dp.message_handler(commands=['start'])
# async def send_welcome(message: types.Message):
#     await message.reply("TESTiiii")
#     try:
#         user_id = message.from_user.id
#         username = message.from_user.username

#         user = await get_user(user_id)
#         if user:
#             await message.reply(f"Привет, {user['username']}! Добро пожаловать обратно!")
#         else:
#             await add_user(user_id, username)
#             await message.reply("Привет! Вы новый пользователь. Введите ваше имя, чтобы начать.")
#             return

#         if await check_subscription(user_id, bot):
#             await message.reply("Вы подписаны на оба канала! Добро пожаловать!")
#             await show_main_menu(message)
#         else:
#             await message.reply("Пожалуйста, подпишитесь на оба канала, чтобы продолжить:")
#             await message.reply(f"1. {CHANNEL_ID_1}\n2. {CHANNEL_ID_2}")

#             markup = InlineKeyboardMarkup()
#             check_btn = InlineKeyboardButton("Проверить подписку", callback_data='check_subscription')
#             markup.add(check_btn)
#             await message.reply("После подписки нажмите кнопку ниже для проверки:", reply_markup=markup)
    
#     except Exception as e:
#         logging.error(f"Ошибка при обработке команды /start: {e}")

# Идентификаторы каналов
CHANNEL_ID_1 = '@RICH_CARSETA'
CHANNEL_ID_2 = '@CHANEL_TRY'


# Проверка подписки пользователя на оба канала (NEW)

async def check_subscription(user_id: int, bot: Bot) -> bool:
    try:
        # Проверяем подписку на первый канал
        logging.info("Начата проверка пользователя по подпискам на канал") 
        try:
            member_1 = await bot.get_chat_member(chat_id=CHANNEL_ID_1, user_id=user_id)
            is_subscribed_1 = member_1.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
        except Exception as e:
            logging.error(f"Ошибка при проверке подписки на канал 1 для пользователя {user_id}: {e}")
            is_subscribed_1 = False

        # Проверяем подписку на второй канал
        try:
            member_2 = await bot.get_chat_member(chat_id=CHANNEL_ID_2, user_id=user_id)
            is_subscribed_2 = member_2.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
        except Exception as e:
            logging.error(f"Ошибка при проверке подписки на канал 2 для пользователя {user_id}: {e}")
            is_subscribed_2 = False

        # Возвращаем True только если пользователь подписан на оба канала
        logging.info("Закончена проверка пользователя по подпискам на канал") 
        return is_subscribed_1 and is_subscribed_2

    except Exception as e:
        logging.error(f"Общая ошибка при проверке подписки для пользователя {user_id}: {e}")
        return False

# Проверка подписки пользователя на оба канала (OLD)

# async def check_subscription(user_id: int, bot: Bot) -> bool:
#     try:
#         member_1 = await bot.get_chat_member(chat_id=CHANNEL_ID_1, user_id=user_id)
#         member_2 = await bot.get_chat_member(chat_id=CHANNEL_ID_2, user_id=user_id)

#         return (member_1.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] and
#                 member_2.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER])
#     except Exception as e:
#         logging.error(f"Ошибка при проверке подписки для пользователя {user_id}: {e}")
#         return False

# Главное меню
async def show_main_menu(message: types.Message):
    try:
        markup = InlineKeyboardMarkup()
        promo_code_btn = InlineKeyboardButton("Активировать промокод", callback_data='activate_promo')
        markup.add(promo_code_btn)
        await message.reply("Выберите действие:", reply_markup=markup)
    except Exception as e:
        logging.error(f"Ошибка при отображении главного меню: {e}")

# Обработка промокода
@dp.callback_query_handler(lambda c: c.data == 'activate_promo')
async def process_activate_promo(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Введите ваш промокод:")
    dp.register_message_handler(handle_promo_code)  # Ждем промокод


async def handle_promo_code(message: types.Message):
    promo_code = message.text.strip()
    async with aiosqlite.connect(DB_NAME) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT reward, expiration_time FROM promo_codes WHERE code = ?', (promo_code,))
            result = await cursor.fetchone()

            if result:
                reward, expiration_time = result
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                if now < expiration_time:
                    await update_user_balance(message.from_user.id, reward)
                    await message.reply(f"Промокод принят! Вы получили {reward} монет.")
                else:
                    await message.reply("Промокод истек.")
            else:
                await message.reply("Неверный промокод. Попробуйте снова.")



# Запуск бота и инициализация базы данных
async def main():
    try:
        await init_db()  # Сначала инициализируем базу данных
        await check_tables()
        await insert_promo_codes()  # Затем вставляем промокоды
        logging.info("Бот успешно запущен.")
        await dp.start_polling()  # Запуск бота
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")

if __name__ == '__main__':
    asyncio.run(main())






# )import logging
# import aiosqlite
# import os
# from dotenv import load_dotenv
# import asyncio
# from aiogram import Bot, Dispatcher, types
# from database import init_db, add_user, get_user, update_user_balance, get_user_balance
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberStatus
# from datetime import datetime, timedelta

# # Загрузка переменных окружения
# load_dotenv()
# API_TOKEN = os.getenv('API_TOKEN')
# DB_NAME = os.getenv('DB_NAME')

# # Настройка логирования
# logging.basicConfig(filename='bot.log', level=logging.ERROR, encoding='utf-8')
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

# # Генерация промокодов
# async def generate_promo_codes():
#     # Логика генерации новых промокодов
#     # Здесь можно генерировать коды и записывать их в БД
#     promo_codes = [
#         ('CODE1', 'normal', 10),
#         ('CODE2', 'normal', 10),
#         ('CODE3', 'normal', 10),
#         ('CODE4', 'normal', 30),
#         ('CODE5', 'normal', 30),
#         ('CODE6', 'normal', 50),
#         ('SPECIAL1', 'special', 100),
#         ('SPECIAL2', 'special', 150),
#         ('SPECIAL3', 'special', 200),
#         ('ADVANCED1', 'advanced', 350),
#         ('ADVANCED2', 'advanced', 400),
#         ('ADVANCED3', 'advanced', 450),
#     ]

#     )expiration_time = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

#     async with aiosqlite.connect(DB_NAME) as conn:
#         async with conn.cursor() as cursor:
#             await cursor.execute('DELETE FROM promo_codes')  # Очистка старых промокодов
#             for code, category, reward in promo_codes:
#                 await cursor.execute('INSERT INTO promo_codes (code, category, reward, expiration_time) VALUES (?, ?, ?, ?)',
#                                      (code, category, reward, expiration_time))
#             await conn.commit()

# # Обработка команды /start
# @dp.message_handler(commands=['start'])
# async def send_welcome(message: types.Message):
#     try:
#         user_id = message.from_user.id
#         username = message.from_user.username

#         # 1. Проверяем, зарегистрирован ли пользователь
#         user = await get_user(user_id)
#         if user:
#             # Если пользователь уже зарегистрирован
#             await message.reply(f"Привет, {user['username']}! Добро пожаловать обратно!")
#         else:
#             # Если пользователь новый, регистрируем его
#             await add_user(user_id, username)
#             await message.reply("Привет! Вы новый пользователь. Введите ваше имя, чтобы начать.")
#             return  # Завершаем обработку команды, пока пользователь не введет имя

#         # 2. Проверяем подписку на каналы
#         if await check_subscription(user_id, bot):
#             # Если пользователь подписан на оба канала
#             await message.reply("Вы подписаны на оба канала! Добро пожаловать!")
#             # Переходим к главному меню
#             await show_main_menu(message)
#         else:
#             # Если пользователь не подписан на оба канала
#             await message.reply("Пожалуйста, подпишитесь на оба канала, чтобы продолжить:")
#             await message.reply(f"1. {CHANNEL_ID_1}\n2. {CHANNEL_ID_2}")
            
#             # Кнопка для повторной проверки подписки
#             markup = InlineKeyboardMarkup()
#             check_btn = InlineKeyboardButton("Проверить подписку", callback_data='check_subscription')
#             markup.add(check_btn)
#             await message.reply("После подписки нажмите кнопку ниже для проверки:", reply_markup=markup)
    
#     except Exception as e:
#         logging.error(f"Ошибка при обработке команды /start: {e}")





# # Идентификаторы каналов
# CHANNEL_ID_1 = '@KLEV_TON'  # Замените на ваш первый канал
# CHANNEL_ID_2 = '@HMSTR_KOMBAT_BOT'  # Замените на ваш второй канал

# # Проверка подписки пользователя на оба канала
# async def check_subscription(user_id: int, bot: Bot) -> bool:
#     try:
#         # Проверка подписки на первый канал
#         member_1 = await bot.get_chat_member(chat_id=CHANNEL_ID_1, user_id=user_id)
#         # Проверка подписки на второй канал
#         member_2 = await bot.get_chat_member(chat_id=CHANNEL_ID_2, user_id=user_id)

#         # Проверка, что пользователь в обоих каналах как минимум является подписчиком
#         if member_1.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] and \
#            member_2.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
#             return True
#         else:
#             return False
#     except Exception as e:
#         logging.error(f"Ошибка при проверке подписки для пользователя {user_id}: {e}")
#         return False





# # Главное меню
# async def show_main_menu(message: types.Message):
#     try:
#         markup = InlineKeyboardMarkup()
#         promo_code_btn = InlineKeyboardButton("Активировать промокод", callback_data='activate_promo')
#         markup.add(promo_code_btn)
#         await message.reply("Выберите действие:", reply_markup=markup)
#     except Exception as e:
#         logging.error(f"Ошибка при отображении главного меню: {e}")

# # Обработка промокода
# @dp.callback_query_handler(lambda c: c.data == 'activate_promo')
# async def process_activate_promo(callback_query: types.CallbackQuery):
#     await bot.send_message(callback_query.from_user.id, "Введите ваш промокод:")
#     dp.register_message_handler(handle_promo_code)  # Ждем промокод



# ############################################
# # # Главное меню
# # async def show_main_menu(message: types.Message):
# #     try:
# #         markup = InlineKeyboardMarkup()
# #         promo_code_btn = InlineKeyboardButton("Активировать промокод", callback_data='activate_promo')
# #         markup.add(promo_code_btn)
# #         await message.reply("Выберите действие:", reply_markup=markup)
# #     except Exception as e:
# #         logging.error(f"Ошибка при отображении главного меню: {e}")

# # # Обработка промокода
# # @dp.callback_query_handler(lambda c: c.data == 'activate_promo')
# # async def process_activate_promo(callback_query: types.CallbackQuery):
# #     await bot.send_message(callback_query.from_user.id, "Введите ваш промокод:")
# #     dp.register_message_handler(handle_promo_code, state=None)  # Ждем промокод
# ############################################





# # Логика обработки введенного промокода
# async def handle_promo_code(message: types.Message):
#     promo_code = message.text.strip()
#     async with aiosqlite.connect(DB_NAME) as conn:
#         async with conn.cursor() as cursor:
#             await cursor.execute('SELECT reward, expiration_time FROM promo_codes WHERE code = ?', (promo_code,))
#             result = await cursor.fetchone()

#             if result:
#                 reward, expiration_time = result, category = result
#                 now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#                 if now < expiration_time:
#                     await update_user_balance(message.from_user.id, reward)
#                     await message.reply(f"Промокод принят! Вы получили {reward} монет.")
#                 else:
#                     await message.reply("Промокод истек.")
#             else:
#                 await message.reply("Неверный промокод. Попробуйте снова.")



# ######################################################
# # # Логика обработки введенного промокода
# # async def handle_promo_code(message: types.Message):
# #     promo_code = message.text.strip()
# #     async with aiosqlite.connect(DB_NAME) as conn:
# #         async with conn.cursor() as cursor:
# #             await cursor.execute('SELECT reward, expiration_time FROM promo_codes WHERE code = ?', (promo_code,))
# #             result = await cursor.fetchone()

# #             if result:
# #                 reward, expiration_time = result, category = result
# #                 now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# #                 if now < expiration_time:
# #                     await update_user_balance(message.from_user.id, reward)
# #                     await message.reply(f"Промокод принят! Вы получили {reward} монет.")
# #                 else:
# #                     await message.reply("Промокод истек.")
# #             else:
# #                 await message.reply("Неверный промокод. Попробуйте снова.")
# #######################################################



# # Запуск бота и инициализация базы данных

# async def main():
#     try:
#         await init_db()  # Инициализация базы данных
#         await generate_promo_codes()  # Генерация промокодов

#     except Exception as e:
#         logging.error(f"Ошибка при запуске бота: {e}")

#) if __name__ == '__main__':
#     asyncio.run(main())


##########################################################################################################################################################################










##########################################################################################################################################################################
#)import logging
# import os
# from dotenv import load_dotenv
# import asyncio
# from aiogram import Bot, Dispatcher, types
# from database import init_db, add_user, get_user, get_car_price, update_user_balance, log_earning, get_user_balance
# from payment_bot import create_payment_link
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# # Загрузка переменных окружения
# load_dotenv()

#)API_TOKEN = os.getenv('API_TOKEN')

# # Настройка логирования
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[
#         logging.FileHandler("bot.log"),
#         logging.StreamHandler()
#     ]
# )

#)bot = Bot(token=API_TOKEN)
# dp = Dispatcher(bot)

# # Обработка команды /start
# @dp.message_handler(commands=['start'])
# async def send_welcome(message: types.Message):
#     try:
#         user = await get_user(message.from_user.id)  # Проверяем, есть ли пользователь в БД
#         if user:
#             # Пользователь найден — приветствие и меню
#             await message.reply(f"Привет, {user['username']}! Добро пожаловать обратно!")
#         else:
#             # Если пользователя нет — просим ввести имя
#             await message.reply("Привет! Введите ваше имя, чтобы начать.")
#             return  # Выходим, ждем имя пользователя

#         # В любом случае показываем меню
#         await asyncio.sleep(1)
#         await show_main_menu(message)

#     except Exception as e:
#         logging.error(f"Ошибка при обработке команды /start: {e}")


# # Обработка имени пользователя
# @dp.message_handler(lambda message: message.text.isalpha())
# async def handle_name(message: types.Message):
#     try:
#         username = message.text
#         await add_user(message.from_user.id, username)  # Добавляем нового пользователя в БД
#         await message.reply(f"Добро пожаловать, {username}!")
        
#         # Показ главного меню
#         await asyncio.sleep(1)
#         await show_main_menu(message)

#     except Exception as e:
#         logging.error(f"Ошибка при обработке имени пользователя: {e}")

# #######################################################################################################
# # # Обработка команды /start
# # @dp.message_handler(commands=['start'])
# # async def send_welcome(message: types.Message):
# #     try:
# #         user = await get_user(message.from_user.id)
# #         if user:
# #             await message.reply(f"Привет, {user['username']}! Добро пожаловать обратно!")
# #         else:
# #             await message.reply("Привет! Введите ваше имя, чтобы начать.")
# #             await asyncio.sleep(2)
# #             await bot.send_message(message.from_user.id, "Для начала создайте свой профиль.")
# #     except Exception as e:
# #         logging.error(f"Ошибка при обработке команды /start: {e}")
# #
# # # Обработка имени пользователя
# # @dp.message_handler(lambda message: message.text.isalpha())
# # async def handle_name(message: types.Message):
# #     try:
# #         username = message.text
# #         await add_user(message.from_user.id, username)
# #         await message.reply(f"Добро пожаловать, {username}!")
# #         await asyncio.sleep(1)
# #         await show_main_menu(message)
# #     except Exception as e:
# #         logging.error(f"Ошибка при обработке имени пользователя: {e}")
# ######################################################################################################

# # Главное меню с новыми кнопками
# async def show_main_menu(message: types.Message):
#     try:
#         markup = InlineKeyboardMarkup()
#         promo_code_btn = InlineKeyboardButton("Ввести промокод", callback_data='enter_promo')
#         open_app_btn = InlineKeyboardButton("Открыть мини-приложение", url='https://botrichcars-3d6fdb98c849.herokuapp.com')  # Укажи ссылку на мини-приложение
#         markup.add(promo_code_btn, open_app_btn)
#         await message.reply("Выберите действие:", reply_markup=markup)
#     except Exception as e:
#         logging.error(f"Ошибка при отображении главного меню: {e}")

# # Обработка нажатия на кнопку "Ввести промокод"
# @dp.callback_query_handler(lambda c: c.data == 'enter_promo')
# async def process_enter_promo(callback_query: types.CallbackQuery):
#     try:
#         await bot.send_message(callback_query.from_user.id, "Введите ваш промокод:")
#         dp.register_message_handler(handle_promo_code, state=None)  # Ждем промокод
#     except Exception as e:
#         logging.error(f"Ошибка при запросе промокода: {e}")



# # Обработка промокода
# async def handle_promo_code(message: types.Message):
#     promo_code = message.text
#     if promo_code == "HAMSTER2024":  # Пример проверочного кода
#         await message.reply("Промокод принят! Вы получили бонус.")
#         # Здесь можно добавить логику для начисления бонусов или других действий
#     else:
#         await message.reply("Неверный промокод. Попробуйте снова.")


# # Генерация промокодов с подпиской
# def create_subscription_buttons(channels):
#     markup = InlineKeyboardMarkup()
#     for channel in channels:
#         markup.add(InlineKeyboardButton(text=f"Подписаться на {channel}", url=f"https://t.me/{channel}"))
#     return markup



# # Создание кнопок для подписки на канал
# async def check_all_subscriptions(user_id, channels):
#     subscribed_channels = []
    
#     for channel in channels:
#         try:
#             member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
#             if member.status in ['member', 'administrator', 'creator']:
#                 subscribed_channels.append(channel)
#         except Exception as e:
#             logging.error(f"Ошибка проверки канала {channel}: {e}")
    
#     )return len(subscribed_channels) == len(channels)



# # Обработка запроса для продвинутого, специального и обычного промокодов:
# @dp.callback_query_handler(lambda c: c.data == 'enter_advanced_promo_code')
# async def process_advanced_promo_code(callback_query: types.CallbackQuery):
#     user_id = callback_query.from_user.id
    
#     # Список каналов для продвинутого промокода (5 каналов)
#     advanced_channels = ['channel1', 'channel2', 'channel3', 'channel4', 'channel5']
    
#     # Генерируем кнопки для подписки
#     markup = create_subscription_buttons(advanced_channels)

#     # Проверяем подписан ли пользователь на все каналы
#     if await check_all_subscriptions(user_id, advanced_channels):
#         promo_code, reward, expiration_time = await create_promo_code(user_id, 'advanced')
#         await bot.send_message(user_id, f"Ваш продвинутый промокод: {promo_code}. Он действителен до {expiration_time} и принесет вам {reward} монет.")
#     else:
#         await bot.send_message(user_id, "Чтобы получить продвинутый промокод, подпишитесь на все каналы:", reply_markup=markup)

# )@dp.callback_query_handler(lambda c: c.data == 'enter_special_promo_code')
# async def process_special_promo_code(callback_query: types.CallbackQuery):
#     user_id = callback_query.from_user.id
    
#     # Список каналов для специального промокода (12 каналов)
#     special_channels = ['channel1', 'channel2', 'channel3', 'channel4', 'channel5', 'channel6', 'channel7', 'channel8', 'channel9', 'channel10', 'channel11', 'channel12']
    
#     # Генерируем кнопки для подписки
#     markup = create_subscription_buttons(special_channels)

#     # Проверяем подписан ли пользователь на все каналы
#     if await check_all_subscriptions(user_id, special_channels):
#         promo_code, reward, expiration_time = await create_promo_code(user_id, 'special')
#         await bot.send_message(user_id, f"Ваш специальный промокод: {promo_code}. Он действителен до {expiration_time} и принесет вам {reward} монет.")
#     else:
#         await bot.send_message(user_id, "Чтобы получить специальный промокод, подпишитесь на все каналы:", reply_markup=markup)



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
################################################################################################################################################################


























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
