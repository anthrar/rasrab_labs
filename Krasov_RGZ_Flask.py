from flask import Flask, jsonify
from flask import request
import random
import requests

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/rate", methods = ['GET'])
def rate():
    try:
        currency = request.args.get('currency', '')
        if currency == 'USD':
            return {"rate": 56 }
        elif currency == 'EUR':
            return {"rate": 23 }
        else:
            return jsonify({"message": "UNKNOWN CURRENCY"}), 400
    except:
        return jsonify({"message": "UNEXPECTED ERROR"}), 500