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


@app.route("/load", methods = ['POST'])
def load():
    data = request.get_json()
    currency_name = data.get('currency', '-')
    if currency_name == '-':
        return jsonify ({"message": "валюта не передана"}), 400
    conn, cur = db_connect()
    cur.execute('select count(*) as count from currencies where currency_name=%s', (currency_name, ))
    row = cur.fetchone()
    if row['count'] > 0:
        return jsonify ({"message": "валюта уже существует"}), 400
    else:
        rate = data['rate']
        cur.execute('insert into currencies(currency_name, rate) values(%s, %s)', (currency_name, rate))
        db_close(conn, cur)
    return {}


@app.route("/update_currency", methods = ['POST'])
def update_currency():
    data = request.get_json()
    currency_name = data.get('currency', '-')
    if currency_name == '-':
        return jsonify ({"message": "валюта не передана"}), 400
    conn, cur = db_connect()
    cur.execute('select count(*) as count from currencies where currency_name=%s', (currency_name, ))
    row = cur.fetchone()
    if row['count'] == 0:
        return jsonify ({"message": "валюта не существует"}), 404
    else:
        rate = data['rate']
        cur.execute('update currencies set rate=%s where currency_name=%s', (rate, currency_name))
        db_close(conn, cur)
    return {}

@app.route("/delete", methods = ['POST'])
def delete():
    data = request.get_json()
    currency_name = data.get('currency', '-')
    if currency_name == '-':
        return jsonify ({"message": "валюта не передана"}), 400
    conn, cur = db_connect()
    cur.execute('select count(*) as count from currencies where currency_name=%s', (currency_name, ))
    row = cur.fetchone()
    if row['count'] == 0:
        return jsonify ({"message": "валюта не существует"}), 404
    else:
        cur.execute('delete from currencies where currency_name=%s', (currency_name, ))
        db_close(conn, cur)
    return {}


if __name__ == '__main__':
    app.run(debug=True, port=5001) 