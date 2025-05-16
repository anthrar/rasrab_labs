import logging
import os
import asyncio
from dotenv import load_dotenv
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

from dotenv import dotenv_values
config = dotenv_values(path.join(path.dirname(__file__), ".env"))


def db_connect():
    global DBS
    conn = psycopg2.connect(
        host = '127.0.0.1',
        database = 'Krasov_rasrab_5',
        user = 'pavel_krasov_knowledge_base',
        password = '777'
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)
    DBS = '%s'
    
    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

load_dotenv()


# получение токена из переменных окружения
TOKEN = config["API_TOKEN"]
print(TOKEN)

class CurrencyConverterStates(StatesGroup):
    check_admin = State()
    add_currency_name = State()
    add_rate = State()
    delete_currency_name = State()
    delete_rate = State()
    change_rate = State()
    change_currency_name = State()
    convert_name = State()
    convert_sum = State()

bot = Bot(token=TOKEN)

dp = Dispatcher()

conn, cur = db_connect()
cur.execute("select chat_id from admins")
admins_ids = []
for row in cur.fetchall():
    admins_ids.append(row['chat_id'])
print(admins_ids)
db_close(conn, cur)

def getDBCurrencies():
    conn, cur = db_connect()
    cur.execute("select currency_name, rate from currencies")
    currencies = {}
    for row in cur.fetchall():
        currencies[row['currency_name'] ] = float(row['rate'])
    db_close(conn, cur)
    return currencies

#Прописываю пользовательские и администраторские команды
admin_commands = [
    BotCommand(command="/start", description = "Начало" ),
    BotCommand(command="/manage_currency", description = "Работа с валютой" ),
    BotCommand(command="/get_currency", description = "Вывод таблицы валют" ),
    BotCommand(command="/convert", description = "Конвертация заданной суммы в рубли" )
]

user_commands = [
    BotCommand(command="/start", description = "Начало" ),
    BotCommand(command="/get_currency", description = "Вывод таблицы валют" ),
    BotCommand(command="/convert", description = "Вывод таблицы валют" )
]

async def setup_bot_commands(bot:Bot, admins):
    #Устанавливаю команды для обычных пользователей
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

    #устанавливаю команды для админов
    for admin_id in admins:
        await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin_id))




@dp.message(Command('start'))
async def start(message: types.Message, state:CurrencyConverterStates):
    await message.reply('Добро пожаловать в бот!')


@dp.message(Command('manage_currency'))
async def manage_currency(message: types.Message, state:CurrencyConverterStates):
    global admins_ids # Обращаюсь к внешней переменной
    # Проверяю есть ли у пользователя права администратора
    if str(message.chat.id) not in admins_ids:
        await message.reply('Нет доступа к команде у' + str(message.chat.id) )
        return
    # Создаю клавиатуру
    builder = InlineKeyboardBuilder()
    builder.button(text="Добавить валюту", callback_data="add_currency")
    builder.button(text="Удалить валюту", callback_data="delete_currency")
    builder.button(text="Изменить курс валюты", callback_data="change_currency")
    await message.answer("Выберите то, что вам надо: ", reply_markup=builder.as_markup())


@dp.callback_query(F.data == 'add_currency')
async def add_currency(query: types.CallbackQuery, state:CurrencyConverterStates):
   await state.set_state(CurrencyConverterStates.add_currency_name) 
   await bot.send_message(chat_id=query.message.chat.id, text="Введите название валюты")
    
@dp.message(CurrencyConverterStates.add_currency_name)
async def add_currency_name(message: types.Message, state:CurrencyConverterStates):
    name = message.text

    currencies = getDBCurrencies() 
    if name in currencies:
        await message.reply("Валюта уже существует")
        await state.set_state(None)
        return

    await state.update_data(add_currency_name=name)
    await state.set_state(CurrencyConverterStates.add_rate)
    await message.reply("Введите курс:")
    
@dp.message(CurrencyConverterStates.add_rate)
async def add_rate(message: types.Message, state:CurrencyConverterStates):
    raw_rate = message.text.replace(",", ".")
    try:
        rate = float(raw_rate)
    except ValueError:
        await message.reply("Неправильное значение, введите ещё раз")
        return
    data = await state.get_data()
    name = data.get("add_currency_name", "ERROR")
    await state.update_data(add_currency_name=name)
    await state.set_state(CurrencyConverterStates.add_rate)
    conn, cur = db_connect()
    cur.execute("insert into currencies(currency_name, rate) values(%s, %s)", (name, rate))
    db_close(conn, cur)
    await state.set_state(None)
    await message.reply(f"Валюта: {name} успешно добавлена")


