import aiosqlite
import logging
import os
from datetime import datetime

# Получение имени базы данных из переменной окружения или дефолтное значение
DB_NAME = os.getenv('DB_NAME', 'CARS2.db')

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def check_tables():
    """Проверить наличие таблиц в базе данных и вывести их имена в лог."""
    async with aiosqlite.connect(DB_NAME) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = await cursor.fetchall()
            logging.info(f"Таблицы в базе данных: {tables}")


async def init_db():
    """Инициализация базы данных, создание таблиц и вставка данных."""
    logging.info("Инициализация базы данных...")
    try:
        async with aiosqlite.connect(DB_NAME) as conn:
            await conn.execute('PRAGMA journal_mode=WAL;')
            # Создание таблиц
            await create_table(conn, "users", '''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    balance REAL DEFAULT 0
                )
            ''')
            await create_table(conn, "cars", '''
                CREATE TABLE IF NOT EXISTS cars (
                    car_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    power REAL NOT NULL,
                    type TEXT NOT NULL
                )
            ''')
            await create_table(conn, "purchases", '''
                CREATE TABLE IF NOT EXISTS purchases (
                    user_id INTEGER,
                    car_id INTEGER,
                    purchase_date TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY(car_id) REFERENCES cars(car_id) ON DELETE CASCADE
                )
            ''')
            await create_table(conn, "earnings", '''
                CREATE TABLE IF NOT EXISTS earnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            ''')
            await create_table(conn, "channels", '''
                CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    link TEXT NOT NULL,
                    promo_type TEXT NOT NULL
                )
            ''')
            # Вставка данных в таблицу channels, если они не существуют
            await conn.execute('''INSERT OR IGNORE INTO channels (name, link, promo_type) VALUES
                ('Channel 1', 'https://t.me/channel1', 'regular'),
                ('Channel 2', 'https://t.me/channel2', 'special'),
                ('Channel 3', 'https://t.me/klev_ton', 'advanced')
            ''')
            await create_table(conn, "promo_codes", '''
                CREATE TABLE IF NOT EXISTS promo_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL UNIQUE,
                    category TEXT NOT NULL,
                    reward INTEGER NOT NULL,
                    expiration_time TEXT NOT NULL
                )
            ''')
            await create_table(conn, "used_promo_codes", '''
                CREATE TABLE IF NOT EXISTS used_promo_codes (
                    user_id INTEGER,
                    promo_code TEXT,
                    PRIMARY KEY (user_id, promo_code)
                )
            ''')

            await conn.commit()

        logging.info("Инициализация базы данных завершена.")
    except Exception as e:
        logging.error(f"Ошибка при инициализации базы данных: {e}")


async def create_table(conn, table_name: str, create_table_sql: str):
    """Вспомогательная функция для создания таблицы."""
    try:
        logging.info(f"Создание таблицы {table_name}...")
        await conn.execute(create_table_sql)
        logging.info(f"Таблица {table_name} успешно создана или уже существует.")
    except Exception as e:
        logging.error(f"Ошибка при создании таблицы {table_name}: {e}", exc_info=True)


async def add_user(user_id: int, username: str):
    """Добавить пользователя в базу данных."""
    if not isinstance(user_id, int) or user_id <= 0:
        logging.error("{user_id} должен быть положительным целым числом.")
        return
    
    if not username or not isinstance(username, str):
        logging.error("username должен быть непустой строкой.")
        return

    try:
        async with aiosqlite.connect(DB_NAME) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
                await conn.commit()
                logging.info(f"Пользователь {username} с ID {user_id} успешно добавлен.")
    except Exception as e:
        logging.error(f"Ошибка при добавлении пользователя {user_id}: {e}", exc_info=True)


async def get_user(user_id: int) -> dict:
    """Получить информацию о пользователе из базы данных по ID пользователя."""
    if not isinstance(user_id, int) or user_id <= 0:
        logging.error("{user_id}user_id должен быть положительным целым числом.")
        return None

    try:
        async with aiosqlite.connect(DB_NAME) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT user_id, username, balance FROM users WHERE user_id = ?', (user_id,))
                row = await cursor.fetchone()
                if row:
                    return {
                        'user_id': row[0],
                        'username': row[1],
                        'balance': row[2]
                    }
                logging.warning(f"Пользователь с ID {user_id} не найден.")
                return None
    except Exception as e:
        logging.error(f"Ошибка получения пользователя {user_id}: {e}", exc_info=True)
        return None


async def update_user_balance(user_id: int, amount: float):
    """Обновить баланс пользователя."""
    if not isinstance(user_id, int) or user_id <= 0:
        logging.error("user_id должен быть положительным целым числом.")
        return

    if not isinstance(amount, (int, float)):
        logging.error("amount должен быть числом.")
        return

    try:
        async with aiosqlite.connect(DB_NAME) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
                result = await cursor.fetchone()
                if result is None:
                    raise ValueError("Пользователь не найден.")

                new_balance = result[0] + amount
                if new_balance < 0:
                    raise ValueError("Недостаточно средств.")

                await cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_balance, user_id))
                await conn.commit()
                logging.info(f"Баланс пользователя {user_id} обновлен. Новый баланс: {new_balance}.")
    except Exception as e:
        logging.error(f"Ошибка при обновлении баланса пользователя {user_id}: {e}", exc_info=True)


