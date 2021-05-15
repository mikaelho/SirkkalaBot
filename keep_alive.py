from flask import Flask
from threading import Thread

from core import Responder

app = Flask('')
responder = Responder()

@app.route('/')
def home():
    content = responder.get_html()
    return f'''
        <html>
        <head>
            <script src="https://unpkg.com/htmx.org@1.1.0"
                integrity="sha384-JVb/MVb+DiMDoxpTmoXWmMYSpQD2Z/1yiruL8+vC6Ri9lk6ORGiQqKSqfmCBbpbX" 
                crossorigin="anonymous">
            </script>
            <link href="https://unpkg.com/tailwindcss@^2/dist/tailwind.min.css" rel="stylesheet">
            <style>
                details summary > * {{ 
                    display: inline;
                }}
                * {{
                    -webkit-tap-highlight-color: transparent;
                }}
                :focus {{
                    outline: none; /* no outline - for most browsers */
                    box-shadow: none; /* no box shadow - for some browsers or if you are using Bootstrap */
                }}
            </style>
        </head>
            {content}
        </html>
    '''

@app.route('/throw/<character>/<move>/<modifier>')
def throw(character, move, modifier):
    this_id = f'{character}-{move}'
    this_url = f'/buttons/{character}/{move}'
    move = move.replace('-', ' ')
    username = responder.get_username_by_character_name(character)
    if not username:
        return None
    result = responder(username, f'a {move} {modifier}')
    
    return f'<span id="{this_id}" style="color: white; background-color: rgba(5, 150, 105);" hx-get="{this_url}" hx-trigger="load delay:7s" hx-swap="outerHTML">&nbsp;&nbsp;{result}&nbsp;&nbsp;</span>'

@app.route('/buttons/<character>/<move>')
def buttons(character, move):
    move = move.replace('-', ' ')
    return responder.buttons(character, move)

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
