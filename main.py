import os
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread
import yt_dlp as youtube_dl

# ==========================================
# 1. BACKGROUND WEB SERVER (DO NOT TOUCH)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================================
# 2. CONFIGURATION & STARTUP SETUP
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ⚠️ UPDATE THESE FOR YOUR SERVER:
VOICE_CHANNEL_ID = 123456789012345678  # <- Put your Voice Channel ID here
MY_SERVER_ID = 123456789012345678      # <- Put your Server (Guild) ID here

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    
    try:
        guild = discord.Object(id=MY_SERVER_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"Instantly synced {len(synced)} slash commands!")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
        
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel:
        try:
            await channel.connect()
            print(f"Connected to voice channel: {channel.name}")
        except Exception as e:
            print(f"Voice connection error on boot: {e}")

# ==========================================
# 3. SLASH COMMANDS SECTION
# ==========================================
FFMPEG_OPTIONS = {'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}

@bot.tree.command(name="play", description="Plays a song from YouTube")
async def play(interaction: discord.Interaction, search: str):
    await interaction.response.defer()
    
    if not interaction.user.voice:
        return await interaction.followup.send("You must be in a voice channel to play music.")
    
    ctx_voice = interaction.guild.voice_client
    if not ctx_voice:
        try:
            ctx_voice = await interaction.user.voice.channel.connect()
        except Exception as e:
            return await interaction.followup.send(f"Could not connect to voice channel: {e}")
    
    try:
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)
            
            if 'entries' in info and len(info['entries']) > 0:
                video_data = info['entries'][0]
            else:
                return await interaction.followup.send("No songs found for that search query.")
                
            url = video_data['url']
            title = video_data['title']
            
            if ctx_voice.is_playing():
                ctx_voice.stop()
                
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx_voice.play(source)
            await interaction.followup.send(f"Now playing: **{title}** 🎶")
            
    except Exception as e:
        print(f"Playback Error: {e}")
        await interaction.followup.send(f"An error occurred while trying to play: {e}")

@bot.tree.command(name="leave", description="Stops music and leaves the voice channel")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Disconnected. 👋")
    else:
        await interaction.response.send_message("I am not in a voice channel.")

# ==========================================
# 4. RUN SYSTEM (DO NOT TOUCH)
# ==========================================
keep_alive()
bot.run(os.environ['DISCORD_TOKEN'])