async def log_earning(user_id: int, amount: float):
    """Зарегистрировать доход пользователя."""
    if not isinstance(user_id, int) or user_id <= 0:
        logging.error("user_id должен быть положительным целым числом.")
        return

    if not isinstance(amount, (int, float)):
        logging.error("amount должен быть числом.")
        return

    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        async with aiosqlite.connect(DB_NAME) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('INSERT INTO earnings (user_id, amount, timestamp) VALUES (?, ?, ?)', (user_id, amount, now))
                await conn.commit()
                logging.info(f"Логирование дохода: пользователь {user_id}, сумма {amount}.")
    except Exception as e:
        logging.error(f"Ошибка при добавлении дохода пользователя {user_id}: {e}", exc_info=True)


async def get_car(car_id: int):
    """Получить информацию об автомобиле по ID."""
    async with aiosqlite.connect(DB_NAME) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT name, power, price FROM cars WHERE car_id = ?', (car_id,))
            return await cursor.fetchone()


async def get_car_price(car_id: int) -> float:
    """Получить цену автомобиля по его ID."""
    if not isinstance(car_id, int) or car_id <= 0:
        logging.error("car_id должен быть положительным целым числом.")
        return None

    try:
        async with aiosqlite.connect(DB_NAME) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT price FROM cars WHERE car_id = ?', (car_id,))
                result = await cursor.fetchone()
                if result:
                    return result[0]
                logging.warning(f"Автомобиль с ID {car_id} не найден.")
                return None
    except Exception as e:
        logging.error(f"Ошибка при получении цены автомобиля {car_id}: {e}", exc_info=True)
        return None


async def get_user_balance_and_details(user_id: int):
    """Получить данные о балансе, покупках и доходах пользователя."""
    if not isinstance(user_id, int) or user_id <= 0:
        logging.error("user_id должен быть положительным целым числом.")
        return None, None, None

    try:
        async with aiosqlite.connect(DB_NAME) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
                balance = await cursor.fetchone()
                balance = balance[0] if balance else None

                await cursor.execute('SELECT car_id, purchase_date FROM purchases WHERE user_id = ?', (user_id,))
                purchases = await cursor.fetchall()

                await cursor.execute('SELECT amount FROM earnings WHERE user_id = ?', (user_id,))
                earnings = await cursor.fetchall()

                return balance, purchases, earnings
    except Exception as e:
        logging.error(f"Ошибка при получении данных пользователя {user_id}: {e}", exc_info=True)
        return None, None, None


async def add_purchase(user_id: int, car_id: int):
    """Добавить покупку автомобиля пользователем."""
    if not isinstance(user_id, int) or user_id <= 0:
        logging.error("user_id должен быть положительным целым числом.")
        return

    if not isinstance(car_id, int) or car_id <= 0:
        logging.error("car_id должен быть положительным целым числом.")
        return

    try:
        car_price = await get_car_price(car_id)
        if car_price is None:
            logging.error(f"Не удалось получить цену для автомобиля с ID {car_id}.")
            return

        # Получение баланса пользователя
        user_balance = await get_user_balance_and_details(user_id)
        if user_balance is None or user_balance[0] is None:
            logging.error(f"Не удалось получить баланс для пользователя с ID {user_id}.")
            return
        
        if user_balance[0] < car_price:
            logging.error("Недостаточно средств для покупки.")
            return
        
        # Списание денег с баланса
        await update_user_balance(user_id, -car_price)

        # Добавление покупки
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        async with aiosqlite.connect(DB_NAME) as conn:
            await conn.execute('INSERT INTO purchases (user_id, car_id, purchase_date) VALUES (?, ?, ?)', (user_id, car_id, now))
            await conn.commit()
            logging.info(f"Пользователь {user_id} успешно купил автомобиль {car_id} за {car_price}.")
    except Exception as e:
        logging.error(f"Ошибка при добавлении покупки пользователем {user_id}: {e}", exc_info=True)


async def add_promo_code(code: str, category: str, reward: int, expiration_time: str):
    """Добавить новый промокод в базу данных."""
    if not isinstance(code, str) or not code:
        logging.error("code должен быть непустой строкой.")
        return

    if not isinstance(category, str) or not category:
        logging.error("category должен быть непустой строкой.")
        return

    if not isinstance(reward, int) or reward <= 0:
        logging.error("reward должен быть положительным целым числом.")
        return

    try:
        async with aiosqlite.connect(DB_NAME) as conn:
            await conn.execute('INSERT INTO promo_codes (code, category, reward, expiration_time) VALUES (?, ?, ?, ?)', 
                               (code, category, reward, expiration_time))
            await conn.commit()
            logging.info(f"Промокод {code} успешно добавлен.")
    except Exception as e:
        logging.error(f"Ошибка при добавлении промокода {code}: {e}", exc_info=True)


