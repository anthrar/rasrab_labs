import logging
import os
import asyncio
from aiogram import Dispatcher, types, Bot
from aiogram.filters.command import Command
from aiogram.types.bot_command import BotCommand
from aiogram.types.bot_command_scope import BotCommandScope
from aiogram.types.bot_command_scope_default import BotCommandScopeDefault
from aiogram.types.bot_command_scope_chat import BotCommandScopeChat
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
import psycopg2
from psycopg2.extras import RealDictCursor
from os import path
import datetime
import requests


from dotenv import dotenv_values
config = dotenv_values(path.join(path.dirname(__file__), ".env_rgz"))

# Функция подключения к БД
def db_connect():
    conn = psycopg2.connect(
        host = '127.0.0.1',
        database = 'RGZ_Rasrab',
        user = 'pavel_krasov_knowledge_base',
        password = '777'
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    return conn, cur

# Функция для работы с БД
def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

# получение токена из переменных окружения
TOKEN = config["API_TOKEN"]
print(TOKEN)

# Создание списка состояний
class CurrencyConverterStates(StatesGroup):
   reg_login = State()
   credit_sum = State()
   debet_sum = State()
   credit_date = State()
   debet_date = State()
   enter_budget = State()
    

# Список команд
user_commands = [
    BotCommand(command="/start", description = "Начало" ),
    BotCommand(command="/reg", description = "Зарегистрироваться" ),
    BotCommand(command="/add_operation", description = "Добавить операцию" ),
    BotCommand(command="/operations", description = "Операции" ),
    BotCommand(command="/setbudget", description = "Установить бюджет" ),
]

async def setup_bot_commands(bot:Bot):
    # Устанавливаю команды для пользователей
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())


# Генерация бота
bot = Bot(token=TOKEN)

# Диспетчер
dp = Dispatcher()


def PrintFloat(value):
    return f"{value:.2f}"


# Команда "Начало"
@dp.message(Command('start'))
async def start(message: types.Message, state:CurrencyConverterStates):
    await message.reply('Добро пожаловать в бот!')


# Команда "Регистрация"
@dp.message(Command('reg'))
async def reg(message: types.Message, state:CurrencyConverterStates):
    conn, cur = db_connect()
    cur.execute('select count(*) as count from users where chat_id=%s', (str(message.chat.id), ))
    user_count = cur.fetchone() # Количество пользователей
    if user_count["count"] > 0:
        await message.reply('Пользователь уже зарегестрирован')
        db_close(conn, cur)
        return
    else:
        await state.set_state(CurrencyConverterStates.reg_login)
        await message.reply('Введите логин')
        db_close(conn, cur)
        return
@dp.message(CurrencyConverterStates.reg_login)
async def reg_login(message: types.Message, state:CurrencyConverterStates):
    name = message.text
    chat_id = str(message.chat.id)
    conn, cur = db_connect()
    cur.execute('insert into users(name, chat_id) values(%s, %s)', (name, chat_id))
    await message.reply('Логин введён. Вы зарегистрированы.')
    db_close(conn, cur)
    await state.set_state(None)

    
# Команда "Добавить операцию"
@dp.message(Command('add_operation'))
async def add_operation(message: types.Message, state:CurrencyConverterStates):
    conn, cur = db_connect()
    cur.execute('select count(*) as count from users where chat_id=%s', (str(message.chat.id), ))
    user_count = cur.fetchone() # Количество пользователей
    if user_count["count"] == 0:
        await message.reply('Пользователь не зарегестрирован')
        return
    # Создаю клавиатуру
    builder = InlineKeyboardBuilder()
    builder.button(text="Расход", callback_data="credit")
    builder.button(text="Доход", callback_data="debet")
    await message.answer("Выберите то, что вам надо: ", reply_markup=builder.as_markup())
    db_close(conn, cur)
# Делаю обработчики кнопок
# Кнопка "Расход"
@dp.callback_query(F.data == 'credit')
async def credit(query: types.CallbackQuery, state:CurrencyConverterStates):
   await state.set_state(CurrencyConverterStates.credit_sum) 
   await bot.send_message(chat_id=query.message.chat.id, text="Пожалуйста, введите сумму")
@dp.message(CurrencyConverterStates.credit_sum)
async def credit_sum(message: types.Message, state:CurrencyConverterStates):
    raw_sum = message.text
    raw_sum = raw_sum.replace(',', '.')
    try:
        sum = float(raw_sum)
    except ValueError:
        await message.reply('Неправильное значение. Введите ещё раз.')
        return
    await state.update_data(credit_sum=sum)
    await state.set_state(CurrencyConverterStates.credit_date)
    await message.reply('Пожалуйста, введите дату в формате ГГГГ-мм-дд')
@dp.message(CurrencyConverterStates.credit_date)
async def credit_date(message: types.Message, state:CurrencyConverterStates):
    raw_date = message.text
    try:
        date = datetime.datetime.strptime(raw_date, "%Y-%m-%d")
    except:
        await message.reply('Введите дату правильно в формате ГГГГ-мм-дд')
        return
    data = await state.get_data()
    sum = data['credit_sum']
    conn, cur = db_connect()
    cur.execute('insert into operations(date, sum, chat_id, type_operation) values(%s, %s, %s, %s)', (date, sum, str(message.chat.id), 'credit'))
    db_close(conn, cur)
    await message.reply('Операция добавлена')
    await state.set_state(None)

