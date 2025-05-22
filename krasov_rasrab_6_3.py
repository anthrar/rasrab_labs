from flask import Flask, jsonify
from flask import request
import random
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)


# Функция подключения к БД
def db_connect():
    conn = psycopg2.connect(
        host = '127.0.0.1',
        database = 'Krasov_Rasrab_6',
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

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/role", methods = ['GET'])
def role():
    chat_id = request.args.get('chat_id', '-')
    conn, cur = db_connect()
    cur.execute('select count(*) as count from admins where chat_id=%s', (chat_id, ))
    row = cur.fetchone()
    db_close(conn, cur)
    if row['count'] == 0:
        return {'role': 'user'}
    else:
        return {'role': 'admin'}
    

@app.route("/admins", methods = ['GET'])
def admins():
    conn, cur = db_connect()
    cur.execute('select chat_id from admins')
    result = []
    # Получаем список всех наших админов
    for row in cur.fetchall():
        result.append(row['chat_id'])
    db_close(conn, cur)
    return {'admins': result}


if __name__ == '__main__':
    app.run(debug=True, port=5003)

