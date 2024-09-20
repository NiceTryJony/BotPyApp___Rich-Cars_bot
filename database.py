import aiosqlite
import logging
from datetime import datetime, timedelta

DB_NAME = 'CARS2.db'

# Инициализация базы данных
async def init_db():
    async with aiosqlite.connect(DB_NAME) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('PRAGMA journal_mode=WAL;')  # Включение WAL режима

            # Создание таблицы users
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    balance REAL DEFAULT 0
                )
            ''')

            # Создание таблицы машин
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS cars (
                    car_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    power REAL NOT NULL
                )
            ''')

            # Создание таблицы покупок
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS purchases (
                    user_id INTEGER,
                    car_id INTEGER,
                    purchase_date TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY(car_id) REFERENCES cars(car_id) ON DELETE CASCADE
                )
            ''')

            # Создание таблицы доходов/заработков
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS earnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            ''')

            # Создание таблицы промокодов
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS promo_codes (
                    code TEXT PRIMARY KEY,
                    user_id INTEGER,
                    reward INTEGER,
                    expiration_date TEXT,
                    type TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            ''')
            await conn.commit()





# Добавление пользователя
async def add_user(user_id, username):
    try:
        async with aiosqlite.connect(DB_NAME) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('''INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)''', (user_id, username))
                await conn.commit()
    except Exception as e:
        logging.error(f"Ошибка при добавлении пользователя {user_id, username}: {e}")



# Получение данных пользователя
async def get_user(user_id):
    try:
            async with aiosqlite.connect(DB_NAME) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute('SELECT user_id, username, balance FROM users WHERE user_id = ?', (user_id,))
                    row = await cursor.fetchone()
                    if row:
                        return {'user_id': row[0], 'username': row[1], 'balance': row[2]}
                    else:
                        logging.warning(f"Пользователь с ID {user_id} не найден.")
                        return None
    except Exception as e:
        logging.error(f"Ошибка при получении пользователя {user_id}: {e}")



async def update_user_balance(user_id, amount):
    try:
            async with aiosqlite.connect(DB_NAME) as conn:
                async with conn.cursor() as cursor:
                    # Проверка существования пользователя
                    await cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
                    if await cursor.fetchone() is None:
                        raise ValueError("Пользователь не найден.")
                    
                    await cursor.execute('''UPDATE users SET balance = balance + ? WHERE user_id = ?''', (amount, user_id))
                    await conn.commit()
    except Exception as e:
        logging.error(f"Ошибка при обновлении баланса пользователя {user_id, amount}: {e}")




# Логирование дохода (покупки или заработка)
async def log_earning(user_id, amount):
    try:    
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            async with aiosqlite.connect(DB_NAME) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute('''INSERT INTO earnings (user_id, amount, timestamp) VALUES (?, ?, ?)''', (user_id, amount, now))
                    await conn.commit()
                    logging.info(f"Логирование дохода: пользователь {user_id}, сумма {amount}.")
    except Exception as e:
        logging.error(f"Ошибка при добавлении дохода {user_id, amount}: {e}")




# Получение цены машины
async def get_car_price(car_id):
    try:
            async with aiosqlite.connect(DB_NAME) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute('''SELECT price FROM cars WHERE car_id = ?''', (car_id,))
                    result = await cursor.fetchone()
                    if result:
                        return result[0]
                    else:
                        logging.warning(f"Машина с ID {car_id} не найдена.")
                        return None
    except Exception as e:
        logging.error(f"Ошибка при получении машины {car_id}: {e}")




# Получение баланса пользователя
async def get_user_balance(user_id):
    try:
                async with aiosqlite.connect(DB_NAME) as conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute('''SELECT balance FROM users WHERE user_id = ?''', (user_id,))
                        result = await cursor.fetchone()
                        return result[0] if result else 0
    except Exception as e:
        logging.error(f"Ошибка при получении баланса пользователя {user_id}: {e}")


# Генерация рандомного промокода
async def create_promo_code(user_id, promo_type):
    promo_code = f"{promo_type}_{user_id}_{int(datetime.now().timestamp())}"  # Генерация уникального промокода
    reward = 0

    # Определение количества монет в зависимости от типа промокода
    if promo_type == 'advanced':
        reward = 100
    elif promo_type == 'special':
        reward = 50
    elif promo_type == 'regular':
        reward = 10

    expiration_time = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')  # Промокод действителен 7 дней

    try:
        async with aiosqlite.connect(DB_NAME) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('''
                    INSERT INTO promo_codes (code, user_id, reward, expiration_date, type) VALUES (?, ?, ?, ?, ?)
                ''', (promo_code, user_id, reward, expiration_time, promo_type))
                await conn.commit()
        return promo_code, reward, expiration_time
    except Exception as e:
        logging.error(f"Ошибка при создании промокода для пользователя {user_id}: {e}")
        return None, 0, None













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