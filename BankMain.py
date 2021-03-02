"""
Created by Meaning#0001
This Bot holds player money info
Also handles transactions
"""

import discord
import json
import time
import datetime
import os
import gspread
import random
import requests
import asyncio
import copy
from discord.ext import commands

prefix = "!"

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=prefix, case_insensitive=True, intents=intents)
client.remove_command("help")
botConf = json.loads(open("./Bank Configs/botConfig.json", "r").read())

gc = gspread.service_account(filename='./Shared Configs/creds.json')
sh = gc.open_by_key('')
ws = sh.worksheet("Customers")
ws2 = sh.worksheet("Transactions")
ws3 = sh.worksheet("Suggestions")
ws4 = sh.worksheet("Added/Removed")
sh2 = gc.open_by_key('')
worksheet2 = sh2.worksheet("BlackSheep | L1")
marketPrice = {"korrelite": float(worksheet2.get("C13")[0][0]), "reknite": float(worksheet2.get("D13")[0][0]),
                       "gellium": float(worksheet2.get("E13")[0][0]), "axnit": float(worksheet2.get("F13")[0][0]),
                       "bnarcor": float(worksheet2.get("G13")[0][0]), "rnarcor": float(worksheet2.get("H13")[0][0])}
baseURLB = "https://api.blox.link/v1/user/"
baseURLR = "https://api.roblox.com/users/"
listedChannels = json.loads(open("./Bank Configs/whitelist.txt", "r").read())

def saveWhitelist():
    open("./Bank Configs/whitelist.txt", "w").write(json.dumps(listedChannels))

class transaction:
    def __init__(self, amount, messageID, sender, receiver):
        self.amount = amount
        self.messageID = messageID
        self.sender = sender
        self.receiver = receiver

def DMoney(num):
    return '{}{:,.2f}'.format(creditEmoji, num)

def Money(num):
    return '${:,.2f}'.format(num)

def compoundInterest(p, r, n, t):
    return ((p * (1 + (r/n)) ** (n * t)) - p)

def investmentInterest(investment):
    interest = 0
    if investment <= 20000:
        interest += investment * 0.08
    elif investment > 20000 and investment <= 100000:
        interest += investment * 0.05
    elif investment > 100000 and investment <= 500000:
        interest += investment * 0.02
    elif investment > 500000:
        interest += investment * 0.015
    return interest

def getUser(dID, GuildID=None):
    if GuildID == None:
        blox = requests.get(baseURLB + str(dID)).json()
    else:
        blox = requests.get(baseURLB + str(dID) + "?guild=" + str(GuildID)).json()
    if blox["status"] == "error":
        return blox["error"]
    else:
        print(blox)
        try:
            robx = requests.get(baseURLR + blox["primaryAccount"]).json()
        except KeyError:
            try:
                robx = requests.get(baseURLR + blox["matchingAccount"]).json()
            except KeyError:
                return "Error Something Wrong Happened"
        return robx["Username"]

@client.group(invoke_without_command=True)
async def help(ctx):
    peeppe = False
    if str(ctx.guild.id) in listedChannels["whitelist"]:
        if ctx.channel.id in listedChannels["whitelist"][str(ctx.guild.id)]:
            peeppe = True
    else:
        peeppe = True

    if peeppe:
        direct = False
        if str(ctx.author.id) in botConf["admins"]:
            direct = True
        embed = discord.Embed(title="Help", description=f'Use {prefix}help <command> for extended information on the command\n<> -> Required\n[] -> Optional', color=0xeecd2b)
        embed.add_field(name="User Commands", value="`bal`\n`send`\n`invest`\n`investments`\n`cancel`\n`price`")
        if direct:
            embed.add_field(name="Director Commands", value="`invested`\n`add`\n`remove`\n`privatise`\n`deprivatise`\n`profit`\n`ideal`\n`interest`")
        await ctx.send(embed=embed)

@help.command()
async def bal(ctx):
    peeppe = False
    if str(ctx.guild.id) in listedChannels["whitelist"]:
        if ctx.channel.id in listedChannels["whitelist"][str(ctx.guild.id)]:
            peeppe = True
    else:
        peeppe = True

    if peeppe:
        embed = discord.Embed(title="Bal", description="See you or someone else's balance", color=0xeecd2b)
        embed.add_field(name="**Syntax**", value=f'{prefix}bal [member]')
        await ctx.send(embed=embed)

@help.command()
async def send(ctx):
    peeppe = False
    if str(ctx.guild.id) in listedChannels["whitelist"]:
        if ctx.channel.id in listedChannels["whitelist"][str(ctx.guild.id)]:
            peeppe = True
    else:
        peeppe = True

    if peeppe:
        embed = discord.Embed(title="Send", description="Send money to someone else", color=0xeecd2b)
        embed.add_field(name="**Syntax**", value=f'{prefix}send/transfer <member> <amount>')
        await ctx.send(embed=embed)

