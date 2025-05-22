import logging
import os
import asyncio
from dotenv import load_dotenv
from aiogram import Dispatcher, types, Bot
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
import psycopg2
from psycopg2.extras import RealDictCursor
from os import path


def db_connect():
    global DBS
    conn = psycopg2.connect(
        host = '127.0.0.1',
        database = 'Krasov_rasrab_5',
        user = 'Krasov_rasrab_5',
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
TOKEN = os.getenv("API_TOKEN")
print(TOKEN)

bot = Bot(token=TOKEN)

dp = Dispatcher()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main()) 