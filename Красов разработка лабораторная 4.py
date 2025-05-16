import logging
import os
import asyncio
from dotenv import load_dotenv
from aiogram import Dispatcher, types, Bot
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup

load_dotenv()

# получение токена из переменных окружения
TOKEN = os.getenv("API_TOKEN")
#print(TOKEN)

class CurrencyConverterStates(StatesGroup):
    saving_name = State()
    saving_rate = State()
    convert_name = State()
    convert_sum = State()


bot = Bot(token=TOKEN)
currencies = {} #создаю словарь,  где будет сохранятся название валюты и её курс

dp = Dispatcher()


@dp.message(Command('save_currency'))
async def save_currency(message: types.Message, state:CurrencyConverterStates):
   await state.set_state(CurrencyConverterStates.saving_name)
   await message.reply('Введите название валюты: ')
@dp.message(CurrencyConverterStates.saving_name)
async def save_currency_name(message: types.Message, state:CurrencyConverterStates):
    await state.update_data(saving_name=message.text)
    await state.set_state(CurrencyConverterStates.saving_rate)
    data = await state.get_data() #достаю данные, которые сохранились
    saved_name = data.get("saving_name", "ОШИБКА")
    await message.reply('Введите курс ' + saved_name)
@dp.message(CurrencyConverterStates.saving_rate)
async def save_currency_rate(message: types.Message, state:CurrencyConverterStates):
    raw_rate = message.text #текст сообщения
    raw_rate = raw_rate.replace(',', '.')
    await state.update_data(saving_rate=raw_rate)
    await state.set_state(None)
    try:
        rate = float(raw_rate)
    except ValueError:
        await state.set_state(CurrencyConverterStates.saving_rate)
        await message.reply('Неправильное значение. Введите ещё раз.')
        return
    data = await state.get_data() #достаю данные, которые сохранились
    saved_name = data.get("saving_name", "ОШИБКА")
    currencies[saved_name] = rate #В словарь по ключу сохраняю значение
    printed_rate = str(currencies[saved_name])
    await message.reply('Сохранён курс ' + saved_name + ':' + printed_rate)

@dp.message(Command('convert'))
async def convert(message: types.Message, state:CurrencyConverterStates):
    await state.set_state(CurrencyConverterStates.convert_name)
    await message.reply('Введите название валюты: ')
@dp.message(CurrencyConverterStates.convert_name)
async def convert_name(message: types.Message, state:CurrencyConverterStates):
    raw_name = message.text
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
    if currency not in currencies:
        await message.reply('Такого быть не может')
        return
    rate = currencies[currency]
    result = sum*rate
    await message.reply('Итоговая сумма составила: ' + str(result))


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main()) 