@help.command()
async def invest(ctx):
    peeppe = False
    if str(ctx.guild.id) in listedChannels["whitelist"]:
        if ctx.channel.id in listedChannels["whitelist"][str(ctx.guild.id)]:
            peeppe = True
    else:
        peeppe = True

    if peeppe:
        embed = discord.Embed(title="Invest", description="Invest your money and after a week you will have a profit.", color=0xeecd2b)
        embed.add_field(name="**Syntax**", value=f'{prefix}invest <amount/all>')
        await ctx.send(embed=embed)

@help.command()
async def investments(ctx):
    peeppe = False
    if str(ctx.guild.id) in listedChannels["whitelist"]:
        if ctx.channel.id in listedChannels["whitelist"][str(ctx.guild.id)]:
            peeppe = True
    else:
        peeppe = True

    if peeppe:
        embed = discord.Embed(title="Investments", description="See any investments you currently have and when they'll be done.", color=0xeecd2b)
        embed.add_field(name="**Syntax**", value=f'{prefix}investments')
        await ctx.send(embed=embed)

@help.command()
async def cancel(ctx):
    peeppe = False
    if str(ctx.guild.id) in listedChannels["whitelist"]:
        if ctx.channel.id in listedChannels["whitelist"][str(ctx.guild.id)]:
            peeppe = True
    else:
        peeppe = True

    if peeppe:
        embed = discord.Embed(title="Cancel", description="Cancel an investment", color=0xeecd2b)
        embed.add_field(name="**Syntax**", value=f'{prefix}cancel <investment #>')
        await ctx.send(embed=embed)

@help.command()
async def price(ctx):
    peeppe = False
    if str(ctx.guild.id) in listedChannels["whitelist"]:
        if ctx.channel.id in listedChannels["whitelist"][str(ctx.guild.id)]:
            peeppe = True
    else:
        peeppe = True

    if peeppe:
        embed = discord.Embed(title="Price", description="Show price of materials or cost of an amount of material", color=0xeecd2b)
        embed.add_field(name="**Syntax**", value=f'{prefix}price [<amount> <material>]')
        await ctx.send(embed=embed)

@help.command()
async def invested(ctx):
    if str(ctx.author.id) in botConf["admins"]:
            embed = discord.Embed(title="Invested", description="Shows how much money is currently invested", color=0xeecd2b)
            embed.add_field(name="**Syntax**", value=f'{prefix}invested')
            await ctx.send(embed=embed)
            return

@help.command()
async def interest(ctx):
    if str(ctx.author.id) in botConf["admins"]:
            embed = discord.Embed(title="Interest", description="Use this to calculate compound interest.", color=0xeecd2b)
            embed.add_field(name="**Syntax**", value=f'{prefix}interest <Intital Amount> <Percent> [Investements per Time] [Time]')
            await ctx.send(embed=embed)
            return

@help.command()
async def add(ctx):
    if str(ctx.author.id) in botConf["admins"]:
            embed = discord.Embed(title="Add", description="Add an amount to players **USE THIS FOR DEPOSITS**", color=0xeecd2b)
            embed.add_field(name="**Syntax**", value=f'{prefix}add <user> <amount>')
            await ctx.send(embed=embed)

@help.command()
async def remove(ctx):
    if str(ctx.author.id) in botConf["admins"]:
            embed = discord.Embed(title="Remove", description="Remove an amount from players **USE THIS FOR WITHDRAWLS**", color=0xeecd2b)
            embed.add_field(name="**Syntax**", value=f'{prefix}remove <user> <amount>')
            await ctx.send(embed=embed)
            return

@help.command()
async def privatise(ctx):
    if str(ctx.author.id) in botConf["admins"]:
            embed = discord.Embed(title="Privatise", description="Privatises a users account", color=0xeecd2b)
            embed.add_field(name="**Syntax**", value=f'{prefix}privatise <user>')
            await ctx.send(embed=embed)
            return

@help.command()
async def deprivatise(ctx):
    if str(ctx.author.id) in botConf["admins"]:
            embed = discord.Embed(title="Deprivatise", description="Deprivatises a users account", color=0xeecd2b)
            embed.add_field(name="**Syntax**", value=f'{prefix}deprivatise <user>')
            await ctx.send(embed=embed)
            return

@help.command()
async def profit(ctx):
    if str(ctx.author.id) in botConf["admins"]:
            embed = discord.Embed(title="Profit", description="Shows you how much you will make for investing an amount of material", color=0xeecd2b)
            embed.add_field(name="**Syntax**", value=f'{prefix}profit <Buy Price> <Sell Price> <Amount>')
            await ctx.send(embed=embed)
            return

@help.command()
async def ideal(ctx):
    if str(ctx.author.id) in botConf["admins"]:
            embed = discord.Embed(title="Ideal", description="Shows you the ideal interest rate from ", color=0xeecd2b)
            embed.add_field(name="**Syntax**", value=f'{prefix}ideal <Produce Per week> <Amount invested>')
            await ctx.send(embed=embed)
            return

