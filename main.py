import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# 1. Web server setup to bypass free hosting sleep timers
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Replace with your actual Discord Voice Channel ID
VOICE_CHANNEL_ID = 123456789012345678  

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel:
        await channel.connect()
        print(f"Successfully anchored in {channel.name}")

# Start the web server and the bot
keep_alive()
bot.run(os.environ['DISCORD_TOKEN'])
