import os

import discord

from core import Responder
import keep_alive

keep_alive.keep_alive()

responder = Responder()

client = discord.Client()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    username = message.author.name.split('#')[0]

    response = responder(username, message.content)

    if response is not None:
        await message.channel.send(response)


client.run(os.environ['DISCORD_TOKEN'])