async def redeem_promo_code(user_id: int, code: str):
    """Использовать промокод."""
    if not isinstance(user_id, int) or user_id <= 0:
        logging.error("user_id должен быть положительным целым числом.")
        return

    if not isinstance(code, str) or not code:
        logging.error("code должен быть непустой строкой.")
        return

    try:
        async with aiosqlite.connect(DB_NAME) as conn:
            await conn.execute('BEGIN TRANSACTION;')

            # Проверка, был ли уже использован промокод
            await conn.execute('SELECT * FROM used_promo_codes WHERE user_id = ? AND promo_code = ?', (user_id, code))
            if await conn.fetchone() is not None:
                logging.warning(f"Промокод {code} уже был использован пользователем {user_id}.")
                await conn.execute('ROLLBACK;')
                return

            # Получение информации о промокоде
            await conn.execute('SELECT reward, expiration_time FROM promo_codes WHERE code = ?', (code,))
            promo_data = await conn.fetchone()
            if promo_data is None:
                logging.warning(f"Промокод {code} не найден.")
                await conn.execute('ROLLBACK;')
                return

            reward, expiration_time = promo_data

            # Проверка на истечение срока действия
            if datetime.now().strftime('%Y-%m-%d') > expiration_time:
                logging.warning(f"Промокод {code} истёк.")
                await conn.execute('ROLLBACK;')
                return

            # Применение вознаграждения
            await update_user_balance(user_id, reward)

            # Логирование использования промокода
            await conn.execute('INSERT INTO used_promo_codes (user_id, promo_code) VALUES (?, ?)', (user_id, code))
            await conn.commit()
            logging.info(f"Промокод {code} успешно применён пользователем {user_id}. Вознаграждение: {reward}.")
    except Exception as e:
        logging.error(f"Ошибка при использовании промокода {code} пользователем {user_id}: {e}", exc_info=True)













##################################################################################################################################################################################
# )import aiosqlite
# import logging
# import os
# from datetime import datetime

# # Получение имени базы данных из переменной окружения или дефолтное значение
# DB_NAME = os.getenv('DB_NAME', 'CARS2.db')

# # Настройка логирования
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# )async def check_tables():
#     """Проверить наличие таблиц в базе данных и вывести их имена в лог."""
#     async with aiosqlite.connect(DB_NAME) as conn:
#         async with conn.cursor() as cursor:
#             await cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#             tables = await cursor.fetchall()
#             logging.info(f"Таблицы в базе данных: {tables}")


# async def init_db():
#     """Инициализация базы данных, создание таблиц и вставка данных."""
#     logging.info("Инициализация базы данных...")
#     try:
#         async with aiosqlite.connect(DB_NAME) as conn:
#             await conn.execute('PRAGMA journal_mode=WAL;')
#             # Создание таблиц
#             await create_table(conn, "users", '''
#                 CREATE TABLE IF NOT EXISTS users (
#                     user_id INTEGER PRIMARY KEY,
#                     username TEXT NOT NULL,
#                     balance REAL DEFAULT 0
#                 )
#             ''')
#             await create_table(conn, "cars", '''
#                 CREATE TABLE IF NOT EXISTS cars (
#                     car_id INTEGER PRIMARY KEY,
#                     name TEXT NOT NULL,
#                     price REAL NOT NULL,
#                     power REAL NOT NULL,
#                     type TEXT NOT NULL
#                 )
#             ''')
#             await create_table(conn, "purchases", '''
#                 CREATE TABLE IF NOT EXISTS purchases (
#                     user_id INTEGER,
#                     car_id INTEGER,
#                     purchase_date TEXT NOT NULL,
#                     FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
#                     FOREIGN KEY(car_id) REFERENCES cars(car_id) ON DELETE CASCADE
#                 )
#             ''')
#             await create_table(conn, "earnings", '''
#                 CREATE TABLE IF NOT EXISTS earnings (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     user_id INTEGER,
#                     amount REAL NOT NULL,
#                     timestamp TEXT NOT NULL,
#                     FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
#                 )
#             ''')
#             await create_table(conn, "channels", '''
#                 CREATE TABLE IF NOT EXISTS channels (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     name TEXT NOT NULL,
#                     link TEXT NOT NULL,
#                     promo_type TEXT NOT NULL
#                 )
#             ''')
#             # Вставка данных в таблицу channels, если они не существуют
#             await conn.execute('''INSERT OR IGNORE INTO channels (name, link, promo_type) VALUES
#                 ('Channel 1', 'https://t.me/channel1', 'regular'),
#                 ('Channel 2', 'https://t.me/channel2', 'special'),
#                 ('Channel 3', 'https://t.me/klev_ton', 'advanced')
#             ''')
#             await create_table(conn, "promo_codes", '''
#                 CREATE TABLE IF NOT EXISTS promo_codes (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     code TEXT NOT NULL UNIQUE,
#                     category TEXT NOT NULL,
#                     reward INTEGER NOT NULL,
#                     expiration_time TEXT NOT NULL
#                 )
#             ''')
#             await create_table(conn, "used_promo_codes", '''
#                 CREATE TABLE IF NOT EXISTS used_promo_codes (
#                     user_id INTEGER,
#                     promo_code TEXT,
#                     PRIMARY KEY (user_id, promo_code)
#                 )
#             ''')

#             await conn.commit()

#         logging.info("Инициализация базы данных завершена.")
#     except Exception as e:
#         logging.error(f"Ошибка при инициализации базы данных: {e}")


# )async def create_table(conn, table_name, create_table_sql):
#     """Вспомогательная функция для создания таблицы."""
#     logging.info(f"Создание таблицы {table_name}...")
#     await conn.execute(create_table_sql)
#     logging.info(f"Таблица {table_name} успешно создана или уже существует.")


# # Добавление пользователя
# async def add_user(user_id: int, username: str):
#     """Добавить пользователя в базу данных."""
#     try:
#         async with aiosqlite.connect(DB_NAME) as conn:
#             async with conn.cursor() as cursor:
#                 await cursor.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
#                 await conn.commit()
#                 logging.info(f"Пользователь {username} с ID {user_id} успешно добавлен.")
#     except Exception as e:
#         logging.error(f"Ошибка при добавлении пользователя {user_id}: {e}", exc_info=True)


