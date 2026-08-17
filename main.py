import os
import re
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread
import yt_dlp as youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# ⚠️ PLACE YOUR ID NUMBERS EXACTLY HERE:
# ==========================================
VOICE_CHANNEL_ID = 1537096867215843439
MY_SERVER_ID = 1536466519012151362

SPOTIFY_TRACK_REGEX = r"https:\/\/open\.spotify\.com\/track\/([a-zA-Z0-9]+)"

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

FFMPEG_OPTIONS = {'options': '-vn'}

# 🌟 SOUNDCLOUD OPTIMIZED CONFIGURATION
YDL_OPTIONS = {
    'format': 'bestaudio/best', 
    'noplaylist': 'True',
    'default_search': 'scsearch', # <- Automatically routes all plain text searches to SoundCloud
}

@bot.tree.command(name="play", description="Type ANY song name to play instantly from SoundCloud")
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
            
    spotify_match = re.match(SPOTIFY_TRACK_REGEX, search.strip())
    search_query = search
    
    if spotify_match:
        try:
            sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
            track_id = spotify_match.group(1)
            track_info = sp.track(track_id)
            track_name = track_info['name']
            artist_name = track_info['artists']['name']
            search_query = f"{track_name} {artist_name}"
        except Exception as e:
            print(f"Spotify API Error: {e}")

    try:
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            # 🌟 CHANGED: Using 'scsearch:' to look up plain text queries on SoundCloud
            if not search_query.startswith("http"):
                info = ydl.extract_info(f"scsearch:{search_query}", download=False)
            else:
                info = ydl.extract_info(search_query, download=False)
            
            if 'entries' in info and len(info['entries']) > 0:
                video_data = info['entries']
            elif 'url' in info:
                video_data = info
            else:
                return await interaction.followup.send("Could not find any music matching that name on SoundCloud.")
                
            url = video_data['url']
            title = video_data['title']
            uploader = video_data.get('uploader', 'Unknown Artist')
            
            if ctx_voice.is_playing():
                ctx_voice.stop()
                
            raw_source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            volume_source = discord.PCMVolumeTransformer(raw_source, volume=0.5)
            
            ctx_voice.play(volume_source)
            await interaction.followup.send(f"☁️ Now playing from SoundCloud: **{title}** by *{uploader}* (Volume: 50%)")
            
    except Exception as e:
        print(f"Playback Error: {e}")
        await interaction.followup.send(f"An error occurred while trying to play from SoundCloud: {e}")

@bot.tree.command(name="volume", description="Adjust the bot's volume level (1 to 100)")
@app_commands.describe(level="Volume level from 1 to 100")
async def volume(interaction: discord.Interaction, level: int):
    ctx_voice = interaction.guild.voice_client
    
    if not ctx_voice or not ctx_voice.is_playing():
        return await interaction.response.send_message("I am not playing any music right now.", ephemeral=True)
        
    if level < 1 or level > 100:
        return await interaction.response.send_message("Please choose a volume level between 1 and 100.", ephemeral=True)
        
    ctx_voice.source.volume = level / 100.0
    await interaction.response.send_message(f"🔊 Volume set to **{level}%**")

@bot.tree.command(name="leave", description="Stops music and leaves the voice channel")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Disconnected. 👋")
    else:
        await interaction.response.send_message("I am not in a voice channel.")

keep_alive()
bot.run(os.environ['DISCORD_TOKEN'])

