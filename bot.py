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

def isLeader(player):
    leader = False
    for role in player.roles:
        if('Leader' in role.name):
            leader = True
    return leader

def getChar(player, guild):
    charsL = discord.utils.get(guild.channels, name='character-assignments').last_message.content

    charsL = charsL.split('\n')

    for i in range(len(charsL)):
        charsL[i] = charsL[i].split(', ')

    charsDict = {}
    for i in charsL:
        charsDict[i[0]] = i[1:]

    return charsDict[player.name]

def everyoneInRoom(sender, people):
    room = getRoom(sender)

    toReturn = True

    for player in people:
        if(room not in player.roles):
            toReturn = False

    return toReturn

async def moveRoom(player):
    room1 = discord.utils.get(player.guild.roles, name='room 1')
    room2 = discord.utils.get(player.guild.roles, name='room 2')
    if(getRoom(player).name == 'room 1'):
        await player.remove_roles(room1)
        await player.add_roles(room2)
    else:
        await player.remove_roles(room2)
        await player.add_roles(room1)
    

@bot.command(name='color')
async def color(ctx):
    player = ctx.message.content[7:]
    player = discord.utils.get(ctx.channel.members, name=player)

    await ctx.channel.send(player.mention + ' ' + ctx.author.name + " wants to exchange colors with you. To except reply 'yes color " + ctx.author.name + "'")

    def check(m):
        return m.content == 'yes color ' + ctx.author.name and m.author == player and m.channel == ctx.channel

    await bot.wait_for('message', check=check)

    await ctx.channel.send(ctx.author.mention + ': ' + getChar(ctx.author, ctx.guild)[0] + '\n' + player.mention + ': ' + getChar(player, ctx.guild)[0])

@bot.command(name='card')
async def card(ctx):
    player = ctx.message.content[6:]
    player = discord.utils.get(ctx.channel.members, name=player)

    await ctx.channel.send(player.mention + ' ' + ctx.author.name + " wants to exchange cards with you. To except reply 'yes card " + ctx.author.name + "'")

    def check(m):
        return m.content == 'yes card ' + ctx.author.name and m.author == player and m.channel == ctx.channel

    await bot.wait_for('message', check=check)

    await ctx.channel.send(ctx.author.mention + ': ' + str(getChar(ctx.author, ctx.guild)) + '\n' + player.mention + ': ' + str(getChar(player, ctx.guild)))

@bot.command(name='pm')
async def makeDM(ctx):
    people = ctx.message.content[4:].split(', ')
    people = [(discord.utils.get(ctx.channel.members, name=player)) for player in people]
    if(people == [None]):
        people = []

    name = (ctx.author.name + ''.join(('-' + player.name) for player in people)).lower().replace(' ', '-')

    if(everyoneInRoom(ctx.author, people)):
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

sending = False

@bot.command(name='send')
async def send(ctx):
    global sending

    people = ctx.message.content[6:].split(', ')
    people = [(discord.utils.get(ctx.channel.members, name=player)) for player in people]
    if(people == [None]):
        people = []

    if(isLeader(ctx.author) and everyoneInRoom(ctx.author, people)):

        def check(m):
            if(ctx.channel.name == 'room-1'):
                return '!send' in m.content and isLeader(m.author) and m.channel.name == 'room-2'
            else:
                return '!send' in m.content and isLeader(m.author) and m.channel.name == 'room-1'

        if(sending == False):
            sending = True
            await discord.utils.get(ctx.channels, name='announcements').send('A send request has been sent')
            await bot.wait_for('message', check=check)

        for player in people:
            print(player.name)
            await moveRoom(player)

    sending == False
    
@bot.command(name='nom')
async def nom(ctx):
    player = ctx.message.content[5:]
    player = discord.utils.get(ctx.channel.members, name=player)

    await ctx.channel.send('@here ' + player.mention + ' has been nominated as leader, vote on this message with reactions (:white_check_mark: or :x:).')

bot.run(token)