@client.event
async def on_ready():
    print('Bot is online')
    global creditEmoji
    i = await client.fetch_guild()
    creditEmoji = await i.fetch_emoji()
    client.loop.create_task(update())
    client.loop.create_task(check_investment())
    await client.change_presence(activity=discord.Game(f'Starscape! use {prefix}help for commands'))

@client.event
async def on_message(message):
    await client.process_commands(message)

@client.event
async def on_message_edit(before, after):
    await client.process_commands(after)
    return

@client.event
async def on_reaction_add(reaction, user):#Checks each reaction
    if client.user.id != reaction.message.author.id:
        return
    message = "message" + str(reaction.message.id)
    check = json.loads(open("./Shared Configs/human.json", "r").read())
    try:
        globals()[message]
    except KeyError:
        globals()[message] = []
    globals()[message].append("user" + str(user.id))
    for x in globals()[message]:
        for y in check:
            try:
                globals()[x + "_" + y]
            except KeyError:
                globals()[x + "_" + y] = None
            if globals()[x + "_" + y] != None:
                if globals()[x + "_" + y].messageID == reaction.message.id:
                    check[x] = check[x] - globals()[x + "_" + y].amount
                    amountocut = (((botConf["Transaction Fee %"]) / 100) * globals()[x + "_" + y].amount)
                    amountCut = globals()[x + "_" + y].amount - amountocut
                    check[y] = check[y] + amountCut
                    ws2.append_row([str(globals()[x + "_" + y].sender)[:-5], Money(globals()[x + "_" + y].amount), Money(amountCut), str(globals()[x + "_" + y].receiver)[:-5]])
                    open("./Shared Configs/human.json", "w").write(json.dumps(check))
                    globals()[x + "_" + y] = None
                    await reaction.message.delete()
                    await client.get_channel(reaction.message.channel.id).send("Transaction Complete")

@client.command()
async def uid(ctx, person, guild=None):
    if str(ctx.author.id) in botConf["admins"]:
        try:
            p = int(person.replace("<", "").replace(">", "").replace("!","").replace("@", "").replace("&", ""))
            if guild != None:
                g = int(guild)
        except ValueError:
            await ctx.send("This is not a valid")
            return
        if guild == None:
            await ctx.reply(getUser(p))
        else:
            await ctx.reply(getUser(p, g))

@client.command(aliases=['account'])
async def bal(ctx, user=None):
    peeppe = False
    if str(ctx.guild.id) in listedChannels["whitelist"]:
        if ctx.channel.id in listedChannels["whitelist"][str(ctx.guild.id)]:
            peeppe = True
    else:
        peeppe = True

    if peeppe:
        private = json.loads(open("./Bank Configs/privateAccounts.json", "r").read())
        if user == None:
            privateAcc = False
            run = False
            check = json.loads(open("./Shared Configs/human.json", "r").read())
            user = "user" + str(ctx.author.id)
            for peeps in check:
                if user == peeps:
                    run = True
                if user in private["private"]:
                    privateAcc = True
            if run:
                if privateAcc:
                    e = discord.Embed(title="Accounts", description="<@" + user.replace("user", "") + "> 's Account: \n " + DMoney(check[user]), color=0xff0073)
                    i = await ctx.author.create_dm()
                    await i.send(embed=e)
                else:
                    await ctx.reply(embed = discord.Embed(title="Accounts", description="<@" + user.replace("user", "") + "> 's Account: \n " + DMoney(check[user]), color=0xff0073))
            else:
                check[user] = 0
                open("./Shared Configs/human.json", "w").write(json.dumps(check))
                await ctx.reply(embed = discord.Embed(title="Accounts", description="<@" + user.replace("user", "") + "> 's Account: \n " + DMoney(check[user]), color=0xff0073))
        else:
            admin = False
            if str(ctx.author.id) in botConf["admins"]:
                admin = True
            privateAcc = False
            run = False
            check = json.loads(open("./Shared Configs/human.json", "r").read())
            try:
                int(user.replace("<", "").replace(">", "").replace("!","").replace("@", "").replace("&", ""))
            except ValueError:
                await ctx.reply("this is not a person")
            user = "user" + str(int(user.replace("<", "").replace(">", "").replace("!","").replace("@", "").replace("&", "")))
            for peeps in check:
                if user == peeps:
                    run = True
                if user in private["private"]:
                    privateAcc = True
            if run:
                if privateAcc and not admin:
                    await ctx.reply("This users account is private. You can't see their balance.")
                else:
                    await ctx.reply(embed = discord.Embed(title="Accounts", description="<@" + user.replace("user", "") + "> 's Account: \n " + DMoney(check[user]), color=0xff0073))
            else:
                check[user] = 0
                open("./Shared Configs/human.json", "w").write(json.dumps(check))
                await ctx.reply(embed = discord.Embed(title="Accounts", description="<@" + user.replace("user", "") + "> 's Account: \n " + DMoney(check[user]), color=0xff0073))