# # Получение информации о пользователе
# async def get_user(user_id: int) -> dict:
#     """Получить информацию о пользователе из базы данных по ID пользователя."""
#     try:
#         async with aiosqlite.connect(DB_NAME) as conn:
#             async with conn.cursor() as cursor:
#                 await cursor.execute('SELECT user_id, username, balance FROM users WHERE user_id = ?', (user_id,))
#                 row = await cursor.fetchone()
#                 if row:
#                     return {
#                         'user_id': row[0],
#                         'username': row[1],
#                         'balance': row[2]
#                     }
#                 logging.warning(f"Пользователь с ID {user_id} не найден.")
#                 return None
#     except Exception as e:
#         logging.error(f"Ошибка получения пользователя {user_id}: {e}", exc_info=True)
#         return None


# # Обновление баланса пользователя
# async def update_user_balance(user_id: int, amount: float):
#     """Обновить баланс пользователя."""
#     try:
#         async with aiosqlite.connect(DB_NAME) as conn:
#             async with conn.cursor() as cursor:
#                 await cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
#                 result = await cursor.fetchone()
#                 if result is None:
#                     raise ValueError("Пользователь не найден.")

#                 new_balance = result[0] + amount
#                 if new_balance < 0:
#                     raise ValueError("Недостаточно средств.")

#                 await cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_balance, user_id))
#                 await conn.commit()
#                 logging.info(f"Баланс пользователя {user_id} обновлен. Новый баланс: {new_balance}.")
#     except Exception as e:
#         logging.error(f"Ошибка при обновлении баланса пользователя {user_id}: {e}", exc_info=True)


# # Логирование дохода
# async def log_earning(user_id: int, amount: float):
#     """Зарегистрировать доход пользователя."""
#     try:
#         now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         async with aiosqlite.connect(DB_NAME) as conn:
#             async with conn.cursor() as cursor:
#                 await cursor.execute('INSERT INTO earnings (user_id, amount, timestamp) VALUES (?, ?, ?)', (user_id, amount, now))
#                 await conn.commit()
#                 logging.info(f"Логирование дохода: пользователь {user_id}, сумма {amount}.")
#     except Exception as e:
#         logging.error(f"Ошибка при добавлении дохода пользователя {user_id}: {e}", exc_info=True)


# # Получение цены автомобиля
# async def get_car_price(car_id: int) -> float:
#     """Получить цену автомобиля по его ID."""
#     try:
#         async with aiosqlite.connect(DB_NAME) as conn:
#             async with conn.cursor() as cursor:
#                 await cursor.execute('SELECT price FROM cars WHERE car_id = ?', (car_id,))
#                 result = await cursor.fetchone()
#                 if result:
#                     return result[0]
#                 logging.warning(f"Автомобиль с ID {car_id} не найден.")
#                 return None
#     except Exception as e:
#         logging.error(f"Ошибка при получении цены автомобиля {car_id}: {e}", exc_info=True)
#         return None


# # Получение данных о покупках и доходах пользователя
# async def get_user_balance_and_details(user_id: int):
#     """Получить данные о балансе, покупках и доходах пользователя."""
#     try:
#         async with aiosqlite.connect(DB_NAME) as conn:
#             # Получение общего баланса пользователя
#             async with conn.cursor() as cursor:
#                 await cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
#                 result = await cursor.fetchone()
#                 if not result:
#                     return None, None, None  # Если пользователя нет в базе данных

#     )            balance = result[0]

#                 # Получение данных о покупках пользователя
#                 await cursor.execute('''
#                     SELECT cars.name, cars.price, purchases.purchase_date 
#                     FROM purchases 
#                     JOIN cars ON purchases.car_id = cars.car_id 
#                     WHERE purchases.user_id = ?
#                 ''', (user_id,))
#                 purchases = await cursor.fetchall()

#                 # Получение данных о доходах пользователя
#                 await cursor.execute('''
#                     SELECT amount, timestamp 
#                     FROM earnings 
#                     WHERE user_id = ?
#                 ''', (user_id,))
#                 earnings = await cursor.fetchall()

#                 return balance, purchases, earnings
#     except Exception as e:
#         logging.error(f"Ошибка при получении данных пользователя {user_id}: {e}")
#         return None, None, None
##################################################################################################################################################################################


# # Пример использования функции добавления пользователя
# async def main():
#     await init_db()
#     await add_user(1, "User1")
#     user_info = await get_user(1)
#     logging.info(f"Информация о пользователе: {user_info}")

#     await update_user_balance(1, 100.0)
#     balance, purchases, earnings = await get_user_balance_and_details(1)
#     logging.info(f"Баланс: {balance}, Покупки: {purchases}, Доходы: {earnings}")

# # Для запуска функции main
# # if __name__ == "__main__":
# #     import asyncio
# #     asyncio.run(main())
















###############################################################################################################################################
# )import aiosqlite
# import logging
# import os
# from datetime import datetime

# # Получение имени базы данных из переменной окружения или дефолтное значение
# DB_NAME = os.getenv('DB_NAME', 'CARS2.db')


# )async def check_tables():
#     async with aiosqlite.connect(DB_NAME) as conn:
#         async with conn.cursor() as cursor:
#             await cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#             tables = await cursor.fetchall()
#             logging.info(f"Таблицы в базе данных: {tables}")



