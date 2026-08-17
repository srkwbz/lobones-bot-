import os
import discord
from discord import app_commands  # NEW: Import slash command tools
from discord.ext import commands
from flask import Flask
from threading import Thread
import yt_dlp as youtube_dl

app = Flask('')
@app.route('/')
def home(): return "Bot is alive!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

VOICE_CHANNEL_ID = 123456789012345678 

# Replace this number with your actual Server (Guild) ID
MY_SERVER_ID = 123456789012345678  

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    
    try:
        # 1. Copy global commands to your specific test server
        guild = discord.Object(id=MY_SERVER_ID)
        bot.tree.copy_global_to(guild=guild)
        
        # 2. Sync directly to that server for instant activation
        synced = await bot.tree.sync(guild=guild)
        print(f"Instantly synced {len(synced)} slash commands to server {MY_SERVER_ID}!")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
        
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel: 
        await channel.connect()

    
    # NEW: This automatically registers your slash commands with Discord global servers
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands!")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
        
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel: await channel.connect()
 on_ready():
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

# 1. Slash command for Play
@bot.tree.command(name="play", description="Plays a song from YouTube")
async def play(interaction: discord.Interaction, search: str):
    # Defers the response to prevent a Discord 3-second timeout
    await interaction.response.defer()
    
    if not interaction.user.voice:
        return await interaction.followup.send("You must be in a voice channel to play music.")
    
    # Connect to voice or get current voice client
    ctx_voice = interaction.guild.voice_client
    if not ctx_voice:
        try:
            ctx_voice = await interaction.user.voice.channel.connect()
        except Exception as e:
            return await interaction.followup.send(f"Could not connect to voice channel: {e}")
    
    try:
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            # Look up the track using ytsearch
            info = ydl.extract_info(f"ytsearch:{search}", download=False)
            
            # CRITICAL FIX: Extract the first entry from search results
            if 'entries' in info and len(info['entries']) > 0:
                video_data = info['entries'][0]
            else:
                return await interaction.followup.send("No songs found for that search query.")
                
            url = video_data['url']
            title = video_data['title']
            
            # Handle audio stream playback
            if ctx_voice.is_playing():
                ctx_voice.stop() # Stops current audio before playing a new one
                
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx_voice.play(source)
            await interaction.followup.send(f"Now playing: **{title}** 🎶")
            
    except Exception as e:
        print(f"Playback Error: {e}")
        await interaction.followup.send(f"An error occurred while trying to play: {e}")

    
    if not interaction.user.voice:
        return await interaction.followup.send("You must be in a voice channel to play music.")
    
    # Check if bot is already in a VC
    ctx_voice = interaction.guild.voice_client
    if not ctx_voice:
        ctx_voice = await interaction.user.voice.channel.connect()
    
    try:
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            # Look up the track
            info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
            url = info['url']
            title = info['title']
            
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx_voice.play(source)
            await interaction.followup.send(f"Now playing: **{title}** 🎶")
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}")

# 2. Slash command for Leave
@bot.tree.command(name="leave", description="Stops music and leaves the voice channel")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Disconnected. 👋")
    else:
        await interaction.response.send_message("I am not in a voice channel.")

# ==========================================
# 3. KEEP THIS BOTTOM SECTION (The startup triggers)
# ==========================================
keep_alive()
bot.run(os.environ['DISCORD_TOKEN'])

# Start the web server and the bot
keep_alive()
bot.run(os.environ['DISCORD_TOKEN'])
