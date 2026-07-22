import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

queue = {}
voice_clients = {}

yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f'{bot.user} online hai!')

@bot.command(name='join')
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        voice_clients[ctx.guild.id] = voice_client
        await ctx.send(f"Join kar liya: {channel.name}")
    else:
        await ctx.send("Pehle voice channel join karo!")

@bot.command(name='play')
async def play(ctx, *, url):
    if ctx.guild.id not in voice_clients:
        await join(ctx)
    
    voice_client = voice_clients[ctx.guild.id]
    
    async with ctx.typing():
        data = ytdl.extract_info(url, download=False)
        song = data['url']
        title = data.get('title', 'Unknown')
    
    player = discord.FFmpegPCMAudio(song, **ffmpeg_options)
    voice_client.play(player, after=lambda e: print(f'Error: {e}'))
    
    await ctx.send(f"▶️ Ab baj raha hai: **{title}**")

@bot.command(name='leave')
async def leave(ctx):
    if ctx.guild.id in voice_clients:
        await voice_clients[ctx.guild.id].disconnect()
        del voice_clients[ctx.guild.id]
        await ctx.send("Chala gaya 👋")

@bot.command(name='pause')
async def pause(ctx):
    voice_client = voice_clients[ctx.guild.id]
    voice_client.pause()
    await ctx.send("Pause ⏸️")

@bot.command(name='resume')
async def resume(ctx):
    voice_client = voice_clients[ctx.guild.id]
    voice_client.resume()
    await ctx.send("Resume ▶️")

@bot.command(name='stop')
async def stop(ctx):
    voice_client = voice_clients[ctx.guild.id]
    voice_client.stop()
    await ctx.send("Stop ⏹️")

token = os.environ.get('your_token')
bot.run(token)