# async def init_db():
#     logging.info("Инициализация базы данных начата........................................................................................................................................")
#     try:
#         async with aiosqlite.connect(DB_NAME) as conn:
#             # Установка режима WAL (журнал транзакций)
#             await conn.execute('PRAGMA journal_mode=WAL;')

#             # Логирование создания таблицы users
#             logging.info("Таблица users создается")
#             await conn.execute('''
#                 CREATE TABLE IF NOT EXISTS users (
#                     user_id INTEGER PRIMARY KEY,
#                     username TEXT NOT NULL,
#                     balance REAL DEFAULT 0
#                 )
#             ''')
#             logging.info("Таблица users успешно создана или уже существует.")

#             # Логирование создания таблицы cars
#             logging.info("Таблица cars создается")
#             await conn.execute('''
#                 CREATE TABLE IF NOT EXISTS cars (
#                     car_id INTEGER PRIMARY KEY,
#                     name TEXT NOT NULL,
#                     price REAL NOT NULL,
#                     power REAL NOT NULL,
#                     type TEXT NOT NULL
#                 )
#             ''')
#             logging.info("Таблица cars успешно создана или уже существует.")

#             # Логирование создания таблицы purchases
#             logging.info("Таблица purchases создается")
#             await conn.execute('''
#                 CREATE TABLE IF NOT EXISTS purchases (
#                     user_id INTEGER,
#                     car_id INTEGER,
#                     purchase_date TEXT NOT NULL,
#                     FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
#                     FOREIGN KEY(car_id) REFERENCES cars(car_id) ON DELETE CASCADE
#                 )
#             ''')
#             logging.info("Таблица purchases успешно создана или уже существует.")

#             # Логирование создания таблицы earnings
#             logging.info("Таблица earnings создается")
#             await conn.execute('''
#                 CREATE TABLE IF NOT EXISTS earnings (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     user_id INTEGER,
#                     amount REAL NOT NULL,
#                     timestamp TEXT NOT NULL,
#                     FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
#                 )
#             ''')
#             logging.info("Таблица earnings успешно создана или уже существует.")

#             # Логирование создания таблицы channels
#             logging.info("Таблица channels создается")
#             await conn.execute('''
#                 CREATE TABLE IF NOT EXISTS channels (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     name TEXT NOT NULL,
#                     link TEXT NOT NULL,
#                     promo_type TEXT NOT NULL
#                 )
#             ''')
#             logging.info("Таблица channels успешно создана или уже существует.")

#             # Вставка данных в таблицу channels, если они не существуют
#             logging.info("Добавление данных в таблицу channels")
#             await conn.execute('''
#                 INSERT OR IGNORE INTO channels (name, link, promo_type) VALUES
#                 ('Channel 1', 'https://t.me/channel1', 'regular'),
#                 ('Channel 2', 'https://t.me/channel2', 'special'),
#                 ('Channel 3', 'https://t.me/klev_ton', 'advanced')
#             ''')
#             logging.info("Данные в таблицу channels успешно добавлены.")

#             # Логирование создания таблицы promo_codes
#             logging.info("Таблица promo_codes создается")
#             await conn.execute('''
#                 CREATE TABLE IF NOT EXISTS promo_codes (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     code TEXT NOT NULL UNIQUE,
#                     category TEXT NOT NULL,
#                     reward INTEGER NOT NULL,
#                     expiration_time TEXT NOT NULL
#                 )
#             ''')
#             logging.info("Таблица promo_codes успешно создана или уже существует.")

#             # Выполняем коммит всех изменений
#             await conn.commit()

#         logging.info("Инициализация базы данных завершена.")

#     except Exception as e:
#         logging.error(f"Ошибка при инициализации базы данных: {e}")







# # Добавление пользователя
# async def add_user(user_id, username):
#     try:
#         async with aiosqlite.connect(DB_NAME) as conn:
#             async with conn.cursor() as cursor:
#                 await cursor.execute('''INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)''', (user_id, username))
#                 await conn.commit()
#     except Exception as e:
#         logging.error(f"Ошибка при добавлении пользователя {user_id}: {e}", exc_info=True)



# # Получение информации о пользователе
# async def get_user(user_id):
#     try:
#         async with aiosqlite.connect(DB_NAME) as conn:
#             async with conn.cursor() as cursor:
#                 await cursor.execute('SELECT user_id, username, balance, is_subscribed FROM users WHERE user_id = ?', (user_id,))
#                 row = await cursor.fetchone()
#                 if row:
#                     return {'user_id': row[0], 
#                             'username': row[1],
#                             'balance': row[2], 
#                             'is_subscribed': row[3]
#                             }
#                 else:
#                     logging.warning(f"Пользователь с ID {user_id} не найден.")
#                     return None
#     except Exception as e:
#         logging.error(f"Ошибка при получении пользователя {user_id}: {e}", exc_info=True)




# # Обновление баланса пользователя
# async def update_user_balance(user_id, amount):
#     try:
#         async with aiosqlite.connect(DB_NAME) as conn:
#             async with conn.cursor() as cursor:
#                 await cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
#                 result = await cursor.fetchone()
#                 if result is None:
#                     raise ValueError("Пользователь не найден.")

#                 new_balance = result[0] + amount
#                 if new_balance < 0:
#                     raise ValueError("Недостаточно средств.")

#                 await cursor.execute('''UPDATE users SET balance = ? WHERE user_id = ?''', (new_balance, user_id))
#                 await conn.commit()
#     except Exception as e:
#         logging.error(f"Ошибка при обновлении баланса пользователя {user_id}: {e}", exc_info=True)


