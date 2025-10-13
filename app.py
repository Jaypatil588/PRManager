from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/webhook', methods=['POST'])
def webhook():
    print("Webhook received on app.py!")
    return ('Webhook received on app.py!')

if __name__ == '__main__':
    app.run(debug=True)

#new changes