# This is the main file you need to run!

from flask import Flask
import api

app = Flask(__name__)

# Backend address - change it if needed
backend_address = "http://127.0.0.1:5000"

app.add_url_rule('/', 'basic', api.basic, methods=['GET'])
app.add_url_rule('/sender-status/<email>', 'sender_status', api.sender_status, methods=['GET'])
app.add_url_rule('/single-email/<email>', 'single_email', api.single_email, methods=['GET'])
app.add_url_rule('/fetch-records/<email>', 'fetch_records', api.fetch_records, methods=['GET'])

if __name__ == '__main__':
    app.run(debug=True)