@client.command(aliases=['transfer'])
async def send(ctx, person, value):
    peeppe = False
    if str(ctx.guild.id) in listedChannels["whitelist"]:
        if ctx.channel.id in listedChannels["whitelist"][str(ctx.guild.id)]:
            peeppe = True
    else:
        peeppe = True

    if peeppe:
        try:
            value = float(value)
        except ValueError:
            await ctx.reply("This must be a number not a word")
            return
        if value <= 0:
            await ctx.message.delete()
            await ctx.reply("You are a poopy head for doing that.")
            return
        accepted = 0
        run = False
        run2 = False
        check = json.loads(open("./Shared Configs/human.json", "r").read())
        user = "user" + str(ctx.author.id)
        personId = person.replace("<", "").replace(">", "").replace("!","").replace("@", "").replace("&", "")
        try:
            int(personId)
        except ValueError:
            await ctx.reply("This is not a valid user")
            return
        person = "user" + personId
        if user == person:
            i = await ctx.reply("You cannot send yourself Money")
            await asyncio.sleep(10)
            await i.delete()
            return
        for peeps in check:#Checks if the person using the command has an account
            if user == peeps:
                run = True
        for peeps in check:#Checks if the person being sent money has an account
            if person == peeps:
                run2 = True
        if run:#if person 1 has an account
            if run2:#if person 2 has an account
                if check[user] >= value:#if person 1 has enough money
                    embed = discord.Embed(title = "Transaction", description="", color=0x529112)
                    embed.add_field(name="{} ---> {}".format(str(ctx.author)[:-5], str(client.get_user(int(personId)))[:-5]), value="{}\n Transaction Fee: {}%".format(DMoney(value), botConf["Transaction Fee %"]))
                    embed.set_footer(text="Click to Transfer Money")
                    i = await ctx.send(embed=embed)
                    await i.add_reaction('✅')
                    globals()[user + "_" + person] = transaction(value, i.id, ctx.author, client.get_user(int(personId)))
                else:
                    await ctx.reply(botConf["moneyless"])
            else:#if person 2 does not have an account
                check[person] = 0
                open("./Shared Configs/human.json", "w").write(json.dumps(check))
                if check[user] >= value:#if person 1 has enough money
                    embed = discord.Embed(title = "Transaction", description="", color=0x529112)
                    embed.add_field(name="{} ---> {}".format(str(ctx.author)[:-5], str(client.get_user(int(personId)))[:-5]), value="{}\n Transaction Fee: {}%".format(DMoney(value), botConf["Transaction Fee %"]))
                    embed.set_footer(text="Click to Transfer Money")
                    i = await ctx.send(embed=embed)
                    await i.add_reaction('✅')
                    globals()[user + "_" + person] = transaction(value, i.id, ctx.author, client.get_user(int(personId)))
                else:
                    await ctx.reply(botConf["moneyless"])
        else:#if person 1 does not have an account
            check[user] = 0
            open("./Shared Configs/human.json", "w").write(json.dumps(check))
            if run2:#if person 2 has an account
                await ctx.reply(botConf["moneyless"])
            else:#if person 2 does not have an account
                check[person] = 0
                open("./Shared Configs/human.json", "w").write(json.dumps(check))
                await ctx.reply(botConf["moneyless"])

@client.command()
async def cancel(ctx, investment):
    peeppe = False
    if str(ctx.guild.id) in listedChannels["whitelist"]:
        if ctx.channel.id in listedChannels["whitelist"][str(ctx.guild.id)]:
            peeppe = True
    else:
        peeppe = True

    if peeppe:
        run = False
        try:
            investment = int(investment)
        except ValueError:
            await ctx.reply("Please enter your investment number.")
            return
        file = json.loads(open("./Bank Configs/Gestation.json", "r").read())
        humans = json.loads(open("./Shared Configs/human.json", "r").read())
        user = "user" + str(ctx.author.id)
        for peep in file:
            if peep == user:
                run = True
        if run:
            try:
                file[user][investment-1]
            except IndexError:
                await ctx.reply("Try entering another account number.")
                return
            humans[user] = humans[user] + file[user][investment-1]["Value"]
            file[user].remove(file[user][investment-1])
            await ctx.reply("Successfully removed investment " + str(investment))
            try:
                file[user][0]
            except IndexError:
                file.pop(user)
            open("./Bank Configs/Gestation.json", "w").write(json.dumps(file))
            open("./Shared Configs/human.json", "w").write(json.dumps(humans))
        else:
            await ctx.reply("You do not have any Investments")


