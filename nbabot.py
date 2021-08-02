import random
import discord
from discord.ext import commands, tasks
import asyncio
import rostergen
import datetime
import coach
import pathlib
import jsonpickle, json

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = ".", case_insensitive = True, intents = intents)
userTL = {}
current = ""
last = ""
timeList = {}
setupCheck = {}
roster = {}
#print(last)

# Startup events
@client.event
async def on_ready():
    global current
    global roster
    global setupCheck
    last = datetime.datetime.utcnow()
    current = datetime.datetime.utcnow()
    last += datetime.timedelta(days = -1)
    for guild in client.guilds:
        setupCheck[guild.id] = False
    print('Init setup complete')

#@tasks.loop(seconds = 10)
#async def saveLoop():
#    global roster
#    if len(roster) > 0:
#        for guild in client.guilds:
#            with open('C:/Users/John/Downloads/guilds/' + str(guild.id) + '/roster.json', 'w') as file:
#                savR = []
    #            for player in roster[guild.id]:
        #            curpl = jsonpickle.encode(player, unpicklable = True, keys = True)
            #        savR.append(curpl)
                #json.dump(savR, file)
                #file.close()
                #print("Saved rosters.")


#saveLoop.start()
# Test command
@client.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def ping(ctx):
    await ctx.send('Pong!')
    await ctx.send(timeList[ctx.message.author.id])

@client.command()
async def save(ctx):
    global roster
    with open('C:/Users/John/Downloads/guilds/' + str(ctx.message.guild.id) + '/roster.json', 'w') as file:
        print("here")
        savR = []
        for player in roster[ctx.message.guild.id]:
            curpl = jsonpickle.encode(player, unpicklable = True, keys = True)
            savR.append(curpl)
        json.dump(savR, file)
        file.close()


@client.command()
async def newgen(ctx):
    global roster
    global userTL
    if pathlib.Path('C:/Users/John/Downloads/guilds/' + str(ctx.message.guild.id)).is_dir():
        with open('C:/Users/John/Downloads/guilds/' + str(ctx.message.guild.id) + '/roster.json') as file:
            fd = file.read()
            h = json.loads(fd)
            l = len(h)
            loadR = []
            for x in range(l):
                p = jsonpickle.decode(h[x])
                loadR.append(p)

            guild = client.get_guild(ctx.message.guild.id)
            roster[ctx.message.guild.id] = loadR
            userTL[guild.id] = {}
            for member in guild.members:
                userTL[ctx.message.guild.id][member.id] = []
                timeList[member.id] = last
            for player in roster[ctx.message.guild.id]:
                if not (player.getClaim() == 'Nobody'):
                    s = str(player.getClaim())
                    s2 = s[2:len(s)-1]
                    tempid = int(s2)
                    userTL[ctx.message.guild.id][tempid].append(player)


    else:
        rostergen.setup()
        pathlib.Path('C:/Users/John/Downloads/guilds/' + str(ctx.message.guild.id)).mkdir(parents = True, exist_ok = True)
        guild = client.get_guild(ctx.message.guild.id)
        userTL[guild.id] = {}
        for member in guild.members:
            userTL[guild.id][member.id] = []
            timeList[member.id] = last
        roster[ctx.message.guild.id] = rostergen.roster
        l = len(roster[ctx.message.guild.id])
        with open('C:/Users/John/Downloads/guilds/' + str(ctx.message.guild.id) + '/roster.json', 'w') as file:
            print("here")
            savR = []
            for x in range(l):
                curpl = jsonpickle.encode(roster[ctx.message.guild.id][x], unpicklable = True, keys = True)
                savR.append(curpl)
            json.dump(savR, file)
            file.close()

