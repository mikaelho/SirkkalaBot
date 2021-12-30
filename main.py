# import asyncio
import os
from threading import Thread

import discord

from flask import Flask

app = Flask(__name__)

from core import Responder


responder = Responder()
config = {}

client = discord.Client()

'''
@app.before_serving
async def before_serving():
    loop = asyncio.get_event_loop()
    await client.login(os.environ['DISCORD_TOKEN'])
    loop.create_task(client.connect())
'''

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
    client.loop.create_task(send_to_channel(result))
    return f'<span id="{this_id}" style="color: white; background-color: rgba(5, 150, 105);" hx-get="{this_url}" hx-trigger="load delay:7s" hx-swap="outerHTML">&nbsp;&nbsp;{result}&nbsp;&nbsp;</span>'

async def send_to_channel(message):
    game_channel = config['channel']
    print('Send', message, 'to channel', game_channel.name)
    await game_channel.send(message)

@app.route('/buttons/<character>/<move>')
def buttons(character, move):
    move = move.replace('-', ' ')
    return responder.buttons(character, move)

def run():
  app.run(host='0.0.0.0',port=8080)

def run_server():
    t = Thread(target=run)
    t.start()

run_server()

@client.event
async def on_ready():
    print('Logged in as', client.user.name, client.user.id)
    config['channel'] = client.get_channel(int(os.environ['KULT_CHANNEL']))
    print('Game channel', config['channel'].name)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id != config['channel'].id:
        return

    username = message.author.name.split('#')[0]

    response = responder(username, message.content)

    if response is not None:
        await message.channel.send(response)


client.run(os.environ['DISCORD_TOKEN'])
