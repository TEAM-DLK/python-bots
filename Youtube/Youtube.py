import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from yt_dlp import YoutubeDL

# --- Configuration ---
API_ID = "YOUR_API_ID"  # Get from https://my.telegram.org/apps
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"
SESSION_NAME = "YOUR_SESSION_STRING"  # Assistant account session string

# --- Initialize Clients ---
app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_client = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)  # Assistant account
call = PyTgCalls(user_client)

# --- Function to Download and Stream YouTube Audio ---
def download_audio(url):
    options = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'cookiefile': 'Youtube/cookies.txt',  # Path to your cookies file
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    }
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        return f"song.{info['ext']}"

@app.on_message(filters.command("play") & filters.private)
async def play_song(client, message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        await message.reply("Usage: `/play <YouTube URL>`")
        return

    url = message.command[1]
    await message.reply("Downloading audio...")

    audio_file = download_audio(url)

    await user_client.join_chat(chat_id)  # Ensure assistant joins the call
    await call.join_group_call(chat_id, AudioPiped(audio_file))

    await message.reply("Playing in the video chat!")

@app.on_message(filters.command("stop") & filters.private)
async def stop_song(client, message):
    chat_id = message.chat.id
    await call.leave_group_call(chat_id)
    await message.reply("Stopped streaming.")

# --- Start Clients ---
async def main():
    await app.start()
    await user_client.start()
    await call.start()
    print("Bot is running...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())