# Wipes user's previous lineup and replaces with 5 unclaimed players
@client.command(aliases = ['nt'])
#@commands.cooldown(1, 600, commands.BucketType.user)
async def newTeam(ctx):
    global roster
    global setupCheck
    global userTL

    if (ctx.message.guild.id not in setupCheck or setupCheck[ctx.message.guild.id] == False):
        await newgen(ctx)
        setupCheck[ctx.message.guild.id] = True
    channel = ctx.message.channel
    message = await ctx.send('Are you sure you want a new team? This will replace your starting 5.')
    await message.add_reaction('👍')
    await message.add_reaction('👎')

    def check(reaction, user):
        return user == ctx.message.author and (str(reaction.emoji) == ('👍') or str(reaction.emoji) == ('👎'))

    try:
        reaction, user = await client.wait_for('reaction_add', timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await channel.send('Team regeneration aborted.')
        #newTeam.reset_cooldown(ctx)
    if(str(reaction.emoji) == ('👎')):
        await channel.send('Team regeneration aborted.')
        #newTeam.reset_cooldown(ctx)
    else:
        myRoster = userTL[ctx.message.guild.id][user.id]
        if len(myRoster) > 0:
            for x in range (len(myRoster)):
                myRoster[x].setClaim("")
            myRoster.clear()
        for x in range(5):
            done = False
            while (not done):
                if  (random.choice(roster[ctx.message.guild.id]).getClaim() == "Nobody"):
                    myRoster.append(random.choice(roster[ctx.message.guild.id]))
                    myRoster[x].setClaim('<@' + str(user.id) + '>')
                    done = True
        await channel.send('New team generated.')
        await save(ctx)
        print(myRoster)
        await message.clear_reactions()

# Lists player's team. Create embed??
@client.command(aliases = ['mt'])
async def myTeam(ctx):
    global roster
    global setupCheck
    global userTL
    if (ctx.message.guild.id not in setupCheck or setupCheck[ctx.message.guild.id] == False):
        await newgen(ctx)
        setupCheck[ctx.message.guild.id] = True
    embs = []
    myRoster = userTL[ctx.message.guild.id][ctx.message.author.id]
    for x in range(len(myRoster)):
        thisEmb = discord.Embed(
            title = myRoster[x].getName() + ", Player " + str(x+1) + "/" + str(len(myRoster)),
            description = myRoster[x].getPos() + " for " + myRoster[x].getTeam().upper(),
            colour = discord.Colour.blue()
        )
        if not (myRoster[x].getID() == 0):
            thisEmb.set_image(url = "https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/" + myRoster[x].getID() + ".png")
        thisEmb.add_field(name = "Name", value = myRoster[x].getName(), inline = False);
        thisEmb.add_field(name = "Team", value = myRoster[x].getTeam().upper(), inline = False)
        thisEmb.add_field(name = "Position", value = myRoster[x].getPos(), inline = False)
        thisEmb.add_field(name = "Age", value = myRoster[x].getAge(), inline = False)
        thisEmb.add_field(name = "2020 PPG", value = myRoster[x].getPPG(), inline = True)
        thisEmb.add_field(name = "2020 True FG%", value = myRoster[x].getTSP(), inline = True)
        thisEmb.add_field(name = "2020 RPG", value = myRoster[x].getRPG(), inline = True)
        thisEmb.add_field(name = "2020 APG", value = myRoster[x].getAPG(), inline = True)
        thisEmb.add_field(name = "2020 SPG", value = myRoster[x].getSPG(), inline = True)
        thisEmb.add_field(name = "2020 BPG", value = myRoster[x].getBPG(), inline = True)
        thisEmb.add_field(name = "Claimed by: ", value = myRoster[x].getClaim(), inline = False)
        embs.append(thisEmb)
    message = await ctx.send(embed = embs[0])
    await message.add_reaction('⏮')
    await message.add_reaction('⬅️')
    await message.add_reaction('➡️')
    await message.add_reaction('⏭')

    i = 0

    def check(reaction, user):
        return user == ctx.message.author and (str(reaction.emoji) == ('⏮') or str(reaction.emoji) == ('➡️') or str(reaction.emoji) == ('⏭') or str(reaction.emoji) == ('⬅️'))
    while True:
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=15.0, check=check)
        except asyncio.TimeoutError:
            await message.clear_reactions()
            break
            #newTeam.reset_cooldown(ctx)
        if(str(reaction.emoji) == ('⏭')):
            i = len(myRoster) - 1
            await message.edit(embed = embs[i])
            await message.remove_reaction('⏭', ctx.message.author)
        elif(str(reaction.emoji) == ('⏮')):
            i = 0
            await message.edit(embed = embs[i])
            await message.remove_reaction('⏮', ctx.message.author)
        elif(str(reaction.emoji) == ('➡️')):
            await message.remove_reaction('➡️', ctx.message.author)
            if (i < (len(myRoster) - 1)):
                i += 1
                await message.edit(embed = embs[i])
        else:
            await message.remove_reaction('⬅️', ctx.message.author)
            if (i > 0):
                i -= 1
                await message.edit(embed = embs[i])
@client.command()
async def test(ctx):
    r = roster[ctx.message.guild.id]
    await ctx.send(ctx.message.guild.id)
    print(len(roster))

