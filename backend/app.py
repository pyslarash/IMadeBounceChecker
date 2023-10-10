# This is the main file you need to run!

from flask import Flask
import api

app = Flask(__name__)

app.add_url_rule('/', 'basic', api.basic, methods=['GET'])
app.add_url_rule('/sender-status/<email>', 'sender_status', api.sender_status, methods=['POST'])
app.add_url_rule('/single-email/<email>', 'single_email', api.single_email, methods=['POST'])
app.add_url_rule('/bulk-emails/<email_col>', 'bulk_emails', api.bulk_emails, methods=['POST'])

if __name__ == '__main__':
    app.run(debug=True)