# # Логирование дохода
# async def log_earning(user_id, amount):
#     try:    
#         now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         async with aiosqlite.connect(DB_NAME) as conn:
#             async with conn.cursor() as cursor:
#                 await cursor.execute('''INSERT INTO earnings (user_id, amount, timestamp) VALUES (?, ?, ?)''', (user_id, amount, now))
#                 await conn.commit()
#                 logging.info(f"Логирование дохода: пользователь {user_id}, сумма {amount}.")
#     except Exception as e:
#         logging.error(f"Ошибка при добавлении дохода {user_id}: {e}", exc_info=True)

# # Получение цены автомобиля
# async def get_car_price(car_id):
#     try:
#         async with aiosqlite.connect(DB_NAME) as conn:
#             async with conn.cursor() as cursor:
#                 await cursor.execute('''SELECT price FROM cars WHERE car_id = ?''', (car_id,))
#                 result = await cursor.fetchone()
#                 if result:
#                     return result[0]
#                 else:
#                     logging.warning(f"Машина с ID {car_id} не найдена.")
#                     return None
#     except Exception as e:
#         logging.error(f"Ошибка при получении машины {car_id}: {e}", exc_info=True)

# # Получение баланса пользователя
# # async def get_user_balance(user_id):
# #     try:
# #         async with aiosqlite.connect(DB_NAME) as conn:
# #             async with conn.cursor() as cursor:
# #                 await cursor.execute('''SELECT balance FROM users WHERE user_id = ?''', (user_id,))
# #                 result = await cursor.fetchone()
# #                 return result[0] if result else 0
# #     except Exception as e:
# #         logging.error(f"Ошибка при получении баланса пользователя {user_id}: {e}", exc_info=True)


# )import aiosqlite

# # Функция для получения данных о покупках и доходах пользователя
# async def get_user_balance_and_details(user_id):
#     try:
#         async with aiosqlite.connect(DB_NAME) as conn:
#             # Получение общего баланса пользователя
#             async with conn.cursor() as cursor:
#                 await cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
#                 result = await cursor.fetchone()
#                 if not result:
#                     return None, None, None  # Если пользователя нет в базе данных

#    )             balance = result[0]

#                 # Получение данных о покупках пользователя
#                 await cursor.execute('''
#                     SELECT cars.name, cars.price, purchases.purchase_date 
#                     FROM purchases 
#                     JOIN cars ON purchases.car_id = cars.car_id 
#                     WHERE purchases.user_id = ?
#                 ''', (user_id,))
#                 purchases = await cursor.fetchall()

#                 # Получение данных о доходах пользователя
#                 await cursor.execute('''
#                     SELECT amount, timestamp 
#                     FROM earnings 
#                     WHERE user_id = ?
#                 ''', (user_id,))
#                 earnings = await cursor.fetchall()

#                 return balance, purchases, earnings
#     except Exception as e:
#         logging.error(f"Ошибка при получении данных пользователя {user_id}: {e}")
#         return None, None, None
















# )import aiosqlite
# from datetime import datetime

# )DB_NAME = 'CARS2.db'

# # Инициализация базы данных
# async def init_db():
#     async with aiosqlite.connect(DB_NAME) as conn:
#         async with conn.cursor() as cursor:
#             await cursor.execute('PRAGMA journal_mode=WAL;')  # Включение WAL режима

#             # Создание таблицы users
#             await cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS users (
#                     user_id INTEGER PRIMARY KEY,
#                     username TEXT,
#                     balance REAL DEFAULT 0
#                 )
#             ''')

#             # Таблица машин
#             await cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS cars (
#                     car_id INTEGER PRIMARY KEY,
#                     name TEXT,
#                     price REAL,
#                     power REAL
#                 )
#             ''')

#             # Таблица покупок
#             await cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS purchases (
#                     user_id INTEGER,
#                     car_id INTEGER,
#                     purchase_date TEXT,
#                     FOREIGN KEY(user_id) REFERENCES users(user_id),
#                     FOREIGN KEY(car_id) REFERENCES cars(car_id)
#                 )
#             ''')

#             await conn.commit()

# # Добавление пользователя
# async def add_user(user_id, username):
#     async with aiosqlite.connect(DB_NAME) as conn:
#         async with conn.cursor() as cursor:
#             await cursor.execute('''
#                 INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)
#             ''', (user_id, username))
#             await conn.commit()

# # Получение данных пользователя
# async def get_user(user_id):
#     async with aiosqlite.connect(DB_NAME) as conn:
#         async with conn.cursor() as cursor:
#             await cursor.execute('SELECT user_id, username, balance FROM users WHERE user_id = ?', (user_id,))
#             row = await cursor.fetchone()
#             if row:
#                 return {'user_id': row[0], 'username': row[1], 'balance': row[2]}
#             return None

# # Обновление баланса пользователя
# async def update_user_balance(user_id, amount):
#     async with aiosqlite.connect(DB_NAME) as conn:
#         async with conn.cursor() as cursor:
#             await cursor.execute('''
#                 UPDATE users SET balance = balance + ? WHERE user_id = ?
#             ''', (amount, user_id))
#             await conn.commit()