# Кнопка "Доход"
@dp.callback_query(F.data == 'debet')
async def credit(query: types.CallbackQuery, state:CurrencyConverterStates):
   await state.set_state(CurrencyConverterStates.debet_sum) 
   await bot.send_message(chat_id=query.message.chat.id, text="Пожалуйста, введите сумму")
@dp.message(CurrencyConverterStates.debet_sum)
async def debet_sum(message: types.Message, state:CurrencyConverterStates):
    raw_sum = message.text
    raw_sum = raw_sum.replace(',', '.')
    try:
        sum = float(raw_sum)
    except ValueError:
        await message.reply('Неправильное значение. Введите ещё раз.')
        return
    await state.update_data(debet_sum=sum)
    await state.set_state(CurrencyConverterStates.debet_date)
    await message.reply('Пожалуйста, введите дату')
@dp.message(CurrencyConverterStates.debet_date)
async def debet_date(message: types.Message, state:CurrencyConverterStates):
    raw_date = message.text
    try:
        date = datetime.datetime.strptime(raw_date, "%Y-%m-%d")
    except:
        print('Введите дату правильно')
        return
    data = await state.get_data()
    sum = data['debet_sum']
    conn, cur = db_connect()
    cur.execute('insert into operations(date, sum, chat_id, type_operation) values(%s, %s, %s, %s)', (date, sum, str(message.chat.id), 'debet'))
    db_close(conn, cur)
    await message.reply('Операция добавлена')
    await state.set_state(None)


# Команда "Операции"
@dp.message(Command('operations'))
async def operations(message: types.Message, state:CurrencyConverterStates):
    conn, cur = db_connect()
    cur.execute('select count(*) as count from users where chat_id=%s', (str(message.chat.id), ))
    user_count = cur.fetchone() # Количество пользователей
    if user_count["count"] == 0:
        await message.reply('Пользователь не зарегестрирован')
        return
    # Создаю клавиатуру
    builder = InlineKeyboardBuilder()
    builder.button(text="RUB", callback_data="RUB")
    builder.button(text="EUR", callback_data="EUR")
    builder.button(text="USD", callback_data="USD")
    await message.answer("Выберите то, что вам надо: ", reply_markup=builder.as_markup())
    db_close(conn, cur)
# Делаю обработчики кнопок
# Кнопка "Список операций"
@dp.callback_query(F.data.in_({"RUB", "EUR", "USD"}))
async def RUB(query: types.CallbackQuery, state:CurrencyConverterStates):
    currency = query.data
    if currency == 'RUB':
        rate = 1
    else:
        r = requests.get('http://127.0.0.1:5000/rate?currency=' + currency)
        if r.status_code != 200:
            await query.message.answer('Сервис курса валют не работает')
            return
        else:
            data = r.json()
            rate = data['rate']
    conn, cur = db_connect()
    cur.execute('select * from operations where chat_id=%s', (str(query.message.chat.id), ))
    operations = ''
    income = 0
    expence = 0 
    rows = cur.fetchall()
    for row in rows:
        if row["type_operation"] == "credit":
            operation_type = "Расход"
            expence += row['sum']/rate
        else:
            operation_type = "Доход"
            income += row['sum']/rate
        operations += (operation_type + ' ' + currency + ' ' + row['date'].strftime('%Y-%m-%d') 
                       + ' ' + PrintFloat(row['sum']/rate) + '\n')
    operations += "Доход всего " + PrintFloat( income) + '\n'
    operations += "Расход всего " + PrintFloat( expence) + '\n'
    month = datetime.datetime.now().strftime("%m")
    cur.execute('select budget from budget where month=%s and chat_id=%s', (month, str(query.message.chat.id) ))
    rows = cur.fetchall()
    if rows:
        operations += 'Бюджет на текущий месяц: ' + PrintFloat(rows[0]['budget']/rate)
    db_close(conn, cur)
    await query.message.answer(operations)



# Команда "Установить бюджет"
@dp.message(Command('setbudget'))
async def setbudget(message: types.Message, state:CurrencyConverterStates):
    conn, cur = db_connect()
    cur.execute('select count(*) as count from users where chat_id=%s', (str(message.chat.id), ))
    user_count = cur.fetchone() # Количество пользователей
    if user_count["count"] == 0:
        await message.reply('Пользователь не зарегестрирован')
        return
    await state.set_state(CurrencyConverterStates.enter_budget)
    await message.reply('Введите бюджет на текущий месяц')
@dp.message(CurrencyConverterStates.enter_budget)
async def enter_budget(message: types.Message, state:CurrencyConverterStates):
    raw_budget = message.text
    raw_budget = raw_budget.replace(',', '.')
    try:
        budget = float(raw_budget)
    except ValueError:
        await message.reply('Неправильное значение. Введите ещё раз.')
        return
    await state.set_state(None)
    month = datetime.datetime.now().strftime("%m")
    conn, cur = db_connect()
    cur.execute('delete from budget where chat_id = %s and month=%s', (str(message.chat.id), month ))
    cur.execute('insert into budget(month, budget, chat_id) values(%s, %s, %s)', (month, budget, str(message.chat.id)))
    db_close(conn, cur)
    await message.reply('Информация успешно сохранена.')


async def main():
    await setup_bot_commands(bot)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main()) 