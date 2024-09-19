import aiosqlite
from datetime import datetime

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

            await conn.commit()

# Добавление пользователя
async def add_user(user_id, username):
    async with aiosqlite.connect(DB_NAME) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)
            ''', (user_id, username))
            await conn.commit()

# Получение данных пользователя
async def get_user(user_id):
    async with aiosqlite.connect(DB_NAME) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT user_id, username, balance FROM users WHERE user_id = ?', (user_id,))
            row = await cursor.fetchone()
            if row:
                return {'user_id': row[0], 'username': row[1], 'balance': row[2]}
            return None

# Обновление баланса пользователя
async def update_user_balance(user_id, amount):
    async with aiosqlite.connect(DB_NAME) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''
                UPDATE users SET balance = balance + ? WHERE user_id = ?
            ''', (amount, user_id))
            await conn.commit()

# Логирование дохода (покупки или заработка)
async def log_earning(user_id, amount):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    async with aiosqlite.connect(DB_NAME) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''
                INSERT INTO earnings (user_id, amount, timestamp)
                VALUES (?, ?, ?)
            ''', (user_id, amount, now))
            await conn.commit()

# Получение цены машины
async def get_car_price(car_id):
    async with aiosqlite.connect(DB_NAME) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''
                SELECT price FROM cars WHERE car_id = ?
            ''', (car_id,))
            result = await cursor.fetchone()
            if result:
                return result[0]
            return None

# Получение баланса пользователя
async def get_user_balance(user_id):
    async with aiosqlite.connect(DB_NAME) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''
                SELECT balance FROM users WHERE user_id = ?
            ''', (user_id,))
            result = await cursor.fetchone()
            return result[0] if result else 0













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