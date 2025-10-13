import requests

def webhook():
    url = "http://127.0.0.1:5000/webhook"
    send = "Webhook.py is running"
    x = requests.post(url, json = send)

webhook()