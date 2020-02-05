import os

from discord.ext import commands
from dotenv import load_dotenv
import discord

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
# guild = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')


@bot.command(name='pm')
async def makeDM(ctx):
    people = ctx.message.content[4:].split(', ')
    people = [(discord.utils.get(ctx.channel.members, name=player)) for player in people]
    if(people == [None]):
        people = []

    name = (ctx.message.author.name + ''.join(('-' + player.name) for player in people)).lower().replace(' ', '-')
    
    room = None
    for role in ctx.message.author.roles:
        if('room' in role.name):
            room = role

    everyoneInRoom = True

    for player in people:
        if(room not in player.roles):
            everyoneInRoom = False

    if(not discord.utils.get(ctx.guild.channels, name=name) and everyoneInRoom):
        await discord.utils.get(ctx.guild.categories, name='pms').create_text_channel(name)
        
        channel = discord.utils.get(ctx.guild.text_channels, name=name)
        await channel.set_permissions(ctx.message.author, read_messages=True, send_messages=True)
        for player in people:
            await channel.set_permissions(player, read_messages=True, send_messages=True)
    else:
        print('no')

    


bot.run(token)