# # Логирование покупки (или заработка)
# async def log_earning(user_id, amount):
#     now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     async with aiosqlite.connect(DB_NAME) as conn:
#         async with conn.cursor() as cursor:
#             await cursor.execute('''
#                 INSERT INTO earnings (user_id, amount, timestamp)
#                 VALUES (?, ?, ?)
#             ''', (user_id, amount, now))
#             await conn.commit()

# # Получение цены машины
# async def get_car_price(car_id):
#     async with aiosqlite.connect(DB_NAME) as conn:
#         async with conn.cursor() as cursor:
#             await cursor.execute('''
#                 SELECT price FROM cars WHERE car_id = ?
#             ''', (car_id,))
#             result = await cursor.fetchone()
#             if result:
#                 return result[0]
#             return None

# # Проверка баланса пользователя
# async def get_user_balance(user_id):
#     async with aiosqlite.connect(DB_NAME) as conn:
#         async with conn.cursor() as cursor:
#             await cursor.execute('''
#                 SELECT balance FROM users WHERE user_id = ?
#             ''', (user_id,))
#             result = await cursor.fetchone()
#             return result[0] if result else 0


















# )import aiosqlite
# from datetime import datetime

# )DB_NAME = 'CARS2.db'

# # Инициализация базы данных
# async def init_db():
#     async with aiosqlite.connect(DB_NAME) as conn:
#         await conn.execute('PRAGMA journal_mode=WAL;')  # Включение WAL режима

#         # Создание таблицы users
#         await conn.execute('''
#             CREATE TABLE IF NOT EXISTS users (
#                 user_id INTEGER PRIMARY KEY,
#                 username TEXT,
#                 balance REAL DEFAULT 0
#             )
#         ''')

#         # Таблица машин
#         await conn.execute('''
#             CREATE TABLE IF NOT EXISTS cars (
#                 car_id INTEGER PRIMARY KEY,
#                 name TEXT,
#                 price REAL,
#                 power REAL
#             )
#         ''')

#         # Таблица покупок
#         await conn.execute('''
#             CREATE TABLE IF NOT EXISTS purchases (
#                 user_id INTEGER,
#                 car_id INTEGER,
#                 purchase_date TEXT,
#                 FOREIGN KEY(user_id) REFERENCES users(user_id),
#                 FOREIGN KEY(car_id) REFERENCES cars(car_id)
#             )
#         ''')

#         await conn.commit()

# # Добавление пользователя
# async def add_user(user_id, username):
#     async with aiosqlite.connect(DB_NAME) as conn:
#         await conn.execute('''
#             INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)
#         ''', (user_id, username))
#         await conn.commit()

# # Получение данных пользователя
# async def get_user(user_id):
#     async with aiosqlite.connect(DB_NAME) as conn:
#         cursor = await conn.execute('SELECT user_id, username, balance FROM users WHERE user_id = ?', (user_id,))
#         row = await cursor.fetchone()
#         if row:
#             return {'user_id': row[0], 'username': row[1], 'balance': row[2]}
#         return None

# # Обновление баланса пользователя
# async def update_user_balance(user_id, amount):
#     async with aiosqlite.connect(DB_NAME) as conn:
#         await conn.execute('''
#             UPDATE users SET balance = balance + ? WHERE user_id = ?
#         ''', (amount, user_id))
#         await conn.commit()

# # Логирование покупки (или заработка)
# async def log_earning(user_id, amount):
#     now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     async with aiosqlite.connect(DB_NAME) as conn:
#         await conn.execute('''
#             INSERT INTO earnings (user_id, amount, timestamp)
#             VALUES (?, ?, ?)
#         ''', (user_id, amount, now))
#         await conn.commit()

# # Получение цены машины
# async def get_car_price(car_id):
#     async with aiosqlite.connect(DB_NAME) as conn:
#         cursor = await conn.execute('''
#             SELECT price FROM cars WHERE car_id = ?
#         ''', (car_id,))
#         result = await cursor.fetchone()
#         if result:
#             return result[0]
#         return None

# # Проверка баланса пользователя
# async def get_user_balance(user_id):
#     async with aiosqlite.connect(DB_NAME) as conn:
#         cursor = await conn.execute('''
#             SELECT balance FROM users WHERE user_id = ?
#         ''', (user_id,))
#         result = await cursor.fetchone()
#         return result[0] if result else 0



























# (import aiosqlite)
# from datetime import datetime

# (DB_NAME = 'CARS2.db')

# # Асинхронная инициализация базы данных
# async def init_db():
#     async with aiosqlite.connect(DB_NAME) as conn:
#         await conn.execute('PRAGMA journal_mode=WAL;')
#         # (cursor = await conn.cursor())

#         # Создание таблицы users
#         await cursor.execute('''
#             CREATE TABLE IF NOT EXISTS users (
#                 user_id INTEGER PRIMARY KEY,
#                 username TEXT,
#                 balance REAL DEFAULT 0
#             )
#         ''')

#         # Таблица машин
#         await cursor.execute('''
#             CREATE TABLE IF NOT EXISTS cars (
#                 car_id INTEGER PRIMARY KEY,
#                 name TEXT,
#                 price REAL,
#                 power REAL
#             )
#         ''')

#         # Таблица покупок
#         await cursor.execute('''
#             CREATE TABLE IF NOT EXISTS purchases (
#                 user_id INTEGER,
#                 car_id INTEGER,
#                 purchase_date TEXT,
#                 FOREIGN KEY(user_id) REFERENCES users(user_id),
#                 FOREIGN KEY(car_id) REFERENCES cars(car_id)
#             )
#         ''')