@client.command()
async def invest(ctx, value):
    peeppe = False
    if str(ctx.guild.id) in listedChannels["whitelist"]:
        if ctx.channel.id in listedChannels["whitelist"][str(ctx.guild.id)]:
            peeppe = True
    else:
        peeppe = True

    if peeppe:
        account = False
        run = False
        check = json.loads(open("./Shared Configs/human.json", "r").read())
        file = json.loads(open("./Bank Configs/Gestation.json", "r").read())
        user = "user" + str(ctx.author.id)
        for player in check:
            if user == player:
                run = True
        for peop in file:
            if user == peop:
                account = True
        if run:
            try:
                value = float(value)
            except ValueError:
                if value.lower() == 'all':
                    value = check[user]
                elif value.lower() == 'half':
                    value = check[user]//2
                else:
                    await ctx.reply("Use a real number")
                    return
            if value <= 0:
                await ctx.reply("Why would you want to do this, You lose money")
                return
            if account:
                if len(file[user]) >= 2:
                    await ctx.reply("I'm sorry but you have maxed investments")
                    return
            if value <= check[user]:
                if value <= 1000000:
                    now = datetime.datetime.now()
                    person = {"Value" : value, "TimeAdded" : str(now)}
                    check[user] -= value
                    try:
                        len(file[user])
                    except KeyError:
                        file[user] = []
                    file[user].append(person)
                    open("./Bank Configs/Gestation.json", 'w').write(json.dumps(file))
                    open("./Shared Configs/human.json", "w").write(json.dumps(check))
                    await ctx.reply("Succesfully invested {}".format(DMoney(value)))
                else:
                    await ctx.reply("I'm sorry but you cannot invest more than {}1,000,000".format(creditEmoji))
            else:
                await ctx.reply("You do not have enough money.")
        else:
            check[user] = 0
            open("./Shared Configs/human.json", "w").write(json.dumps(check))
            await ctx.reply("You do not have enough money.")

@client.command()
async def invested(ctx):
    if str(ctx.author.id) in botConf["admins"]:
        op = json.loads(open("./Bank Configs/Gestation.json").read())
        total = 0
        for i in op:
            for j in range(len(op[i])):
                total = total + op[i][j]["Value"]
        em = discord.Embed(title="Everything Invested", description="The total amount of money currently invested is:\n{}".format(DMoney(total)), color=0xa8ff61)
        await ctx.reply(embed=em)

@client.command()
async def investments(ctx, account=None):
    peeppe = False
    if str(ctx.guild.id) in listedChannels["whitelist"]:
        if ctx.channel.id in listedChannels["whitelist"][str(ctx.guild.id)]:
            peeppe = True
    else:
        peeppe = True

    if peeppe:
        run = False
        private = False
        file = json.loads(open("./Bank Configs/Gestation.json", "r").read())
        private = json.loads(open("./Bank Configs/privateAccounts.json", "r").read())
        check = json.loads(open("./Shared Configs/human.json", "r").read())
        if account == None:
            user = "user" + str(ctx.author.id)
            for humans in file:
                if humans == user:
                    run = True
            for humans in private["private"]:
                if user == humans:
                    private = True
            if run:
                em = discord.Embed(title="Investment", description=f"{ctx.author.mention}'s investments", color=0xa8ff61)
                for i in range(len(file[user])):
                    interest = 0
                    amount = file[user][i]["Value"]
                    interest += investmentInterest(amount)
                    start = datetime.datetime.strptime(file[user][i]["TimeAdded"], '%Y-%m-%d %H:%M:%S.%f')
                    end = datetime.timedelta(days=7)
                    dif = start + end
                    sde = str(dif - datetime.datetime.now())[:-7].split(" ")
                    if len(sde) <= 1:
                        timeed = sde[0].split(":")
                        finalStr = "0 Days, {} Hours, {} Minutes, {} Seconds".format(timeed[0], timeed[1], timeed[2])
                    else:
                        sde[1] = sde[1].replace(",", "")
                        timeed = sde[2].split(":")
                        sde.pop(2)
                        finalStr = " ".join(sde) + ", " + "{} Hours, {} Minutes, {} Seconds".format(timeed[0], timeed[1], timeed[2])
                    em.add_field(name="Investment {}".format(i+1), value="Amount In: {}\nAmount Out: {}\nWill Be Ready in {}".format(DMoney(file[user][i]["Value"]), DMoney(amount + interest), finalStr))
                if private == True:
                    i = await ctx.author.create_dm()
                    await i.send(embed=em)
                else:
                    await ctx.reply(embed=em)
            else:
                await ctx.reply("You do not have any current investments")
        else:
            admin = False
            if str(ctx.author.id) in botConf["admins"]:
                admin = True
            try:
                temp_user = await client.fetch_user(int(account.replace("<", "").replace(">", "").replace("!","").replace("@", "").replace("&", "")))
                user = "user" + str(temp_user.id)
            except discord.errors.NotFound:
                await ctx.send("Sorry I couldn't find this user")
                return
            except ValueError:
                await ctx.send("Please @ the player.")
                return
            for humans in file:
                if humans == user:
                    run = True
            for humans in private["private"]:
                if user == humans:
                    private = True
            if run:
                em = discord.Embed(title="Investment", description=f"{temp_user.mention}'s investments", color=0xa8ff61)
                for i in range(len(file[user])):
                    interest = 0
                    amount = file[user][i]["Value"]
                    interest += investmentInterest(amount)
                    start = datetime.datetime.strptime(file[user][i]["TimeAdded"], '%Y-%m-%d %H:%M:%S.%f')
                    end = datetime.timedelta(days=7)
                    dif = start + end
                    sde = str(dif - datetime.datetime.now())[:-7].split(" ")
                    if len(sde) <= 1:
                        timeed = sde[0].split(":")
                        finalStr = "0 Days, {} Hours, {} Minutes, {} Seconds".format(timeed[0], timeed[1], timeed[2])
                    else:
                        sde[1] = sde[1].replace(",", "")
                        timeed = sde[2].split(":")
                        sde.pop(2)
                        finalStr = " ".join(sde) + ", " + "{} Hours, {} Minutes, {} Seconds".format(timeed[0], timeed[1], timeed[2])
                    em.add_field(name="Investment {}".format(i+1), value="Amount In: {}\nAmount Out: {}\nWill Be Ready in {}".format(DMoney(file[user][i]["Value"]), DMoney(amount + interest), finalStr))
                if private == True and admin == False:
                    i = await ctx.author.create_dm()
                    await i.send(embed=em)
                else:
                    await ctx.reply(embed=em)
            else:
                await ctx.reply("This person does not have any current investments")


