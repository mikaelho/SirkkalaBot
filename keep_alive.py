from flask import Flask
from threading import Thread

from core import Responder

app = Flask('')

@app.route('/')
def home():
    content = Responder().get_html()
    return f'''
        <html>
        <head>
            <link href="https://unpkg.com/tailwindcss@^2/dist/tailwind.min.css" rel="stylesheet">
        </head>
        {content}
        </html>
    '''

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
