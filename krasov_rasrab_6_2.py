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


@app.route("/convert", methods = ['GET'])
def convert():
    currency_name = request.args.get('currency', '-')
    sum = request.args.get('sum', '-')
    if currency_name == '-':
        return jsonify ({"message": "валюта не передана"}), 400
    if sum == '-':
        return jsonify ({"message": "Сумма не передана"}), 400
    try:
        sum = float(sum)
    except ValueError:
        return jsonify ({"message": "Неправильное значение суммы"}), 400
    conn, cur = db_connect()
    cur.execute('select count(*) as count from currencies where currency_name=%s', (currency_name, ))
    row = cur.fetchone()
    if row['count'] == 0:
        return jsonify ({"message": "валюта не существует"}), 404
    else:
        cur.execute('select rate from currencies where currency_name=%s', (currency_name, ))
        row = cur.fetchone()
        rate = float(row['rate'])
        result = rate*sum
    return {'result': result}


@app.route("/currencies", methods = ['GET'])
def currencies():
    conn, cur = db_connect()
    cur.execute('select * from currencies')
    currencies = cur.fetchall()
    return {"currencies": currencies}


if __name__ == '__main__':
    app.run(debug=True, port=5002) 