@client.command()
async def profit(ctx, x, y, z):
    if str(ctx.author.id) in botConf["admins"]:
        try:
            y = float(y)
            x = float(x)
            z = float(z)
        except ValueError:
            await ctx.send("Maker sure they are all numbers")
            return
        difference = y - x
        amount = difference*z
        cp = x/difference
        percent = 100/cp
        embed = discord.Embed(title="Profit", description="Buy Amount: {}\nSell Amount: {}\n Amount: {}".format(x, y, z), color=0xa8ff61)
        embed.add_field(name="These are the stats", value="**Profit:** {}\n**Credits per Credit: **{}\n**Return:** %{}".format(DMoney(amount), round(cp, 1), round(percent, 2)))
        await ctx.reply(embed=embed)

@client.command()
async def price(ctx, Value=None, ore=None):
    run = False
    if str(ctx.guild.id) in listedChannels["whitelist"]:
        if ctx.channel.id in listedChannels["whitelist"][str(ctx.guild.id)]:
            run = True
    else:
        run = True

    if run:
        if ore == None or Value == None:
            em = discord.Embed(title="Material Prices", description="Here are the prices for each material", color=0xffffff)
            for i in marketPrice:
                em.add_field(name=i, value=DMoney(marketPrice[i]))
            await ctx.reply(embed=em)
        else:
            try:
                Value = int(Value)
            except ValueError:
                await ctx.reply("This is not a number")
                return
            try:
                marketPrice[ore.lower()]
            except KeyError:
                await ctx.reply("Please enter the material using these spellings\n`Korrelite`\n`Reknite`\n`Gellium`\n`Axnit`\n`BNarcor`\n`RNarcor`")
                return
            em = discord.Embed(title="Material Price", description="Here is how much {} {} will get you".format(Value, ore), color=0xffffff)
            em.add_field(name="{} {}".format(Value, ore), value="cost: {}".format(DMoney(Value * marketPrice[ore.lower()])))
            await ctx.reply(embed=em)

@client.command()
async def privatise(ctx, user):
    if str(ctx.author.id) in botConf["admins"]:
        run = False
        try:
            int(user.replace("<", "").replace(">", "").replace("!","").replace("@", "").replace("&", ""))
        except ValueError:
            await ctx.send("This is not a person")
            return
        player = client.get_user(int(user.replace("<", "").replace(">", "").replace("!","").replace("@", "").replace("&", "")))
        user = "user" + str(player.id)
        humans = json.loads(open("./Shared Configs/human.json", "r").read())
        private = json.loads(open("./Bank Configs/privateAccounts.json", "r").read())
        for human in humans:
            if human == user:
                run = True
        if run:
            if user in private["private"]:
                await ctx.send("This persons account is already private!")
                return
            else:
                private["private"].append(user)
                open("./Bank Configs/privateAccounts.json", "w").write(json.dumps(private))
                await ctx.send("Account has been privatised.")
        else:
            humans[user] = 0
            private["private"].append(user)
            open("./Shared Configs/human.json", "w").write(json.dumps(humans))
            open("./Bank Configs/privateAccounts.json", "w").write(json.dumps(private))
            await ctx.send("Account has been privatised.")

@client.command()
async def deprivatise(ctx, user):
    if str(ctx.author.id) in botConf["admins"]:
        run = False
        try:
            int(user.replace("<", "").replace(">", "").replace("!","").replace("@", "").replace("&", ""))
        except ValueError:
            await ctx.send("This is not a person")
            return
        player = client.get_user(int(user.replace("<", "").replace(">", "").replace("!","").replace("@", "").replace("&", "")))
        user = "user" + str(player.id)
        humans = json.loads(open("./Shared Configs/human.json", "r").read())
        private = json.loads(open("./Bank Configs/privateAccounts.json", "r").read())
        for human in humans:
            if human == user:
                run = True
        if run:
            if user in private["private"]:
                private["private"].remove(user)
                open("./Bank Configs/privateAccounts.json", "w").write(json.dumps(private))
                await ctx.send("Account has been deprivatised.")
                return
            else:
                await ctx.send("Account is already deprivatised.")
        else:
            await ctx.send("This user does not have an account")


