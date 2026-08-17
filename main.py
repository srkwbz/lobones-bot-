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
YDL_OPTIONS = {
    'format': 'bestaudio/best', 
    'noplaylist': 'True',
    'default_search': 'ytmsearch', # Fallback query method
}

@bot.tree.command(name="play", description="Type ANY song name or artist to play instantly")
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
            artist_name = track_info['artists'][0]['name']
            search_query = f"{track_name} {artist_name}"
        except Exception as e:
            print(f"Spotify API Error: {e}")

    try:
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            # If the user didn't paste a raw link, treat it as a universal text search
            if not search_query.startswith("http"):
                final_search = f"ytmsearch:{search_query}"
            else:
                final_search = search_query

            info = ydl.extract_info(final_search, download=False)
            
            if 'entries' in info and len(info['entries']) > 0:
                video_data = info['entries'][0]
            elif 'url' in info:
                video_data = info
            else:
                return await interaction.followup.send("Could not find any music matching that name.")
                
            url = video_data['url']
            title = video_data['title']
            
            # Extract artist name if available from YouTube Music metadata
            uploader = video_data.get('uploader', 'Unknown Artist')
            
            if ctx_voice.is_playing():
                ctx_voice.stop()
                
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx_voice.play(source)
            await interaction.followup.send(f"🎶 Now playing: **{title}** by *{uploader}*")
            
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

keep_alive()
bot.run(os.environ['DISCORD_TOKEN'])