@dp.callback_query(F.data == 'delete_currency')
async def delete_currency(query: types.CallbackQuery, state:CurrencyConverterStates):
   await state.set_state(CurrencyConverterStates.delete_currency_name) 
   await bot.send_message(chat_id=query.message.chat.id, text="Введите название валюты, которую вы хотите удалить")

@dp.message(CurrencyConverterStates.delete_currency_name)
async def delete_currency_name(message: types.Message, state:CurrencyConverterStates):
    name = message.text

    currencies = getDBCurrencies() 
    if not name in currencies:
        await message.reply("Нет такой валюты, введите ещё раз")
        return
    
    conn, cur = db_connect()
    cur.execute("delete from currencies where currency_name = %s", (name, ))
    db_close(conn, cur)
    await state.set_state(None)
    await message.reply(f"Валюта: {name} успешно удалена")


@dp.callback_query(F.data == 'change_currency')
async def change_currency(query: types.CallbackQuery, state:CurrencyConverterStates):
   await state.set_state(CurrencyConverterStates.change_currency_name) 
   await bot.send_message(chat_id=query.message.chat.id, text="Введите название валюты, которую вы хотите изменить")

@dp.message(CurrencyConverterStates.change_currency_name)
async def change_currency_nam(message: types.Message, state:CurrencyConverterStates):
    name = message.text
    currencies = getDBCurrencies() 
    if not name in currencies:
        await message.reply("Нет такой валюты, введите ещё раз")
        return

    await state.update_data(change_currency_name=name)
    await state.set_state(CurrencyConverterStates.change_rate)
    await message.reply("Введите курс:")



@dp.message(CurrencyConverterStates.change_rate)
async def change_rate(message: types.Message, state:CurrencyConverterStates):
    raw_rate = message.text.replace(",", ".")
    try:
        rate = float(raw_rate)
    except ValueError:
        await message.reply("Неправильное значение, введите ещё раз")
        return
    data = await state.get_data()
    name = data.get("change_currency_name", "ERROR")
    await state.update_data(change_currency_name=name)
    await state.set_state(CurrencyConverterStates.change_rate)

    conn, cur = db_connect()
    cur.execute("update currencies set rate=%s where currency_name = %s", (rate, name ))
    db_close(conn, cur)

    await state.set_state(None)
    await message.reply(f"Валюта: {name} успешно изменена")

@dp.message(Command('get_currency'))
async def get_currency(message: types.Message, state:CurrencyConverterStates):
    reply = 'Таблица валют\n\n'
    
    currencies = getDBCurrencies() 
    for name, rate in currencies.items():
        reply +=  f"{name} = {rate}\n" 
 
    await message.reply(reply)


@dp.message(Command('convert'))
async def convert(message: types.Message, state:CurrencyConverterStates):
    await state.set_state(CurrencyConverterStates.convert_name)
    await message.reply('Введите название валюты: ')

@dp.message(CurrencyConverterStates.convert_name)
async def convert_name(message: types.Message, state:CurrencyConverterStates):
    raw_name = message.text
    currencies = getDBCurrencies()
    if raw_name not in currencies:
        await message.reply('Нет такой валюты. Введите ещё раз')
        return
    await state.update_data(convert_name=message.text)
    await state.set_state(CurrencyConverterStates.convert_sum)
    await message.reply('Введите сумму: ')

@dp.message(CurrencyConverterStates.convert_sum)
async def convert_sum(message: types.Message, state:CurrencyConverterStates):
    raw_sum = message.text
    raw_sum = raw_sum.replace(',', '.')
    await state.update_data(convert_sum=raw_sum)
    try:
        sum = float(raw_sum)
    except ValueError:
        await message.reply('Неправильное значение. Введите ещё раз.')
        return
    data = await state.get_data() #достаю данные, которые сохранились
    currency = data.get("convert_name", "ОШИБКА")
    await state.set_state(None)

    currencies = getDBCurrencies()
    if currency not in currencies:
        await message.reply('Такого быть не может')
        return
    rate = currencies[currency]
    result = sum*rate
    await message.reply('Итоговая сумма составила: ' + str(result))



async def main():
    await setup_bot_commands(bot, admins_ids)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main()) 