#         await conn.commit()

# # Асинхронное добавление пользователя
# async def add_user(user_id, username):
#     async with aiosqlite.connect(DB_NAME) as conn:
#         cursor = await conn.cursor()
#         await cursor.execute('''
#             INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)
#         ''', (user_id, username))
#         await conn.commit()

# # Асинхронное получение данных пользователя
# async def get_user(user_id):
#     async with aiosqlite.connect(DB_NAME) as conn:
#         cursor = await conn.cursor()
#         await cursor.execute('SELECT user_id, username, balance FROM users WHERE user_id = ?', (user_id,))
#         row = await cursor.fetchone()
#         if row:
#             return {'user_id': row[0], 'username': row[1], 'balance': row[2]}
#         return None

# # Асинхронное обновление баланса пользователя
# async def update_user_balance(user_id, amount):
#     async with aiosqlite.connect(DB_NAME) as conn:
#         cursor = await conn.cursor()
#         await cursor.execute('''
#             UPDATE users SET balance = balance + ? WHERE user_id = ?
#         ''', (amount, user_id))
#         await conn.commit()

# # Асинхронное логирование заработка
# async def log_earning(user_id, amount):
#     now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     async with aiosqlite.connect(DB_NAME) as conn:
#         cursor = await conn.cursor()
#         await cursor.execute('''
#             INSERT INTO earnings (user_id, amount, timestamp)
#             VALUES (?, ?, ?)
#         ''', (user_id, amount, now))
#         await conn.commit()

# # Асинхронное получение цены машины
# async def get_car_price(car_id):
#     async with aiosqlite.connect(DB_NAME) as conn:
#         cursor = await conn.cursor()
#         await cursor.execute('''
#             SELECT price FROM cars WHERE car_id = ?
#         ''', (car_id,))
#         result = await cursor.fetchone()
#         if result:
#             return result[0]
#         return None

# # Асинхронная проверка баланса пользователя
# async def get_user_balance(user_id):
#     async with aiosqlite.connect(DB_NAME) as conn:
#         cursor = await conn.cursor()
#         await cursor.execute('''
#             SELECT balance FROM users WHERE user_id = ?
#         ''', (user_id,))
#         result = await cursor.fetchone()
#         return result[0] if result else 0

# # Пример запуска асинхронной инициализации базы данных
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(init_db())






































#(import) aiosqlite
#from datetime import datetime

# ВСЕ (действие) сделаны для их отключения (при потребности просто уберите ''' () ''')




#(DB_NAME = 'CARS2.db')

# (def init_db():)
#     with sqlite3.connect(DB_NAME) as conn:
#         cursor = conn.cursor()

#         # Создание таблицы users
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS users (
#                 user_id INTEGER PRIMARY KEY,
#                 username TEXT,
#                 balance REAL DEFAULT 0
#             )
#         ''')

#         # Таблица машин
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS cars (
#                 car_id INTEGER PRIMARY KEY,
#                 name TEXT,
#                 price REAL,
#                 power REAL
#             )
#         ''')

#         # Таблица покупок
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS purchases (
#                 user_id INTEGER,
#                 car_id INTEGER,
#                 purchase_date TEXT,
#                 FOREIGN KEY(user_id) REFERENCES users(user_id),
#                 FOREIGN KEY(car_id) REFERENCES cars(car_id)
#             )
#         ''')
#         conn.commit()
#         conn.close()

# # Добавление пользователя
# def add_user(user_id, username):
#     with sqlite3.connect(DB_NAME) as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#             INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)
#         ''', (user_id, username))
#         conn.commit()

# # Получение данных пользователя
#     #def get_user(user_id):
#     #   with sqlite3.connect(DB_NAME) as conn:
#     #      cursor = conn.cursor()
#     #     cursor.execute('''
#     #        SELECT * FROM users WHERE user_id = ?
#     #   ''', (user_id,))
#     #  return cursor.fetchone()
        
# (def get_user(user_id):)
#     with sqlite3.connect(DB_NAME) as conn:
#         cursor = conn.cursor()
#         cursor.execute('SELECT user_id, username, balance FROM users WHERE user_id = ?', (user_id,))
#         row = cursor.fetchone()
#         if row:
#             return {'user_id': row[0], 'username': row[1], 'balance': row[2]}
#         return None



# # Обновление баланса пользователя
# def update_user_balance(user_id, amount):
#     with sqlite3.connect(DB_NAME) as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#             UPDATE users SET balance = balance + ? WHERE user_id = ?
#         ''', (amount, user_id))
#         conn.commit()

# # Логирование покупки
# def log_earning(user_id, amount):
#     now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     with sqlite3.connect(DB_NAME) as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#             INSERT INTO earnings (user_id, amount, timestamp)
#             VALUES (?, ?, ?)
#         ''', (user_id, amount, now))
#         conn.commit()

# # Получение цены машины
# def get_car_price(car_id):
#     with sqlite3.connect(DB_NAME) as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#             SELECT price FROM cars WHERE car_id = ?
#         ''', (car_id,))
#         result = cursor.fetchone()
#         if result:
#             return result[0]
#         return None

# # Проверка баланса
# def get_user_balance(user_id):
#     with sqlite3.connect(DB_NAME) as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#             SELECT balance FROM users WHERE user_id = ?
#         ''', (user_id,))
#         result = cursor.fetchone()
#         return result[0] if result else 0

# (if __name__ == "__main__":)