@client.command(aliases = ['fa'])
@commands.cooldown(10, 3600, commands.BucketType.user)
async def freeAgent(ctx):
    global roster
    global setupCheck
    global userTL
    if (ctx.message.guild.id not in setupCheck or setupCheck[ctx.message.guild.id] == False):
        await newgen(ctx)
        setupCheck[ctx.message.guild.id] = True
    global current
    done = False
    while not done:
        faPlayer = random.choice(roster[ctx.message.guild.id])
        if faPlayer.getClaim() == "Nobody":
            done = True
    e = discord.Embed(
        title = faPlayer.getName(),
        description = faPlayer.getPos() + " for " + faPlayer.getTeam().upper(),
        colour = discord.Colour.blue()
    )
    if not (faPlayer.getID() == 0):
        e.set_image(url = "https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/" + faPlayer.getID() + ".png")
    e.add_field(name = "Name", value = faPlayer.getName(), inline = False);
    e.add_field(name = "Team", value = faPlayer.getTeam().upper(), inline = False)
    e.add_field(name = "Position", value = faPlayer.getPos(), inline = False)
    e.add_field(name = "Age", value = faPlayer.getAge(), inline = False)
    e.add_field(name = "2020 PPG", value = faPlayer.getPPG(), inline = True)
    e.add_field(name = "2020 True FG%", value = faPlayer.getTSP(), inline = True)
    e.add_field(name = "2020 RPG", value = faPlayer.getRPG(), inline = True)
    e.add_field(name = "2020 APG", value = faPlayer.getAPG(), inline = True)
    e.add_field(name = "2020 SPG", value = faPlayer.getSPG(), inline = True)
    e.add_field(name = "2020 BPG", value = faPlayer.getBPG(), inline = True)
    e.add_field(name = "Claimed by: ", value = faPlayer.getClaim(), inline = False)
    message = await ctx.send(embed = e)
    #current
    current = datetime.datetime.utcnow()

    await message.add_reaction('✔️')
    await message.add_reaction('❌')


    #print(td)
    def check(reaction, user):
        return ((str(reaction.emoji) == ('✔️') or str(reaction.emoji) == ('❌')) and not user.bot and reaction.message == message)

    while True:
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await message.clear_reactions()
            #await ctx.send("Player was not claimed.")
            break
            #newTeam.reset_cooldown(ctx)
        if(str(reaction.emoji) == ('✔️')):
            current = datetime.datetime.utcnow()
            myRoster = userTL[ctx.message.guild.id][user.id]
            #td = (current - timeList[user.id]).total_seconds()
            td = 10900
            print(td)
            if (int(td) < 10800):
                await ctx.send("You claimed too recently. Next claim available in " + str(int((3600-td)/60)) + "m")
                await message.remove_reaction('✔️', user)
            else:
                await message.clear_reactions()
                timeList[user.id] = current
                myRoster.append(faPlayer)
                await ctx.send(faPlayer.getName() + " was picked up by " + '<@' + str(user.id) + '>' + " as a free agent!")
                faPlayer.setClaim('<@' + str(user.id) + '>')
                await save(ctx)
                return
        elif(str(reaction.emoji) == ('❌')):
            pass


# Test command. Lamarcus Aldridge Babey
@client.command()
async def lamarcus(ctx):
    global roster
    global setupCheck
    if (ctx.message.guild.id not in setupCheck or setupCheck[ctx.message.guild.id] == False):
        await newgen(ctx)
        setupCheck[ctx.message.guild.id] = True
    channel = ctx.message.channel
    await ctx.send(roster[ctx.message.guild.id][5].playerStr())

@client.command()
async def drop(ctx, p):
    global roster
    global setupCheck
    global userTL
    if (ctx.message.guild.id not in setupCheck or setupCheck[ctx.message.guild.id] == False):
        await newgen(ctx)
        setupCheck[ctx.message.guild.id] = True
    temp = []
    global current
    current = datetime.datetime.utcnow()
    for x in range(len(userTL[ctx.message.guild.id][ctx.message.author.id])):
        rp = (userTL[ctx.message.guild.id][ctx.message.author.id][x])
        temp.append(rp.getName().lower())
    if p.lower() in temp:
        r = userTL[ctx.message.guild.id][ctx.message.author.id]
        pl = temp.index(p)
        r[pl].setClaim("")
        del r[pl]
        await ctx.send("Player removed.")
        await save(ctx)
    else:
        await ctx.send("Player not is in your roster.")