@client.command()
async def interest(ctx, p, r, n=None, t=None):
    if str(ctx.author.id) in botConf["admins"]:
        try:
            p = float(p.replace("$", "").replace(",", ""))
            r = float(r.replace("%", ""))/100
            n = int(n) if n!= None else 1
            t = int(t) if t!= None else 1
        except ValueError:
            await ctx.send("Please enter a number.")
            return
        await ctx.reply(Money(compoundInterest(p, r, n, t)))

@client.command()
async def Ideal(ctx, reliable, invested):
    if str(ctx.author.id) in botConf["admins"]:
        try:
            reliable = float(reliable.replace("$", "").replace(",", ""))
            invested = float(invested.replace("$", "").replace(",", ""))
        except ValueError:
            await ctx.send("Enter a number please")
            return
        embedArr = []
        embedArr.append(discord.Embed(title="Ideal Interest Amount", description="", color=0xa8ff61))
        embednum = 0
        d = 0
        interest = 0
        while interest < reliable:
            try:
                embedArr[embednum//25]
            except IndexError:
                embedArr.append(discord.Embed(title="", description="",color=0xa8ff61))
            d += 0.01
            i = round(d, 2)
            interest = compoundInterest(invested, i, 1, 1)
            embedArr[embednum//25].add_field(name="Percent: {}%".format(int(round(i * 100))), value="Interest: {}\nDifference: {}".format(DMoney(interest), DMoney(reliable - interest)))
            embednum += 1
        embedArr[embednum//26].set_footer(text="Ideal Interest: {}%".format(int(round((i - 0.01) * 100))))
        for i in embedArr:
            await asyncio.sleep(1)
            await ctx.send(embed=i)

@client.command()
async def add(ctx, user, value):
    if str(ctx.author.id) in botConf["admins"]:
        try:
            value = float(value)
        except ValueError:
            await ctx.send("This is an invalid number")
            return
        try:
            int(user.replace("<", "").replace(">", "").replace("!","").replace("@", "").replace("&", ""))
        except ValueError:
            await ctx.send("This is not a user")
            return
        player = await client.fetch_user(int(user.replace("<", "").replace(">", "").replace("!","").replace("@", "").replace("&", "")))
        user = "user" + str(player.id)
        check = json.loads(open("./Shared Configs/human.json", "r").read())
        if user in check:
            check[user] = check[user] + value
            try:
                name = client.get_user(int(user.replace("user", ""))).name
            except AttributeError:
                name = user.replace("user", "")
            ws4.append_row([str(ctx.author)[:-5], Money(value), "Add", name])
            await ctx.send("Money added successfully")
            open("./Shared Configs/human.json", "w").write(json.dumps(check))
        else:
            check[user] = value
            try:
                name = client.get_user(int(user.replace("user", ""))).name
            except AttributeError:
                name = user.replace("user", "")
            ws4.append_row([str(ctx.author)[:-5], Money(value), "Add", name])
            await ctx.send("Money added successfully")
            open("./Shared Configs/human.json", "w").write(json.dumps(check))

@client.command()
async def remove(ctx, user, value):
    if str(ctx.author.id) in botConf["admins"]:
        try:
            value = float(value)
        except ValueError:
            await ctx.send("This is an invalid number")
            return
        try:
            int(user.replace("<", "").replace(">", "").replace("!","").replace("@", "").replace("&", ""))
        except ValueError:
            await ctx.send("This is not a user")
            return
        player = await client.fetch_user(int(user.replace("<", "").replace(">", "").replace("!","").replace("@", "").replace("&", "")))
        user = "user" + str(player.id)
        check = json.loads(open("./Shared Configs/human.json", "r").read())
        if user in check:
            if check[user] - value < 0:
                await ctx.send("This user cannot lose money")
            else:
                check[user] = check[user] - value
                try:
                    name = client.get_user(int(user.replace("user", ""))).name
                except AttributeError:
                    name = user.replace("user", "")
                ws4.append_row([str(ctx.author)[:-5], Money(value), "Remove", name])
                await ctx.send("Money removed successfully")
                open("./Shared Configs/human.json", "w").write(json.dumps(check))
        else:
            check[user] = 0
            try:
                name = client.get_user(int(user.replace("user", ""))).name
            except AttributeError:
                name = user.replace("user", "")
            ws4.append_row([str(ctx.author)[:-5], Money(value), "Remove", name])
            await ctx.send("This user cannot lose money")
            open("./Shared Configs/human.json", "w").write(json.dumps(check))

@client.command()
async def whitelist(ctx):
    if str(ctx.author.id) in botConf["admins"]:
        try:
            if ctx.channel.id in listedChannels["whitelist"][str(ctx.guild.id)]:
                await ctx.send("Channel already whitelisted")
                return
            else:
                listedChannels["whitelist"][str(ctx.guild.id)].append(ctx.channel.id)
                await ctx.send("Channel has been whitelisted")
                saveWhitelist()
                return
        except KeyError:
            listedChannels["whitelist"][str(ctx.guild.id)] = []
            listedChannels["whitelist"][str(ctx.guild.id)].append(ctx.channel.id)
            await ctx.send("Channel has been whitelisted")
            saveWhitelist()
            return

@client.command()
async def unwhitelist(ctx):
    if str(ctx.author.id) in botConf["admins"]:
        try:
            if ctx.channel.id in listedChannels["whitelist"][str(ctx.guild.id)]:
                listedChannels["whitelist"][str(ctx.guild.id)].remove(ctx.channel.id)
                if len(listedChannels["whitelist"][str(ctx.guild.id)]) == 0:
                    listedChannels["whitelist"].pop(str(ctx.guild.id))
                saveWhitelist()
                await ctx.send("Channel has been unwhitelisted")
                return
            else:
                await ctx.send("Channel already open")
                return
        except KeyError:
            await ctx.send("Channel already open")
            return


async def update():
    while True:
        print("Starting...")
        startTime = time.time()
        marketPrice = {"korrelite": float(worksheet2.get("C13")[0][0]), "reknite": float(worksheet2.get("D13")[0][0]),
                    "gellium": float(worksheet2.get("E13")[0][0]), "axnit": float(worksheet2.get("F13")[0][0]),
                    "bnarcor": float(worksheet2.get("G13")[0][0]), "rnarcor": float(worksheet2.get("H13")[0][0])}
        interest = 0
        invested = {}
        cell_list = ws.range(f'A2:B100')
        for cell in cell_list:
            cell.value = ''
        ws.update_cells(cell_list)
        cell_list = ws.range(f'E2:F100')
        for cell in cell_list:
            cell.value = ''
        ws.update_cells(cell_list)
        i = 2
        balance = json.loads(open("./Shared Configs/human.json", "r").read())
        suggestions = json.loads(open("./Shared Configs/suggestions.json", "r").read())
        investment = json.loads(open("./Bank Configs/Gestation.json", "r").read())
        for p in investment:
            tot = 0
            for j in range(len(investment[p])):
                val = investment[p][j]["Value"]
                interest += investmentInterest(val)
                tot += val
            invested[p] = tot
        invested1 = sorted(invested.items(), key=lambda x: x[1], reverse=True)
        balance1 = sorted(balance.items(), key=lambda x: x[1], reverse=True)
        await asyncio.sleep(2)
        for users in balance1:
            total = 0
            try:
                for e in range(len(investment[users[0]])):
                    total += investment[users[0]][e]["Value"]
            except KeyError:
                total = 0
            user = users[0].replace("user", "")
            if users[0] == "Main Account":
                continue
            if balance[users[0]] <= 0:
                continue
            try:
                name = client.get_user(int(user)).name
            except AttributeError:
                name = user
            await asyncio.sleep(1)
            ws.update_cell(i, 1, name)
            await asyncio.sleep(1)
            ws.update_cell(i, 2, Money(balance[users[0]]))
            i += 1
        i = 2
        await asyncio.sleep(10)
        for users in invested1:
            user = users[0].replace("user", "")
            try:
                name = client.get_user(int(user)).name
            except AttributeError:
                name = user
            await asyncio.sleep(1)
            ws.update_cell(i, 5, name)
            await asyncio.sleep(1)
            ws.update_cell(i, 6, Money(users[1]))
            i += 1
        ws.update_cell(25, 4, interest)
        for e in range(len(suggestions["suggestion"])):
            await asyncio.sleep(1)
            sug = suggestions["suggestion"][e]
            ws3.append_row([sug["user"], sug["suggested"]])
        open("./Shared Configs/suggestions.json", "w").write('{"suggestion" : []}')
        endTime = time.time()
        print("Finished in {} Seconds".format(endTime - startTime))
        await asyncio.sleep(7200)

async def check_investment():
    while True:
        print("Checking")
        file = json.loads(open("./Bank Configs/Gestation.json", "r").read())
        file2 = copy.deepcopy(file)
        humans = json.loads(open("./Shared Configs/human.json", "r").read())

        for people in file:
            for i in range(len(file[people])):
                date_time_str = file[people][i]["TimeAdded"]
                timeAdded = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
                timeReady =  timeAdded + datetime.timedelta(days=7)
                currentTime = datetime.datetime.now()
                if timeReady < currentTime:
                    if False:
                        amount = file[people][i]["Value"]
                        recieve = amount + ((config["Added Interest"] / 100) * amount)
                        file2[people][i]["Value"] = recieve
                        file2[people][i]["TimeAdded"] = str(datetime.datetime.now())
                    else:
                        interest = 0
                        amount = file[people][i]["Value"]
                        interest += investmentInterest(amount)
                        recieve = amount + interest
                        file2[people].remove(file[people][i])
                        try:
                            file2[people][0]
                        except IndexError:
                            file2.pop(people)
                        humans[people] = humans[people] + recieve
        open("./Bank Configs/Gestation.json", "w").write(json.dumps(file2))
        open("./Shared Configs/human.json", "w").write(json.dumps(humans))
        await asyncio.sleep(300)

client.run(botConf["api"])
