import discord
import random
import os

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '!omikuji':
        results = ['大吉', '中吉', '小吉', '吉', '末吉', '凶']
        choice = random.choice(results)
        await message.channel.send(f'{message.author.mention} さんの運勢は **{choice}** です！')

# Renderの環境変数からトークンを読み込む
TOKEN = os.getenv('DISCORD_TOKEN')
client.run(TOKEN)
