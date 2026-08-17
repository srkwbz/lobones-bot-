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
# ==========================================
# 1. KEEP THIS TOP SECTION (Your existing setup)
# ==========================================
import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "Bot is alive!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

VOICE_CHANNEL_ID = 123456789012345678 # Your channel ID here

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel: await channel.connect()


# ==========================================
# 2. THE MIDDLE SECTION (Where you stack your commands)
# ==========================================

# Your existing !ping command
import yt_dlp as youtube_dl
import discord
from discord.ext import commands

# Basic ffmpeg and ydl options
FFMPEG_OPTIONS = {'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}

@bot.command()
async def play(ctx, *, search: str):
    # Ensure user is in a voice channel
    if not ctx.author.voice:
        return await ctx.send("You must be in a voice channel to play music.")
    
    # Join the voice channel
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()
    
    async with ctx.typing():
        # Search for and stream audio
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
            url = info['url']
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source)
            await ctx.send(f"Playing: {info['title']}")


# ==========================================
# 3. KEEP THIS BOTTOM SECTION (The startup triggers)
# ==========================================
keep_alive()
bot.run(os.environ['DISCORD_TOKEN'])

# Start the web server and the bot
keep_alive()
bot.run(os.environ['DISCORD_TOKEN'])
