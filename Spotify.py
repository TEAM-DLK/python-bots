import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types.input_stream import AudioPiped
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import os

# Telegram Bot API Credentials
API_ID = "your_api_id"
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"

# Spotify API Credentials
SPOTIFY_CLIENT_ID = "your_spotify_client_id"
SPOTIFY_CLIENT_SECRET = "your_spotify_client_secret"

# Initialize Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
))

# Initialize Telegram Client
app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
pytgcalls = PyTgCalls(app)

# Helper function to get the YouTube link of a Spotify song
def get_youtube_link(spotify_url):
    track = sp.track(spotify_url)
    track_name = track['name'] + " " + track['artists'][0]['name']
    
    # Search and get the first YouTube video link
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch:{track_name}", download=False)
        return result['entries'][0]['url'] if result['entries'] else None

# Function to play audio in video chat
async def play_audio(chat_id, spotify_url):
    youtube_url = get_youtube_link(spotify_url)
    if not youtube_url:
        return "No audio found."
    
    # Download the audio
    file_path = "song.mp3"
    ydl_opts = {"format": "bestaudio/best", "outtmpl": file_path}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    # Play in group video chat
    await pytgcalls.join_group_call(
        chat_id,
        AudioPiped(file_path),
        stream_type=StreamType().local_stream,
    )

    return "Playing audio..."

# Telegram command to play Spotify song
@app.on_message(filters.command("play"))
async def play_command(client, message):
    if len(message.command) < 2:
        await message.reply("Usage: /play <spotify_track_link>")
        return

    spotify_url = message.command[1]
    chat_id = message.chat.id
    
    response = await play_audio(chat_id, spotify_url)
    await message.reply(response)

# Start the bot
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply("🎵 Send a Spotify link using /play <spotify_url> to play it in voice chat.")

@app.on_message(filters.command("stop"))
async def stop_command(client, message):
    chat_id = message.chat.id
    await pytgcalls.leave_group_call(chat_id)
    await message.reply("Stopped playing.")

# Run the bot
async def main():
    await pytgcalls.start()
    await app.run()

asyncio.run(main())