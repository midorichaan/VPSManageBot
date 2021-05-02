import discord
from discord.ext import commands

import config

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

bot.config = config

#on_ready
@bot.event
async def on_ready():
    print("on_ready!")

#on_connect
@bot.event
async def on_connect():
    print("on_connect!")
    
    ext = ["cogs.mido_admins", "jishaku"]
    
    for c in ext:
        try:
            bot.load_extension(c)
        except Exception as e:
            print(f"[Error] {e}")
        else:
            print(f"{c} load.")
    
#command_log
@bot.event
async def on_command(ctx):
    print(f"[Log] {ctx.author} ({ctx.author.id}) → {ctx.command}")

#error
@bot.event
async def on_command_error(ctx, error):
    print(f"[Error] {ctx.author} ({ctx.author.id}) → {error}")
    
    try:
        await ctx.reply(f"```py\n{error}\n```")
    except:
        await ctx.send(f"```py\n{error}\n```")
        
bot.run(config.BOT_TOKEN)