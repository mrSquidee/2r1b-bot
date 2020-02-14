import os

from discord.ext import commands
from dotenv import load_dotenv
import discord

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
# guild = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

def getRoom(player):
    room = None
    for role in player.roles:
        if('room' in role.name):
            room = role
    return room

def getChar(player, guild):
    charsL = discord.utils.get(guild.channels, name='character-assignments').last_message.content

    charsL = charsL.split('\n')

    for i in range(len(charsL)):
        charsL[i] = charsL[i].split(', ')

    charsDict = {}
    for i in charsL:
        charsDict[i[0]] = i[1:]

    return charsDict[player.name]

@bot.command(name='test')
async def test(ctx):
    print(getChar(ctx.author, ctx.guild))

@bot.command(name='color')
async def color(ctx):
    player = ctx.message.content[7:]
    player = discord.utils.get(ctx.channel.members, name=player)

    await ctx.channel.send(player.mention + ' ' + ctx.author.name + " wants to exchange colors with you. To except reply 'I consent to sharing my color with " + ctx.author.name + "'")

    def check(m):
        return m.content == 'I consent to sharing my color with ' + ctx.author.name and m.author == player

    msg = await bot.wait_for('message', check=check)

    await ctx.channel.send(ctx.author.name + ': ' + getChar(ctx.author, ctx.guild)[0] + '\n' + player.name + ': ' + getChar(player, ctx.guild)[0])


@bot.command(name='pm')
async def makeDM(ctx):
    people = ctx.message.content[4:].split(', ')
    people = [(discord.utils.get(ctx.channel.members, name=player)) for player in people]
    if(people == [None]):
        people = []

    name = (ctx.author.name + ''.join(('-' + player.name) for player in people)).lower().replace(' ', '-')
    
    room = getRoom(ctx.author)

    everyoneInRoom = True

    for player in people:
        if(room not in player.roles):
            everyoneInRoom = False

    if(everyoneInRoom):
        if(not discord.utils.get(ctx.guild.channels, name=name)):
            await discord.utils.get(ctx.guild.categories, name='pms').create_text_channel(name)
            
            channel = discord.utils.get(ctx.guild.text_channels, name=name)
            await channel.set_permissions(ctx.author, read_messages=True, send_messages=True, read_message_history=True)
            for player in people:
                await channel.set_permissions(player, read_messages=True, send_messages=True, read_message_history=True)
        else:
            await ctx.channel.send(ctx.author.mention + ' That PM already exists (or you typed someones name wrong).')
    else:
        await ctx.channel.send(ctx.author.mention + ' Not every member of that PM is in the same room.')

    


bot.run(token)