@client.command()
async def claims(ctx):
    global roster
    global setupCheck
    if (ctx.message.guild.id not in setupCheck or setupCheck[ctx.message.guild.id] == False):
        await newgen(ctx)
        setupCheck[ctx.message.guild.id] = True
    current = datetime.datetime.utcnow()
    td = (current - timeList[ctx.message.author.id]).total_seconds()
    if (td < 3600):
        await ctx.send("Claim is available in " + str(int(3600 - td)/60) + "m")
    else:
        await ctx.send("You are eligible to claim a player as a free agent.")


# Searches player database and returns an embed for matching players
@client.command(aliases = ['pi', 'playersearch', 'ps', 'search', 's'])
async def playerInfo(ctx, pname):
    global roster
    global setupCheck
    if (ctx.message.guild.id not in setupCheck or setupCheck[ctx.message.guild.id] == False):
        await newgen(ctx)
        setupCheck[ctx.message.guild.id] = True
    channel = ctx.message.channel
    match = False
    await ctx.send("Working on that...")
    for x in range(len(roster[ctx.message.guild.id])):
        if (roster[ctx.message.guild.id][x].getName().lower() == pname.lower()):
            await ctx.send("Player found!")
            e = discord.Embed(
                title = roster[ctx.message.guild.id][x].getName(),
                description = roster[ctx.message.guild.id][x].getPos() + " for " + roster[ctx.message.guild.id][x].getTeam().upper(),
                colour = discord.Colour.blue()
            )
            if not (roster[ctx.message.guild.id][x].getID() == 0):
                e.set_image(url = "https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/" + roster[ctx.message.guild.id][x].getID() + ".png")
            e.add_field(name = "Name", value = roster[ctx.message.guild.id][x].getName(), inline = False);
            e.add_field(name = "Team", value = roster[ctx.message.guild.id][x].getTeam().upper(), inline = False)
            e.add_field(name = "Position", value = roster[ctx.message.guild.id][x].getPos(), inline = False)
            e.add_field(name = "Age", value = roster[ctx.message.guild.id][x].getAge(), inline = False)
            e.add_field(name = "2020 PPG", value = roster[ctx.message.guild.id][x].getPPG(), inline = True)
            e.add_field(name = "2020 True FG%", value = roster[ctx.message.guild.id][x].getTSP(), inline = True)
            e.add_field(name = "2020 RPG", value = roster[ctx.message.guild.id][x].getRPG(), inline = True)
            e.add_field(name = "2020 APG", value = roster[ctx.message.guild.id][x].getAPG(), inline = True)
            e.add_field(name = "2020 SPG", value = roster[ctx.message.guild.id][x].getSPG(), inline = True)
            e.add_field(name = "2020 BPG", value = roster[ctx.message.guild.id][x].getBPG(), inline = True)
            e.add_field(name = "Claimed by: ", value = roster[ctx.message.guild.id][x].getClaim(), inline = False)
            await ctx.send(embed = e)
            match = True
            return
    if (not match):
        await ctx.send("Player not found. Make sure the name is spelled right and enclosed in quotes.")

@client.command(aliases = ['mtl'])
async def myTeamList(ctx):
    global roster
    global setupCheck
    if (ctx.message.guild.id not in setupCheck or setupCheck[ctx.message.guild.id] == False):
        await newgen(ctx)
        setupCheck[ctx.message.guild.id] = True
    myRoster = userTL[ctx.message.guild.id][ctx.message.author.id]
    tl = discord.Embed(
        title = "My Roster List",
        description = "Player, Position, and Team:",
        colour = discord.Colour.blue()
    )
    for x in range (len(myRoster)):
        tl.add_field(name = myRoster[x].getName(), value = (myRoster[x].getPos() + " for " + myRoster[x].getTeam().upper()), inline = False)
    await ctx.send(embed = tl)

# Error catching
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send('Command is on cooldown. Try again in ' + str(round(error.retry_after, 2)) + 's')
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Bad argument, try again")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You're missing an argument")

@client.event
async def on_message(message):
    await client.process_commands(message)

# Close the bot
@client.command(aliases=["quit", 'stop'])
@commands.has_permissions(administrator=True)
async def close(ctx):
    await client.close()

client.run('ODYyMDA2ODcwODM1NTkzMjI3.YOSEdQ._TY5KP6ERQZwsDZh-QC6oqbWBgE')
